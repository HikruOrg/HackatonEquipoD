import os
import tempfile
from pathlib import Path
from typing import List, Dict
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError
import io
from PIL import Image

class AzureBlobImageReader:
    """Handle reading images from Azure Blob Storage organized by user folders."""
    
    def __init__(self, connection_string: str = None, container_name: str = "images"):
        """
        Initialize Azure Blob client.
        
        Args:
            connection_string: Azure Storage connection string. If None, uses environment variable.
            container_name: Name of the blob container containing user folders
        """
        self.connection_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = container_name
        
        if not self.connection_string:
            raise ValueError("Azure Storage connection string not provided. Set AZURE_STORAGE_CONNECTION_STRING environment variable or pass connection_string parameter.")
        
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            self.container_client = self.blob_service_client.get_container_client(container_name)
        except Exception as e:
            raise AzureError(f"Failed to initialize Azure Blob Storage client: {str(e)}")
    
    def list_user_folders(self) -> List[str]:
        """List all user folders (top-level directories) in the container."""
        try:
            folders = set()
            blob_list = self.container_client.list_blobs()
            
            for blob in blob_list:
                # Extract user folder from blob path (first part before '/')
                if '/' in blob.name:
                    user_folder = blob.name.split('/')[0]
                    folders.add(user_folder)
            
            return list(folders)
        except Exception as e:
            raise AzureError(f"Failed to list user folders: {str(e)}")
    
    def list_user_images(self, user_folder: str) -> List[str]:
        """List all image files for a specific user."""
        try:
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
            images = []
            
            # List blobs with the user folder prefix
            blob_list = self.container_client.list_blobs(name_starts_with=f"{user_folder}/")
            
            for blob in blob_list:
                file_ext = Path(blob.name).suffix.lower()
                if file_ext in image_extensions:
                    images.append(blob.name)
            
            return images
        except Exception as e:
            raise AzureError(f"Failed to list images for user {user_folder}: {str(e)}")
    
    def download_image_as_temp_file(self, blob_name: str) -> str:
        """
        Download an image from blob storage to a temporary file.
        
        Args:
            blob_name: Full blob name (including user folder path)
            
        Returns:
            Path to temporary file containing the image
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            
            # Create temporary file
            file_extension = Path(blob_name).suffix or '.jpg'
            temp_file = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False)
            
            # Download blob data
            blob_data = blob_client.download_blob()
            temp_file.write(blob_data.readall())
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            raise AzureError(f"Failed to download image {blob_name}: {str(e)}")
    
    def download_image_as_pil(self, blob_name: str) -> Image.Image:
        """
        Download an image from blob storage and return as PIL Image.
        
        Args:
            blob_name: Full blob name (including user folder path)
            
        Returns:
            PIL Image object
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob()
            
            # Load image data into PIL Image
            image_data = blob_data.readall()
            image = Image.open(io.BytesIO(image_data))
            
            return image
            
        except Exception as e:
            raise AzureError(f"Failed to download and load image {blob_name}: {str(e)}")
    
    def get_user_image_count(self, user_folder: str) -> int:
        """Get the count of images for a specific user."""
        return len(self.list_user_images(user_folder))
    
    def validate_connection(self) -> bool:
        """Test if the Azure connection and container are accessible."""
        try:
            # Try to list a single page of blobs to test connection & container existence
            blob_iter = self.container_client.list_blobs(results_per_page=1).by_page()
            # Force one page retrieval (won't matter if empty, only tests access)
            next(blob_iter, None)
            return True
        except Exception as e:
            # Surface the underlying reason via stdout for easier debugging
            print(f"[AzureBlobImageReader] Connection validation failed: {e}")
            return False

def cleanup_temp_files(temp_files: List[str]):
    """Clean up temporary files."""
    for temp_file in temp_files:
        try:
            Path(temp_file).unlink(missing_ok=True)
        except Exception:
            pass  # Ignore cleanup errors