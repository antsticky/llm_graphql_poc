import psycopg2
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine

conn = psycopg2.connect(
    dbname="book_store_db",
    user="admin",
    password="admin",
    host="localhost",
    port="5432"
)

db_url = "postgresql+psycopg2://admin:admin@localhost/book_store_db"
engine = create_engine(db_url)

sql_database = SQLDatabase(engine)
chat_model = ChatOpenAI(temperature=0)

db_chain = SQLDatabaseChain.from_llm(chat_model, sql_database)

def text_to_sql(text):
    try:
        result = db_chain.run(text)
        return result
    except Exception as e:
        return str(e)

def main():
    prompt = "What is the total number of pages in the books written by Bernard Ortega, published by the company where John Jones is the CEO"
    
    results = text_to_sql(prompt)
    print(results)

