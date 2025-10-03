from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def home():
    return {"mensaje": "Bienvenido a API Canchas Deluxe"}
