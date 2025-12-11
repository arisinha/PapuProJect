from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class BuscarInput(BaseModel):
    query: str

@app.post("/buscar")
def buscar(body: BuscarInput):
    # tu lógica real aquí
    return {"result": f"Buscaste: {body.query}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)