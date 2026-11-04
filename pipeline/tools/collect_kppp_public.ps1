param(
    [int[]]$NoticeIds = @(29761, 19567),
    [string]$OutputDirectory = (Join-Path $PSScriptRoot 'kppp-public-evidence'),
    [switch]$DiscoverClient,
    [switch]$CountBdaStatuses,
    [switch]$PortalSnapshot,
    [switch]$ExportBdaIndex
)

$ErrorActionPreference = 'Stop'
$baseUrl = 'https://kppp.karnataka.gov.in'
$portalPath = '/supplier-registration-service/v1/api/portal-service'
$requests = New-Object 'System.Collections.Generic.List[object]'
$collected = New-Object 'System.Collections.Generic.List[object]'
$timestamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
$OutputDirectory = Join-Path $OutputDirectory $timestamp
$null = New-Item -ItemType Directory -Path $OutputDirectory -Force

function Write-JsonFile($Name, $Value) {
    $json = ConvertTo-Json -InputObject $Value -Depth 80
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Join-Path $OutputDirectory $Name), $json, $encoding)
}

function Invoke-PublicJson($Path, $Body = $null) {
    $method = if ($null -eq $Body) { 'GET' } else { 'POST' }
    if ($method -eq 'POST' -and $Path -notmatch '^/search/(auction-search|auctions-ending-today)\?') {
        throw "Only read-only search POSTs are allowed: $Path"
    }
    $parameters = @{
        Uri = "$baseUrl$portalPath$Path"
        Method = $method
        UseBasicParsing = $true
        TimeoutSec = 30
        Headers = @{ Accept = 'application/json' }
    }
    if ($null -ne $Body) {
        $parameters.ContentType = 'application/json'
        $parameters.Body = ConvertTo-Json -InputObject $Body -Compress
    }
    $record = [ordered]@{
        fetchedAtUtc = [DateTime]::UtcNow.ToString('o')
        method = $method
        url = $parameters.Uri
        requestBody = $Body
        status = $null
        totalCount = $null
        data = $null
        error = $null
    }
    try {
        $response = Invoke-WebRequest @parameters
        $record.status = [int]$response.StatusCode
        $record.totalCount = $response.Headers['X-Total-Count']
        $parsed = ConvertFrom-Json -InputObject $response.Content
        if ($response.Content.TrimStart().StartsWith('[')) {
            $record.data = @($parsed | ForEach-Object { $_ })
        }
        else {
            $record.data = $parsed
        }
    }
    catch {
        if ($null -ne $_.Exception.Response) {
            $record.status = [int]$_.Exception.Response.StatusCode
        }
        $record.error = $_.Exception.Message
        if ($record.status -in @(401, 403, 429)) {
            $requests.Add([pscustomobject]$record)
            Write-JsonFile 'requests.json' $requests.ToArray()
            throw "Stopped on HTTP $($record.status); do not bypass access or rate controls."
        }
    }
    $requests.Add([pscustomobject]$record)
    Write-JsonFile 'requests.json' $requests.ToArray()
    if ($null -ne $record.error) { throw "Request failed: $method $Path; see requests.json." }
    Write-Host "$method $Path -> $($record.status)"
    return [pscustomobject]$record
}

foreach ($noticeId in $NoticeIds) {
    if ($noticeId -le 0) { throw 'Notice IDs must be positive integers.' }
    $view = Invoke-PublicJson "/$noticeId/view-auction"
    $documents = Invoke-PublicJson "/$noticeId/auction-documents"
    $corrigenda = Invoke-PublicJson "/$noticeId/auction-corrigendum"
    $recallDocuments = Invoke-PublicJson "/$noticeId/get-recall-auction-documents"
    $slots = New-Object 'System.Collections.Generic.List[object]'
    foreach ($slot in @($view.data.auctionBiddingSlotDTO)) {
        if ($null -eq $slot.id) { continue }
        $slotId = [int]$slot.id
        if ($view.data.auctionNoticeDTO.itemGroupType -eq 'LOT_WISE') {
            $lots = Invoke-PublicJson "/$noticeId/bidding-slot/$slotId/get-all-lots"
            $slots.Add([pscustomobject]@{ slotId = $slotId; lots = $lots.data })
        }
        elseif ($view.data.auctionNoticeDTO.itemGroupType -eq 'ITEM_WISE') {
            $items = Invoke-PublicJson "/$noticeId/slot/$slotId/get-all-items"
            $slots.Add([pscustomobject]@{ slotId = $slotId; items = $items.data })
        }
        else { throw "Unknown auction group type for notice $noticeId." }
    }
    $changes = New-Object 'System.Collections.Generic.List[object]'
    foreach ($corrigendum in @($corrigenda.data)) {
        if ($null -eq $corrigendum.id) { continue }
        $corrigendumId = [int]$corrigendum.id
        $detail = Invoke-PublicJson "/$noticeId/auction-corrigendum/$corrigendumId/get-auction-corrigendum"
        $files = Invoke-PublicJson "/$noticeId/auction-corrigendum/$corrigendumId/get-auction-corrigendum-files"
        $changes.Add([pscustomobject]@{ id = $corrigendumId; detail = $detail.data; files = $files.data })
    }
    $collected.Add([pscustomobject]@{
        noticeId = $noticeId
        view = $view.data
        documents = $documents.data
        slots = $slots.ToArray()
        corrigenda = $corrigenda.data
        changes = $changes.ToArray()
        recallDocuments = $recallDocuments.data
    })
}

if ($CountBdaStatuses -or $ExportBdaIndex) {
    $indexById = @{}
    foreach ($status in @('PUBLISHED', 'LIVE_AUCTION', 'BIDDING_CLOSED', 'NO_PARTICIPATIONS', 'NO_BIDS_RECEIVED', 'CANCELLED', 'UNDER_EVALUATION', 'EVALUATED', 'FINALIZED')) {
        $pageNumber = 0
        $pageSize = if ($ExportBdaIndex) { 100 } else { 1 }
        $seen = 0
        $expected = $null
        do {
            $search = Invoke-PublicJson "/search/auction-search?page=$pageNumber&size=$pageSize" @{ auctionStatus = $status; departmentId = 1566 }
            if ($null -eq $search.totalCount) { throw 'Missing X-Total-Count; completeness cannot be checked.' }
            $total = [int]$search.totalCount
            if ($null -eq $expected) { $expected = $total }
            elseif ($total -ne $expected) { throw "Count changed while collecting $status; retry later." }
            if ($ExportBdaIndex) {
                foreach ($row in @($search.data)) {
                    if ($null -eq $row.auctionNoticeId) { throw 'Search row has no auctionNoticeId.' }
                    $key = [string]$row.auctionNoticeId
                    if ($indexById.ContainsKey($key)) { throw "Duplicate notice $key; snapshot changed or pagination repeated." }
                    $copy = $row.PSObject.Copy()
                    $copy | Add-Member -NotePropertyName statusKey -NotePropertyValue $status
                    $indexById[$key] = $copy
                }
                $seen += @($search.data).Count
                if (@($search.data).Count -eq 0 -and $seen -lt $total) { throw "Unexpected empty page for $status." }
                if (@($search.data).Count -lt $pageSize -and $seen -lt $total) { throw 'Server page size changed; refusing to silently truncate the index.' }
                if ($seen -gt $total) { throw "Search returned more rows than its total for $status." }
            }
            $pageNumber++
            if ($pageNumber -gt 200) { throw 'Page safety limit reached.' }
        } while ($ExportBdaIndex -and $seen -lt $total)
    }
    if ($ExportBdaIndex) {
        $index = @($indexById.Values | Sort-Object auctionNoticeId)
        Write-JsonFile 'bda-auction-index.json' $index
        $index | Export-Csv -LiteralPath (Join-Path $OutputDirectory 'bda-auction-index.csv') -NoTypeInformation -Encoding UTF8
        Write-Host "Saved $($index.Count) unique BDA notice records."
    }
}

if ($PortalSnapshot) {
    foreach ($path in @('/metrics/get-count', '/metrics/get-portal-metrics', '/get-current-time', '/ANNOUNCEMENTS/get-portal-announcements', '/EVENTS/get-portal-announcements', '/departments/activeDepartment')) {
        $null = Invoke-PublicJson $path
    }
    $null = Invoke-PublicJson '/search/auctions-ending-today?page=0&size=1' @{ auctionStatus = 'LIVE_AUCTION' }
}

if ($DiscoverClient) {
    $references = New-Object 'System.Collections.Generic.List[object]'
    $sources = New-Object 'System.Collections.Generic.List[object]'
    foreach ($bundle in @('main.js', 'common.js', '976.js')) {
        $response = Invoke-WebRequest -Uri "$baseUrl/$bundle" -UseBasicParsing -TimeoutSec 30
        $source = [string]$response.Content
        $hasher = [System.Security.Cryptography.SHA256]::Create()
        try {
            $digest = $hasher.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($source))
            $hash = [BitConverter]::ToString($digest).Replace('-', '').ToLowerInvariant()
        }
        finally { $hasher.Dispose() }
        $sources.Add([pscustomobject]@{ url = "$baseUrl/$bundle"; characters = $source.Length; sha256Utf8 = $hash })
        $matches = [regex]::Matches($source, 'this\._?http\.(get|post|put|delete|patch)\(')
        foreach ($match in $matches) {
            $length = [Math]::Min(900, $source.Length - $match.Index)
            $expression = $source.Substring($match.Index, $length)
            $boundary = [regex]::Match($expression, '\}(?:[\w$]+\(|\}return)')
            if ($boundary.Success) { $expression = $expression.Substring(0, $boundary.Index + 1) }
            $references.Add([pscustomobject]@{
                source = $bundle
                characterOffset = $match.Index
                method = $match.Groups[1].Value.ToUpperInvariant()
                expression = $expression
                verification = 'CLIENT_REFERENCE_ONLY'
            })
        }
    }
    Write-JsonFile 'client-http-references.json' ([ordered]@{
        scope = 'Heuristic HTTP call-site inventory of main.js, common.js and auction corrigendum chunk 976.js; not an exhaustive backend API specification. Nothing discovered here is automatically called.'
        sources = $sources.ToArray()
        references = $references.ToArray()
    })
}

Write-JsonFile 'auctions.json' $collected.ToArray()
Write-JsonFile 'requests.json' $requests.ToArray()
Write-Host "Saved $($collected.Count) auctions and $($requests.Count) request records to $OutputDirectory"