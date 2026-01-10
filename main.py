#####################################################################
# Rozwiązanie zadania z FastAPI na ocenę 5.0
# Autor: Rami Ayoush
# ###################################################################

from http.client import responses
import sqlite3

from fastapi import FastAPI, HTTPException
import requests

from typing import Any

app = FastAPI()

######################################################################
# Część wstępna labu: punkty 1-4 konspektu (przed obsługą bazy danych)
######################################################################

# Wyswietla napis "Hello World"
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Wyswietla napis "Hello {name}"
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# Oblicza sumę x oraz y; domyślnie x = 0, y = 10
@app.get("/sum")
def sum(x: int = 0, y: int = 10):
    return x+y

# Oblicza różnicę x i y; domyślnie x = 4, y = 3
@app.get("/subtract")
def difference(x: int = 4, y: int = 3):
    return x-y

# Oblicza iloczyn x i y; domyślnie x = 4, y = 3
@app.get("/multiply")
def multiplication(x: int = 4, y: int = 3):
    return x*y

# Podaje nazwę miejsca o współrzędnych geograficznych lat (szerokość geograficzna) i lon (długość geograficzna)
@app.get("/geocode")
def geoc(lat: float, lon: float):
    url=f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}" #http://api.open-notify.org/?lat={lat}&lon={lon}
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return response.json()

#######################################################################
# Część labu od punktu 5 (obsługa bazy danych)
#######################################################################

# Funkcja łączy się z bazą danych dbase i zwraca cursor
def init_connection(dbase: str):
    db = sqlite3.connect(dbase)
    cursor = db.cursor()
    return db, cursor

######################################################################
# Funkcje do obsługi tabeli movie
######################################################################


# Pobiera informacje o filmach z bazy movies-extended.db; zwraca wynik 
# w formie listy słowników
@app.get('/movies')
def get_movies():
    try:
        db, cursor = init_connection('movies-extended.db')
        movies = cursor.execute('SELECT * FROM movie').fetchall()
        output = []
        for movie in movies:
            movie = {'id': movie[0], 'title': movie[1], 'director': movie[2], 'year': movie[3], 'description': movie[4]}
            output.append(movie)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")

# Pobiera informacje o filmie z id = {movie_id} z tabeli movie
@app.get('/movies/{movie_id}')
def get_single_movie(movie_id:int):
    try:
        db, cursor = init_connection('movies-extended.db')
        movie = cursor.execute(f"SELECT * FROM movie WHERE id={movie_id}").fetchone()
        if movie is None:
            return {"message": "Nie znaleziono filmu"}
        return {'id': movie[0], 'title': movie[1], 'director': movie[2], 'year': movie[3], 'description': movie[4]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")
    
# Dodaje film do tabeli movie
@app.post("/movies")
def add_movie(params: dict[str, Any]):
    try:
        db, cursor = init_connection('movies-extended.db')
        cursor.execute('INSERT INTO movie (title, director, year, description) VALUES (?, ?, ?, ?)', (params["title"], params["director"], params["year"], params["description"]))
        db.commit()
        if cursor.rowcount > 0:
            return {"message": f"Film zostal dodany!"}
        else:
            return {"message": f"Nic nie dodano!"}       
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")

# Usuwa wszystkie filmy z tabeli movie
@app.delete("/movies")
async def rem_movies_all():
    try:
        db, cursor = init_connection('movies-extended.db')
        cursor.execute('DELETE FROM movie;')
        db.commit()

        if cursor.rowcount > 0:
            return {"message": f"Wszystkie filmy zostały usunięte!"}
        else:
            return {"message": f"Nic nie zostało zmodyfikowane/pusta tabela"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")


# Aktualizuje dane filmu o id = {id} z tabeli movie
@app.put("/movies/{id}")
def update_movie_id(id: int, params: dict[str, Any]):
    try:
        db, cursor = init_connection('movies-extended.db')
        cursor.execute('UPDATE movie SET title = ?, director = ?, year = ?, description = ? WHERE id = ?;', (params["title"], params["director"], params["year"], params["description"], id))
        db.commit()
        if cursor.rowcount > 0:
            return {"message": f"Dane filmu zostały zaktualizowane"}
        else:
            return {"message": f"Nic nie zostało zmodyfikowane"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")

# Usuwa film o id = {id} z tabeli movie
@app.delete("/movies/{id}")
def rem_movie_id(id: int):
    try:
        db, cursor = init_connection('movies-extended.db')
        cursor.execute('DELETE FROM movie WHERE id = ?;', (id,))
        db.commit()
        if cursor.rowcount > 0:
            return {"message": f"Film został usunięty"}
        else:
            return {"message": f"Nic nie zostało zmodyfikowane"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")

##########################################################################
# Funkcje do obsługi tabeli actors
##########################################################################

# Pobiera informacje o aktorach z tabeli actors z bazy movies-extended.db;
# zwraca wynik w formie listy słowników
@app.get('/actors')
def get_actors():
    try:
        db, cursor = init_connection('movies-extended.db')
        actors = cursor.execute('SELECT * FROM actor').fetchall()
        output = []
        for act in actors:
            actor = {'id': act[0], 'name': act[1], 'surname': act[2]}
            output.append(actor)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")

# Pobiera informacje o aktorze z id = {actor_id} z tabeli actor
@app.get('/actors/{actor_id}')
def get_single_actor(actor_id:int):
    try:
        db, cursor = init_connection('movies-extended.db')
        act = cursor.execute(f"SELECT * FROM actor WHERE id={actor_id}").fetchone()
        if act is None:
            return {"message": "Nie znaleziono aktora"}
        return {'id': act[0], 'name': act[1], 'surname': act[2]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")

# Dodaje aktora do tabeli actors
@app.post("/actors")
def add_actor(params: dict[str, Any]):
    try:
        db, cursor = init_connection('movies-extended.db')
        cursor.execute('INSERT INTO actor (name, surname) VALUES (?, ?)', (params["name"], params["surname"]))
        db.commit()
        if cursor.rowcount > 0:
            return {"message": f"Aktor zostal dodany!"}
        else:
            return {"message": f"Nikogo nie dodano!"}       
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")
    
# Usuwa aktora o id = {id} z tabeli actors
@app.delete("/actors/{id}")
def rem_actor_id(id: int):
    try:
        db, cursor = init_connection('movies-extended.db')
        cursor.execute('DELETE FROM actor WHERE id = ?;', (id,))
        db.commit()
        if cursor.rowcount > 0:
            return {"message": f"Aktor został usunięty"}
        else:
            return {"message": f"Nic nie zostało zmodyfikowane"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")
    
# Aktualizuje dane aktora o id = {id} z tabeli actor
@app.put("/actors/{id}")
def update_movie_id(id: int, params: dict[str, Any]):
    try:
        db, cursor = init_connection('movies-extended.db')
        cursor.execute('UPDATE actor SET name = ?, surname = ? WHERE id = ?;', (params["name"], params["surname"], id))
        db.commit()
        if cursor.rowcount > 0:
            return {"message": f"Dane aktora zostały zaktualizowane"}
        else:
            return {"message": f"Nic nie zostało zmodyfikowane"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")
    
#############################################################################
# Funkcja obsługująca joina tabel actor i movie_actor_through
#############################################################################

# Pobiera informacje o aktorach grających w filmie z id = {film_id} z tabeli
# actors
@app.get('/movies/{film_id}/actors')
def get_cast(film_id:int):
    try:
        db, cursor = init_connection('movies-extended.db')
        actors = cursor.execute(f"SELECT name, surname FROM actor a INNER JOIN movie_actor_through m ON a.id = m.actor_id WHERE m.movie_id = {film_id};")
        #act = cursor.execute(f"SELECT * FROM actor WHERE id={actor_id}").fetchone()
        output = []
        for act in actors:
            actor = {'name': act[0], 'surname': act[1]}
            output.append(actor)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")
