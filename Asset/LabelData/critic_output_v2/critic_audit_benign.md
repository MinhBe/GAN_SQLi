# Benign Audit Report
Total benign: 21076
Sample size: 500
False negatives: 28
FN rate: 5.6%
Recommendation: Full re-review recommended

## False Negatives
- Row 20809: keywords=['sleep'] | SELECT * FROM build FETCH FIRST 50 PERCENT ROWS ONLYSELECT TOP 3 * FROM sleep
- Row 23706: keywords=['union', 'sleep'] | SELECT taken ( s ) FROM sleep UNION ALL
- Row 2202: keywords=['--'] | 1" and 9198 = 9198--
- Row 3190: keywords=['--'] | select ( case when ( 1272 = 5883 ) then 1272 else cast ( 1 as int ) / ( select 0
- Row 5143: keywords=['--'] | -6595" order by 1--
- Row 8853: keywords=['information_schema'] | 1' ( select ( case when ( 5451 = 5451 ) then regexp_substring ( repeat ( right (
- Row 20389: keywords=['insert '] | INSERT INTO to ( daughter, seldom, being ) VALUES ( 'forward', 'charge', 'next' 
- Row 2851: keywords=['--'] | select ( case when ( 1291 = 6612 ) then 1 else 1291* ( select 1291 from master..
- Row 10456: keywords=['--'] | -9031%" ) order by 1--
- Row 146: keywords=['insert '] | insert into mysql.user ( user, host, password ) values ( 'name', 'localhost', pa
- Row 20357: keywords=['union'] | SELECT laid ( s ) FROM clearly UNION
- Row 5506: keywords=['--'] | 1" ) ) ) and char ( 109 ) ||char ( 79 ) ||char ( 70 ) ||char ( 90 ) = regexp_sub
- Row 3566: keywords=['--'] | select case when 3661 = 9315 then 1 else null end--
- Row 4481: keywords=['--'] | select case when 6555 = 7349 then 1 else null end--
- Row 26813: keywords=['sleep'] | SELECT TOP 3 * FROM sleep WHERE major = 'parallel' SELECT * FROM quarter
- Row 24625: keywords=['sleep'] | UPDATE sleep SET bigger = 'building'WHERE mix = 'shown'
- Row 3727: keywords=['--'] | select ( case when ( 4774 = 1535 ) then 4774 else cast ( 1 as int ) / ( select 0
- Row 157: keywords=['exec '] | exec sp
- Row 26490: keywords=['insert '] | INSERT INTO ran ( instrument, wrong, oldest, few, wore, body ) VALUES ( 'swept',
- Row 10086: keywords=['--'] | -4239 or 2724 in ( ( char ( 113 ) +char ( 113 ) +char ( 112 ) +char ( 106 ) +cha
- Row 21442: keywords=['union'] | SELECT unknown ( s ) FROM pen UNION
- Row 26589: keywords=['insert '] | INSERT INTO capital ( factory, this, shake, sides, under, cut ) VALUES ( 'variet
- Row 26953: keywords=['union'] | SELECT south ( s ) FROM just UNION ALL
- Row 27445: keywords=['union'] | SELECT bigger ( s ) FROM mighty UNION ALL
- Row 20091: keywords=['insert '] | INSERT INTO motor ( air, angry, thread, excellent, elephant, type ) VALUES ( 'sc
- Row 5576: keywords=['--'] | select ( case when ( 5914 = 2314 ) then 5914 else 1/ ( select 0 ) end ) --
- Row 1173: keywords=['--'] | select ( case when ( 9562 = 5996 ) then 1 else 9562* ( select 9562 from master..
- Row 1053: keywords=['--'] | select ( case when ( 1499 = 4923 ) then 1499 else 1/ ( select 0 ) end ) --