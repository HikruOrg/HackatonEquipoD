# Azure Image Categorizer

A full-stack application for categorizing images stored in Azure Blob Storage using Azure Computer Vision AI. The system processes images by user folders and generates categorization reports with confidence scores.

![Azure Image Processor](https://img.shields.io/badge/Azure-Computer%20Vision-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![React](https://img.shields.io/badge/React-19+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9+-blue)

## 🚀 Features

- **Azure Integration**: Direct integration with Azure Blob Storage and Computer Vision services
- **Flexible Category Management**: Upload JSON files or create categories manually through the UI
- **Multi-User Processing**: Process images for specific users or all users in storage
- **Visual Results**: Interactive charts and detailed results display
- **Export Options**: Generate Excel and HTML reports
- **Real-time Processing**: Live feedback during image categorization
- **Responsive Design**: Modern, mobile-friendly interface

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │    │   Backend       │    │   Azure         │
│   (React +      │◄──►│   (FastAPI +    │◄──►│   Services      │
│   TypeScript)   │    │   Python)       │    │                 │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       ├─ Blob Storage
        │                       │                       ├─ Computer Vision
        │                       │                       └─ Cognitive Services
        │                       │
        └─── HTTP/REST API ─────┘
```

## 📦 Project Structure

```
HackatonEquipoD/
├── backend/                 # Python FastAPI backend
│   ├── app.py              # Main FastAPI application
│   ├── main.py             # Core processing pipeline
│   ├── categorize.py       # Azure Computer Vision integration
│   ├── azure_storage.py    # Azure Blob Storage client
│   ├── report.py           # Report generation (Excel/HTML)
│   ├── categories.json     # Default category definitions
│   ├── requirements.txt    # Python dependencies
│   ├── setup_mock_data.py  # Test data generator
│   └── outputs/            # Generated reports
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx         # Main application component
│   │   ├── ClassifierPage.tsx # Main UI for image processing
│   │   ├── main.tsx        # React entry point
│   │   └── assets/         # Static assets
│   ├── package.json        # Node.js dependencies
│   ├── tsconfig.json       # TypeScript configuration
│   └── vite.config.ts      # Vite build configuration
└── README.md              # This file
```

## 🛠️ Setup & Installation

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **Azure Account** with:
  - Blob Storage account
  - Computer Vision service

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration** (Optional):
   Create a `.env` file in the backend directory:
   ```env
   AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
   AZURE_COMPUTER_VISION_ENDPOINT=https://your-cv.cognitiveservices.azure.com/
   AZURE_COMPUTER_VISION_KEY=your_cv_key_here
   ```

4. **Start the backend server:**
   ```bash
   # Using uvicorn directly
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   
   # Or using Python
   python app.py
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## 🎯 Usage

### 1. Access the Application
Open your browser and go to `http://localhost:5173`

### 2. Configure Azure Connection
- **Azure Storage Connection String**: Enter your Azure Storage connection string
- **User Filter** (Optional): Process specific user folder, or leave empty for all users
- **Azure Container**: Container name (default: "images")
- **Computer Vision Settings** (Optional): Endpoint and key if not in environment

### 3. Define Categories

#### Option A: Upload JSON File
Upload a JSON file with category structure:
```json
{
  "animals": ["dog", "cat", "bird", "horse"],
  "vehicles": ["car", "bus", "truck", "bicycle"],
  "food": ["pizza", "apple", "cake"],
  "nature": ["tree", "mountain", "beach", "ocean"]
}
```

#### Option B: Manual Entry
- Toggle to "Switch to manual category entry"
- Add categories and labels using the two-field input
- Example: Category "animals" with labels "dog", "cat", "bird"

### 4. Process Images
Click "Process Images" to start categorization. The system will:
- Connect to Azure Blob Storage
- Process images using Computer Vision
- Generate categorization results
- Create downloadable reports

### 5. View Results
- **Status Summary**: Processing status and result count
- **Interactive Chart**: Visual confidence scores by user and category
- **Detailed Table**: Sortable results with progress bars
- **User Cards**: Individual summaries for each user
- **Download Links**: Excel and HTML reports

## 🔧 API Reference

### POST `/process`
Process images and generate categorization results.

**Parameters:**
- `categories_json` (File): JSON file with category mappings
- `azure_connection_string` (Form): Azure Storage connection string
- `user` (Form, Optional): Specific user folder to process
- `azure_container` (Form, Optional): Container name (default: "images")
- `azure_cv_endpoint` (Form, Optional): Computer Vision endpoint
- `azure_cv_key` (Form, Optional): Computer Vision key

**Response:**
```json
{
  "status": "success",
  "message": "Processed 6 category results",
  "user_filter": null,
  "total_results": 6,
  "results": [
    {"user": "user1", "category": "animals", "score": 0.85},
    {"user": "user1", "category": "nature", "score": 0.72}
  ],
  "output_files": {
    "excel": "outputs/top3_by_user.xlsx",
    "html": "outputs/index.html"
  }
}
```

### GET `/download/{filename}`
Download generated reports (Excel or HTML).

### GET `/health`
Health check endpoint with service status.

## 🧪 Testing

### Backend Testing
```bash
cd backend
python test_api.py
```

### Frontend Testing
```bash
cd frontend
npm run lint
npm run build
```

### Mock Data Setup
Generate test data for local development:
```bash
cd backend
python setup_mock_data.py
```

## 📊 Sample Category Structure

```json
{
  "people": ["person", "man", "woman", "boy", "girl", "child"],
  "animals": ["dog", "cat", "bird", "horse", "cow", "sheep"],
  "vehicles": ["car", "bus", "truck", "bicycle", "motorcycle"],
  "food": ["pizza", "apple", "cake", "bread", "fruit"],
  "nature": ["tree", "mountain", "beach", "ocean", "forest", "sky"],
  "objects": ["chair", "table", "book", "phone", "computer"],
  "buildings": ["house", "building", "church", "school", "office"]
}
```

## 🚀 Deployment

### Backend Deployment
- Use Azure App Service, AWS Lambda, or Docker containers
- Configure environment variables for Azure services
- Ensure CORS settings allow frontend domain

### Frontend Deployment
- Build for production: `npm run build`
- Deploy to Azure Static Web Apps, Vercel, or Netlify
- Update API_URL in ClassifierPage.tsx for production backend

## 🔐 Security Considerations

- **Connection Strings**: Never commit connection strings to version control
- **API Keys**: Use environment variables or Azure Key Vault
- **CORS**: Configure allowed origins in production
- **Authentication**: Consider adding user authentication for production use

## 🐛 Troubleshooting

### Common Issues

1. **Azure Connection Failed**
   - Verify connection string format
   - Check container exists and is accessible
   - Ensure network/firewall allows Azure access

2. **Computer Vision Errors**
   - Verify endpoint URL and key
   - Check service limits and quotas
   - Ensure images are in supported formats (JPG, PNG)

3. **Frontend/Backend Communication**
   - Check if backend is running on port 8000
   - Verify CORS configuration
   - Check browser developer console for errors

### Debug Mode
Add debug logging to backend:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review Azure documentation for service-specific issues

## 🙏 Acknowledgments

- Azure Computer Vision for AI-powered image analysis
- FastAPI for the robust backend framework
- React and Vite for the modern frontend experience
- Bootstrap for responsive UI components
- Recharts for data visualization

---

**Built with ❤️ for efficient image categorization and analysis**