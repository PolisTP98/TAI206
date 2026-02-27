# -----------------
# | IMPORTACIONES |
# -----------------

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


# --------------------------------------
# | INICIALIZAR LA INSTANCIA DE LA API |
# --------------------------------------

app = FastAPI(
    title = "API de biblioteca digital", 
    description = "Isaac Abdiel Sánchez López", 
    version = "1.0"
)


# --------------------------------------
# | MODELOS DE VALIDACIÓN CON Pydantic |
# --------------------------------------

# INFORMACIÓN DE UN LIBRO
class CreateBook(BaseModel):
    title: str = Field(..., min_length = 1, description = "Título del libro")
    author: str = Field(..., min_length = 1, description = "Autor del libro")

# INDICAR SI UN LIBRO ESTÁ DISPONIBLE PARA UN PRÉSTAMO
class BookOut(CreateBook):
    id: str
    available: bool

# GENERAR UN PRÉSTAMO
class CreateLoan(BaseModel):
    book_id: str
    user_name: str = Field(..., min_length = 1, description = "Nombre del usuario")

# INFORMACIÓN DE UN PRÉSTAMO
class LoanOut(BaseModel):
    id: str
    book_id: str
    user_name: str
    loan_date: datetime
    return_date: Optional[datetime] = None


# ----------------------------
# | BASE DE DATOS EN MEMORIA |
# ----------------------------

# ALMACENAR LIBROS
books_list = []

# ALMACENAR PRÉSTAMOS
loans_list = []


# -------------
# | FUNCIONES |
# -------------

# DETERMINAR SI UN LIBRO ESTÁ DISPONIBLE PARA UN PRÉSTAMO
def is_available(book_id: str) -> bool:
    for loan in loans_list:
        if loan["book_id"] == book_id and loan["return_date"] is None:
            return False
    return True

# BUSCAR UN LIBRO POR SU ID
def find_book(book_id: str):
    for book in books_list:
        if book["id"] == book_id:
            return book
    return None

# BUSCAR UN PRÉSTAMO POR SU ID
def find_loan(loan_id: str):
    for loan in loans_list:
        if loan["id"] == loan_id:
            return loan
    return None


# -------------
# | ENDPOINTS |
# -------------

# REGISTRAR UN LIBRO
@app.post("/books", status_code = status.HTTP_201_CREATED)
def register_book(book: CreateBook):
    new_book = {
        # GENERAR UN ID ÚNICO
        "id": str(uuid.uuid4()), 
        "title": book.title, 
        "author": book.author
    }
    books_list.append(new_book)
    return BookOut(
        id = new_book["id"], 
        title = new_book["title"], 
        author = new_book["author"], 
        available = True
    )

# LISTA DE LIBROS DISPONIBLES PARA PRÉSTAMOS
@app.get("/books/available", response_model = List[BookOut])
def available_books():
    result = []
    for book in books_list:
        available = is_available(book["id"])
        if available:
            result.append(BookOut(
                id = book["id"], 
                title = book["title"], 
                author = book["author"], 
                available = True
            ))        
    return result

# BUSCAR UN LIBRO POR SU NOMBRE
@app.get("/books/search", response_model=List[BookOut])
def search_by_name(name: str = Query(..., min_length = 1, description = "Nombre parcial o completo")):
    name_lower = name.lower()
    result = []
    for book in books_list:
        if name_lower in book["title"].lower():
            available = is_available(book["id"])
            result.append(BookOut(
                id = book["id"], 
                title = book["title"], 
                author = book["author"], 
                available = available
            ))
    if not result:
        pass
    return result

# REGISTRAR UN PRÉSTAMO
@app.post("/loans", status_code = status.HTTP_201_CREATED)
def register_loan(loan: CreateLoan):
    book = find_book(loan.book_id)
    if not book:
        raise HTTPException(status_code = 404, detail = "Libro no encontrado")
    if not is_available(loan.book_id):
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "El libro ya está prestado actualmente"
        )
    new_loan = {
        "id": str(uuid.uuid4()), 
        "book_id": loan.book_id, 
        "user_name": loan.user_name, 
        "loan_date": datetime.now(), 
        "return_date": None
    }
    loans_list.append(new_loan)
    return LoanOut(**new_loan)

# REGRESAR UN LIBRO
@app.put("/loans/{loan_id}/return", status_code = status.HTTP_200_OK)
def return_book(loan_id: str):
    loan = find_loan(loan_id)
    if not loan:
        raise HTTPException(status_code = 404, detail = "Préstamo no encontrado")
    loan["return_date"] = datetime.now()
    return LoanOut(**loan)

# ELIMINAR UN PRÉSTAMO
@app.delete("/loans/{loan_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_loan(loan_id: str):
    loan = find_loan(loan_id)
    if not loan:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "El registro de préstamo no existe"
        )
    loans_list.remove(loan)
    return

# COMPROBAR EL FUNCIONAMIENTO DE LA API
@app.get("/")
def check_status():
    return {
        "status": "200", 
        "message": "connection OK"
    }