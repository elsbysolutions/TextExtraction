from fastapi import APIRouter, HTTPException, UploadFile, Form, File
from core.text_extractors import extract_text, determine_input_type


router = APIRouter()

@router.post("/extract-text")
async def extract_text_from_source(file: UploadFile = File(None), input_source: str = Form(None)):
    if not file and not input_source:
        raise HTTPException(status_code=400, detail="Either 'file' or 'input_source' must be provided.")

    try:
        if file:
            # Check if it's a valid local file (PDF, DOCX, TXT, CSV, HTML)
            file_content = await file.read()
            extracted_text = extract_text(file_content, file.filename)
        elif input_source:
            # Call your extract_text function with input_source
            extracted_text = extract_text(input_source)

        return {"text": extracted_text}
    except Exception as e:
        # Handle exceptions appropriately, e.g., return an error response
        raise HTTPException(status_code=500, detail=str(e))