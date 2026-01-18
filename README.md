# Photo Mesh

A comprehensive multi-platform photo management and analysis application that combines AI-powered image processing with semantic search capabilities.

## 📋 Overview

Photo Mesh is a full-stack application that enables intelligent photo organization, analysis, and search. It uses computer vision and machine learning to automatically detect objects, extract text, identify faces, and enable semantic search across your photo collection.

### Key Features

- 🤖 **AI-Powered Analysis**: Object detection using YOLO models
- 🔍 **Semantic Search**: Find images using natural language queries
- 📝 **OCR Capabilities**: Extract text from images
- 👥 **Face Detection**: Identify and track faces in photos
- 🎨 **Color Analysis**: Automatic color palette extraction
- 🏷️ **Auto-Tagging**: Intelligent image categorization
- 📱 **Cross-Platform**: Desktop (Windows, macOS, Linux), Mobile (iOS, Android), and Web

## 🏗️ Architecture

The application consists of three main components:

### 1. Backend (Go)
- RESTful API server built with Go
- Image upload and management
- Metadata storage and retrieval
- Integration with AI services
- CORS-enabled for cross-origin requests

**Tech Stack:**
- Go 1.24
- Gorilla Mux (routing)
- Google Cloud Vision API (optional)
- UUID generation

### 2. AI Service (Python)
- Microservice architecture for AI processing
- Multiple AI models and analysis types
- Minimal dependencies with fallback support

**Capabilities:**
- **Object Detection**: YOLO models (YOLOv8n, YOLOv8s, YOLOv8l)
- **OCR**: Text extraction from images
- **Color Analysis**: Dominant color detection
- **Image Features**: Basic image statistics and analysis
- **Semantic Search**: Image understanding and matching

**Tech Stack:**
- Python 3.13+
- Flask with CORS support
- Pillow (PIL) for image processing
- NumPy for numerical operations
- Ultralytics YOLO (optional)
- PyTesseract (optional)

### 3. Frontend (Flutter)
- Cross-platform mobile and desktop application
- Modern, responsive UI
- Real-time image analysis results

**Tech Stack:**
- Flutter 3.8+
- Dart 3.8+
- Material Design

## 🚀 Getting Started

### Prerequisites

- **Go**: 1.24 or higher
- **Python**: 3.13 or higher
- **Flutter**: 3.8 or higher
- **Dart**: 3.8 or higher

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd photo_mesh
```

#### 2. Backend Setup

```bash
cd backend
go mod download
go run main.go
```

The backend server will start on `http://localhost:8080`

#### 3. AI Service Setup

```bash
cd ai
pip install -r requirements.txt

# For full AI capabilities (optional):
pip install ultralytics opencv-python pytesseract torch
```

Start the AI service:

```bash
# Minimal service (basic features only)
python minimal_ai_service.py

# Or full YOLO service (if dependencies installed)
python yolo_service.py

# Or OCR service
python ocr_service.py
```

The AI service will start on `http://localhost:5000`

#### 4. Frontend Setup

```bash
cd frontend
flutter pub get
flutter run
```

Select your target platform when prompted (iOS, Android, Web, Windows, macOS, Linux).

## 📁 Project Structure

```
photo_mesh/
├── ai/                          # AI/ML microservice
│   ├── minimal_ai_service.py    # Lightweight AI service
│   ├── yolo_service.py          # YOLO object detection service
│   ├── ocr_service.py           # OCR text extraction service
│   ├── requirements.txt         # Python dependencies
│   └── yolov8*.pt              # Pre-trained YOLO models
│
├── backend/                     # Go backend server
│   ├── main.go                  # Main server file
│   ├── ai_processor.go          # AI integration logic
│   ├── go.mod                   # Go dependencies
│   └── uploads/                 # Uploaded images directory
│
└── frontend/                    # Flutter application
    ├── lib/
    │   └── main.dart            # Main app entry point
    ├── android/                 # Android platform files
    ├── ios/                     # iOS platform files
    ├── web/                     # Web platform files
    ├── windows/                 # Windows platform files
    ├── macos/                   # macOS platform files
    ├── linux/                   # Linux platform files
    └── pubspec.yaml             # Flutter dependencies
```

## 🔧 Configuration

### Backend Configuration

The backend server listens on port `8080` by default. Modify [backend/main.go](backend/main.go) to change server settings.

### AI Service Configuration

The AI service runs on port `5000` by default. Available models:
- `yolov8n.pt` - Nano (fastest, least accurate)
- `yolov8s.pt` - Small (balanced)
- `yolov8l.pt` - Large (slowest, most accurate)

### Environment Variables

```bash
# Optional: Google Cloud Vision API
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Optional: Configure ports
export BACKEND_PORT=8080
export AI_SERVICE_PORT=5000
```

## 📡 API Endpoints

### Backend API

#### Upload Image
```http
POST /api/upload
Content-Type: multipart/form-data

Response: {
  "id": "uuid",
  "url": "image_url",
  "metadata": {...}
}
```

#### Get All Images
```http
GET /api/images

Response: [{
  "id": "uuid",
  "url": "image_url",
  "objects": [...],
  "faces": [...],
  "text": [...]
}]
```

#### Search Images
```http
POST /api/search
Content-Type: application/json

{
  "query": "search query"
}
```

### AI Service API

#### Analyze Image
```http
POST /analyze
Content-Type: multipart/form-data

Response: {
  "objects": [...],
  "colors": [...],
  "tags": [...],
  "confidence": 0.95
}
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
go test ./...
```

### Frontend Tests
```bash
cd frontend
flutter test
```

## 📦 Building for Production

### Build Backend
```bash
cd backend
go build -o photo_mesh_server
```

### Build Frontend

**Android:**
```bash
flutter build apk --release
```

**iOS:**
```bash
flutter build ios --release
```

**Web:**
```bash
flutter build web --release
```

**Desktop (Windows/macOS/Linux):**
```bash
flutter build windows --release
flutter build macos --release
flutter build linux --release
```

## 🛠️ Development

### Code Style

- **Go**: Follow standard Go formatting (`gofmt`)
- **Python**: PEP 8 style guide
- **Dart**: Follow Dart style guide (`dart format`)

### Adding New Features

1. Create a feature branch
2. Implement your changes
3. Add tests
4. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

**AI Service Fails to Start:**
- Ensure Python 3.13+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- For full features, install optional dependencies

**Backend Connection Errors:**
- Verify the backend is running on port 8080
- Check CORS settings if accessing from browser
- Ensure uploads directory exists and has write permissions

**Flutter Build Errors:**
- Run `flutter clean` and `flutter pub get`
- Check Flutter and Dart SDK versions
- Ensure platform-specific tools are installed (Xcode for iOS, Android Studio for Android)

## 📄 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]

## 🙏 Acknowledgments

- YOLO models by Ultralytics
- Flutter framework by Google
- Go standard library and community packages

## 📞 Support

For issues and questions, please open an issue on the GitHub repository.

---

Built with ❤️ using Go, Python, and Flutter
