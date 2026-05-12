"""db_sandbox.py — SQLite in-memory để check payload chạy được không."""
import sqlite3
import threading


class DBSandbox:
    """Thread-safe SQLite sandbox để evaluate payload executability."""

    def __init__(self):
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.cur = self.conn.cursor()
        self._setup_schema()

    def _setup_schema(self):
        try:
            self.cur.execute(
                "CREATE TABLE dummy (id INTEGER, name TEXT, email TEXT)"
            )
            self.cur.execute(
                "INSERT INTO dummy VALUES (1, 'admin', 'admin@test.com')"
            )
            self.cur.execute(
                "INSERT INTO dummy VALUES (2, 'user', 'user@test.com')"
            )
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def evaluate(self, payload: str) -> int:
        """Returns 1 nếu payload chạy được trong context SQL, 0 nếu syntax error."""
        if not payload or not isinstance(payload, str):
            return 0

        wrapped = f"SELECT * FROM dummy WHERE id={payload}"

        with self._lock:
            try:
                self.cur.execute(wrapped)
                _ = self.cur.fetchall()
                return 1
            except (sqlite3.OperationalError, sqlite3.Warning, sqlite3.DatabaseError):
                return 0
            except Exception:
                return 0

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
