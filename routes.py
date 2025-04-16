# routes.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, FileResponse
import os
import boto3
from botocore.exceptions import NoCredentialsError
from app.processor import process_video
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

router = APIRouter()

@router.get("/generate-presigned-upload-url")
async def generate_presigned_upload_url(filename: str):
    try:
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': BUCKET_NAME, 'Key': f"uploads/{filename}", 'ContentType': 'video/mp4'},
            ExpiresIn=3600
        )
        return {"url": url}
    except NoCredentialsError:
        return JSONResponse(status_code=403, content={"message": "Credentials not found"})
    except Exception as e:
        print(f"Error generating pre-signed upload URL: {e}")
        return JSONResponse(status_code=500, content={"message": "Failed to generate pre-signed upload URL"})

@router.post("/upload")
async def upload_video(request: Request):
    data = await request.json()
    file_name = data.get("file_name")
    if not file_name:
        return JSONResponse(status_code=400, content={"message": "Missing file_name"})

    input_filename = f"uploads/{file_name}"

    try:
        output_filename = await process_video_from_s3(input_filename)
        return {"message": "Processed", "output_video_s3_key": f"processed/{output_filename}"} # Return the S3 key
    except NoCredentialsError:
        return JSONResponse(status_code=403, content={"message": "Credentials not found"})
    except Exception as e:
        print(f"Error processing video from S3: {e}")
        return JSONResponse(status_code=500, content={"message": f"Failed to process video: {e}"})

async def process_video_from_s3(input_filename: str):
    local_input_path = f"uploads/{os.path.basename(input_filename)}"
    try:
        s3_client.download_file(BUCKET_NAME, input_filename, local_input_path)
        output_video = process_video(local_input_path)
        output_filename = os.path.basename(output_video)
        s3_client.upload_file(output_video, BUCKET_NAME, f"processed/{output_filename}")
        os.remove(local_input_path)  # Clean up local file
        os.remove(output_video)      # Clean up local output file
        return output_filename
    except NoCredentialsError:
        if os.path.exists(local_input_path):
            os.remove(local_input_path)
        raise
    except Exception as e:
        print(f"Error in process_video_from_s3: {e}")
        if os.path.exists(local_input_path):
            os.remove(local_input_path)
        raise

@router.get("/download-s3-url")
async def generate_presigned_download_url(s3_key: str):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        return {"url": url}
    except NoCredentialsError:
        return JSONResponse(status_code=403, content={"message": "Credentials not found"})
    except Exception as e:
        print(f"Error generating pre-signed download URL: {e}")
        return JSONResponse(status_code=500, content={"message": "Failed to generate pre-signed download URL"})

# Remove the old download route
# @router.get("/download/{file_name}")
# async def download_video(file_name: str):
#     file_path = f"outputs/{file_name}"
#     if os.path.exists(file_path):
#         return FileResponse(file_path, media_type='video/mp4', filename=file_name)
#     return {"error": "File not found"}