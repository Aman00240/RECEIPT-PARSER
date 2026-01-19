from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from app.schemas import ReceiptCreate
from app.services.vision import extract_receipt_data
from app.utils import rate_limit


router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post("/scan", response_model=ReceiptCreate, dependencies=[Depends(rate_limit)])
async def scan_receipt(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400, detail="Invalid File Type. Please upload a JPEG or PNG"
        )

    image_bytes = await file.read()

    try:
        receipt_data = await extract_receipt_data(image_bytes)
        return receipt_data
    except Exception as e:
        print(f"Error Processing requet {e}")
        raise HTTPException(status_code=500, detail="Failed to process receipt")
