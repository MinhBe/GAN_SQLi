$inputFile = "C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data.csv"
$outputFile = "C:\Projects\GAN_SQLi\Training-data\LabelData\batches_labeled\labeled_batch_11001_12000.csv"

$validTypes = @('error_based', 'boolean_blind', 'time_blind', 'union_based')
$validEngines = @('oracle', 'mysql', 'postgresql', 'mssql', 'sqlite', 'generic')
$validConfidence = @('0.70', '0.85', '1.00')

$timeMarkers = @('sleep(', 'pg_sleep(', 'WAITFOR', 'dbms_pipe.receive_message', 'benchmark(',
    'generate_series(1,5000000)', 'randomblob(500000000)', 'repeat(', 'regexp_substring')

$errorMarkers = @('xmltype(', 'extractvalue(', 'updatexml(', 'floor(rand(', 'utl_inaddr', 'ctxsys.drithsx.sn')

$oracleMarkers = @('xmltype(', 'dbms_pipe', 'utl_inaddr', 'sys_context', 'from dual', 'ctxsys', 'rownum')
$mysqlMarkers = @('sleep(', 'benchmark(', 'floor(rand(', 'extractvalue(', 'updatexml(', 'information_schema.', '@@version', '@@datadir', 'load_file(')
$pgsqlMarkers = @('pg_sleep(', 'generate_series(', '::text', '::int', '::numeric', '::boolean', 'string_agg(', 'array_agg(')
$mssqlMarkers = @('WAITFOR DELAY', 'WAITFOR', 'master..sysdatabases', 'xp_cmdshell', 'sysobjects', 'syscolumns', 'sysusers')
$sqliteMarkers = @('randomblob(', 'sqlite_version(', 'sqlite_master')

function Get-SqliType($payloadNorm, $dbEngine) {
    $lower = $payloadNorm.ToLower()

    # Check time_blind markers (highest priority)
    foreach ($marker in $timeMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) {
            # Special case: dbms_pipe with xmltype is error_based, not time_blind
            if ($m -eq 'dbms_pipe.receive_message' -and $lower.Contains('xmltype(')) {
                return 'error_based'
            }
            return 'time_blind'
        }
    }

    # Check error_based markers
    foreach ($marker in $errorMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'error_based' }
    }

    # convert(int, + string pattern - MSSQL conversion error
    if ($lower -match 'convert\s*\(\s*int\s*,' -and $lower -match '\bselect\b') { return 'error_based' }
    # 1/ + select pattern - division by zero error
    if ($lower -match '1/' -and ($lower -match '\(?\s*select\s+0' -or $lower -match 'select\s+0\s+from\s+dual')) { return 'error_based' }
    # cast.*as int + / pattern
    if ($lower -match 'cast.*as\s+int' -and $lower -match '/') { return 'error_based' }

    # Check union_based markers
    if ($lower -match '\bunion\s+(all\s+)?select\b') { return 'union_based' }
    if ($lower -match '\border\s+by\s+\d+') { return 'union_based' }

    # Default: boolean_blind
    return 'boolean_blind'
}

function Get-DbEngine($payloadNorm) {
    $lower = $payloadNorm.ToLower()

    # Oracle markers (highest priority)
    foreach ($marker in $oracleMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'oracle' }
    }
    if ($lower -match 'chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr\s*\(\s*\d+\s*\)') { return 'oracle' }

    # PostgreSQL markers
    foreach ($marker in $pgsqlMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'postgresql' }
    }

    # MSSQL markers
    foreach ($marker in $mssqlMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'mssql' }
    }

    # MySQL markers
    foreach ($marker in $mysqlMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'mysql' }
    }
    if ($lower.EndsWith('#')) { return 'mysql' }

    # SQLite markers
    foreach ($marker in $sqliteMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'sqlite' }
    }

    return 'generic'
}

function Get-Confidence($payloadNorm, $sqliType, $dbEngine) {
    $lower = $payloadNorm.ToLower()
    $tokenCount = $lower.Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries).Count

    # Count distinct markers for type and engine
    $typeMarkersFound = @()
    $timeMarkersFound = 0; $errorMarkersFound = 0; $unionMarkersFound = 0

    foreach ($m in $timeMarkers) {
        if ($lower.Contains($m.ToLower())) { $timeMarkersFound++ }
    }
    foreach ($m in $errorMarkers) {
        if ($lower.Contains($m.ToLower())) { $errorMarkersFound++ }
    }
    if ($lower -match '\bunion\s+(all\s+)?select\b') { $unionMarkersFound++ }
    if ($lower -match '\border\s+by\s+\d+') { $unionMarkersFound++ }

    # More than 1 marker of the same type = confident 1.00
    if ($timeMarkersFound -ge 2) { return '1.00' }
    if ($errorMarkersFound -ge 2) { return '1.00' }
    if ($unionMarkersFound -ge 2) { return '1.00' }

    # Engine markers count
    $engineCount = 0
    if ($dbEngine -eq 'oracle') {
        foreach ($m in $oracleMarkers) { if ($lower.Contains($m.ToLower())) { $engineCount++ } }
        if ($lower -match 'chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr\s*\(\s*\d+\s*\)') { $engineCount++ }
    } elseif ($dbEngine -eq 'mysql') {
        foreach ($m in $mysqlMarkers) { if ($lower.Contains($m.ToLower())) { $engineCount++ } }
        if ($lower.EndsWith('#')) { $engineCount++ }
    } elseif ($dbEngine -eq 'postgresql') {
        foreach ($m in $pgsqlMarkers) { if ($lower.Contains($m.ToLower())) { $engineCount++ } }
    } elseif ($dbEngine -eq 'mssql') {
        foreach ($m in $mssqlMarkers) { if ($lower.Contains($m.ToLower())) { $engineCount++ } }
    } elseif ($dbEngine -eq 'sqlite') {
        foreach ($m in $sqliteMarkers) { if ($lower.Contains($m.ToLower())) { $engineCount++ } }
    }

    $totalMarkers = $timeMarkersFound + $errorMarkersFound + $unionMarkersFound + $engineCount

    if ($totalMarkers -ge 2) { return '1.00' }
    if ($totalMarkers -eq 1) { return '0.85' }

    # Payload length / token check for low confidence
    if ($payloadNorm.Length -lt 15) { return '0.70' }
    if ($tokenCount -le 2) { return '0.70' }
    if ($payloadNorm -match "^\s*1\s*=\s*1\s*$" -or $payloadNorm -match "^\s*['\""]\s*OR\s+" -or $payloadNorm -match "^\s*['\""]\s*AND\s+") {
        return '0.70'
    }

    return '0.85'
}

# Read CSV
$data = Import-Csv -LiteralPath $inputFile
$results = @()

foreach ($row in $data) {
    $idStr = $row.id
    $id = [int]::Parse($idStr.Trim('"'))

    if ($id -ge 11001 -and $id -le 12000) {
        $payloadNorm = $row.payload_norm
        $dbEngine = Get-DbEngine -payloadNorm $payloadNorm
        $sqliType = Get-SqliType -payloadNorm $payloadNorm -dbEngine $dbEngine
        $confidence = Get-Confidence -payloadNorm $payloadNorm -sqliType $sqliType -dbEngine $dbEngine

        $results += [PSCustomObject]@{
            id = $id
            sqli_type = $sqliType
            db_engine = $dbEngine
            confidence = $confidence
        }
    }
}

$results | Export-Csv -LiteralPath $outputFile -NoTypeInformation -Encoding UTF8

Write-Host "Done. Labeled $($results.Count) rows (id 11001-12000) -> $outputFile"
Write-Host "Breakdown:"
$results | Group-Object sqli_type | Select-Object Name, Count | Format-Table -AutoSize
