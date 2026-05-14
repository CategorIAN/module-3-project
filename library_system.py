"""
Module 3 Project: Library Management System
library_system.py — Database models and query functions

Your job: Implement the SQLAlchemy models and all functions marked with # TODO.
"""

from sqlalchemy import create_engine, String, Integer, Boolean, ForeignKey, Table, Column, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from datetime import date, timedelta
from sqlalchemy import func

engine = create_engine("sqlite:///library.db", echo=False)

class Base(DeclarativeBase):
    pass

# TODO: Create the association table for Book <-> Genre (many-to-many)
book_genres = Table(
     "book_genres",
     Base.metadata,
     Column("book_id",  Integer, ForeignKey("books.id"),  primary_key=True),
     Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
 )

#=======Created Relations=============
book_authors = Table(
    "book_authors",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id", primary_key=True)),
    Column("author_id", Integer, ForeignKey("authors.id", primary_key=True))
)

#Need books to members
book_members = Table(
    "book_members",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id", primary_key=True)),
    Column("borrower_id", Integer, ForeignKey("borrowers.id", primary_key=True))
)

# TODO: Implement the Author model
# Attributes: id (PK), name (required), bio (optional)
class Author(Base):
    __tablename__ = "authors"
    # TODO: define columns
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    bio: Mapped[str] = mapped_column(nullable=True)

# TODO: Implement the Genre model
# Attributes: id (PK), name (required, unique)
class Genre(Base):
    __tablename__ = "genres"
    # TODO: define columns
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    books: Mapped[list["Author"]] = relationship(
        secondary=book_authors, back_populates="books"
    )

# TODO: Implement the Book model
# Attributes: id (PK), title (required), isbn (unique, required),
#             published_year (optional), author_id (FK), available (bool, default True)
# Relationships: author (many-to-one), genres (many-to-many via book_genres)
class Book(Base):
    __tablename__ = "books"
    # TODO: define columns and relationships
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    isbn: Mapped[int] = mapped_column(unique=True, nullable=False)
    year_published: Mapped[int] = mapped_column(nullable=True)
    available: Mapped[bool] = mapped_column(default=True)
    authors: Mapped[list["Author"]] = relationship(
        secondary=book_authors, back_populates="authors"
    )
    genres: Mapped[list["Genre"]] = relationship(
        secondary=book_genres, back_populates="genres"
    )


# TODO: Implement the Borrower model
# Attributes: id (PK), name (required), email (unique, required), phone (optional)
class Borrower(Base):
    __tablename__ = "borrowers"
    # TODO: define columns
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    phone: Mapped[int] = mapped_column(nullable=True)
    

# TODO: Implement the Checkout model
# Attributes: id (PK), book_id (FK), borrower_id (FK),
#             checkout_date (date), due_date (date), return_date (date, nullable)
# Relationships: book, borrower
class Checkout(Base):
    __tablename__ = "checkouts"
    # TODO: define columns and relationships
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    borrower_id: Mapped[int] = mapped_column(ForeignKey("borrowers.id"))
    checkout_date: Mapped[date] = mapped_column()
    due_date: Mapped[date] = mapped_column()
    return_date: Mapped[date] = mapped_column(nullable=True)


def init_db():
    """Create all database tables. Call this before using any other functions."""
    # TODO: Base.metadata.create_all(engine)
    Base.metadata.create_all(engine)


# ============================================================
# CRUD FUNCTIONS — implement each one
# ============================================================

def add_author(name: str, bio: str = None):
    """Add a new author. Returns the created Author object."""
    # TODO: open Session, create Author, add + commit, return it
    with Session(engine) as session:
        author = Author(name = name, bio = bio)
        session.add(author)
        session.commit()
        session.refresh(author)
        return author


def add_book(title: str, isbn: str, author_id: int,
             published_year: int = None, genre_names: list = None):
    """
    Add a new book. Assigns genres by name (creates genre if it doesn't exist yet).
    Returns the created Book object.
    """
    # TODO: implement
    with Session(engine) as session:
        author = session.get(Author, author_id)
        genre_objects = []
        if genre_names:
            for name in genre_names:
                genre = session.query(Genre).filter_by(name=name).first()
                if not genre:
                    genre = Genre(name=name)
                    session.add(genre)
                genre_objects.append(genre)
        book = Book(
            title = title, 
            isbn = isbn, 
            published_year = published_year, 
            genres = genre_objects,
            authors = [author]
        )
        session.add(book)
        session.commit()
        session.refresh(book)
        return book

def add_borrower(name: str, email: str, phone: str = None):
    """Register a new borrower. Returns the created Borrower object."""
    # TODO: implement
    with Session(engine) as session:
        borrower = Borrower(
            name = name,
            email = email,
            phone = phone
        )
        session.add(borrower)
        session.commit()
        session.refresh(borrower)
        return borrower

def checkout_book(book_id: int, borrower_id: int, days: int = 14):
    """
    Check out a book. Sets book.available = False. due_date = today + days.
    Raises ValueError if the book is not available.
    Returns the created Checkout object.
    """
    # TODO: implement
    with Session(engine) as session:
        try:
            book = session.get(Book, book_id)
            if book is None or not book.available:
                raise ValueError("Book Not Available")
            else:
                check_out = Checkout(
                book_id = book_id,
                borrower_id = borrower_id,
                checkout_date = date.today(),
                due_date = date.today() + timedelta(days=14)
                )
                session.add(check_out)
                book.available = False
                session.commit()
                session.refresh(check_out)
                return check_out
        except ValueError as e:
            print(e)

def return_book(checkout_id: int):
    """
    Return a book. Sets book.available = True, sets return_date = today.
    Returns the updated Checkout object.
    """
    # TODO: implement
    with Session(engine) as session:
        checkout = session.get(Checkout, checkout_id)
        checkout.return_date = date.today()
        book = session.get(Book, checkout.book_id)
        book.available = True
        return checkout


# ============================================================
# QUERY FUNCTIONS
# ============================================================

def find_books_by_author(author_name: str) -> list:
    """Return all books whose author name contains author_name (case-insensitive)."""
    # TODO: implement — use LIKE or ilike for partial matching
    with Session(engine) as session:
        return (
            session.query(Book)
            .join(Book.authors)
            .filter(Author.name.ilike(f"%{author_name}%"))
            .all()
        )

def get_overdue_books() -> list:
    """Return all Checkout objects where due_date < today and return_date is None."""
    # TODO: implement
    with Session(engine) as session:
        return (
            session.query(Checkout)
            .filter(Checkout.due_date < date.today(), Checkout.return_date is None)
        )

def get_popular_genres(limit: int = 3) -> list:
    """Return the top `limit` genres by checkout count."""
    # TODO: implement — needs a join through Book to Checkout
    with Session(engine) as session:
        return (
            session.query(Genre.name, func.count(Checkout.id).label("checkout_count"))
            .join(Genre.books)
            .join(Checkout, Book.id == Checkout.book_id)
            .group_by(Genre.id)
            .order_by(func.count(Checkout.id).desc())
            .limit(limit)
            .all()
        )

def get_available_books() -> list:
    """Return all Book objects where available == True."""
    # TODO: implement
    with Session(engine) as session:
        return (
            session.query(Book)
            .filter(Book.available == True)
            .all()
        )
