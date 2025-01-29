from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import (
    BooksBook,
    BooksLanguage,
    BooksFormat,
    BooksSubject,
    BooksBookshelf,
    BooksAuthor,
    BooksBookAuthor,
    BooksBookLanguage,
    BooksBookSubject,
    BooksBookBookshelf,
)

app = FastAPI()


@app.get("/books/", response_model=dict, tags=["Books"])
def get_books(
        gutenberg_id: Optional[int] = None,
        language: Optional[str] = None,
        mime_type: Optional[str] = None,
        topic: Optional[str] = None,
        author: Optional[str] = None,
        title: Optional[str] = None,
        skip: int = 0,
        limit: int = 25,
        db: Session = Depends(get_db)
):
    """
    Retrieve books with optional filters.

    - **gutenberg_id**: Filter by Gutenberg ID
    - **language**: Filter by language code (e.g., "en")
    - **mime_type**: Filter by file format (e.g., "text/plain")
    - **topic**: Filter by topic (subject or bookshelf)
    - **author**: Filter by author's name
    - **title**: Filter by book title
    - **skip**: Number of records to skip for pagination
    - **limit**: Number of records to return

    Returns:
    - A list of books sorted by download count.
    """
    query = db.query(BooksBook)

    # Filter by Gutenberg ID if provided
    if gutenberg_id:
        query = query.filter(BooksBook.gutenberg_id == gutenberg_id)

    # Filter by languages (multiple values supported)
    if language:
        languages = language.split(",")
        query = query.join(BooksBookLanguage).join(BooksLanguage).filter(BooksLanguage.code.in_(languages))

    # Filter by mime type
    if mime_type:
        query = query.join(BooksFormat).filter(BooksFormat.mime_type == mime_type)

    # Filter by topics (subjects or bookshelves)
    if topic:
        topics = topic.split(",")
        query = query.join(BooksBookSubject).join(BooksSubject).filter(BooksSubject.name.ilike(f"%{topics[0]}%")).union(
            query.join(BooksBookBookshelf).join(BooksBookshelf).filter(BooksBookshelf.name.ilike(f"%{topics[0]}%"))
        )
        for t in topics[1:]:
            query = query.union(
                query.join(BooksBookSubject).join(BooksSubject).filter(BooksSubject.name.ilike(f"%{t}%")).union(
                    query.join(BooksBookBookshelf).join(BooksBookshelf).filter(BooksBookshelf.name.ilike(f"%{t}%"))
                )
            )

    # Filter by author
    if author:
        query = query.join(BooksBookAuthor).join(BooksAuthor).filter(BooksAuthor.name.ilike(f"%{author}%"))

    # Filter by title
    if title:
        query = query.filter(BooksBook.title.ilike(f"%{title}%"))

    # Total count of books meeting the criteria
    total_count = query.count()

    # Pagination and sorting by download count
    query = query.order_by(BooksBook.download_count.desc()).offset(skip).limit(limit)
    books = query.all()

    # Build the response with book details
    result = []
    for book in books:
        book_info = {
            "title": book.title,
            "authors": [],
            "subjects": [],
            "bookshelves": [],
            "languages": [],
            "download_links": []
        }

        # Fetch authors from the BooksBookAuthor bridge table
        authors = db.query(BooksAuthor).join(BooksBookAuthor).filter(BooksBookAuthor.book_id == book.id).all()
        book_info['authors'] = [author.name for author in authors]

        subjects = db.query(BooksSubject).join(BooksBookSubject).filter(BooksBookSubject.book_id == book.id).all()
        book_info['subjects'] = [subject.name for subject in subjects]

        bookshelves = db.query(BooksBookshelf).join(BooksBookBookshelf).filter(BooksBookBookshelf.book_id == book.id).all()
        book_info['bookshelves'] = [bookshelf.name for bookshelf in bookshelves]

        languages = db.query(BooksLanguage).join(BooksBookLanguage).filter(BooksBookLanguage.book_id == book.id).all()
        book_info['languages'] = [language.code for language in languages]

        download_links = db.query(BooksFormat).filter(BooksFormat.book_id == book.id).all()
        book_info['download_links'] = [download_link.url for download_link in download_links]
        result.append(book_info)

    return {"total_count": total_count, "books": result}

