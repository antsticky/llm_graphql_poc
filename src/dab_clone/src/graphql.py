from typing import Dict, Type

import graphene

from sqlalchemy import inspect
from sqlalchemy.sql import text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.types import Boolean, Integer, String, Float, Date, DateTime, Time


def map_sqlalchemy_to_graphql(column_type):
    if isinstance(column_type, Boolean):
        return graphene.Boolean()
    elif isinstance(column_type, Integer):
        return graphene.Int()
    elif isinstance(column_type, Float):
        return graphene.Float()
    elif isinstance(column_type, (String, Date, DateTime, Time)):
        return graphene.String()
    else:
        return graphene.String()


def generate_graphql_types(
    inspector: Inspector,
) -> Dict[str, Type[graphene.ObjectType]]:
    graphql_types = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)

        attrs = {col["name"]: map_sqlalchemy_to_graphql(col["type"]) for col in columns}
        graphql_types[table_name] = type(table_name, (graphene.ObjectType,), attrs)

    return graphql_types


class Query(graphene.ObjectType):
    pass


def get_db_graphql_schema(engine: Engine) -> graphene.Schema:
    graphql_types = generate_graphql_types(inspector=inspect(engine))

    for table_name, graphql_type in graphql_types.items():
        field_name = f"all_{table_name}"
        print(f"Adding field: {field_name}")

        Query._meta.fields[field_name] = graphene.Field(
            graphene.List(
                graphql_type,
                description=f"Fetch rows from {table_name} table with pagination",
            ),
            limit=graphene.Int(),  # Argument for maximum number of rows
            offset=graphene.Int(),  # Argument for starting position
            resolver=lambda self, info, limit=None, offset=None, table_name=table_name: [
                dict(row._mapping)
                for row in engine.connect()
                .execute(
                    text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset"),
                    {
                        "limit": limit or 10,
                        "offset": offset or 0,
                    },  # Default values if not provided
                )
                .fetchall()
            ],
        )

    return graphene.Schema(query=Query)
