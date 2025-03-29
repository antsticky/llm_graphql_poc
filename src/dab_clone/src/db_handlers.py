from typing import Dict, List, Any
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.reflection import Inspector


def get_engine(connection_string):
    engine = create_engine(connection_string)
    inspector = inspect(engine)

    try:
        with engine.connect() as connection:
            print("Connected to the database!")
    except Exception as e:
        print(f"Error connecting to the database: {e}")

    return engine, inspector


def serialize_sqlalchemy_type(sql_type) -> str:
    return str(sql_type)


def get_tables(inspector: Inspector) -> Dict[str, List[Dict[str, Any]]]:
    table_info = {}

    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        table_info[table] = [
            {"name": col["name"], "type": serialize_sqlalchemy_type(col["type"])}
            for col in columns
        ]

    return table_info
