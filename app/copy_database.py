"""Copy every table from one database into another (SQLite → Railway Postgres).

    python -m app.copy_database --source sqlite:///career_platform.db --target "$DATABASE_PUBLIC_URL"
"""
import argparse

from sqlalchemy import create_engine, func, insert, select, text

import app.models  # noqa: F401  # register every table on Base.metadata
from app.config import resolve_database_url
from app.db import Base
from app.migrations import ensure_columns


class TargetNotEmpty(Exception):
    pass


def _count(conn, table) -> int:
    return conn.execute(select(func.count()).select_from(table)).scalar_one()


def copy_database(source_url: str, target_url: str, replace: bool = False) -> dict[str, int]:
    tables = Base.metadata.sorted_tables
    source = create_engine(resolve_database_url(source_url, "", on_railway=False))
    target = create_engine(resolve_database_url(target_url, "", on_railway=False))
    try:
        Base.metadata.create_all(target)
        ensure_columns(target)
        counts = {}
        with source.connect() as src, target.begin() as dst:
            filled = [table.name for table in tables if _count(dst, table)]
            if filled and not replace:
                raise TargetNotEmpty(f"target already has rows in {', '.join(filled)}; pass --replace to overwrite")
            for table in reversed(tables):
                dst.execute(table.delete())
            for table in tables:
                rows = [dict(row._mapping) for row in src.execute(select(table))]
                if rows:
                    dst.execute(insert(table), rows)
                counts[table.name] = len(rows)
            if dst.dialect.name == "postgresql":
                # Rows were inserted with explicit ids, so move each id sequence past them.
                for table in tables:
                    dst.execute(text(
                        f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), "
                        f"COALESCE((SELECT MAX(id) FROM {table.name}), 0) + 1, false)"
                    ))
        with target.connect() as dst:
            for table in tables:
                if _count(dst, table) != counts[table.name]:
                    raise RuntimeError(f"row count mismatch in {table.name} after copy")
        return counts
    finally:
        source.dispose()
        target.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--replace", action="store_true", help="delete existing rows in the target first")
    args = parser.parse_args()
    for name, count in copy_database(args.source, args.target, args.replace).items():
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()
