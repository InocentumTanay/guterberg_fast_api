from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from typing import Optional
from .database import get_db
from .models import (
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


# Add your routes here
@app.get("/")
def read_root():
    return {"message": "Gutenberg Fast API"}


from fastapi import HTTPException


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
    try:
        query = db.query(BooksBook)

        if gutenberg_id:
            query = query.filter(BooksBook.gutenberg_id == gutenberg_id)
        if language:
            languages = language.split(",")
            query = query.join(BooksBookLanguage).join(BooksLanguage).filter(BooksLanguage.code.in_(languages))
        if mime_type:
            query = query.join(BooksFormat).filter(BooksFormat.mime_type == mime_type)
        if topic:
            topics = topic.split(",")
            query = query.join(BooksBookSubject).join(BooksSubject).filter(BooksSubject.name.ilike(f"%{topics[0]}%"))
            query = query.union(
                query.join(BooksBookBookshelf).join(BooksBookshelf).filter(BooksBookshelf.name.ilike(f"%{topics[0]}%"))
            )
            for t in topics[1:]:
                query = query.union(
                    query.join(BooksBookSubject).join(BooksSubject).filter(BooksSubject.name.ilike(f"%{t}%"))
                ).union(
                    query.join(BooksBookBookshelf).join(BooksBookshelf).filter(BooksBookshelf.name.ilike(f"%{t}%"))
                )
        if author:
            query = query.join(BooksBookAuthor).join(BooksAuthor).filter(BooksAuthor.name.ilike(f"%{author}%"))
        if title:
            query = query.filter(BooksBook.title.ilike(f"%{title}%"))

        query = query.order_by(BooksBook.download_count.desc()).offset(skip).limit(limit)
        books = query.all()
        total_count = db.query(BooksBook).count()
        page_count = len(books)

        result = []
        for book in books:
            book_info = {
                "id": book.id,
                "download_count": book.download_count,
                "gutenberg_id": book.gutenberg_id,
                "title": book.title,
                "authors": [],
                "subjects": [],
                "bookshelves": [],
                "languages": [],
                "download_links": []
            }
            authors = db.query(BooksAuthor).join(BooksBookAuthor).filter(BooksBookAuthor.book_id == book.id).all()
            subjects = db.query(BooksSubject).join(BooksBookSubject).filter(BooksBookSubject.book_id == book.id).all()
            bookshelves = db.query(BooksBookshelf).join(BooksBookBookshelf).filter(
                BooksBookBookshelf.book_id == book.id).all()
            languages = db.query(BooksLanguage).join(BooksBookLanguage).filter(
                BooksBookLanguage.book_id == book.id).all()
            download_links = db.query(BooksFormat).filter(BooksFormat.book_id == book.id).all()

            book_info['authors'] = [author.name for author in authors]
            book_info['subjects'] = [subject.name for subject in subjects]
            book_info['bookshelves'] = [bookshelf.name for bookshelf in bookshelves]
            book_info['languages'] = [language.code for language in languages]
            book_info['download_links'] = [download_link.url for download_link in download_links]

            result.append(book_info)

        return {"total_count": total_count, "page_count": page_count, "books": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
