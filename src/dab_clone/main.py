from flask import Flask, jsonify
from graphql_server.flask import GraphQLView

from dab_clone.src.auth import authenticate_request

from dab_clone.src.errors import custom_format_error
from dab_clone.src.graphql import get_db_graphql_schema
from dab_clone.src.db_handlers import get_engine, get_tables


DATABASE_URL = "postgresql+psycopg2://admin:admin@localhost:5432/book_store_db"
engine, inspector = get_engine(connection_string=DATABASE_URL)

app = Flask(__name__)


@app.route("/table_models", methods=["GET"])
def list_tables():
    return jsonify(get_tables(inspector=inspector))


@app.route("/graphql", methods=["POST", "GET"])
@authenticate_request
def graphql_view():
    view = GraphQLView.as_view(
        "graphql",
        schema=get_db_graphql_schema(engine=engine),
        graphiql=True,
        format_error=custom_format_error,
        auto_camelcase=False,
    )
    return view()


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
