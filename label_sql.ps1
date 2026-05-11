$InputPath = "C:\Projects\GAN_SQLi\Asset\LabelData\unlabeled_10001_12000.csv"
$OutputPath = "C:\Projects\GAN_SQLi\Asset\LabelData\labeled_10001_12000.csv"

function Get-SQLiLabel {
    param([string]$Payload)
    
    $p = $Payload.ToLower()
    $hasErrorMarkers = 0
    $hasTimeMarkers = 0
    $hasUnionMarkers = 0
    $hasBooleanMarkers = 0
    $hasOracle = 0
    $hasMysql = 0
    $hasPgsql = 0
    $hasMssql = 0
    $hasSqlite = 0
    
    if ($p -match "xmltype\s*\(") { $hasErrorMarkers += 2; $hasOracle += 2 }
    if ($p -match "extractvalue\s*\(") { $hasErrorMarkers += 2; $hasMysql += 1 }
    if ($p -match "updatexml\s*\(") { $hasErrorMarkers += 2; $hasMysql += 1 }
    if ($p -match "floor\s*\(\s*rand\s*\(" -and $p -match "group\s+by") { $hasErrorMarkers += 3; $hasMysql += 2 }
    if ($p -match "utl_inaddr\.get_host_address") { $hasErrorMarkers += 2; $hasOracle += 2 }
    if ($p -match "ctxsys\.drithsx\.sn") { $hasErrorMarkers += 2; $hasOracle += 2 }
    if ($p -match "dbms_utility") { $hasErrorMarkers += 1; $hasOracle += 1 }
    
    if ($p -match "sleep\s*\(\s*[0-9]") { $hasTimeMarkers += 2; $hasMysql += 2 }
    if ($p -match "pg_sleep\s*\(") { $hasTimeMarkers += 2; $hasPgsql += 2 }
    if ($p -match "waitfor\s+delay") { $hasTimeMarkers += 2; $hasMssql += 2 }
    if ($p -match "dbms_pipe\.receive_message") { 
        if ($p -match "receive_message\s*\(\s*[^,]+,\s*[0-9]") {
            $hasTimeMarkers += 2
        } else {
            $hasTimeMarkers += 1
        }
        $hasOracle += 2
    }
    if ($p -match "benchmark\s*\(") { $hasTimeMarkers += 2; $hasMysql += 1 }
    if ($p -match "generate_series\s*\(\s*1\s*,\s*50") { $hasTimeMarkers += 2; $hasPgsql += 1 }
    if ($p -match "generate_series\s*\(\s*1\s*,\s*1[0-9][0-9][0-9][0-9]") { $hasTimeMarkers += 2; $hasPgsql += 1 }
    if ($p -match "randomblob\s*\(\s*[0-9]{5,}") { $hasTimeMarkers += 2; $hasSqlite += 2 }
    if ($p -match "repeat\s*\(\s*.*,\s*[0-9]{6,}") { $hasTimeMarkers += 2; $hasMysql += 1 }
    if ($p -match "sysibm\.systables.*sysibm\.systables.*sysibm\.systables") { $hasTimeMarkers += 2 }
    if ($p -match "rdb\$.*rdb\$.*rdb\$") { $hasTimeMarkers += 2 }
    if ($p -match "all_users.*all_users.*all_users") { $hasTimeMarkers += 2 }
    
    if ($p -match "union\s+(all\s+)?select") { $hasUnionMarkers += 2 }
    if ($p -match "order\s+by\s+\d+") { $hasUnionMarkers += 1 }
    
    if ($p -match "case\s+when") { $hasBooleanMarkers += 2 }
    if ($p -match "elt\s*\(") { $hasBooleanMarkers += 1; $hasMysql += 1 }
    if ($p -match "\bif\s*\(") { $hasBooleanMarkers += 1; $hasMysql += 1 }
    if ($p -match "iif\s*\(") { $hasBooleanMarkers += 1; $hasMssql += 1 }
    if ($p -match "rlike\s*\(") { $hasBooleanMarkers += 1; $hasMysql += 1 }
    if ($p -match "where\s+\d+\s*=\s*\d+") { $hasBooleanMarkers += 1 }
    if ($p -match "and\s+\d+\s*=\s*\d+") { $hasBooleanMarkers += 1 }
    if ($p -match "or\s+\d+\s*=\s*\d+") { $hasBooleanMarkers += 1 }
    if ($p -match "or\s+'1'\s*=\s*'1") { $hasBooleanMarkers += 2 }
    if ($p -match "ord\s*\(\s*(mid|substr)") { $hasBooleanMarkers += 2 }
    
    if ($p -match "from\s+dual") { $hasOracle += 2 }
    if ($p -match "sys_context\s*\(") { $hasOracle += 2 }
    if ($p -match "rownum") { $hasOracle += 1 }
    if ($p -match "sys\.all_tables") { $hasOracle += 2 }
    if ($p -match "chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr\s*\(") { $hasOracle += 2 }
    
    if ($p -match "information_schema\.") { $hasMysql += 2 }
    if ($p -match "group_concat\s*\(") { $hasMysql += 2 }
    if ($p -match "load_file\s*\(") { $hasMysql += 2 }
    if ($p -match "into\s+outfile") { $hasMysql += 2 }
    if ($p -match "@@(version|datadir|servername)") { $hasMysql += 2 }
    if ($p -match "mysql\.db") { $hasMysql += 2 }
    if ($Payload -match "#\s*(\w+)?$") { $hasMysql += 1 }
    
    if ($p -match "::text|::int|::numeric") { $hasPgsql += 2 }
    if ($p -match "string_agg\s*\(") { $hasPgsql += 2 }
    if ($p -match "array_agg\s*\(") { $hasPgsql += 2 }
    if ($p -match "pg_read_file\s*\(") { $hasPgsql += 2 }
    
    if ($p -match "master\.\.sysdatabases") { $hasMssql += 2 }
    if ($p -match "xp_cmdshell") { $hasMssql += 2 }
    if ($p -match "\bsysobjects\b") { $hasMssql += 2 }
    if ($p -match "\bsyscolumns\b") { $hasMssql += 2 }
    if ($p -match "\bsysusers\b") { $hasMssql += 2 }
    
    if ($p -match "sqlite_version\s*\(") { $hasSqlite += 2 }
    if ($p -match "sqlite_master") { $hasSqlite += 2 }
    
    $type = "boolean_blind"
    $engine = "generic"
    $typeConf = 0.70
    $engineConf = 0.70
    
    if ($hasOracle -gt 0) {
        $engine = "oracle"
        $engineConf = if ($hasOracle -ge 2) { 1.00 } else { 0.85 }
    }
    elseif ($hasPgsql -gt 0) {
        $engine = "postgresql"
        $engineConf = if ($hasPgsql -ge 2) { 1.00 } else { 0.85 }
    }
    elseif ($hasMysql -gt 0) {
        $engine = "mysql"
        $engineConf = if ($hasMysql -ge 2) { 1.00 } else { 0.85 }
    }
    elseif ($hasMssql -gt 0) {
        $engine = "mssql"
        $engineConf = if ($hasMssql -ge 2) { 1.00 } else { 0.85 }
    }
    elseif ($hasSqlite -gt 0) {
        $engine = "sqlite"
        $engineConf = if ($hasSqlite -ge 2) { 1.00 } else { 0.85 }
    }
    
    if ($hasErrorMarkers -gt 0 -and $hasTimeMarkers -eq 0) {
        $type = "error_based"
        $typeConf = if ($hasErrorMarkers -ge 2) { 1.00 } else { 0.85 }
        if ($hasUnionMarkers -gt 0) { $typeConf = 0.85 }
    }
    elseif ($hasTimeMarkers -gt 0) {
        $type = "time_blind"
        $typeConf = if ($hasTimeMarkers -ge 2) { 1.00 } else { 0.85 }
        if ($hasBooleanMarkers -gt 0 -and $hasTimeMarkers -lt 2) { $typeConf = 0.85 }
    }
    elseif ($hasUnionMarkers -gt 0) {
        $type = "union_based"
        $typeConf = if ($hasUnionMarkers -ge 2) { 1.00 } else { 0.85 }
    }
    elseif ($hasBooleanMarkers -gt 0) {
        $type = "boolean_blind"
        $typeConf = if ($hasBooleanMarkers -ge 2) { 1.00 } else { 0.85 }
    }
    
    $words = [regex]::Matches($Payload, "\w+").Count
    if ($words -lt 8) {
        if ($typeConf -eq 1.00) { $typeConf = 0.85 }
        elseif ($typeConf -eq 0.85) { $typeConf = 0.70 }
        if ($engineConf -eq 1.00) { $engineConf = 0.85 }
    }
    
    if ($engine -eq "generic") {
        if ($typeConf -eq 1.00) { $typeConf = 0.85 }
    }
    
    $finalConf = [Math]::Min($typeConf, $engineConf)
    
    if ($finalConf -ge 0.93) { $finalConf = 1.00 }
    elseif ($finalConf -ge 0.78) { $finalConf = 0.85 }
    else { $finalConf = 0.70 }
    
    return @{
        type = $type
        engine = $engine
        confidence = $finalConf
    }
}

$csv = Import-Csv -LiteralPath $InputPath
$results = @()
$count = 0

foreach ($row in $csv) {
    $label = Get-SQLiLabel -Payload $row.payload_norm
    
    $results += [PSCustomObject]@{
        id = $row.id
        sqli_type = $label.type
        db_engine = $label.engine
        confidence = $label.confidence.ToString("F2")
        payload = $row.payload_norm
    }
    
    $count++
    if ($count % 100 -eq 0) {
        Write-Host "Processed $count rows..."
    }
}

$results | Export-Csv -LiteralPath $OutputPath -NoTypeInformation -Encoding UTF8
Write-Host "Done! Total: $($results.Count) rows"

$results | Group-Object sqli_type | ForEach-Object { Write-Host "$($_.Name): $($_.Count)" }
$results | Group-Object db_engine | ForEach-Object { Write-Host "$($_.Name): $($_.Count)" }
