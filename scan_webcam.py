#!/usr/bin/env python3
"""
Simple Real-time ArUco Scanner
Opens the webcam and scans ArUco markers in real-time.
"""

import cv2
import sys

def main():
    # Use standard 6x6 ArUco dictionary
    dict_type = cv2.aruco.DICT_6X6_250
    
    # 1. Initialize ArUco Dictionary and Parameters with compatibility checks
    try:
        if hasattr(cv2.aruco, "getPredefinedDictionary"):
            aruco_dict = cv2.aruco.getPredefinedDictionary(dict_type)
        else:
            aruco_dict = cv2.aruco.Dictionary_get(dict_type)
            
        if hasattr(cv2.aruco, "DetectorParameters"):
            parameters = cv2.aruco.DetectorParameters()
        else:
            parameters = cv2.aruco.DetectorParameters_create()
            
        # OpenCV 4.7.0+ introduced ArucoDetector class
        detector = None
        if hasattr(cv2.aruco, "ArucoDetector"):
            detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    except AttributeError:
        print("Error: cv2.aruco module not found. Make sure 'opencv-contrib-python' is installed.")
        sys.exit(1)

    # 2. Open the default camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open the webcam.")
        sys.exit(1)
        
    print("==================================================")
    print("Webcam ArUco Scanner Started!")
    print("Aim camera at an ArUco marker (from DICT_6X6_250)")
    print("Press 'q' to quit.")
    print("==================================================")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break
            
        # Convert to grayscale (ArUco detection works on grayscale images)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 3. Detect markers
        if detector is not None:
            corners, ids, rejected = detector.detectMarkers(gray)
        else:
            corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            
        # 4. If markers are detected, draw them and print the IDs
        if ids is not None:
            # Draw green borders and ID markers on the frame
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            
            # Print and display the IDs
            for marker_id, marker_corners in zip(ids.flatten(), corners):
                print(f"Detected ArUco ID: {marker_id}")
                
                # Draw ID text on screen above the marker
                top_left = tuple(marker_corners[0][0].astype(int))
                cv2.putText(
                    frame, 
                    f"ID: {marker_id}", 
                    (top_left[0], top_left[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, 
                    (0, 0, 255), 
                    2
                )
                
        # Show the video feed
        cv2.imshow("Realtime ArUco Scanner (Press 'q' to quit)", frame)
        
        # Press 'q' to quit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    # Clean up and close windows
    cap.release()
    cv2.destroyAllWindows()
    print("Scanner stopped.")

if __name__ == "__main__":
    main()
