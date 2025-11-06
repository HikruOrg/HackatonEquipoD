from fastapi import FastAPI, Query, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv
from main import run_pipeline  # función que corre tu flujo principal

# Load environment variables from a .env file if present (supports several locations)
for _candidate in [Path('.env'), Path(__file__).parent / '.env', Path(__file__).parent.parent / '.env']:
    try:
        if _candidate.exists():
            load_dotenv(dotenv_path=_candidate)
            break
    except Exception:
        pass

app = FastAPI(
    title="Azure Image Categorizer API",
    description="API for categorizing images in Azure Blob Storage by user folders",
    version="1.0.0"
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Azure Image Categorizer API running",
        "version": "1.0.0",
        "endpoints": {
            "process": "/process",
            "health": "/health",
            "download": "/download/{filename}"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    azure_storage_configured = bool(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    azure_cv_configured = bool(os.getenv("AZURE_COMPUTER_VISION_ENDPOINT") and os.getenv("AZURE_COMPUTER_VISION_KEY"))
    local_data_exists = Path("mock_data").exists()
    
    return {
        "status": "healthy",
        "azure_storage_env_configured": azure_storage_configured,
        "azure_computer_vision_env_configured": azure_cv_configured,
        "azure_parameter_supported": True,
        "local_data_available": local_data_exists,
        "storage_mode": "azure" if azure_storage_configured else "local",
        "classification_service": "Azure Computer Vision",
        "note": "Azure connection strings and Computer Vision credentials can be provided as parameters or environment variables"
    }

@app.post("/process")
async def process_images(
    user: str | None = Query(None, description="Specific user to process. If None, processes all users."),
    categories_json: UploadFile = File(..., description="JSON file with category mappings"),
    use_azure: bool | None = Query(None, description="Force Azure or local storage. If None, auto-detects from environment."),
    azure_container: str = Query("images", description="Azure container name"),
    # Switch these to Form so they can be sent alongside the file in multipart/form-data
    azure_connection_string: str | None = Form(None, description="Azure Storage connection string. If not provided, uses environment variable."),
    azure_cv_endpoint: str | None = Form(None, description="Azure Computer Vision endpoint. If not provided, uses environment variable."),
    azure_cv_key: str | None = Form(None, description="Azure Computer Vision subscription key. If not provided, uses environment variable.")
):
    """
    Process images and generate categorization results using Azure Computer Vision.
    
    - **user**: Optional user folder to process. If omitted, processes all users.
    - **categories_json**: JSON file with category mappings
    - **use_azure**: Force storage type (optional, auto-detects if not specified)
    - **azure_container**: Azure container name (default: 'images')
    - **azure_connection_string**: Azure Storage connection string (optional, uses environment if not provided)
    - **azure_cv_endpoint**: Azure Computer Vision endpoint (optional, uses environment if not provided)
    - **azure_cv_key**: Azure Computer Vision subscription key (optional, uses environment if not provided)
    """
    try:
        # Validate uploaded file
        if not categories_json.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
            
        if not categories_json.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Categories file must be a JSON file")
        
        # Check file size (limit to 10MB)
        file_size = 0
        categories_content = await categories_json.read()
        file_size = len(categories_content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=413, detail="File size too large. Maximum 10MB allowed.")
        
        # Read and validate categories JSON
        try:
            categories_data = json.loads(categories_content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        # Validate categories structure
        if not isinstance(categories_data, dict):
            raise HTTPException(status_code=400, detail="Categories JSON must be an object/dictionary")
        
        for key, value in categories_data.items():
            if not isinstance(value, list):
                raise HTTPException(status_code=400, detail=f"Category '{key}' must contain a list of labels")
            if not all(isinstance(label, str) for label in value):
                raise HTTPException(status_code=400, detail=f"All labels in category '{key}' must be strings")
        
        # Save categories to temporary file for processing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(categories_data, temp_file)
            temp_categories_path = temp_file.name
        
        try:
            results = run_pipeline(
                user_filter=user, 
                categories_file=temp_categories_path,
                use_azure=use_azure,
                azure_container=azure_container,
                azure_connection_string=azure_connection_string,
                azure_cv_endpoint=azure_cv_endpoint,
                azure_cv_key=azure_cv_key
            )
            
            return JSONResponse({
                "status": "success", 
                "message": f"Processed {len(results)} category results",
                "user_filter": user,
                "total_results": len(results),
                "results": results,
                "output_files": {
                    "excel": "outputs/top3_by_user.xlsx",
                    "html": "outputs/index.html"
                }
            })
            
        except Exception as processing_error:
            raise HTTPException(
                status_code=500, 
                detail=f"Processing error: {str(processing_error)}"
            )
        finally:
            # Clean up temporary file
            Path(temp_categories_path).unlink(missing_ok=True)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/download/{filename}")
def download_file(filename: str):
    """Download generated output files (Excel or HTML)"""
    if filename not in ["top3_by_user.xlsx", "index.html"]:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = Path("outputs") / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404, 
            detail="File not found. Run /process endpoint first to generate outputs."
        )
    
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if filename.endswith('.xlsx') else "text/html"
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )
