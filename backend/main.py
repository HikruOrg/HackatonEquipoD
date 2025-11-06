from pathlib import Path
import pandas as pd
import os
from categorize import load_categories, flatten_labels, classify_image, map_to_groups
from report import save_excel, save_html
from azure_storage import AzureBlobImageReader, cleanup_temp_files

DATA_DIR = Path("mock_data")
CATEGORIES_FILE = Path("categories.json")

def run_pipeline(user_filter=None, categories_file=None, use_azure=None, azure_container="images", 
                azure_connection_string=None, azure_cv_endpoint=None, azure_cv_key=None):
    """
    Run the image categorization pipeline.
    
    Args:
        user_filter: If provided, only process this specific user folder
        categories_file: Path to categories JSON file. If None, uses default.
        use_azure: If True, use Azure Blob Storage. If None, auto-detect from environment.
        azure_container: Name of Azure container (default: "images")
        azure_connection_string: Azure Storage connection string. If None, uses environment variable.
        azure_cv_endpoint: Azure Computer Vision endpoint. If None, uses environment variable.
        azure_cv_key: Azure Computer Vision key. If None, uses environment variable.
    """

    # Use provided categories file or default
    categories_path = categories_file if categories_file else CATEGORIES_FILE
    mapping = load_categories(categories_path)
    candidate_labels = flatten_labels(mapping)

    rows = []
    temp_files = []  # Track temp files for cleanup
    
    # Determine if we should use Azure or local storage
    if use_azure is None:
        use_azure = bool(azure_connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    
    try:
        if use_azure:
            # Use Azure Blob Storage
            print("🌐 Using Azure Blob Storage")
            azure_reader = AzureBlobImageReader(
                connection_string=azure_connection_string,
                container_name=azure_container
            )
            
            if not azure_reader.validate_connection():
                # Try to extract account name for better diagnostics
                account_name = None
                try:
                    if azure_reader.connection_string:
                        parts = [p for p in azure_reader.connection_string.split(';') if p]
                        for p in parts:
                            if p.lower().startswith('accountname='):
                                account_name = p.split('=', 1)[1]
                                break
                except Exception:
                    pass
                raise Exception(
                    f"Failed to connect to Azure Blob Storage. Container='{azure_container}'. "
                    f"Account='{account_name or 'unknown'}'. Verify: connection string is valid, container exists, and network/firewall allows access."
                )
            
            # Get list of users to process
            if user_filter:
                user_folders = [user_filter] if user_filter in azure_reader.list_user_folders() else []
                if not user_folders:
                    print(f"⚠️  User folder '{user_filter}' not found in Azure storage")
                    return []
            else:
                user_folders = azure_reader.list_user_folders()
            
            if not user_folders:
                print("⚠️  No user folders found in Azure storage")
                return []
            
            # Process each user folder
            for user in user_folders:
                print(f"🔍 Processing user: {user}")
                scores_total = {}
                
                # Get all image files for this user
                image_blobs = azure_reader.list_user_images(user)
                
                if not image_blobs:
                    print(f"  ⚠️  No images found for user {user}")
                    continue
                
                # Process each image
                for blob_name in image_blobs:
                    print(f"  📷 {Path(blob_name).name}")
                    
                    # Download image to temporary file
                    temp_file = azure_reader.download_image_as_temp_file(blob_name)
                    temp_files.append(temp_file)
                    
                    # Classify the image
                    results = classify_image(temp_file, candidate_labels, azure_cv_endpoint, azure_cv_key)
                    grouped = map_to_groups(results, mapping)
                    
                    # Accumulate scores
                    for cat, sc in grouped.items():
                        scores_total[cat] = scores_total.get(cat, 0) + sc
                
                # Calculate average scores per category
                for cat in scores_total:
                    scores_total[cat] /= len(image_blobs)
                
                # Get top 3 categories
                top3 = sorted(scores_total.items(), key=lambda x: x[1], reverse=True)[:3]
                for cat, sc in top3:
                    rows.append({"user": user, "category": cat, "score": round(sc, 3)})
        
        else:
            # Use local storage (existing logic)
            print("💾 Using local storage")
            
            # Get list of user folders to process
            user_folders = []
            if user_filter:
                # Process only specific user
                user_folder = DATA_DIR / user_filter
                if user_folder.is_dir():
                    user_folders.append(user_folder)
                else:
                    print(f"⚠️  User folder '{user_filter}' not found")
                    return []
            else:
                # Process all user folders
                user_folders = [f for f in DATA_DIR.iterdir() if f.is_dir()]

            if not user_folders:
                print("⚠️  No user folders found to process")
                return []

            for user_folder in user_folders:
                user = user_folder.name
                print(f"🔍 Processing user: {user}")
                scores_total = {}
                
                # Get all image files
                image_files = list(user_folder.glob("*.jpg")) + list(user_folder.glob("*.jpeg")) + list(user_folder.glob("*.png"))
                
                if not image_files:
                    print(f"  ⚠️  No images found for user {user}")
                    continue

                for img_file in image_files:
                    print(f"  📷 {img_file.name}")
                    results = classify_image(img_file, candidate_labels, azure_cv_endpoint, azure_cv_key)
                    grouped = map_to_groups(results, mapping)

                    # acumula los scores
                    for cat, sc in grouped.items():
                        scores_total[cat] = scores_total.get(cat, 0) + sc

                # promedio final por categoría
                for cat in scores_total:
                    scores_total[cat] /= len(image_files)

                # top 3 categorías
                top3 = sorted(scores_total.items(), key=lambda x: x[1], reverse=True)[:3]
                for cat, sc in top3:
                    rows.append({"user": user, "category": cat, "score": round(sc, 3)})
        
        # Generate reports
        df = pd.DataFrame(rows)
        save_excel(df)
        save_html(df)
        return rows
        
    finally:
        # Clean up temporary files
        if temp_files:
            cleanup_temp_files(temp_files)
