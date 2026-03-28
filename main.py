from fastapi import FastAPI

app = FastAPI()
@app.get("/data")

def data():
    return {"message": "Hello, World!"}