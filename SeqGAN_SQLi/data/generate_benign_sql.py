"""Generate ~5000 benign SQL queries for Discriminator training (V4 Fix-7).

Benign queries: valid SQL WITHOUT injection patterns.
Used as negative class in Discriminator alongside fake G outputs.

Output: data/benign_sql.csv
  Columns: payload_norm, sqli_type, confidence
"""
import csv
import random
from pathlib import Path

random.seed(42)

TABLES = ["users", "products", "orders", "customers", "employees",
          "accounts", "transactions", "inventory", "logs", "sessions"]
COLS_INT = ["id", "age", "price", "quantity", "total", "count", "year", "month"]
COLS_STR = ["name", "email", "username", "title", "description", "status", "category"]
COLS_ALL = COLS_INT + COLS_STR
CONDITIONS_INT = ["id = 1", "age > 18", "price < 100", "quantity >= 5",
                  "total BETWEEN 10 AND 500", "count > 0", "year = 2024"]
CONDITIONS_STR = ["status = 'active'", "category = 'electronics'",
                  "name IS NOT NULL", "email LIKE '%@gmail.com'"]
CONDITIONS_ALL = CONDITIONS_INT + CONDITIONS_STR

LIMIT_VALS = [1, 5, 10, 20, 50, 100]
ORDER_DIRS = ["ASC", "DESC"]


def rand_cols(n=None):
    cols = random.sample(COLS_ALL, k=random.randint(1, 4) if n is None else n)
    return ", ".join(cols)


def rand_table():
    return random.choice(TABLES)


def rand_cond():
    n = random.randint(1, 2)
    conds = random.sample(CONDITIONS_ALL, k=n)
    return " AND ".join(conds)


def templates():
    """Yield benign SQL query strings."""

    # Simple SELECT
    for _ in range(800):
        yield f"SELECT {rand_cols()} FROM {rand_table()}"

    # SELECT with WHERE
    for _ in range(800):
        yield f"SELECT {rand_cols()} FROM {rand_table()} WHERE {rand_cond()}"

    # SELECT with ORDER BY + LIMIT
    for _ in range(600):
        col = random.choice(COLS_ALL)
        yield (f"SELECT {rand_cols()} FROM {rand_table()} "
               f"ORDER BY {col} {random.choice(ORDER_DIRS)} "
               f"LIMIT {random.choice(LIMIT_VALS)}")

    # SELECT with GROUP BY + HAVING
    for _ in range(400):
        col = random.choice(COLS_INT)
        yield (f"SELECT {col}, COUNT(*) FROM {rand_table()} "
               f"GROUP BY {col} HAVING COUNT(*) > {random.randint(1, 10)}")

    # SELECT COUNT / MAX / MIN / AVG
    aggs = ["COUNT(*)", "MAX(id)", "MIN(id)", "AVG(price)", "SUM(total)"]
    for _ in range(400):
        yield f"SELECT {random.choice(aggs)} FROM {rand_table()}"

    # SELECT with JOIN
    pairs = [("users", "orders"), ("products", "inventory"),
             ("customers", "transactions"), ("employees", "logs")]
    for _ in range(500):
        t1, t2 = random.choice(pairs)
        yield (f"SELECT {t1}.id, {t2}.{random.choice(COLS_STR)} "
               f"FROM {t1} INNER JOIN {t2} ON {t1}.id = {t2}.{t1[:-1]}_id")

    # INSERT
    for _ in range(400):
        t = rand_table()
        yield (f"INSERT INTO {t} (name, status) "
               f"VALUES ('John Doe', 'active')")

    # UPDATE
    for _ in range(400):
        t = rand_table()
        yield (f"UPDATE {t} SET status = 'inactive' "
               f"WHERE id = {random.randint(1, 999)}")

    # DELETE
    for _ in range(200):
        t = rand_table()
        yield f"DELETE FROM {t} WHERE id = {random.randint(1, 999)}"

    # CREATE TABLE (simplified)
    for _ in range(100):
        t = rand_table() + "_archive"
        yield (f"CREATE TABLE IF NOT EXISTS {t} "
               f"(id INT PRIMARY KEY, name VARCHAR(255), created_at TIMESTAMP)")

    # Subqueries (benign)
    for _ in range(400):
        t1, t2 = random.sample(TABLES, 2)
        yield (f"SELECT * FROM {t1} WHERE id IN "
               f"(SELECT {t1[:-1]}_id FROM {t2} WHERE status = 'active')")


def main():
    out_path = Path(__file__).parent / "benign_sql.csv"
    rows = list(templates())
    random.shuffle(rows)
    rows = rows[:5000]  # cap at 5000

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["payload_norm", "sqli_type", "confidence"])
        writer.writeheader()
        for q in rows:
            writer.writerow({
                "payload_norm": q,
                "sqli_type": "benign",
                "confidence": 0.95,
            })
    print(f"Generated {len(rows)} benign SQL queries → {out_path}")


if __name__ == "__main__":
    main()
