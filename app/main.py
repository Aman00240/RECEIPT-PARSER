from fastapi import FastAPI
from app.routers import receipts


app = FastAPI(
    title="AI Receipt Parser",
    description="A stateless API that uses Llama 3.2 Vision to extract data from receipts.",
)

app.include_router(receipts.router)


@app.get("/")
def home():
    return {"status": "ok", "message": "Receipt Parser API is runnign"}
