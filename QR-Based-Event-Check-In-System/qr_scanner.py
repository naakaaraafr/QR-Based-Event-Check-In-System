import cv2
from pyzbar.pyzbar import decode
import json
import time

def scan_qr_code():
    """
    Standalone QR code scanner that returns the decoded data when found.
    
    Returns:
        str: Decoded QR code data or None if scanning is canceled
    """
    print("Starting QR code scanner...")
    print("Press 'q' to quit or 'r' to reset if scanner freezes.")
    
    # Initialize camera
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)  # Width
    cam.set(4, 480)  # Height
    
    if not cam.isOpened():
        print("Could not open camera. Please check your camera connection and permissions.")
        return None
    
    qr_data = None
    start_time = time.time()
    timeout = 60  # 60 seconds timeout
    
    while time.time() - start_time < timeout:
        # Read frame
        success, frame = cam.read()
        if not success:
            print("Failed to grab frame. Is the camera in use by another application?")
            break
        
        # Add a message to the frame
        cv2.putText(frame, "Scanning for QR code...", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Check for QR codes
        decoded_objects = decode(frame)
        
        # Draw rectangles around detected QR codes
        for obj in decoded_objects:
            points = obj.polygon
            if len(points) == 4:
                # Convert to int tuple points
                pts = [(int(p.x), int(p.y)) for p in points]
                # Draw polygon
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
            
            # Get decoded data
            qr_data = obj.data.decode('utf-8')
            
            # Display data on frame
            cv2.putText(frame, "QR Code Found!", (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Keep frame displayed for a moment
            cv2.imshow('QR Code Scanner', frame)
            cv2.waitKey(1000)  # Display for 1 second
            
            # Clean up and return data
            cam.release()
            cv2.destroyAllWindows()
            
            # Try to parse as JSON to validate
            try:
                json_data = json.loads(qr_data)
                print(f"Decoded QR data: {json.dumps(json_data, indent=2)}")
                return qr_data
            except json.JSONDecodeError:
                print(f"Warning: QR code doesn't contain valid JSON. Raw data: {qr_data}")
                return qr_data
        
        # Display frame
        cv2.imshow('QR Code Scanner', frame)
        
        # Check for keyboard input
        key = cv2.waitKey(1)
        if key == ord('q'):
            print("Scanning canceled by user")
            break
        elif key == ord('r'):
            # Reset camera if it freezes
            cam.release()
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                print("Failed to reset camera")
                break
    
    # Clean up
    cam.release()
    cv2.destroyAllWindows()
    
    if time.time() - start_time >= timeout:
        print("QR scanning timed out")
    
    return None

# For testing as standalone script
if __name__ == "__main__":
    result = scan_qr_code()
    if result:
        print(f"Successfully scanned QR code: {result}")
    else:
        print("No QR code scanned")