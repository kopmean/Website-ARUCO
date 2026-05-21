#!/usr/bin/env python3
"""
ArUco & QR Code Generator Flask Web Server
Serves a beautiful, interactive web interface for generating markers/codes dynamically.
"""

import io
import sys
import cv2
import numpy as np
from flask import Flask, render_template, request, send_file, jsonify

try:
    import qrcode
except ImportError:
    qrcode = None

app = Flask(__name__)

# Predefined dictionaries mapping string names to OpenCV ArUco constants
ARUCO_DICTS = {}

def init_aruco_dicts():
    global ARUCO_DICTS
    if not hasattr(cv2, "aruco") or cv2.aruco is None:
        return
        
    ARUCO_DICTS = {
        "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
        "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
        "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
        "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
        "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
        "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
        "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
        "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
        "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
        "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
        "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
        "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
        "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
        "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
        "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
        "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
        "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
        "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
        "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
        "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11,
    }

# Initialize dicts
init_aruco_dicts()

@app.route("/")
def index():
    """Renders the main web interface."""
    dicts = list(ARUCO_DICTS.keys())
    return render_template("index.html", dicts=dicts)

@app.route("/generate/aruco")
def generate_aruco():
    """Generates an ArUco marker dynamically in-memory and returns it."""
    if not ARUCO_DICTS:
        return "Error: OpenCV ArUco module not loaded", 500
        
    try:
        marker_id = int(request.args.get("id", 0))
        dict_name = request.args.get("dict", "DICT_6X6_250")
        size = int(request.args.get("size", 400))
        add_padding = request.args.get("padding", "true").lower() == "true"
        
        # Limit sizing to sensible values
        size = max(50, min(size, 2000))
        
        if dict_name not in ARUCO_DICTS:
            return f"Error: Unknown dictionary '{dict_name}'", 400
            
        dict_const = ARUCO_DICTS[dict_name]
        
        # API version check
        if hasattr(cv2.aruco, "getPredefinedDictionary"):
            aruco_dict = cv2.aruco.getPredefinedDictionary(dict_const)
        else:
            aruco_dict = cv2.aruco.Dictionary_get(dict_const)
            
        # Draw marker
        if hasattr(cv2.aruco, "generateImageMarker"):
            marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size)
        else:
            marker_img = cv2.aruco.drawMarker(aruco_dict, marker_id, size)
            
        # Add white padding if requested (necessary for optimal scanner detection)
        if add_padding:
            padding = max(10, int(size * 0.1))
            marker_img = cv2.copyMakeBorder(
                marker_img, 
                padding, padding, padding, padding, 
                cv2.BORDER_CONSTANT, 
                value=[255, 255, 255]
            )
            
        # Encode image to PNG in-memory
        success, encoded_img = cv2.imencode(".png", marker_img)
        if not success:
            return "Error: Failed to encode image", 500
            
        # Return image bytes
        img_bytes = io.BytesIO(encoded_img.tobytes())
        return send_file(img_bytes, mimetype="image/png")
        
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/generate/qr")
def generate_qr():
    """Generates a standard QR code dynamically in-memory and returns it."""
    if qrcode is None:
        return "Error: 'qrcode' module not installed", 500
        
    try:
        data = request.args.get("data", "12345")
        size = int(request.args.get("size", 400))
        
        size = max(50, min(size, 2000))
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=max(1, size // 40),
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Draw image and resize
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size))
        
        # Save to buffer
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype="image/png")
        
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    # Run locally on port 5000
    app.run(debug=True, host="127.0.0.1", port=5000)
