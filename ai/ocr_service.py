"""
Tesseract OCR Text Extraction Service
Runs on port 5001
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Tesseract path if needed (Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/ocr', methods=['POST'])
def extract_text():
    """Extract text from uploaded image"""
    try:
        # Read image from request
        image_bytes = request.data
        if not image_bytes:
            return jsonify({"error": "No image data received"}), 400
        
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        logger.info(f"Processing image for OCR: {image.size}")
        
        # Perform OCR with detailed data
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # Extract text with bounding boxes
        extractions = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            text = data['text'][i].strip()
            if text and len(text) > 0:  # Skip empty strings
                confidence = float(data['conf'][i])
                
                # Only include text with reasonable confidence
                if confidence > 30:  # Lowered threshold to catch more text
                    extraction = {
                        "text": text,
                        "confidence": min(confidence / 100.0, 1.0),  # Normalize to 0-1
                        "bounding_box": {
                            "x": int(data['left'][i]),
                            "y": int(data['top'][i]),
                            "width": int(data['width'][i]),
                            "height": int(data['height'][i])
                        }
                    }
                    extractions.append(extraction)
        
        logger.info(f"Extracted {len(extractions)} text elements")
        
        # Sort by confidence
        extractions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return jsonify(extractions)
    
    except Exception as e:
        logger.error(f"OCR error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    try:
        # Test if Tesseract is available
        version = pytesseract.get_tesseract_version()
        return jsonify({
            "status": "healthy",
            "service": "Tesseract OCR",
            "version": str(version)
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "service": "Tesseract OCR",
            "error": str(e)
        }), 500

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "Tesseract OCR",
        "version": "1.0",
        "endpoints": {
            "/ocr": "POST - Extract text from image",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    logger.info("🚀 Tesseract OCR Service starting on port 5001")
    
    # Test Tesseract availability
    try:
        version = pytesseract.get_tesseract_version()
        logger.info(f"✓ Tesseract version: {version}")
        logger.info("🎯 Ready to extract text!")
    except Exception as e:
        logger.error(f"⚠️  Tesseract not available: {e}")
        logger.error("Please install Tesseract OCR to use this service")
    
    app.run(host='0.0.0.0', port=5001, debug=False)