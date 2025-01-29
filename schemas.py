from pydantic import BaseModel
from typing import Optional


class BooksAuthorSchema(BaseModel):
    id: int
    birth_year: Optional[int]
    death_year: Optional[int]
    name: str


class BooksBookSchema(BaseModel):
    id: int
    download_count: Optional[int]
    gutenberg_id: int
    media_type: str
    title: Optional[str]


class BooksBookshelfSchema(BaseModel):
    id: int
    name: str


class BooksLanguageSchema(BaseModel):
    id: int
    code: str


class BooksSubjectSchema(BaseModel):
    id: int
    name: str


class BooksBookAuthorSchema(BaseModel):
    id: int
    book_id: int
    author_id: int


class BooksBookBookshelfSchema(BaseModel):
    id: int
    book_id: int
    bookshelf_id: int


class BooksBookLanguageSchema(BaseModel):
    id: int
    book_id: int
    language_id: int


class BooksBookSubjectSchema(BaseModel):
    id: int
    book_id: int
    subject_id: int


class BooksFormatSchema(BaseModel):
    id: int
    mime_type: str
    url: str
    book_id: int
