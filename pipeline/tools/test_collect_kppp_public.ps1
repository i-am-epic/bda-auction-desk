$ErrorActionPreference = 'Stop'
$collector = Join-Path $PSScriptRoot 'collect_kppp_public.ps1'
$testRoot = Join-Path $PSScriptRoot ('kppp-public-evidence/tests-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'))

function Invoke-WebRequest {
    param($Uri, $Method, $Headers, $ContentType, $Body, [switch]$UseBasicParsing, $TimeoutSec)

    if ($Method -ne 'POST' -or $Uri -notmatch '^https://kppp\.karnataka\.gov\.in/supplier-registration-service/v1/api/portal-service/search/auction-search\?page=\d+&size=100$') {
        throw "Unexpected request in offline test: $Method $Uri"
    }
    $criteria = ConvertFrom-Json -InputObject $Body
    if ($criteria.departmentId -ne 1566) { throw 'Missing BDA department filter.' }
    $pageNumber = [int]([regex]::Match($Uri, '[?&]page=(\d+)').Groups[1].Value)
    $total = if ($criteria.auctionStatus -eq 'FINALIZED') { 101 } else { 0 }
    $rows = @()
    if ($total -gt 0) {
        $first = $pageNumber * 100 + 1
        $last = [Math]::Min($first + 99, 101)
        $rows = @(for ($identifier = $first; $identifier -le $last; $identifier++) {
            $noticeId = if ($mode -eq 'duplicate' -and $pageNumber -eq 1) { 100 } else { $identifier }
            [pscustomobject]@{ auctionNoticeId = $noticeId; auctionNoticeNumber = "BDA/TEST/AUCTION$noticeId" }
        })
        if ($mode -eq 'changing-count' -and $pageNumber -eq 1) { $total = 102 }
        if ($mode -eq 'truncated' -and $pageNumber -eq 0) { $rows = @($rows[0]) }
    }
    $content = if ($mode -eq 'invalid-json') { 'not-json' } else { ConvertTo-Json -InputObject $rows -Compress }
    return [pscustomobject]@{ StatusCode = 200; Headers = @{ 'X-Total-Count' = [string]$total }; Content = $content }
}

$expectedErrors = @{
    duplicate = 'Duplicate notice'
    'changing-count' = 'Count changed'
    truncated = 'Server page size changed'
    'invalid-json' = 'Request failed'
}

foreach ($mode in @('success', 'duplicate', 'changing-count', 'truncated', 'invalid-json')) {
    $output = Join-Path $testRoot $mode
    $failure = $null
    try { & $collector -NoticeIds @() -ExportBdaIndex -OutputDirectory $output }
    catch { $failure = $_.Exception.Message }

    if ($mode -eq 'success') {
        if ($failure) { throw "Successful fixture failed: $failure" }
        $directory = Get-ChildItem -LiteralPath $output -Directory | Select-Object -First 1
        $index = Get-Content (Join-Path $directory.FullName 'bda-auction-index.json') -Raw | ConvertFrom-Json
        if ($index.Count -ne 101 -or @($index | Select-Object -ExpandProperty auctionNoticeId -Unique).Count -ne 101) {
            throw 'Index completeness assertion failed.'
        }
        if (@($index | Where-Object { $_.statusKey -ne 'FINALIZED' }).Count) { throw 'Canonical status was not preserved.' }
        $csv = @(Import-Csv -LiteralPath (Join-Path $directory.FullName 'bda-auction-index.csv'))
        if ($csv.Count -ne 101) { throw 'CSV row count assertion failed.' }
    }
    elseif (-not $failure -or $failure -notlike "*$($expectedErrors[$mode])*") {
        throw "Expected $mode failure, got: $failure"
    }

    $directory = Get-ChildItem -LiteralPath $output -Directory | Select-Object -First 1
    $records = Get-Content (Join-Path $directory.FullName 'requests.json') -Raw | ConvertFrom-Json
    if (-not $records.Count) { throw 'Request evidence was not retained.' }
    if ($mode -eq 'invalid-json' -and -not $records[-1].error) { throw 'JSON failure was not recorded.' }
    Write-Host "PASS: $mode"
}

Write-Host 'All 5 offline collector checks passed. No network requests were made.'