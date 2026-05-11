$inputFile = "C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data.csv"
$outputFile = "C:\Projects\GAN_SQLi\Training-data\LabelData\batches_labeled\labeled_batch_11001_12000.csv"

$lines = Get-Content -LiteralPath $inputFile -Encoding UTF8
$results = @()

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

function Test-RegexPattern($payload, $pattern) {
    return [regex]::IsMatch($payload, $pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
}

function Get-SqliType($payload) {
    $lower = $payload.ToLower()
    
    $hasXmlType = (Test-RegexPattern $lower 'xmltype\s*\(')
    $hasDbmsPipeTime = (Test-RegexPattern $lower 'dbms_pipe\.receive_message\s*\(')
    
    if ((Test-RegexPattern $lower 'sleep\s*\(')) { return 'time_blind' }
    if ((Test-RegexPattern $lower 'pg_sleep\s*\(')) { return 'time_blind' }
    if ((Test-RegexPattern $lower 'WAITFOR\s+DELAY')) { return 'time_blind' }
    if ($hasDbmsPipeTime) {
        if ($hasXmlType) {
            return 'error_based'
        }
        return 'time_blind'
    }
    if ((Test-RegexPattern $lower 'benchmark\s*\(')) { return 'time_blind' }
    if ((Test-RegexPattern $lower 'generate_series\s*\(\s*1\s*,\s*5000000')) { return 'time_blind' }
    if ((Test-RegexPattern $lower 'randomblob\s*\(\s*500000000')) { return 'time_blind' }
    if ((Test-RegexPattern $lower 'regexp_substring.*repeat.*500000000')) { return 'time_blind' }
    
    if ($hasXmlType) { return 'error_based' }
    if ((Test-RegexPattern $lower 'extractvalue\s*\(')) { return 'error_based' }
    if ((Test-RegexPattern $lower 'updatexml\s*\(')) { return 'error_based' }
    if ((Test-RegexPattern $lower 'floor\s*\(\s*rand\s*\(')) { return 'error_based' }
    if ((Test-RegexPattern $lower 'utl_inaddr')) { return 'error_based' }
    if ((Test-RegexPattern $lower 'ctxsys\.drithsx\.sn')) { return 'error_based' }
    
    if ((Test-RegexPattern $lower 'convert\s*\(\s*int\s*,')) { return 'error_based' }
    if ((Test-RegexPattern $lower '1\s*/\s*\(?\s*select\s+0')) { return 'error_based' }
    if ((Test-RegexPattern $lower 'select\s+0\s+from\s+dual')) { 
        if ((Test-RegexPattern $lower '/')) { return 'error_based' }
    }
    
    if ((Test-RegexPattern $lower '\bunion\s+(all\s+)?select\b')) { return 'union_based' }
    if ((Test-RegexPattern $lower '\border\s+by\s+\d+')) { return 'union_based' }
    
    return 'boolean_blind'
}

function Get-DbEngine($payload) {
    $lower = $payload.ToLower()
    
    if ((Test-RegexPattern $lower 'xmltype\s*\(')) { return 'oracle' }
    if ((Test-RegexPattern $lower 'dbms_pipe')) { return 'oracle' }
    if ((Test-RegexPattern $lower 'utl_inaddr')) { return 'oracle' }
    if ((Test-RegexPattern $lower 'sys_context')) { return 'oracle' }
    if ((Test-RegexPattern $lower 'from\s+dual')) { return 'oracle' }
    if ((Test-RegexPattern $lower 'ctxsys')) { return 'oracle' }
    if ((Test-RegexPattern $lower 'rownum')) { return 'oracle' }
    if ((Test-RegexPattern $lower 'chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr\s*\(\s*\d+\s*\)')) { return 'oracle' }
    
    if ((Test-RegexPattern $lower 'pg_sleep\s*\(')) { return 'postgresql' }
    if ((Test-RegexPattern $lower 'generate_series\s*\(')) { return 'postgresql' }
    if ($lower.Contains('::text')) { return 'postgresql' }
    if ($lower.Contains('::int')) { return 'postgresql' }
    if ($lower.Contains('::numeric')) { return 'postgresql' }
    if ($lower.Contains('::boolean')) { return 'postgresql' }
    if ((Test-RegexPattern $lower 'string_agg\s*\(')) { return 'postgresql' }
    if ((Test-RegexPattern $lower 'array_agg\s*\(')) { return 'postgresql' }
    
    if ((Test-RegexPattern $lower 'WAITFOR\s+DELAY')) { return 'mssql' }
    if ($lower.Contains('master..sysdatabases')) { return 'mssql' }
    if ($lower.Contains('xp_cmdshell')) { return 'mssql' }
    if ($lower.Contains('sysobjects')) { return 'mssql' }
    if ($lower.Contains('syscolumns')) { return 'mssql' }
    if ($lower.Contains('sysusers')) { return 'mssql' }
    
    if ((Test-RegexPattern $lower 'sleep\s*\(')) { return 'mysql' }
    if ((Test-RegexPattern $lower 'benchmark\s*\(')) { return 'mysql' }
    if ((Test-RegexPattern $lower 'floor\s*\(\s*rand\s*\(')) { return 'mysql' }
    if ((Test-RegexPattern $lower 'extractvalue\s*\(')) { return 'mysql' }
    if ((Test-RegexPattern $lower 'updatexml\s*\(')) { return 'mysql' }
    if ($lower.Contains('information_schema.')) { return 'mysql' }
    if ($lower.Contains('@@version')) { return 'mysql' }
    if ($lower.Contains('@@datadir')) { return 'mysql' }
    if ((Test-RegexPattern $lower 'load_file\s*\(')) { return 'mysql' }
    if ($lower.Trim().EndsWith('#')) { return 'mysql' }
    
    if ((Test-RegexPattern $lower 'randomblob\s*\(')) { return 'sqlite' }
    if ((Test-RegexPattern $lower 'sqlite_version\s*\(')) { return 'sqlite' }
    if ($lower.Contains('sqlite_master')) { return 'sqlite' }
    
    return 'generic'
}

function Count-TypeMarkers($payload, $sqliType) {
    $lower = $payload.ToLower()
    $count = 0
    
    if ($sqliType -eq 'time_blind') {
        if ((Test-RegexPattern $lower 'sleep\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'pg_sleep\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'WAITFOR\s+DELAY')) { $count++ }
        if ((Test-RegexPattern $lower 'dbms_pipe\.receive_message')) { $count++ }
        if ((Test-RegexPattern $lower 'benchmark\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'generate_series\s*\(\s*1\s*,\s*5000000')) { $count++ }
    } elseif ($sqliType -eq 'error_based') {
        if ((Test-RegexPattern $lower 'xmltype\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'extractvalue\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'updatexml\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'floor\s*\(\s*rand\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'utl_inaddr')) { $count++ }
        if ((Test-RegexPattern $lower 'ctxsys\.drithsx\.sn')) { $count++ }
        if ((Test-RegexPattern $lower 'convert\s*\(\s*int')) { $count++ }
    } elseif ($sqliType -eq 'union_based') {
        if ((Test-RegexPattern $lower '\bunion\s+(all\s+)?select\b')) { $count++ }
        if ((Test-RegexPattern $lower 'null\s*,\s*null')) { $count++ }
    }
    
    return $count
}

function Count-EngineMarkers($payload, $dbEngine) {
    $lower = $payload.ToLower()
    $count = 0
    
    if ($dbEngine -eq 'oracle') {
        if ((Test-RegexPattern $lower 'xmltype\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'dbms_pipe')) { $count++ }
        if ((Test-RegexPattern $lower 'from\s+dual')) { $count++ }
        if ((Test-RegexPattern $lower 'chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr')) { $count++ }
        if ((Test-RegexPattern $lower 'ctxsys')) { $count++ }
    } elseif ($dbEngine -eq 'mysql') {
        if ((Test-RegexPattern $lower 'sleep\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'extractvalue\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'floor\s*\(\s*rand')) { $count++ }
        if ($lower.Trim().EndsWith('#')) { $count++ }
        if ($lower.Contains('information_schema.')) { $count++ }
    } elseif ($dbEngine -eq 'postgresql') {
        if ((Test-RegexPattern $lower 'pg_sleep\s*\(')) { $count++ }
        if ((Test-RegexPattern $lower 'generate_series\s*\(')) { $count++ }
        if ($lower.Contains('::text')) { $count++ }
    } elseif ($dbEngine -eq 'mssql') {
        if ((Test-RegexPattern $lower 'WAITFOR')) { $count++ }
        if ($lower.Contains('sysobjects')) { $count++ }
    }
    
    return $count
}

function Get-Confidence($payload, $sqliType, $dbEngine) {
    $typeMarkers = Count-TypeMarkers -payload $payload -sqliType $sqliType
    $engineMarkers = Count-EngineMarkers -payload $payload -dbEngine $dbEngine
    
    $total = $typeMarkers + $engineMarkers
    
    if ($total -ge 2) { return '1.00' }
    if ($total -eq 1) { return '0.85' }
    
    if ($payload.Length -lt 20) { return '0.70' }
    
    $tokens = $payload.ToLower().Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)
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
Write-Host "=== First 30 samples (with verification) ==="
Write-Host "Format: id | sqli_type | db_engine | confidence | payload_snippet"
Write-Host "---"

$samples = $results | Select-Object -First 30
foreach ($s in $samples) {
    $pay = ''
    for ($j = 1; $j -lt $lines.Count; $j++) {
        $cols2 = Parse-CsvLine -line $lines[$j]
        if ($cols2.Count -ge 2 -and $cols2[0].Trim() -eq $s.id.ToString()) {
            $pay = $cols2[1]
            break
        }
    }
    $snippet = $pay
    if ($snippet.Length -gt 80) { $snippet = $snippet.Substring(0, 80) + "..." }
    Write-Host "$($s.id) | $($s.sqli_type) | $($s.db_engine) | $($s.confidence) | $snippet"
}
