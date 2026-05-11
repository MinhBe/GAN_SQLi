import csv

targets = ['8002', '8005', '8008', '8014', '8021', '8022', '8024', '8026', '8027', '8019', '8034', '8086', '8126', '8099', '8181', '8131', '8148', '8155']
with open('split_data_labeled_8001_10000.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['id'] in targets:
            print(f"{row['id']}: {row['sqli_type']}, {row['db_engine']}, {row['confidence']}")
