import click
from faker import Faker

from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, ForeignKey


ALLOWED_VALUES = ["book", "author", "publisher"]

Base = declarative_base()

# Author table
class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    nationality = Column(String, nullable=True)
    sex = Column(String, nullable=False)  # Male/Female
    eye_color = Column(String, nullable=True)
    height = Column(Integer, nullable=False)
    spouse_name = Column(String, nullable=True)

# Publisher table
class Publisher(Base):
    __tablename__ = 'publisher'
    id = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False)
    establish_date = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email_address = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False)
    ceo_name = Column(String, nullable=True)
    yearly_income = Column(Integer, nullable=True)

# Book table
class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'), nullable=False)
    publisher_id = Column(Integer, ForeignKey('publisher.id'), nullable=False)
    publish_date = Column(Date, nullable=True)
    price = Column(Float, nullable=False)
    genre = Column(String, nullable=False)
    page_count = Column(Integer, nullable=False)
    hardcover = Column(Boolean, nullable=False)
    language = Column(String, nullable=True)

    author = relationship("Author", back_populates="books")
    publisher = relationship("Publisher", back_populates="books")

Author.books = relationship("Book", order_by=Book.id, back_populates="author")
Publisher.books = relationship("Book", order_by=Book.id, back_populates="publisher")

# Create Database and Tables
engine = create_engine('postgresql://admin:admin@localhost/book_store_db')
Base.metadata.create_all(engine)

# Add Example Data
Session = sessionmaker(bind=engine)
session = Session()

# Example Authors
authors = [
    Author(name="George Orwell", date_of_birth="1903-06-25", nationality="British", sex="Male", eye_color="Blue", height=170, spouse_name="Eileen Blair"),
    Author(name="Jane Austen", date_of_birth="1775-12-16", nationality="British", sex="Female", eye_color="Brown", height=155, spouse_name=None),
    Author(name="Mark Twain", date_of_birth="1835-11-30", nationality="American", sex="Male", eye_color="Gray", height=175, spouse_name="Olivia Langdon")
]

# Example Publishers
publishers = [
    Publisher(company_name="Penguin Books", establish_date="1935-07-30", address="80 Strand, London", phone_number="123456789", email_address="info@penguin.co.uk", is_active=True, ceo_name="John Smith", yearly_income=5000000),
    Publisher(company_name="HarperCollins", establish_date="1989-03-17", address="195 Broadway, New York", phone_number="987654321", email_address="contact@harpercollins.com", is_active=True, ceo_name="Emma Brown", yearly_income=7500000),
    Publisher(company_name="Vintage Books", establish_date="1954-01-01", address="1745 Broadway, New York", phone_number="456789123", email_address="support@vintagebooks.com", is_active=False, ceo_name="Liam Johnson", yearly_income=None)
]

# Example Books
books = [
    Book(title="1984", author_id=1, publisher_id=1, publish_date="1949-06-08", price=15.99, genre="Dystopian", page_count=328, hardcover=True, language="English"),
    Book(title="Pride and Prejudice", author_id=2, publisher_id=2, publish_date="1813-01-28", price=12.99, genre="Romance", page_count=279, hardcover=False, language="English"),
    Book(title="Adventures of Huckleberry Finn", author_id=3, publisher_id=3, publish_date="1885-02-18", price=10.99, genre="Adventure", page_count=366, hardcover=False, language="English")
]

def create_publisher():
    fake = Faker()
    publishers = []
    for _ in range(100):
        publishers.append(Publisher(
            company_name=fake.company(),
            establish_date=fake.date_this_century() if fake.boolean(chance_of_getting_true=70) else None,
            address=fake.address(),
            phone_number=fake.phone_number() if fake.boolean(chance_of_getting_true=80) else None,
            email_address=fake.email() if fake.boolean(chance_of_getting_true=80) else None,
            is_active=fake.boolean(),
            ceo_name=fake.name() if fake.boolean(chance_of_getting_true=70) else None,
            yearly_income=fake.random_int(min=100000, max=10000000) if fake.boolean(chance_of_getting_true=60) else None
        ))

    # Add and commit data
    session.add_all(publishers)
    session.commit()

    print("100 publishers have been successfully added!")


def create_author():
    fake = Faker()
    
    authors = []
# This code snippet is a function named `create_author` that generates fake data for authors using the
# Faker library. Here's a breakdown of what it does:
    for _ in range(50):
        authors.append(Author(
            name=fake.name(),
            date_of_birth=fake.date_of_birth(minimum_age=20, maximum_age=90),
            nationality=fake.country() if fake.boolean(chance_of_getting_true=70) else None,
            sex=fake.random_element(elements=["Male", "Female"]),
            eye_color=fake.random_element(elements=["Blue", "Brown", "Green", "Gray", "Hazel", "Amber"]) if fake.boolean(chance_of_getting_true=80) else None,
            height=fake.random_int(min=150, max=200),
            spouse_name=fake.name() if fake.boolean(chance_of_getting_true=50) else None
        ))

    # Add and commit data
    session.add_all(authors)
    session.commit()

    print("50 authors have been successfully added!")
        
def create_book():
    fake = Faker()
    
    # Fetch all authors and publishers
    authors = session.query(Author).all()
    publishers = session.query(Publisher).all()

    # Ensure there are authors and publishers in the database
    if not authors or not publishers:
        raise ValueError("No authors or publishers found in the database. Populate them first.")

    # Generate 500 Book entries
    books = []
    for _ in range(500):
        books.append(Book(
            title=fake.sentence(nb_words=3),  # Random book title with 3 words
            author_id=fake.random_element(elements=[author.id for author in authors]),
            publisher_id=fake.random_element(elements=[publisher.id for publisher in publishers]),
            publish_date=fake.date_this_century() if fake.boolean(chance_of_getting_true=70) else None,
            price=round(fake.random_number(digits=2, fix_len=True) * fake.random.uniform(1, 3), 2),  # Price between ~10-300
            genre=fake.random_element(elements=["Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Biography", "Mystery"]),
            page_count=fake.random_int(min=50, max=1000),
            hardcover=fake.boolean(),
            language=fake.random_element(elements=["English", "Spanish", "French", "German", "Italian", None])
        ))

    # Add and commit data
    session.add_all(books)
    session.commit()

    print("500 books have been successfully added!")
    

def validate_literal(ctx, param, value):
    if value not in ALLOWED_VALUES:
        raise click.BadParameter(f"Value must be one of {', '.join(ALLOWED_VALUES)}")
    return value

@click.command()
@click.option("--table_type", prompt="Table Name", callback=validate_literal, help="Accepted values: book, author, publisher")
def main(table_type):
    match table_type:
        case "book":
            create_book()
        case "author":
            create_author()
        case "publisher":
            create_publisher()