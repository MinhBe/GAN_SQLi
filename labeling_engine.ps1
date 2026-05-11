param(
    [string]$InputPath = "C:\Projects\GAN_SQLi\Asset\LabelData\unlabeled_10001_12000.csv",
    [string]$OutputPath = "C:\Projects\GAN_SQLi\Asset\LabelData\labeled_10001_12000.csv"
)

function Get-SQLiType {
    param([string]$Payload)
    
    $lowerPayload = $Payload.ToLower()
    
    $errorMarkers = @(
        "xmltype(",
        "extractvalue(",
        "updatexml(",
        "floor(rand(",
        "group by",
        "convert(int,",
        "cast(.*as int)",
        "utl_inaddr.get_host_address(",
        "ctxsys.drithsx.sn(",
        "dbms_utility"
    )
    $errorFound = 0
    foreach ($m in $errorMarkers) {
        if ($lowerPayload -match [regex]::Escape($m)) { $errorFound++ }
    }
    if ($lowerPayload -match "floor\s*\(\s*rand\s*\(" -and $lowerPayload -match "group\s+by") {
        $errorFound += 2
    }
    
    $timeMarkers = @(
        "sleep(",
        "pg_sleep(",
        "waitfor delay",
        "dbms_pipe.receive_message",
        "benchmark(",
        "generate_series(1,50",
        "generate_series(1,100",
        "generate_series(1,200",
        "generate_series(1,500",
        "generate_series(1,1000",
        "randomblob(5000",
        "randomblob(10000",
        "randomblob(50000",
        "randomblob(100000",
        "randomblob(500000",
        "repeat\s*\(\s*.*,\s*500000",
        "repeat\s*\(\s*.*,\s*1000000"
    )
    $timeFound = 0
    foreach ($m in $timeMarkers) {
        if ($lowerPayload -match [regex]::Escape($m)) { $timeFound++ }
    }
    if ($lowerPayload -match "sysibm\.systables.*sysibm\.systables.*sysibm\.systables") { $timeFound += 2 }
    if ($lowerPayload -match "rdb\$.*rdb\$.*rdb\$") { $timeFound += 2 }
    if ($lowerPayload -match "all_users.*all_users.*all_users") { $timeFound += 2 }
    
    $unionMarkers = @(
        "union select",
        "union all select"
    )
    $unionFound = 0
    foreach ($m in $unionMarkers) {
        if ($lowerPayload -match [regex]::Escape($m)) { $unionFound++ }
    }
    if ($lowerPayload -match "order\s+by\s+\d+") { $unionFound++ }
    
    $booleanMarkers = @(
        "case when",
        "if(",
        "iif(",
        "and 1=1",
        "and 1=2",
        "or 1=1",
        "rlike",
        "elt(",
        "ord(mid(",
        "ord(substr(",
        "' or '1'='1",
        "' or ''='"
    )
    $booleanFound = 0
    foreach ($m in $booleanMarkers) {
        if ($lowerPayload -match [regex]::Escape($m)) { $booleanFound++ }
    }
    if ($lowerPayload -match "where\s+\d+\s*=\s*\d+") { $booleanFound++ }
    if ($lowerPayload -match "and\s+\d+\s*=\s*\d+") { $booleanFound++ }
    if ($lowerPayload -match "or\s+\d+\s*=\s*\d+") { $booleanFound++ }
    
    $type = "boolean_blind"
    $confidence = 0.70
    
    if ($timeFound -gt 0 -and $errorFound -eq 0) {
        $type = "time_blind"
        $confidence = 0.85
        if ($timeFound -ge 2) { $confidence = 1.00 }
    }
    elseif ($errorFound -gt 0) {
        $type = "error_based"
        $confidence = 0.85
        if ($errorFound -ge 2) { $confidence = 1.00 }
        if ($unionFound -gt 0) { $confidence = 0.85 }
    }
    elseif ($unionFound -gt 0) {
        $type = "union_based"
        $confidence = 0.85
        if ($lowerPayload -match "union\s+all\s+select.*null") { $confidence = 1.00 }
        if ($lowerPayload -match "union\s+all\s+select.*\d+.*#") { $confidence = 1.00 }
    }
    elseif ($booleanFound -gt 0) {
        $type = "boolean_blind"
        $confidence = 0.85
        if ($booleanFound -ge 2) { $confidence = 1.00 }
    }
    
    return @{ Type = $type; ConfidenceBase = $confidence; Markers = @{ Error = $errorFound; Time = $timeFound; Union = $unionFound; Boolean = $booleanFound } }
}

function Get-DBEngine {
    param([string]$Payload, [hashtable]$Markers)
    
    $lowerPayload = $Payload.ToLower()
    
    $oracleMarkers = @(
        "xmltype(",
        "utl_inaddr",
        "dbms_pipe",
        "dbms_utility",
        "ctxsys.drithsx",
        "sys_context(",
        "from dual",
        "sys.all_tables",
        "rownum"
    )
    $oracleFound = 0
    foreach ($m in $oracleMarkers) {
        if ($lowerPayload -match [regex]::Escape($m)) { $oracleFound++ }
    }
    if ($lowerPayload -match "chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr\s*\(") { $oracleFound += 2 }
    
    $mysqlMarkers = @(
        "sleep(",
        "benchmark(",
        "group_concat(",
        "floor(rand(",
        "extractvalue(",
        "updatexml(",
        "information_schema.",
        "load_file(",
        "into outfile",
        "@@version",
        "@@datadir",
        "mysql.db"
    )
    $mysqlFound = 0
    foreach ($m in $mysqlMarkers) {
        if ($lowerPayload -match [regex]::Escape($m)) { $mysqlFound++ }
    }
    if ($Payload -match "#\s*$") { $mysqlFound++ }
    if ($Payload -match "#\s*\w+$") { $mysqlFound++ }
    
    $pgsqlMarkers = @(
        "pg_sleep(",
        "generate_series(",
        "::text",
        "::int",
        "::numeric",
        "string_agg(",
        "array_agg(",
        "pg_read_file("
    )
    $pgsqlFound = 0
    foreach ($m in $pgsqlMarkers) {
        if ($lowerPayload -match [regex]::Escape($m)) { $pgsqlFound++ }
    }
    if ($lowerPayload -match "::text") { $pgsqlFound += 2 }
    
    $mssqlMarkers = @(
        "waitfor delay",
        "master..sysdatabases",
        "xp_cmdshell",
        "@@servername",
        "sysobjects",
        "syscolumns",
        "sysusers"
    )
    $mssqlFound = 0
    foreach ($m in $mssqlMarkers) {
        if ($lowerPayload -match [regex]::Escape($m)) { $mssqlFound++ }
    }
    
    $sqliteMarkers = @(
        "randomblob(",
        "sqlite_version(",
        "sqlite_master"
    )
    $sqliteFound = 0
    foreach ($m in $sqliteMarkers) {
        if ($lowerPayload -match [regex]::Escape($m)) { $sqliteFound++ }
    }
    
    $db2Found = 0
    if ($lowerPayload -match "sysibm\.systables") { $db2Found += 2 }
    $firebirdFound = 0
    if ($lowerPayload -match "rdb\$") { $firebirdFound += 2 }
    
    $engine = "generic"
    $engineConfidence = 0.70
    
    if ($oracleFound -gt 0) {
        $engine = "oracle"
        $engineConfidence = 0.85
        if ($oracleFound -ge 2) { $engineConfidence = 1.00 }
    }
    elseif ($pgsqlFound -gt 0) {
        $engine = "postgresql"
        $engineConfidence = 0.85
        if ($pgsqlFound -ge 2) { $engineConfidence = 1.00 }
    }
    elseif ($mysqlFound -gt 0) {
        $engine = "mysql"
        $engineConfidence = 0.85
        if ($mysqlFound -ge 2) { $engineConfidence = 1.00 }
    }
    elseif ($mssqlFound -gt 0) {
        $engine = "mssql"
        $engineConfidence = 0.85
        if ($mssqlFound -ge 2) { $engineConfidence = 1.00 }
    }
    elseif ($sqliteFound -gt 0) {
        $engine = "sqlite"
        $engineConfidence = 0.85
        if ($sqliteFound -ge 2) { $engineConfidence = 1.00 }
    }
    
    return @{ Engine = $engine; Confidence = $engineConfidence }
}

function Get-FinalConfidence {
    param([double]$TypeConf, [double]$EngineConf, [string]$Type, [string]$Engine)
    
    $minConf = [Math]::Min($TypeConf, $EngineConf)
    $result = $minConf
    
    $words = [regex]::Matches($Payload, "\w+").Count
    if ($words -lt 5) {
        if ($result -eq 1.00) { $result = 0.85 }
        elseif ($result -eq 0.85) { $result = 0.70 }
    }
    
    if ($Engine -eq "generic") {
        if ($result -eq 1.00) { $result = 0.85 }
    }
    
    if ($Type -eq "error_based" -and $Engine -eq "oracle" -and $TypeConf -eq 1.00) { $result = 1.00 }
    if ($Type -eq "time_blind" -and $Engine -eq "mysql" -and $TypeConf -eq 1.00) { $result = 1.00 }
    if ($Type -eq "time_blind" -and $Engine -eq "postgresql" -and $TypeConf -eq 1.00) { $result = 1.00 }
    
    if ($result -gt 1.00) { $result = 1.00 }
    if ($result -ge 0.93) { $result = 1.00 }
    elseif ($result -ge 0.78) { $result = 0.85 }
    else { $result = 0.70 }
    
    return $result
}

$csv = Import-Csv -LiteralPath $InputPath
$results = @()
$count = 0

foreach ($row in $csv) {
    $id = $row.id
    $payload = $row.payload_norm
    
    $typeInfo = Get-SQLiType -Payload $payload
    $engineInfo = Get-DBEngine -Payload $payload -Markers $typeInfo.Markers
    $finalConf = Get-FinalConfidence -TypeConf $typeInfo.ConfidenceBase -EngineConf $engineInfo.Confidence -Type $typeInfo.Type -Engine $engineInfo.Engine -Payload $payload
    
    $results += [PSCustomObject]@{
        id = $id
        sqli_type = $typeInfo.Type
        db_engine = $engineInfo.Engine
        confidence = $finalConf.ToString("F2")
    }
    
    $count++
    if ($count % 200 -eq 0) {
        Write-Host "Processed $count rows..."
    }
}

$results | Export-Csv -LiteralPath $OutputPath -NoTypeInformation -Encoding UTF8
Write-Host "Done! Saved to $OutputPath"
Write-Host "Total labeled: $($results.Count) rows"
