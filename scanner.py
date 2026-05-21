#!/usr/bin/env python3
"""
ArUco Marker and QR Code Scanner
Scans and decodes ArUco markers and standard QR codes from a webcam stream or a static image.
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

def process_frame(frame, aruco_dict, detector_params, scan_aruco=True, scan_qr=True):
    """
    Detects and decodes ArUco markers and QR codes in a single frame/image.
    Modifies the frame in-place to draw bounding boxes and labels.
    Returns: (detected_aruco_list, detected_qr_list)
    """
    import cv2
    
    detected_aruco = []
    detected_qr = []
    
    # 1. ARUCO DETECTION
    if scan_aruco and cv2.aruco is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Determine appropriate API call depending on OpenCV version (4.7.0+ change)
        try:
            if hasattr(cv2.aruco, "ArucoDetector"):
                detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)
                corners, ids, rejected = detector.detectMarkers(gray)
            else:
                corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=detector_params)
                
            if ids is not None and len(ids) > 0:
                # ids is returned as a 2D array: [[id1], [id2], ...]
                for marker_id, marker_corners in zip(ids.flatten(), corners):
                    detected_aruco.append({
                        "id": int(marker_id),
                        "corners": marker_corners
                    })
                
                # Draw boxes around detected ArUco markers
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                
                # Add text label for each marker (above the top-left corner)
                for marker in detected_aruco:
                    mid = marker["id"]
                    corners_coords = marker["corners"][0] # corners is shape (1, 4, 2)
                    top_left = (int(corners_coords[0][0]), int(corners_coords[0][1]))
                    cv2.putText(frame, f"ArUco ID: {mid}", (top_left[0], top_left[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        except Exception as e:
            print(f"Warning: ArUco detection error: {e}")

    # 2. QR CODE DETECTION
    if scan_qr:
        qr_detector = cv2.QRCodeDetector()
        
        # Use detectAndDecodeMulti for modern versions of OpenCV, fallback to detectAndDecode
        try:
            if hasattr(qr_detector, "detectAndDecodeMulti"):
                retval, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(frame)
                if retval and points is not None:
                    for info, pts in zip(decoded_info, points):
                        if info: # only include non-empty results
                            detected_qr.append({
                                "data": info,
                                "points": pts
                            })
            else:
                retval, points, _ = qr_detector.detectAndDecode(frame)
                if retval and points is not None:
                    detected_qr.append({
                        "data": retval,
                        "points": points
                    })
                    
            # Draw boxes around detected QR codes
            for qr in detected_qr:
                pts = np.int32(qr["points"]).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
                
                # Find top-left point
                top_left_idx = np.argmin(np.sum(qr["points"], axis=1))
                top_left = (int(qr["points"][top_left_idx][0]), int(qr["points"][top_left_idx][1]))
                cv2.putText(frame, f"QR: {qr['data']}", (top_left[0], top_left[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        except Exception as e:
            print(f"Warning: QR detection error: {e}")
            
    return detected_aruco, detected_qr

def run_image_scan(image_path, dict_name, scan_aruco, scan_qr, output_path):
    """
    Reads a static image, scans it, prints findings, draws bounding boxes,
    and saves the annotated output image.
    """
    import cv2
    
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Error: Could not read image '{image_path}'")
        sys.exit(1)
        
    get_opencv_aruco_dicts()
    aruco_dict_const = ARUCO_DICTS.get(dict_name, cv2.aruco.DICT_6X6_250)
    
    # Set parameters
    if hasattr(cv2.aruco, "DetectorParameters"):
        detector_params = cv2.aruco.DetectorParameters()
    else:
        detector_params = cv2.aruco.DetectorParameters_create()
        
    try:
        if hasattr(cv2.aruco, "getPredefinedDictionary"):
            aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_const)
        else:
            aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_const)
    except AttributeError:
        aruco_dict = None
        
    detected_aruco, detected_qr = process_frame(frame, aruco_dict, detector_params, scan_aruco, scan_qr)
    
    print("\n--- Detection Results ---")
    if scan_aruco:
        print(f"Detected {len(detected_aruco)} ArUco markers:")
        for marker in detected_aruco:
            print(f"  - ArUco ID: {marker['id']}")
            
    if scan_qr:
        print(f"Detected {len(detected_qr)} QR codes:")
        for qr in detected_qr:
            print(f"  - QR Code Data: {qr['data']}")
            
    # Save the annotated image
    cv2.imwrite(output_path, frame)
    print(f"\nSaved annotated image to: {output_path}")

def run_webcam_scan(dict_name, scan_aruco, scan_qr):
    """
    Opens the default webcam and runs real-time detection, displaying
    bounding boxes and printing findings to the terminal.
    """
    import cv2
    
    get_opencv_aruco_dicts()
    aruco_dict_const = ARUCO_DICTS.get(dict_name, cv2.aruco.DICT_6X6_250)
    
    # Set parameters
    if hasattr(cv2.aruco, "DetectorParameters"):
        detector_params = cv2.aruco.DetectorParameters()
    else:
        detector_params = cv2.aruco.DetectorParameters_create()
        
    try:
        if hasattr(cv2.aruco, "getPredefinedDictionary"):
            aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_const)
        else:
            aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_const)
    except AttributeError:
        aruco_dict = None
        
    # Open camera (index 0 is default)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(1)
        
    print("\n==================================================")
    print("Starting webcam scanner...")
    print("Press 'q' in the camera window to quit.")
    print("==================================================\n")
    
    last_printed_aruco = set()
    last_printed_qr = set()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame from webcam.")
            break
            
        detected_aruco, detected_qr = process_frame(frame, aruco_dict, detector_params, scan_aruco, scan_qr)
        
        # Real-time console reporting (only print when new codes appear to avoid clutter)
        current_aruco = {m['id'] for m in detected_aruco}
        current_qr = {q['data'] for q in detected_qr}
        
        new_aruco = current_aruco - last_printed_aruco
        new_qr = current_qr - last_printed_qr
        
        if new_aruco:
            for aid in new_aruco:
                print(f"[FOUND] ArUco ID: {aid}")
        if new_qr:
            for qdata in new_qr:
                print(f"[FOUND] QR Code: {qdata}")
                
        last_printed_aruco = current_aruco
        last_printed_qr = current_qr
        
        # Display the frame
        cv2.imshow("ArUco & QR Scanner - Press 'q' to Quit", frame)
        
        # Quit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    print("Scanner stopped.")

def main():
    parser = argparse.ArgumentParser(description="Scan ArUco markers and QR codes from camera or image.")
    parser.add_argument(
        "--image", 
        type=str, 
        help="Path to static image to scan. If not provided, webcam will be used instead."
    )
    parser.add_argument(
        "--dict", 
        type=str, 
        default="DICT_6X6_250", 
        help="ArUco dictionary name to use for detection (default: DICT_6X6_250)."
    )
    parser.add_argument(
        "--no-aruco", 
        action="store_true", 
        help="Disable ArUco marker scanning."
    )
    parser.add_argument(
        "--no-qr", 
        action="store_true", 
        help="Disable QR code scanning."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="scan_result.png", 
        help="Output file path for saving annotated static image results (default: scan_result.png)."
    )
    
    args = parser.parse_args()
    
    scan_aruco = not args.no_aruco
    scan_qr = not args.no_qr
    
    if args.image:
        run_image_scan(args.image, args.dict, scan_aruco, scan_qr, args.output)
    else:
        run_webcam_scan(args.dict, scan_aruco, scan_qr)

if __name__ == "__main__":
    main()
