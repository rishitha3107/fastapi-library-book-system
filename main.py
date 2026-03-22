from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI()

# ───────────── DATA ─────────────

books = [
    {"id":1,"title":"Python Basics","author":"John Carter","genre":"Tech","is_available":True},
    {"id":2,"title":"AI Revolution","author":"Sarah Lee","genre":"Science","is_available":True},
    {"id":3,"title":"World History","author":"Mike Brown","genre":"History","is_available":True},
    {"id":4,"title":"Mystery House","author":"Anna Smith","genre":"Fiction","is_available":True},
    {"id":5,"title":"Deep Learning","author":"Andrew Ng","genre":"Tech","is_available":True},
    {"id":6,"title":"Space Science","author":"Carl Sagan","genre":"Science","is_available":True},
]

borrow_records = []
record_counter = 1
queue = []


# ───────────── Q6 MODELS ─────────────

class BorrowRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    member_id: str = Field(..., min_length=4)
    book_id: int = Field(..., gt=0)
    borrow_days: int = Field(..., gt=0, le=60)
    member_type: str = "regular"


class NewBook(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    is_available: bool = True


# ───────────── Q7 HELPERS ─────────────

def find_book(book_id:int):
    for b in books:
        if b["id"] == book_id:
            return b
    return None


def calculate_due_date(borrow_days, member_type="regular"):
    if member_type == "premium":
        borrow_days = min(borrow_days,60)
    else:
        borrow_days = min(borrow_days,30)

    return f"Return by: Day {15 + borrow_days}"


def filter_books_logic(genre=None, author=None, is_available=None):

    result = books

    if genre is not None:
        result = [b for b in result if b["genre"].lower()==genre.lower()]

    if author is not None:
        result = [b for b in result if author.lower() in b["author"].lower()]

    if is_available is not None:
        result = [b for b in result if b["is_available"]==is_available]

    return result


# ───────────── Q1 HOME ─────────────

@app.get("/")
def home():
    return {"message":"Welcome to City Public Library"}


# ───────────── Q2 GET BOOKS ─────────────

@app.get("/books")
def get_books():

    available = [b for b in books if b["is_available"]]

    return {
        "books":books,
        "total":len(books),
        "available_count":len(available)
    }


# ───────────── Q4 BORROW RECORDS ─────────────

@app.get("/borrow-records")
def get_records():
    return {"records":borrow_records,"total":len(borrow_records)}


# ───────────── Q5 BOOK SUMMARY ─────────────

@app.get("/books/summary")
def summary():

    genre_count = {}

    for b in books:
        genre_count[b["genre"]] = genre_count.get(b["genre"],0)+1

    available = [b for b in books if b["is_available"]]

    return {
        "total_books":len(books),
        "available":len(available),
        "borrowed":len(books)-len(available),
        "genre_breakdown":genre_count
    }


# ───────────── Q10 FILTER BOOKS ─────────────

@app.get("/books/filter")
def filter_books(
        genre:str=Query(None),
        author:str=Query(None),
        is_available:bool=Query(None)
):

    result = filter_books_logic(genre,author,is_available)

    return {"books":result,"count":len(result)}


# ───────────── Q16 SEARCH BOOKS ─────────────

@app.get("/books/search")
def search_books(keyword:str):

    result = [
        b for b in books
        if keyword.lower() in b["title"].lower()
        or keyword.lower() in b["author"].lower()
    ]

    return {"results":result,"total_found":len(result)}


# ───────────── Q17 SORT BOOKS ─────────────

@app.get("/books/sort")
def sort_books(
        sort_by:str="title",
        order:str="asc"
):

    if sort_by not in ["title","author","genre"]:
        return {"error":"Invalid sort field"}

    if order not in ["asc","desc"]:
        return {"error":"Invalid order"}

    reverse = order=="desc"

    sorted_books = sorted(books,key=lambda x:x[sort_by],reverse=reverse)

    return {
        "sort_by":sort_by,
        "order":order,
        "books":sorted_books
    }


# ───────────── Q18 PAGINATION ─────────────

@app.get("/books/page")
def paginate(page:int=1,limit:int=3):

    start = (page-1)*limit
    end = start+limit

    total_pages = math.ceil(len(books)/limit)

    return {
        "total":len(books),
        "total_pages":total_pages,
        "page":page,
        "limit":limit,
        "books":books[start:end]
    }


# ───────────── Q19 SEARCH BORROW RECORDS ─────────────

@app.get("/borrow-records/search")
def search_records(member_name:str):

    result = [
        r for r in borrow_records
        if member_name.lower() in r["member_name"].lower()
    ]

    return {"results":result,"total_found":len(result)}


# ───────────── Q19 PAGINATE BORROW RECORDS ─────────────

@app.get("/borrow-records/page")
def paginate_records(page:int=1,limit:int=2):

    start=(page-1)*limit
    end=start+limit

    total_pages=math.ceil(len(borrow_records)/limit)

    return {
        "total":len(borrow_records),
        "page":page,
        "limit":limit,
        "total_pages":total_pages,
        "records":borrow_records[start:end]
    }


# ───────────── Q20 BROWSE BOOKS ─────────────

@app.get("/books/browse")
def browse_books(
        keyword:str=None,
        sort_by:str="title",
        order:str="asc",
        page:int=1,
        limit:int=3
):

    result = books

    if keyword:
        result=[
            b for b in result
            if keyword.lower() in b["title"].lower()
            or keyword.lower() in b["author"].lower()
        ]

    reverse = order=="desc"

    result = sorted(result,key=lambda x:x[sort_by],reverse=reverse)

    start=(page-1)*limit
    end=start+limit

    total=len(result)

    total_pages=math.ceil(total/limit)

    return {
        "keyword":keyword,
        "sort_by":sort_by,
        "order":order,
        "page":page,
        "limit":limit,
        "total_found":total,
        "total_pages":total_pages,
        "books":result[start:end]
    }


# ───────────── Q11 ADD BOOK ─────────────

@app.post("/books")
def add_book(new_book:NewBook,response:Response):

    existing=[b["title"].lower() for b in books]

    if new_book.title.lower() in existing:
        response.status_code=status.HTTP_400_BAD_REQUEST
        return {"error":"Duplicate title"}

    new_id=max(b["id"] for b in books)+1

    book={
        "id":new_id,
        "title":new_book.title,
        "author":new_book.author,
        "genre":new_book.genre,
        "is_available":new_book.is_available
    }

    books.append(book)

    response.status_code=status.HTTP_201_CREATED

    return {"book":book}


# ───────────── Q12 UPDATE BOOK ─────────────

@app.put("/books/{book_id}")
def update_book(
        book_id:int,
        response:Response,
        genre:str=None,
        is_available:bool=None
):

    book=find_book(book_id)

    if not book:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"error":"Book not found"}

    if genre is not None:
        book["genre"]=genre

    if is_available is not None:
        book["is_available"]=is_available

    return {"updated":book}


# ───────────── Q13 DELETE BOOK ─────────────

@app.delete("/books/{book_id}")
def delete_book(book_id:int,response:Response):

    book=find_book(book_id)

    if not book:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"error":"Book not found"}

    books.remove(book)

    return {"message":f"{book['title']} deleted"}


# ───────────── Q14 QUEUE ─────────────

@app.post("/queue/add")
def add_queue(member_name:str,book_id:int):

    book=find_book(book_id)

    if not book:
        return {"error":"Book not found"}

    if book["is_available"]:
        return {"message":"Book available — borrow directly"}

    queue.append({
        "member_name":member_name,
        "book_id":book_id
    })

    return {"message":"Added to queue"}


@app.get("/queue")
def get_queue():
    return {"queue":queue}


# ───────────── Q15 RETURN WORKFLOW ─────────────

@app.post("/return/{book_id}")
def return_book(book_id:int):

    book=find_book(book_id)

    if not book:
        return {"error":"Book not found"}

    book["is_available"]=True

    for q in queue:

        if q["book_id"]==book_id:

            queue.remove(q)

            record={
                "member_name":q["member_name"],
                "book_id":book_id,
                "auto_assigned":True
            }

            borrow_records.append(record)

            book["is_available"]=False

            return {"message":"returned and re-assigned"}

    return {"message":"returned and available"}


# ───────────── Q8 BORROW BOOK ─────────────

@app.post("/borrow")
def borrow(data:BorrowRequest):

    global record_counter

    book=find_book(data.book_id)

    if not book:
        return {"error":"Book not found"}

    if not book["is_available"]:
        return {"error":"Book already borrowed"}

    book["is_available"]=False

    due=calculate_due_date(data.borrow_days,data.member_type)

    record={
        "record_id":record_counter,
        "member_name":data.member_name,
        "member_id":data.member_id,
        "book_id":data.book_id,
        "due_date":due
    }

    borrow_records.append(record)

    record_counter+=1

    return record


# ───────────── Q3 GET BOOK BY ID (KEEP LAST) ─────────────

@app.get("/books/{book_id}")
def get_book(book_id:int):

    book=find_book(book_id)

    if not book:
        return {"error":"Book not found"}

    return book
