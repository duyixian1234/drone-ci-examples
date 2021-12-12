"""App"""
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root() -> str:
    """Root"""
    return "Hello World"
