"""
YOLOv8 Object Detection Service
Runs on port 5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load YOLOv8 model
logger.info("Loading YOLOv8 model...")
try:
    # Try to load yolov8s for better accuracy, fallback to nano if not available
    try:
        model = YOLO('yolov8s.pt')
        logger.info("Loaded YOLOv8-Small model successfully!")
    except:
        model = YOLO('yolov8n.pt')
        logger.info("Loaded YOLOv8-Nano model successfully!")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

@app.route('/detect', methods=['POST'])
def detect_objects():
    """Detect objects in the uploaded image"""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        # Read image from request
        image_bytes = request.data
        if not image_bytes:
            return jsonify({"error": "No image data received"}), 400
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        logger.info(f"Processing image: {img_array.shape}")
        
        # Run inference with lower confidence threshold to get more detections
        results = model(img_array, conf=0.25, verbose=False)
        
        # Extract detections
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                
                # Only include detections with reasonable confidence
                if confidence >= 0.3:
                    detection = {
                        "name": class_name,
                        "confidence": round(confidence, 3),
                        "bounding_box": {
                            "x": int(x1),
                            "y": int(y1),
                            "width": int(x2 - x1),
                            "height": int(y2 - y1)
                        }
                    }
                    detections.append(detection)
        
        logger.info(f"Detected {len(detections)} objects")
        
        # Return detections sorted by confidence
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        return jsonify(detections)
    
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy" if model is not None else "unhealthy",
        "model": "YOLOv8",
        "ready": model is not None
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "YOLOv8 Object Detection",
        "version": "1.0",
        "endpoints": {
            "/detect": "POST - Detect objects in image",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    if model is None:
        logger.error("⚠️  Model failed to load. Service may not work correctly.")
    else:
        logger.info("🚀 YOLOv8 Detection Service starting on port 5000")
        logger.info(f"📊 Model can detect {len(model.names)} object classes")
        logger.info("🎯 Ready to process images!")
    
    app.run(host='0.0.0.0', port=5555, debug=False)