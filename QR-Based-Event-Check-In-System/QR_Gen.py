import qrcode
import json
import os
import firebase_admin
from firebase_admin import firestore

def generate_event_qr(event_id, event_data, user_id=None):
    """
    Generate a QR code with embedded event details
    
    Args:
        event_id (str): The ID of the event
        event_data (dict): Event details from Firebase
        user_id (str, optional): User ID if generating user-specific QR code
    
    Returns:
        PIL Image: The generated QR code image
    """
    # Create the data payload as a JSON string
    qr_data = {
        "event_id": event_id,
        "event_name": event_data.get("Name", event_id),  # Use actual event name if available
        "event_time": event_data.get("Date & Time", ""),
        "location": event_data.get("Location", "")
    }
    
    # Add user ID if provided (for user-specific QR codes)
    if user_id:
        qr_data["user_id"] = user_id
        
        # Try to get the user email to include in QR code
        try:
            db = firestore.client()
            user_doc = db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                # Add user email if available
                if user_data.get('email'):
                    qr_data["user_email"] = user_data.get('email')
        except Exception as e:
            print(f"Error getting user details: {e}")
    else:
        # If no user_id is provided, the QR code won't be valid for check-in
        print("Warning: Generating QR code without user_id. This QR code won't be valid for check-in.")
    
    # Convert to JSON string
    qr_string = json.dumps(qr_data)
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # Add data to QR code
    qr.add_data(qr_string)
    qr.make(fit=True)
    
    # Create an image from the QR Code
    img = qr.make_image(fill_color="black", back_color="white")
    
    return img

def save_qr_image(img, event_id, user_id=None):
    """
    Save QR code image to file in the Generated QR folder
    
    Args:
        img (PIL.Image): QR code image
        event_id (str): Event ID
        user_id (str, optional): User ID for user-specific QR codes
    
    Returns:
        str: Path to saved file
    """
    # Get the QR-Generator directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Generated QR folder
    qr_save_dir = os.path.join(current_dir, "Generated QR")
    
    # Create the Generated QR folder if it doesn't exist
    if not os.path.exists(qr_save_dir):
        os.makedirs(qr_save_dir)
    
    # Create filename based on event_id and user_id
    if user_id:
        # For user-specific QR codes
        filename = f"{event_id}_{user_id}.png"
    else:
        # For general event QR codes
        filename = f"{event_id}_event.png"
    
    # Create full path
    filepath = os.path.join(qr_save_dir, filename)
    
    # Save the image
    img.save(filepath)
    
    return filepath

def generate_and_save_event_qr(event_id, event_data, user_id=None):
    """
    Generate and save a QR code for an event
    
    Args:
        event_id (str): Event ID
        event_data (dict): Event data
        user_id (str, optional): User ID for personalized QR
        
    Returns:
        str: Path to the saved QR code image
    """
    # Generate the QR code
    qr_img = generate_event_qr(event_id, event_data, user_id)
    
    # Save the QR code to the Generated QR folder
    filepath = save_qr_image(qr_img, event_id, user_id)
    
    return filepath

def get_event_data_from_firebase(event_id):
    """
    Get event data from Firebase
    
    Args:
        event_id (str): Event ID to lookup
        
    Returns:
        dict: Event data from Firebase or None if not found
    """
    try:
        # Initialize Firestore client
        db = firestore.client()
        
        # Get the event document
        event_doc = db.collection('Events').document(event_id).get()
        
        if event_doc.exists:
            return event_doc.to_dict()
        else:
            return None
    except Exception as e:
        print(f"Error getting event data: {e}")