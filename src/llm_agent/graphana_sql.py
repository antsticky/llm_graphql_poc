from flask import Flask, jsonify
from sqlalchemy import create_engine, inspect
from sqlalchemy.sql import text
import graphene
from graphql_server.flask import GraphQLView

import os
korte = os.getenv("KORTE")
print(korte)

# Define connection parameters
DATABASE_URL = "postgresql+psycopg2://admin:admin@localhost:5432/book_store_db"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

from functools import wraps
from flask import request, jsonify

def authenticate_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        #if not auth_header or not validate_token(auth_header):
        #    return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

def validate_token(auth_header):
    # Replace this with your actual token validation logic
    # For example, decode JWT or check against a database
    token = auth_header.split(" ")[1] if " " in auth_header else None
    return token == "your_secure_token"


# Test the database connection
try:
    with engine.connect() as connection:
        print("Connected to the database!")
except Exception as e:
    print(f"Error connecting to the database: {e}")

# Inspect the database schema
inspector = inspect(engine)

# Flask app setup
app = Flask(__name__)

# Serialize SQLAlchemy types to JSON-compatible strings
def serialize_sqlalchemy_type(sql_type):
    return str(sql_type)

@app.route('/table_models', methods=['GET'])
def list_tables():
    table_info = {}
    
    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        table_info[table] = [
            {
                "name": col["name"],
                "type": serialize_sqlalchemy_type(col["type"])
            }
            for col in columns
        ]
    
    return jsonify(table_info)

# Map SQLAlchemy column types to GraphQL types
def map_sqlalchemy_to_graphql(column_type):
    from sqlalchemy.types import Boolean, Integer, String, Float, Date, DateTime, Time

    if isinstance(column_type, Boolean):
        return graphene.Boolean()
    elif isinstance(column_type, Integer):
        return graphene.Int()
    elif isinstance(column_type, Float):
        return graphene.Float()
    elif isinstance(column_type, (String, Date, DateTime, Time)):
        return graphene.String()
    else:
        return graphene.String()  # Default fallback

# Dynamically generate GraphQL types from tables
def generate_graphql_types():
    graphql_types = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)

        # Define a GraphQL type for the table with correct column mappings
        attrs = {
            col['name']: map_sqlalchemy_to_graphql(col['type']) for col in columns
        }
        graphql_types[table_name] = type(table_name, (graphene.ObjectType,), attrs)
    
    return graphql_types

graphql_types = generate_graphql_types()
print("Generated GraphQL Types:", graphql_types)

# Create the GraphQL Query object
class Query(graphene.ObjectType):
    pass

for table_name, graphql_type in graphql_types.items():
    # Add query field dynamically with pagination arguments
    field_name = f"all_{table_name}"
    print(f"Adding field: {field_name}")
    
    Query._meta.fields[field_name] = graphene.Field(
        graphene.List(
            graphql_type,
            description=f"Fetch rows from {table_name} table with pagination"
        ),
        limit=graphene.Int(),  # Argument for maximum number of rows
        offset=graphene.Int(),  # Argument for starting position
        resolver=lambda self, info, limit=None, offset=None, table_name=table_name: [
            dict(row._mapping)
            for row in engine.connect().execute(
                text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset"),
                {"limit": limit or 10, "offset": offset or 0}  # Default values if not provided
            ).fetchall()
        ]
    )



# Create the GraphQL schema
schema = graphene.Schema(query=Query)


def custom_format_error(error):
    # Log the actual error (optional)
    print(f"GraphQL Error: {error}")

    # Return a sanitized and user-friendly error response
    return {
        "message": "An unexpected error occurred. Please contact support if this persists."
    }

# Add the GraphQL endpoint to Flask
@app.route('/graphql', methods=['POST', 'GET'])
@authenticate_request
def graphql_view():
    view = GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True,  # Enable GraphiQL for GET requests
        format_error=custom_format_error,  # Your existing error formatting
        auto_camelcase=False
    )
    return view()


def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
