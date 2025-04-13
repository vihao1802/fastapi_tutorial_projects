from fastapi import FastAPI
from typing import List, Optional
from fastapi import Query

app = FastAPI()

book_db = [
    { "id": 1, "title": "To Kill a Mockingbird", "author": "Harper Lee" },
    { "id": 2, "title": "Harry Potter 1", "author": "J.K. Rowling" },
    { "id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald" },
    { "id": 4, "title": "1984", "author": "George Orwell" },
    { "id": 5, "title": "The Catcher in the Rye", "author": "J.D. Salinger" },
    { "id": 6, "title": "Pride and Prejudice", "author": "Jane Austen" },
    { "id": 7, "title": "The Lord of the Rings", "author": "J.R.R. Tolkien" },
    { "id": 8, "title": "Moby-Dick", "author": "Herman Melville" },
    { "id": 9, "title": "The Hobbit", "author": "J.R.R. Tolkien" },
    { "id": 10, "title": "War and Peace", "author": "Leo Tolstoy" }
];


@app.get("/books")
def search_books(title: Optional[str] = Query(None), author: Optional[str] = Query(None)):
    results = book_db
    if title:
        results = [book for book in results if title.lower() in book["title"].lower()]
    if author:
        results = [book for book in results if author.lower() in book["author"].lower()]
    return results


@app.get("/books/{book_id}")
def getBookById(book_id: int):
    return [book for book in book_db if book['id'] == book_id]