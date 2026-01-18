"""
Minimal AI Service for Photo Mesh
Works without OpenCV, NumPy conflicts, or complex dependencies
Focuses on basic image analysis and semantic search functionality
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageStat
import io
import json
import logging
import os
import base64
from typing import Dict, List, Any
import re
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class MinimalAIService:
    def __init__(self):
        logger.info("🤖 Initializing Minimal AI Service...")
        self.color_names = {
            'red': [(255, 0, 0), (139, 0, 0), (220, 20, 60)],
            'green': [(0, 128, 0), (0, 255, 0), (34, 139, 34)],
            'blue': [(0, 0, 255), (0, 0, 139), (30, 144, 255)],
            'yellow': [(255, 255, 0), (255, 215, 0), (255, 165, 0)],
            'purple': [(128, 0, 128), (75, 0, 130), (138, 43, 226)],
            'orange': [(255, 165, 0), (255, 140, 0), (255, 69, 0)],
            'pink': [(255, 192, 203), (255, 20, 147), (255, 105, 180)],
            'brown': [(165, 42, 42), (139, 69, 19), (160, 82, 45)],
            'gray': [(128, 128, 128), (169, 169, 169), (105, 105, 105)],
            'black': [(0, 0, 0), (25, 25, 25), (47, 79, 79)],
            'white': [(255, 255, 255), (248, 248, 255), (245, 245, 245)]
        }
        logger.info("✅ Minimal AI Service ready!")
    
    def analyze_image_basic(self, image_bytes: bytes) -> Dict[str, Any]:
        """Basic image analysis using only Pillow"""
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            
            result = {
                "objects": [],
                "text": [],
                "caption": "",
                "emotions": {},
                "colors": [],
                "search_keywords": [],
                "relationships": [],
                "semantic_concepts": [],
                "clip_embedding": []
            }
            
            logger.info(f"🖼️  Analyzing image: {width}x{height}")
            
            # Basic image properties
            aspect_ratio = width / height
            total_pixels = width * height
            
            # Color analysis
            result["colors"] = self.analyze_colors(image)
            logger.info(f"🎨 Detected colors: {result['colors']}")
            
            # Basic "object" detection based on image properties
            objects = []
            
            # Detect orientation
            if aspect_ratio > 1.5:
                objects.append({
                    "name": "landscape",
                    "confidence": 0.9,
                    "bounding_box": {"x": 0, "y": 0, "width": width, "height": height}
                })
            elif aspect_ratio < 0.67:
                objects.append({
                    "name": "portrait",
                    "confidence": 0.9,
                    "bounding_box": {"x": 0, "y": 0, "width": width, "height": height}
                })
            
            # Detect size category
            if total_pixels > 2000000:  # > 2MP
                size_category = "high_resolution"
            elif total_pixels > 500000:  # > 0.5MP
                size_category = "medium_resolution"
            else:
                size_category = "low_resolution"
            
            objects.append({
                "name": size_category,
                "confidence": 0.8,
                "bounding_box": {"x": 0, "y": 0, "width": width, "height": height}
            })
            
            # Brightness analysis
            brightness = self.analyze_brightness(image)
            if brightness > 200:
                objects.append({
                    "name": "bright_image",
                    "confidence": 0.7,
                    "bounding_box": {"x": 0, "y": 0, "width": width, "height": height}
                })
            elif brightness < 80:
                objects.append({
                    "name": "dark_image",
                    "confidence": 0.7,
                    "bounding_box": {"x": 0, "y": 0, "width": width, "height": height}
                })
            
            result["objects"] = objects
            
            # Generate basic emotions based on colors and brightness
            result["emotions"] = self.analyze_emotions_from_colors(result["colors"], brightness)
            
            # Generate caption
            result["caption"] = self.generate_basic_caption(result["colors"], objects, brightness)
            
            # Generate search keywords
            keywords = set()
            keywords.update(result["colors"])
            keywords.update([obj["name"] for obj in objects])
            keywords.update(result["emotions"].keys())
            
            # Add common photography terms
            if aspect_ratio > 1.3:
                keywords.add("wide")
                keywords.add("horizontal")
            elif aspect_ratio < 0.8:
                keywords.add("tall")
                keywords.add("vertical")
            
            result["search_keywords"] = list(keywords)
            
            # Generate semantic concepts
            concepts = []
            for color in result["colors"][:3]:
                concepts.append({
                    "concept": f"{color} tones",
                    "confidence": 0.7,
                    "category": "visual"
                })
            
            for emotion, confidence in result["emotions"].items():
                if confidence > 0.5:
                    concepts.append({
                        "concept": emotion,
                        "confidence": confidence,
                        "category": "emotion"
                    })
            
            result["semantic_concepts"] = concepts
            
            # Generate simple embedding based on features
            result["clip_embedding"] = self.generate_simple_embedding(result)
            
            logger.info("✅ Basic image analysis complete")
            return result
            
        except Exception as e:
            logger.error(f"💥 Image analysis error: {e}")
            return {"error": str(e)}
    
    def analyze_colors(self, image: Image.Image) -> List[str]:
        """Analyze dominant colors in the image"""
        try:
            # Get image statistics
            stat = ImageStat.Stat(image)
            r, g, b = stat.mean
            
            # Find closest color name
            colors = []
            dominant_color = self.rgb_to_color_name(r, g, b)
            colors.append(dominant_color)
            
            # Sample different regions for more colors
            width, height = image.size
            regions = [
                (0, 0, width//2, height//2),              # Top-left
                (width//2, 0, width, height//2),          # Top-right
                (0, height//2, width//2, height),         # Bottom-left
                (width//2, height//2, width, height),     # Bottom-right
                (width//4, height//4, 3*width//4, 3*height//4)  # Center
            ]
            
            color_counts = {}
            for region in regions:
                try:
                    crop = image.crop(region)
                    stat = ImageStat.Stat(crop)
                    r, g, b = stat.mean
                    color = self.rgb_to_color_name(r, g, b)
                    color_counts[color] = color_counts.get(color, 0) + 1
                except:
                    continue
            
            # Get top colors
            sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
            for color, count in sorted_colors[:4]:  # Top 4 colors
                if color not in colors:
                    colors.append(color)
            
            return colors[:3]  # Return top 3
            
        except Exception as e:
            logger.error(f"Color analysis error: {e}")
            return ["mixed"]
    
    def rgb_to_color_name(self, r: float, g: float, b: float) -> str:
        """Convert RGB values to closest color name"""
        # Normalize to 0-255 range
        r, g, b = int(r), int(g), int(b)
        
        # Check for grayscale
        if abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30:
            if r < 60:
                return "black"
            elif r > 200:
                return "white"
            else:
                return "gray"
        
        # Find closest color
        min_distance = float('inf')
        closest_color = "mixed"
        
        for color_name, rgb_values in self.color_names.items():
            for target_r, target_g, target_b in rgb_values:
                distance = ((r - target_r) ** 2 + (g - target_g) ** 2 + (b - target_b) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_color = color_name
        
        return closest_color
    
    def analyze_brightness(self, image: Image.Image) -> float:
        """Calculate average brightness of the image"""
        try:
            # Convert to grayscale and get average
            grayscale = image.convert('L')
            stat = ImageStat.Stat(grayscale)
            return stat.mean[0]
        except:
            return 128  # Default middle brightness
    
    def analyze_emotions_from_colors(self, colors: List[str], brightness: float) -> Dict[str, float]:
        """Analyze emotions based on colors and brightness"""
        emotions = {}
        
        # Color-based emotions
        color_emotions = {
            'red': {'energetic': 0.8, 'passionate': 0.7, 'exciting': 0.6},
            'blue': {'calm': 0.8, 'peaceful': 0.7, 'cool': 0.6},
            'green': {'natural': 0.8, 'peaceful': 0.6, 'fresh': 0.7},
            'yellow': {'happy': 0.8, 'cheerful': 0.7, 'bright': 0.6},
            'purple': {'mysterious': 0.7, 'elegant': 0.6, 'creative': 0.5},
            'orange': {'warm': 0.8, 'energetic': 0.6, 'friendly': 0.7},
            'pink': {'romantic': 0.8, 'soft': 0.7, 'feminine': 0.6},
            'brown': {'earthy': 0.8, 'natural': 0.6, 'warm': 0.5},
            'black': {'dramatic': 0.8, 'mysterious': 0.7, 'elegant': 0.6},
            'white': {'clean': 0.8, 'pure': 0.7, 'minimal': 0.6},
            'gray': {'neutral': 0.8, 'calm': 0.5, 'balanced': 0.6}
        }
        
        for color in colors:
            if color in color_emotions:
                for emotion, score in color_emotions[color].items():
                    emotions[emotion] = max(emotions.get(emotion, 0), score)
        
        # Brightness-based emotions
        if brightness > 180:
            emotions['bright'] = 0.8
            emotions['cheerful'] = emotions.get('cheerful', 0) + 0.3
        elif brightness < 80:
            emotions['moody'] = 0.7
            emotions['dramatic'] = emotions.get('dramatic', 0) + 0.3
        else:
            emotions['balanced'] = 0.6
        
        # Normalize emotions
        for emotion in emotions:
            emotions[emotion] = min(emotions[emotion], 1.0)
        
        return emotions
    
    def generate_basic_caption(self, colors: List[str], objects: List[Dict], brightness: float) -> str:
        """Generate a basic caption based on analysis"""
        try:
            parts = []
            
            # Add brightness description
            if brightness > 200:
                parts.append("A bright")
            elif brightness < 80:
                parts.append("A dark")
            else:
                parts.append("A")
            
            # Add color description
            if len(colors) > 1:
                color_text = f"{colors[0]} and {colors[1]}"
            elif colors:
                color_text = colors[0]
            else:
                color_text = "colorful"
            
            parts.append(color_text)
            
            # Add object information
            orientations = [obj["name"] for obj in objects if obj["name"] in ["landscape", "portrait"]]
            if orientations:
                parts.append(orientations[0])
            
            parts.append("image")
            
            return " ".join(parts)
            
        except:
            return "A photograph"
    
    def generate_simple_embedding(self, analysis_result: Dict) -> List[float]:
        """Generate a simple feature vector for semantic search"""
        try:
            # Create a 50-dimensional feature vector
            features = [0.0] * 50
            
            # Color features (first 11 dimensions)
            color_map = {
                'red': 0, 'green': 1, 'blue': 2, 'yellow': 3, 'purple': 4,
                'orange': 5, 'pink': 6, 'brown': 7, 'black': 8, 'white': 9, 'gray': 10
            }
            
            for color in analysis_result.get("colors", []):
                if color in color_map:
                    features[color_map[color]] = 1.0
            
            # Object features (next 10 dimensions)
            object_features = {
                'landscape': 11, 'portrait': 12, 'bright_image': 13, 'dark_image': 14,
                'high_resolution': 15, 'medium_resolution': 16, 'low_resolution': 17
            }
            
            for obj in analysis_result.get("objects", []):
                obj_name = obj.get("name", "")
                if obj_name in object_features:
                    features[object_features[obj_name]] = obj.get("confidence", 0.5)
            
            # Emotion features (next 20 dimensions)
            emotion_start = 18
            emotions = analysis_result.get("emotions", {})
            for i, (emotion, score) in enumerate(list(emotions.items())[:20]):
                if i < 20:
                    features[emotion_start + i] = score
            
            # Text-based features (last 12 dimensions)
            keywords = analysis_result.get("search_keywords", [])
            for i, keyword in enumerate(keywords[:12]):
                if i < 12:
                    # Simple hash-based feature
                    hash_val = abs(hash(keyword)) % 100
                    features[38 + i] = hash_val / 100.0
            
            return features
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return [0.0] * 50

# Global service instance
ai_service = MinimalAIService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "minimal_ai",
        "features": [
            "basic_color_analysis",
            "brightness_detection",
            "emotion_mapping",
            "simple_captioning",
            "keyword_generation"
        ]
    })

@app.route('/detect', methods=['POST'])
def detect_objects():
    """Object detection endpoint (basic analysis)"""
    try:
        image_data = request.get_data()
        result = ai_service.analyze_image_basic(image_data)
        return jsonify(result.get("objects", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ocr', methods=['POST'])
def extract_text():
    """OCR endpoint (returns empty - no OCR without external deps)"""
    try:
        return jsonify([])  # No OCR capability in minimal version
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze/complete', methods=['POST'])
def analyze_complete():
    """Complete image analysis endpoint"""
    try:
        image_data = request.get_data()
        result = ai_service.analyze_image_basic(image_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search/semantic', methods=['POST'])
def semantic_search():
    """Semantic search with text query"""
    try:
        data = request.get_json()
        query = data['query']
        
        # Generate simple embedding for text query
        words = query.lower().split()
        embedding = [0.0] * 50
        
        # Map words to features
        color_words = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'brown', 'black', 'white', 'gray']
        for i, color in enumerate(color_words):
            if any(color in word for word in words):
                embedding[i] = 1.0
        
        # Add other semantic features
        if any(word in ['bright', 'light', 'sunny'] for word in words):
            embedding[13] = 1.0
        if any(word in ['dark', 'night', 'shadow'] for word in words):
            embedding[14] = 1.0
        if any(word in ['wide', 'landscape', 'horizontal'] for word in words):
            embedding[11] = 1.0
        if any(word in ['tall', 'portrait', 'vertical'] for word in words):
            embedding[12] = 1.0
        
        return jsonify({
            "query": query,
            "embedding": embedding
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Minimal AI Service starting...")
    print("📊 Available endpoints:")
    print("  • /health - Health check")
    print("  • /detect - Basic object detection")
    print("  • /ocr - Text extraction (disabled)")
    print("  • /analyze/complete - Full basic analysis")
    print("  • /search/semantic - Semantic search")
    print("")
    print("ℹ️  This is a minimal version that works without complex dependencies")
    print("   Features: Color analysis, brightness detection, basic emotions")
    
    app.run(host='0.0.0.0', port=5151, debug=False)