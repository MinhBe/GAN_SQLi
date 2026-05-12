"""parser_gate.py — Syntax validity check với sqlparse + sqlglot fallback."""
import sqlparse

try:
    import sqlglot
    HAS_SQLGLOT = True
except ImportError:
    HAS_SQLGLOT = False


class SQLParserGate:
    """Wrap payload trong context query và kiểm tra parse được không."""

    def __init__(self, dialect: str = "mysql", use_sqlglot: bool = True):
        self.dialect = dialect
        self.use_sqlglot = use_sqlglot and HAS_SQLGLOT

    def evaluate(self, payload: str) -> int:
        if not payload or not isinstance(payload, str):
            return 0
        wrapped = f"SELECT * FROM dummy WHERE id={payload}"

        try:
            parsed = sqlparse.parse(wrapped)
            if not parsed or not parsed[0].tokens:
                return 0
        except Exception:
            return 0

        if self.use_sqlglot:
            try:
                sqlglot.parse_one(wrapped, dialect=self.dialect)
            except Exception:
                return 0

        return 1
