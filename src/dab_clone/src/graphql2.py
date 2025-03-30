from sqlalchemy import inspect
from sqlalchemy.sql import text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.types import Boolean, Integer, String, Float, Date, DateTime, Time
import graphene

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

def generate_graphql_types(engine, inspector):
    graphql_types = {}

    tables = inspector.get_table_names()

    for table_name in tables:
        columns = inspector.get_columns(table_name)
        fields = {}

        for column in columns:
            column_name = column["name"]
            column_type = column["type"]
            fields[column_name] = map_sqlalchemy_to_graphql(column_type)

        if table_name == "book":
            fields["publisher"] = graphene.List(
                lambda: graphql_types["publisher"],
                limit=graphene.Int(),
                offset=graphene.Int(),
                resolver=lambda self, info, limit=None, offset=None: fetch_related_data(
                    engine,
                    "publisher",
                    "is_active",
                    self.get("hardcover"),
                    limit,
                    offset,
                ),
                description="List of publishers of the book with optional limit and offset for pagination",
            )
            fields["author"] = graphene.Field(
                lambda: graphql_types["author"],
                limit=graphene.Int(),
                offset=graphene.Int(),
                resolver=lambda self, info, limit=None, offset=None: fetch_related_data(
                    engine, "author", "id", self.get("author_id"), limit, offset
                ),
                description="Author of the book",
            )

        graphql_types[table_name] = type(
            table_name.capitalize(), (graphene.ObjectType,), fields
        )

    return graphql_types


def fetch_related_data(
    engine, table_name, foreign_key, foreign_value, limit=None, offset=None
):
    query = text(
        f"SELECT * FROM {table_name} WHERE {foreign_key} = :foreign_value LIMIT :limit OFFSET :offset"
    )
    results = (
        engine.connect()
        .execute(
            query,
            {
                "foreign_value": foreign_value,
                "limit": limit or 10,
                "offset": offset or 0,
            },
        )
        .fetchall()
    )

    resolved_data = [dict(row._mapping) for row in results] if results else None
    return resolved_data


def get_db_graphql_schema(engine, inspector):
    graphql_types = generate_graphql_types(engine, inspector)

    class Query(graphene.ObjectType):
        all_books = graphene.List(
            graphql_types["book"],
            limit=graphene.Int(),
            offset=graphene.Int(),
            resolver=lambda self, info, limit=None, offset=None: [
                dict(row._mapping)
                for row in engine.connect()
                .execute(
                    text("SELECT * FROM book LIMIT :limit OFFSET :offset"),
                    {"limit": limit or 10, "offset": offset or 0},
                )
                .fetchall()
            ],
        )

    return graphene.Schema(query=Query)
