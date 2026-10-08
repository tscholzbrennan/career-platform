from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

# Columns added to existing tables after the first deploy. create_all() only
# creates missing tables, so databases that already exist get these via ALTER.
ADDED_COLUMNS = {
    "profiles": {
        "full_name": "VARCHAR(255)",
        "seeking": "VARCHAR(255)",
        "about": "TEXT",
        "highlights": "JSON",
    },
    "experiences": {
        "category": "VARCHAR(50) DEFAULT 'work'",
    },
}


def ensure_columns(engine: Engine) -> None:
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table, columns in ADDED_COLUMNS.items():
            existing = {column["name"] for column in inspector.get_columns(table)}
            for name, ddl_type in columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl_type}"))
