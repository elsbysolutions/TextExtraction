from fastapi import APIRouter, HTTPException, UploadFile, Form
from core.text_extractors import extract_text, determine_input_type

router = APIRouter()

@router.post("/extract-text")
async def extract_text_from_source(request_data: dict):
    input_source = request_data.get("input_source", "")  # Extract input_source from the request_data dictionary
    input_source = rf'{input_source}'
    try:
        # Call your extract_text function with input_source
        extracted_text = extract_text(input_source)
        return {"text": extracted_text}
    except Exception as e:
        # Handle exceptions appropriately, e.g., return an error response
        raise HTTPException(status_code=500, detail=str(e))