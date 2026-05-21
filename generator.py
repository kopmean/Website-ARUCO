#!/usr/bin/env python3
"""
ArUco Marker and QR Code Generator
Generates square ArUco fiducial markers or standard QR codes representing numbers or text.
"""

import sys
import argparse
import numpy as np

# Dictionary mapping string names to OpenCV ArUco constants
ARUCO_DICTS = {}

def get_opencv_aruco_dicts():
    global ARUCO_DICTS
    import cv2
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

def generate_aruco(marker_id, dictionary_name, size, output_path):
    """
    Generates an ArUco marker and saves it as an image.
    """
    import cv2
    
    # Initialize dictionaries mapping
    get_opencv_aruco_dicts()
    
    if dictionary_name not in ARUCO_DICTS:
        print(f"Error: Dictionary '{dictionary_name}' is not recognized.")
        print("Available dictionaries:", ", ".join(ARUCO_DICTS.keys()))
        sys.exit(1)
        
    dict_const = ARUCO_DICTS[dictionary_name]
    
    # Check ArUco API version (OpenCV 4.7.0+ changed API structure)
    try:
        if hasattr(cv2.aruco, "getPredefinedDictionary"):
            aruco_dict = cv2.aruco.getPredefinedDictionary(dict_const)
        else:
            aruco_dict = cv2.aruco.Dictionary_get(dict_const)
    except AttributeError:
        print("Error: OpenCV ArUco module is not installed or available.")
        print("Please make sure you have 'opencv-contrib-python' installed.")
        sys.exit(1)
        
    print(f"Generating ArUco marker from dictionary {dictionary_name} with ID {marker_id}...")
    
    # Create the marker image
    # For OpenCV 4.7.0+, generateImageMarker is preferred. Fall back to drawMarker if needed.
    try:
        if hasattr(cv2.aruco, "generateImageMarker"):
            # generateImageMarker(dictionary, id, sidePixels[, img[, borderBits]])
            marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size)
        else:
            # drawMarker(dictionary, id, sidePixels[, img[, borderBits]])
            marker_img = cv2.aruco.drawMarker(aruco_dict, marker_id, size)
    except Exception as e:
        print(f"Error generating marker image: {e}")
        sys.exit(1)
        
    # Add a white border (padding) around the marker so the detector can find it.
    # Without a white border, the black edge of the marker touching the image edge
    # prevents the detection algorithm from recognizing the outer boundary.
    padding = max(10, int(size * 0.1))
    marker_img = cv2.copyMakeBorder(
        marker_img, 
        padding, padding, padding, padding, 
        cv2.BORDER_CONSTANT, 
        value=[255, 255, 255]
    )
        
    # Write image
    cv2.imwrite(output_path, marker_img)
    print(f"Success! Saved ArUco marker with padding to: {output_path}")

def generate_qr(data, size, output_path):
    """
    Generates a standard QR code containing data and saves it.
    """
    try:
        import qrcode
    except ImportError:
        print("Error: 'qrcode' module not found. Run 'pip install qrcode pillow'")
        sys.exit(1)
        
    print(f"Generating QR Code containing: '{data}'...")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=max(1, size // 40), # rough scaling
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size))
    img.save(output_path)
    print(f"Success! Saved QR Code to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate ArUco markers or QR codes.")
    parser.add_argument(
        "--type", 
        choices=["aruco", "qr"], 
        default="aruco", 
        help="Type of code to generate: 'aruco' or 'qr'."
    )
    parser.add_argument(
        "--id", 
        type=int, 
        default=0, 
        help="Numeric ID for ArUco marker (ignored for QR codes)."
    )
    parser.add_argument(
        "--data", 
        type=str, 
        default="12345", 
        help="Text or numeric data for QR code (ignored for ArUco markers)."
    )
    parser.add_argument(
        "--dict", 
        type=str, 
        default="DICT_6X6_250", 
        help="ArUco dictionary name to use (default: DICT_6X6_250)."
    )
    parser.add_argument(
        "--size", 
        type=int, 
        default=400, 
        help="Size of the output image in pixels (default: 400)."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output file path (defaults to: 'aruco_marker_<id>.png' or 'qrcode.png')."
    )
    
    args = parser.parse_args()
    
    # Determine default output name if not provided
    if args.type == "aruco":
        output_path = args.output if args.output else f"aruco_marker_{args.id}.png"
        generate_aruco(args.id, args.dict, args.size, output_path)
    else:
        output_path = args.output if args.output else "qrcode.png"
        generate_qr(args.data, args.size, output_path)

if __name__ == "__main__":
    main()
