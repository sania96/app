from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import os
from app.processor import process_video

router = APIRouter()

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    input_path = f"uploads/{file.filename}"
    
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Call the processing function and get the output path
    output_path = process_video(input_path)
    
    # Extract the filename (e.g., 'sample_censored.mp4')
    output_filename = os.path.basename(output_path)
    
    # Return just the filename for the frontend to construct the URL
    return {"message": "Processed", "output_video": output_filename}

@router.get("/download/{file_name}")
async def download_video(file_name: str):
    file_path = f"outputs/{file_name}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='video/mp4', filename=file_name)
    return {"error": "File not found"}
