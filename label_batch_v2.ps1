$inputFile = "C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data.csv"
$outputFile = "C:\Projects\GAN_SQLi\Training-data\LabelData\batches_labeled\labeled_batch_11001_12000.csv"

$lines = Get-Content -LiteralPath $inputFile -Encoding UTF8
$results = @()

$timeMarkers = @(
    'sleep(', 
    'pg_sleep(', 
    'WAITFOR DELAY', 
    'WAITFOR ',
    'dbms_pipe.receive_message', 
    'benchmark(',
    'generate_series(1,5000000)', 
    'generate_series(1, 5000000)',
    'randomblob(500000000)', 
    'repeat(', 
    'regexp_substring'
)

$errorMarkers = @(
    'xmltype(', 
    'extractvalue(', 
    'updatexml(', 
    'floor(rand(', 
    'utl_inaddr', 
    'ctxsys.drithsx.sn'
)

$oracleMarkers = @(
    'xmltype(', 
    'dbms_pipe', 
    'utl_inaddr', 
    'sys_context', 
    'from dual', 
    'ctxsys', 
    'rownum'
)
$mysqlMarkers = @(
    'sleep(', 
    'benchmark(', 
    'floor(rand(', 
    'extractvalue(', 
    'updatexml(', 
    'information_schema.', 
    '@@version', 
    '@@datadir', 
    'load_file('
)
$pgsqlMarkers = @(
    'pg_sleep(', 
    'generate_series(', 
    '::text', 
    '::int', 
    '::numeric', 
    '::boolean', 
    'string_agg(', 
    'array_agg('
)
$mssqlMarkers = @(
    'WAITFOR DELAY', 
    'master..sysdatabases', 
    'xp_cmdshell', 
    'sysobjects', 
    'syscolumns', 
    'sysusers'
)
$sqliteMarkers = @(
    'randomblob(', 
    'sqlite_version(', 
    'sqlite_master'
)

function Parse-CsvLine($line) {
    $columns = @()
    $current = ''
    $inQuotes = $false
    $i = 0
    while ($i -lt $line.Length) {
        $c = $line[$i]
        if ($c -eq '"') {
            if ($inQuotes -and $i+1 -lt $line.Length -and $line[$i+1] -eq '"') {
                $current += '"'
                $i += 2
                continue
            }
            $inQuotes = -not $inQuotes
        } elseif ($c -eq ',' -and -not $inQuotes) {
            $columns += $current
            $current = ''
        } else {
            $current += $c
        }
        $i++
    }
    $columns += $current
    return $columns
}

function Get-SqliType($payload) {
    $lower = $payload.ToLower()
    
    $hasXmlType = $lower.Contains('xmltype(')
    $hasDbmsPipe = $lower.Contains('dbms_pipe.receive_message')
    
    foreach ($marker in $timeMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) {
            if ($m -eq 'dbms_pipe.receive_message' -and $hasXmlType) {
                return 'error_based'
            }
            return 'time_blind'
        }
    }
    
    foreach ($marker in $errorMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { 
            return 'error_based' 
        }
    }
    
    if ($lower -match 'convert\s*\(\s*int\s*,') { return 'error_based' }
    if ($lower -match '1/\s*\(?\s*select\s+0') { return 'error_based' }
    if ($lower -match 'cast.*as\s+int.*/') { return 'error_based' }
    
    if ($lower -match '\bunion\s+(all\s+)?select\b') { return 'union_based' }
    if ($lower -match '\border\s+by\s+\d+') { return 'union_based' }
    
    return 'boolean_blind'
}

function Get-DbEngine($payload) {
    $lower = $payload.ToLower()
    
    foreach ($marker in $oracleMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'oracle' }
    }
    if ($lower -match 'chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr\s*\(\s*\d+\s*\)') { return 'oracle' }
    
    foreach ($marker in $pgsqlMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'postgresql' }
    }
    
    foreach ($marker in $mssqlMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'mssql' }
    }
    
    foreach ($marker in $mysqlMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'mysql' }
    }
    if ($lower.Trim().EndsWith('#')) { return 'mysql' }
    
    foreach ($marker in $sqliteMarkers) {
        $m = $marker.ToLower()
        if ($lower.Contains($m)) { return 'sqlite' }
    }
    
    return 'generic'
}

function Get-Confidence($payload, $sqliType, $dbEngine) {
    $lower = $payload.ToLower()
    
    $typeScore = 0
    $engineScore = 0
    
    if ($sqliType -eq 'time_blind') {
        foreach ($m in $timeMarkers) { if ($lower.Contains($m.ToLower())) { $typeScore++ } }
    } elseif ($sqliType -eq 'error_based') {
        foreach ($m in $errorMarkers) { if ($lower.Contains($m.ToLower())) { $typeScore++ } }
        if ($lower -match 'convert\s*\(\s*int') { $typeScore++ }
    } elseif ($sqliType -eq 'union_based') {
        if ($lower -match '\bunion\s+(all\s+)?select\b') { $typeScore++ }
        if ($lower -match 'null\s*,\s*null') { $typeScore++ }
    }
    
    if ($dbEngine -eq 'oracle') {
        foreach ($m in $oracleMarkers) { if ($lower.Contains($m.ToLower())) { $engineScore++ } }
        if ($lower -match 'chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr') { $engineScore++ }
    } elseif ($dbEngine -eq 'mysql') {
        foreach ($m in $mysqlMarkers) { if ($lower.Contains($m.ToLower())) { $engineScore++ } }
        if ($lower.Trim().EndsWith('#')) { $engineScore++ }
    } elseif ($dbEngine -eq 'postgresql') {
        foreach ($m in $pgsqlMarkers) { if ($lower.Contains($m.ToLower())) { $engineScore++ } }
    } elseif ($dbEngine -eq 'mssql') {
        foreach ($m in $mssqlMarkers) { if ($lower.Contains($m.ToLower())) { $engineScore++ } }
    }
    
    $total = $typeScore + $engineScore
    
    if ($total -ge 2) { return '1.00' }
    if ($total -eq 1) { return '0.85' }
    
    if ($payload.Length -lt 20) { return '0.70' }
    
    $tokens = $lower.Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)
    if ($tokens.Count -le 3) { return '0.70' }
    
    return '0.85'
}

$count = 0
for ($i = 1; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    
    $cols = Parse-CsvLine -line $line
    if ($cols.Count -lt 2) { continue }
    
    $idStr = $cols[0].Trim()
    try {
        $id = [int]$idStr
    } catch {
        continue
    }
    
    if ($id -ge 11001 -and $id -le 12000) {
        $payload = $cols[1]
        
        $dbEngine = Get-DbEngine -payload $payload
        $sqliType = Get-SqliType -payload $payload
        $confidence = Get-Confidence -payload $payload -sqliType $sqliType -dbEngine $dbEngine
        
        $results += [PSCustomObject]@{
            id = $id
            sqli_type = $sqliType
            db_engine = $dbEngine
            confidence = $confidence
        }
        $count++
    }
}

$results = $results | Sort-Object { [int]$_.id }

$results | Export-Csv -LiteralPath $outputFile -NoTypeInformation -Encoding UTF8

Write-Host "Done. Labeled $count rows from id=11001 to 12000"
Write-Host "Output: $outputFile"
Write-Host ""
Write-Host "=== BREAKDOWN ==="
$results | Group-Object sqli_type | Select-Object Name, Count | Format-Table -AutoSize
Write-Host ""
Write-Host "By db_engine:"
$results | Group-Object db_engine | Select-Object Name, Count | Format-Table -AutoSize
Write-Host ""
Write-Host "By confidence:"
$results | Group-Object confidence | Select-Object Name, Count | Format-Table -AutoSize
Write-Host ""
Write-Host "=== First 20 samples ==="
$results | Select-Object -First 20 | Format-Table -AutoSize
