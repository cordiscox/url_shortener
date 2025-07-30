from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import sqlite3
import shortuuid
import prometheus_fastapi_instrumentator # <--- Importar

# Inicializar la app FastAPI
app = FastAPI()

prometheus_fastapi_instrumentator.Instrumentator().instrument(app).expose(app)

conn = sqlite3.connect("urls.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT NOT NULL UNIQUE,
    long_url TEXT NOT NULL
)
""")
conn.commit()

@app.post("/shorten")
def shorten_url(request: Request, long_url: str):
    short_code = shortuuid.uuid()[:8]
    try:
        cursor.execute("INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (short_code, long_url))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Could not generate unique short code.")
    base_url = str(request.base_url)
    return {"short_url": f"{base_url}{short_code}"}

@app.get("/{short_code}")
def redirect_to_long_url(short_code: str):
    cursor.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    if result:
        return RedirectResponse(url=result[0])
    else:
        raise HTTPException(status_code=404, detail="URL not found")