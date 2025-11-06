# Sample Test Script for Azure Image Categorizer API

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_process_all_users():
    """Test processing all users with default categories"""
    print("🔍 Testing process all users...")
    
    # Use the default categories file
    categories_file = Path("categories.json")
    
    if not categories_file.exists():
        print("❌ categories.json not found")
        return
    
    with open(categories_file, 'rb') as f:
        files = {'categories_json': f}
        response = requests.post(f"{BASE_URL}/process", files=files)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Processed {result.get('total_results', 0)} results")
        print(f"Results: {result.get('results', [])[:3]}...")  # Show first 3 results
    else:
        print(f"❌ Error: {response.text}")
    print()

def test_process_specific_user():
    """Test processing a specific user"""
    print("🔍 Testing process specific user...")
    
    user_to_test = "user1"  # Change this to a user that exists in your data
    categories_file = Path("categories.json")
    
    if not categories_file.exists():
        print("❌ categories.json not found")
        return
    
    with open(categories_file, 'rb') as f:
        files = {'categories_json': f}
        params = {'user': user_to_test}
        response = requests.post(f"{BASE_URL}/process", files=files, params=params)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Processed user '{user_to_test}'")
        print(f"Results: {result.get('results', [])}")
    else:
        print(f"❌ Error: {response.text}")
    print()

def test_download_files():
    """Test downloading generated files"""
    print("🔍 Testing file downloads...")
    
    # Test Excel download
    response = requests.get(f"{BASE_URL}/download/top3_by_user.xlsx")
    if response.status_code == 200:
        print("✅ Excel file download successful")
        with open("test_download.xlsx", "wb") as f:
            f.write(response.content)
        print("   Saved as test_download.xlsx")
    else:
        print(f"❌ Excel download failed: {response.status_code}")
    
    # Test HTML download
    response = requests.get(f"{BASE_URL}/download/index.html")
    if response.status_code == 200:
        print("✅ HTML file download successful")
        with open("test_download.html", "wb") as f:
            f.write(response.content)
        print("   Saved as test_download.html")
    else:
        print(f"❌ HTML download failed: {response.status_code}")
    print()

def test_process_with_azure_params():
    """Test processing with Azure connection string as parameter"""
    print("🔍 Testing process with Azure parameters...")
    
    # Example Azure connection strings (replace with real ones for testing)
    azure_storage_connection = "DefaultEndpointsProtocol=https;AccountName=yourname;AccountKey=yourkey;EndpointSuffix=core.windows.net"
    azure_cv_endpoint = "https://your-resource-name.cognitiveservices.azure.com/"
    azure_cv_key = "your_computer_vision_subscription_key"
    
    categories_file = Path("categories.json")
    
    if not categories_file.exists():
        print("❌ categories.json not found")
        return
    
    with open(categories_file, 'rb') as f:
        files = {'categories_json': f}
        params = {
            'use_azure': True,
            'azure_container': 'images',
            'azure_connection_string': azure_storage_connection,
            'azure_cv_endpoint': azure_cv_endpoint,
            'azure_cv_key': azure_cv_key
        }
        response = requests.post(f"{BASE_URL}/process", files=files, params=params)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success with Azure Computer Vision!")
        print(f"Results: {result.get('results', [])[:3]}...")
    else:
        print(f"❌ Error: {response.text}")
        if "computer vision" in response.text.lower() or "endpoint" in response.text.lower():
            print("💡 Note: This test requires valid Azure Computer Vision credentials")
    print()

def test_custom_categories():
    """Test with custom categories"""
    print("🔍 Testing custom categories...")
    
    # Create a custom categories JSON
    custom_categories = {
        "technology": ["computer", "phone", "laptop", "tablet"],
        "outdoor": ["tree", "mountain", "sky", "grass"],
        "indoor": ["chair", "table", "bed", "couch"]
    }
    
    # Save to temporary file
    temp_file = Path("temp_categories.json")
    with open(temp_file, 'w') as f:
        json.dump(custom_categories, f)
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'categories_json': f}
            response = requests.post(f"{BASE_URL}/process", files=files)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success with custom categories!")
            print(f"Results: {result.get('results', [])[:3]}...")
        else:
            print(f"❌ Error: {response.text}")
    finally:
        # Clean up
        if temp_file.exists():
            temp_file.unlink()
    print()

def main():
    """Run all tests"""
    print("🚀 Azure Image Categorizer API Test Suite")
    print("=" * 50)
    
    try:
        test_health_check()
        test_process_all_users()
        test_process_specific_user()
        test_download_files()
        test_custom_categories()
        test_process_with_azure_params()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Is the API server running?")
        print("   Start the server with: uvicorn app:app --reload")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()