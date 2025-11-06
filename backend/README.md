# Azure Image Categorizer API

A FastAPI-based service that categorizes images stored in Azure Blob Storage (or local storage) by user folders, using **Azure Computer Vision API** for AI-powered image classification to generate top-3 category reports.

## 🎯 Features

- **Azure Computer Vision Integration**: Uses Azure Cognitive Services for superior image classification
- **Multi-storage Support**: Works with both Azure Blob Storage and local file systems
- **Custom Categories**: Upload your own category mappings via JSON file
- **User Filtering**: Process specific users or all users
- **Advanced Classification**: Leverages Azure's pre-trained models for tags, categories, objects, and descriptions
- **Multiple Output Formats**: Generates Excel reports and HTML dashboards
- **REST API**: Easy integration with web applications
- **Confidence Scoring**: Provides weighted confidence scores for categorizations
- **Parameter-based Configuration**: Azure credentials can be provided via API parameters

## 📋 Requirements

- Python 3.8+
- Azure Storage Account (for cloud mode)
- **Azure Computer Vision resource** (for image classification)
- At least 100 images across ≥5 users for meaningful results

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd backend

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Azure Storage connection string
# For local testing, set USE_LOCAL_STORAGE=true
```

### 3. Start the API

**Windows:**
```cmd
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Manual:**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Directory Structure

```
backend/
├── app.py                 # FastAPI application
├── main.py               # Main processing pipeline
├── categorize.py         # Image classification logic
├── report.py             # Report generation (Excel/HTML)
├── azure_storage.py      # Azure Blob Storage integration
├── categories.json       # Default category mappings
├── requirements.txt      # Python dependencies
├── .env.example         # Environment configuration template
├── start.bat/.sh        # Startup scripts
├── mock_data/           # Local test images (create user folders here)
└── outputs/             # Generated reports
    ├── top3_by_user.xlsx
    └── index.html
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
AZURE_CONTAINER_NAME=images

# Azure Computer Vision Configuration
AZURE_COMPUTER_VISION_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
AZURE_COMPUTER_VISION_KEY=your_subscription_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Local Development
USE_LOCAL_STORAGE=false  # Set to true for local testing
```

### Azure Blob Storage Structure

Organize your images in Azure Blob Storage as follows:

```
container: images/
├── user1/
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
├── user2/
│   ├── image1.jpg
│   └── ...
└── user3/
    └── ...
```

### Local Storage Structure (for testing)

```
mock_data/
├── user1/
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
├── user2/
│   ├── image1.jpg
│   └── ...
└── user3/
    └── ...
```

## 📊 Categories JSON Format

The categories file defines how individual image labels are grouped into categories:

```json
{
  "people": ["person", "man", "woman", "boy", "girl", "child"],
  "animals": ["dog", "cat", "bird", "horse", "cow", "sheep"],
  "vehicles": ["car", "bus", "truck", "bicycle", "motorcycle"],
  "food": ["pizza", "apple", "cake", "sandwich", "fruit"],
  "nature": ["tree", "mountain", "beach", "ocean", "forest", "sky"],
  "objects": ["chair", "table", "book", "phone", "computer"]
}
```

## 🌐 API Endpoints

### POST /process

Process images and generate categorization reports.

**Parameters:**
- `user` (optional): Specific user folder to process
- `categories_json` (required): JSON file with category mappings
- `use_azure` (optional): Force Azure or local storage
- `azure_container` (optional): Azure container name (default: "images")
- `azure_connection_string` (optional): Azure Storage connection string
- `azure_cv_endpoint` (optional): Azure Computer Vision endpoint
- `azure_cv_key` (optional): Azure Computer Vision subscription key

**Example Request:**
```bash
curl -X POST "http://localhost:8000/process?user=user1" \
     -F "categories_json=@categories.json"
```

**Example with Azure Computer Vision Parameters:**
```bash
curl -X POST "http://localhost:8000/process" \
     -F "categories_json=@categories.json" \
     -d "azure_connection_string=DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey" \
     -d "azure_cv_endpoint=https://myresource.cognitiveservices.azure.com/" \
     -d "azure_cv_key=my_computer_vision_key"
```

**Response:**
```json
{
  "status": "success",
  "message": "Processed 9 category results",
  "user_filter": "user1",
  "total_results": 9,
  "results": [
    {"user": "user1", "category": "people", "score": 0.856},
    {"user": "user1", "category": "nature", "score": 0.743},
    {"user": "user1", "category": "animals", "score": 0.621}
  ],
  "output_files": {
    "excel": "outputs/top3_by_user.xlsx",
    "html": "outputs/index.html"
  }
}
```

### GET /health

Check API health and configuration status.

**Response:**
```json
{
  "status": "healthy",
  "azure_configured": true,
  "local_data_available": true,
  "storage_mode": "azure"
}
```

### GET /download/{filename}

Download generated output files.

**Supported files:**
- `top3_by_user.xlsx` - Excel report
- `index.html` - HTML dashboard

## 📈 Output Files

### Excel Report (top3_by_user.xlsx)
Contains columns:
- `user`: User identifier
- `category`: Category name
- `score`: Confidence score (0-1)

### HTML Dashboard (index.html)
Interactive bar chart showing top-3 categories per user with confidence scores.

## 🔍 Usage Examples

### Process All Users with Custom Categories
```python
import requests

# Upload custom categories and process all users
with open('my_categories.json', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/process',
        files={'categories_json': f}
    )
print(response.json())
```

### Process with Azure Connection String Parameter
```python
import requests

# Process with Azure connection string as parameter
azure_conn_string = "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net"

with open('categories.json', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/process',
        files={'categories_json': f},
        params={
            'azure_connection_string': azure_conn_string,
            'azure_container': 'images',
            'use_azure': True
        }
    )
print(response.json())
```

### Process Specific User
```python
import requests

with open('categories.json', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/process?user=john_doe',
        files={'categories_json': f}
    )
```

### Download Results
```python
import requests

# Download Excel report
excel_response = requests.get('http://localhost:8000/download/top3_by_user.xlsx')
with open('results.xlsx', 'wb') as f:
    f.write(excel_response.content)

# Download HTML dashboard  
html_response = requests.get('http://localhost:8000/download/index.html')
with open('dashboard.html', 'wb') as f:
    f.write(html_response.content)
```

## 🧪 Testing

### Local Testing Setup
1. Create `mock_data` directory structure with user folders
2. Add test images to user folders
3. Set `USE_LOCAL_STORAGE=true` in .env
4. Start the API and test endpoints

### Azure Testing Setup
1. Create Azure Storage Account
2. Create container named "images"
3. Upload test images organized by user folders
4. Configure connection string in .env
5. Test API endpoints

## 🚨 Error Handling

The API includes comprehensive error handling for:

- **Invalid file formats**: Only JSON files accepted for categories
- **File size limits**: Maximum 10MB upload size
- **Invalid JSON structure**: Validates category mappings format
- **Azure connection failures**: Graceful fallback and error messages
- **Missing user folders**: Clear error messages for invalid users
- **Processing errors**: Detailed error reporting

## 🔧 Troubleshooting

### Common Issues

**1. Azure Connection Failed**
```
Error: Failed to connect to Azure Blob Storage
```
- Check your connection string in .env
- Verify container name exists
- Ensure Azure Storage account is accessible

**2. No Images Found**
```
Warning: No images found for user X
```
- Verify folder structure in Azure/local storage
- Check supported image formats (jpg, jpeg, png, bmp, gif)
- Ensure images are directly in user folders

**3. Invalid Categories JSON**
```
Error: Invalid JSON format
```
- Validate JSON syntax
- Ensure categories are objects with string arrays
- Check for proper encoding (UTF-8)

### Debug Mode

Enable debug mode for detailed logging:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 📝 Development

### Adding New Features

1. **New Classification Models**: Modify `categorize.py`
2. **Additional Output Formats**: Extend `report.py`
3. **New Storage Backends**: Create new storage classes
4. **API Enhancements**: Update `app.py` endpoints

### Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📄 License

[Your License Here]

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Open an issue in the repository