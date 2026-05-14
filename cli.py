"""
Module 3 Project: Library Management System
cli.py — Command-line interface

Your job: Implement each menu handler function below.
The main menu loop is already provided — just fill in the handlers.
"""

from library_system import (
    init_db, add_author, add_book, add_borrower,
    checkout_book, return_book, find_books_by_author,
    get_overdue_books, get_popular_genres, get_available_books, Session, engine, Author
)


def menu_add_book():
    """Prompt for book details and add to the database."""
    # TODO: Use input() to collect title, isbn, author name, year, genres
    # Tip: You may need to add the author first if they don't exist
    # TODO: Call add_book() and print a confirmation message
    title = input("Title: ")
    isbn = input("ISBN: ")
    author_name = input("Author Name: ")
    published_year = int(input("Publised Year: "))
    genres = input("Genres (Separated By Commas): ")
    genre_names = [genre.strip() for genre in genres.split(",")]
    with Session(engine) as session:
        author = (
            session.query(Author)
            .filter(Author.name.ilike(author_name))
            .first()
        )

        if author is None:
            author = Author(name=author_name)
            session.add(author)
            session.commit()
            session.refresh(author)

        author_id = author.id

    add_book(
        title,
        isbn,
        author_id,
        published_year,
        genre_names=genre_names
    )
    add_book(title, isbn, author_id, published_year, genre_names)


def menu_add_borrower():
    """Prompt for borrower details and register in the database."""
    # TODO: Use input() to collect name, email, phone
    # TODO: Call add_borrower() and print a confirmation message
    name = input("Name: ")
    email = input("Email: ")
    phone = input("Phone (Optional): ").strip()

    if phone == "":
        phone = None

    borrower = add_borrower(name, email, phone)

    print(f'Borrower "{borrower.name}" added successfully.')


def menu_checkout():
    """Prompt for book ID and borrower ID, then check out the book."""
    # TODO: Show available books (call get_available_books())
    # TODO: Prompt for book_id and borrower_id
    # TODO: Call checkout_book() and handle ValueError (book not available)
    
    available_books = get_available_books()

    print("\nAvailable Books:")
    for book in available_books:
        print(f"{book.id}: {book.title}")

    book_id = int(input("\nBook ID: "))
    borrower_id = int(input("Borrower ID: "))

    try:
        checkout = checkout_book(book_id, borrower_id)

        print(
            f'Book "{checkout.book.title}" checked out successfully.'
        )

    except ValueError as e:
        print(f"Error: {e}")


def menu_return():
    """Prompt for checkout ID and return the book."""
    # TODO: Prompt for checkout_id, call return_book(), print confirmation
    checkout_id = int(input("Checkout ID: "))

    try:
        checkout = return_book(checkout_id)

        print(
            f'Book "{checkout.book.title}" returned successfully.'
        )

    except ValueError as e:
        print(f"Error: {e}")


def menu_search_by_author():
    """Prompt for author name and display matching books."""
    # TODO: Prompt for author_name, call find_books_by_author(), print results
    author_name = input("Author Name: ")

    books = find_books_by_author(author_name)

    if not books:
        print("No matching books found.")
        return

    print("\nMatching Books:")

    for book in books:
        print(f"{book.id}: {book.title}")


def menu_overdue():
    """Display all overdue checkouts."""
    # TODO: Call get_overdue_books() and print results
    overdue_books = get_overdue_books()

    if not overdue_books:
        print("No overdue books.")
        return

    print("\nOverdue Checkouts:")

    for checkout in overdue_books:
        print(
            f"Checkout ID: {checkout.id} | "
            f"Book: {checkout.book.title} | "
            f"Borrower: {checkout.borrower.name} | "
            f"Due Date: {checkout.due_date}"
        )


def menu_popular_genres():
    """Display the most popular genres by checkout count."""
    # TODO: Call get_popular_genres() and print results
    popular_genres = get_popular_genres()

    if not popular_genres:
        print("No genre data available.")
        return

    print("\nMost Popular Genres:")

    for genre, checkout_count in popular_genres:
        print(f"{genre.name}: {checkout_count} checkouts")


def main():
    init_db()

    while True:
        print("\n=== Library Management System ===")
        print("1. Add a book")
        print("2. Register a borrower")
        print("3. Check out a book")
        print("4. Return a book")
        print("5. Search by author")
        print("6. View overdue books")
        print("7. View popular genres")
        print("8. Quit")

        choice = input("\nChoose an option (1-8): ").strip()

        if choice == "1":
            menu_add_book()
        elif choice == "2":
            menu_add_borrower()
        elif choice == "3":
            menu_checkout()
        elif choice == "4":
            menu_return()
        elif choice == "5":
            menu_search_by_author()
        elif choice == "6":
            menu_overdue()
        elif choice == "7":
            menu_popular_genres()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-8.")


if __name__ == "__main__":
    main()
