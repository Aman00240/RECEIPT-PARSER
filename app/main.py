from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import receipts


app = FastAPI(
    title="AI Receipt Parser",
    description="A stateless API that uses Llama 3.2 Vision to extract data from receipts.",
)

origins = ["http://127.0.0.1:8501", "https://receipt-parser-frontend.onrender.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(receipts.router)


@app.get("/")
def home():
    return {"status": "ok", "message": "Receipt Parser API is runnign"}
