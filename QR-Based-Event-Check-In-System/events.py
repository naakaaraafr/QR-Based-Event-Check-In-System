from datetime import datetime, timezone
import re
import pytz
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os
from PIL import Image
import io
import cv2
from pyzbar.pyzbar import decode
import json
import time

def app():
    st.title(':violet[Events :]')
    db = firestore.client()

    # Get current user info from session
    current_username = st.session_state.get("username")
    current_uid = st.session_state.get("user_uid")
    user_email = st.session_state.get("useremail")

    if not current_uid:
        st.warning("User not logged in.")
        return

    # Initialize QR scanning session states
    if "qr_scanning" not in st.session_state:
        st.session_state.qr_scanning = False
    
    if "current_event_id" not in st.session_state:
        st.session_state.current_event_id = None

    # Function to process QR code data and mark attendance
    def process_qr_data(qr_data):
        try:
            # Parse the QR code data (JSON)
            event_info = json.loads(qr_data)
            
            # Extract event ID and user information from QR
            event_id = event_info.get("event_id")
            qr_user_id = event_info.get("user_id")
            qr_user_email = event_info.get("user_email")
            
            if not event_id:
                st.error("Invalid QR code: Missing event ID")
                return False
                
            if not qr_user_id:
                st.error("Invalid QR code: Missing user identification information")
                return False
                
            # Check if this is the expected event
            if event_id != st.session_state.current_event_id:
                st.error(f"QR code is for event '{event_id}', but you're trying to check in to '{st.session_state.current_event_id}'")
                return False
                
            # Get the user details from the database
            try:
                user_doc = db.collection('users').document(qr_user_id).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    username = user_data.get('username', qr_user_id)
                    user_email = qr_user_email if qr_user_email else user_data.get('email', '')
                else:
                    username = qr_user_id  # Fallback to user_id if no username found
                    user_email = qr_user_email if qr_user_email else ''
            except Exception as e:
                st.error(f"Error retrieving user details: {str(e)}")
                username = qr_user_id  # Fallback to user_id
                user_email = qr_user_email if qr_user_email else ''
                
            # Create check-in record using QR data
            check_in_data = {
                "user_id": qr_user_id,  # Use user ID from QR code
                "username": username,  # Get username from database, not QR code
                "user_email": user_email,
                "check_in_time": datetime.now(timezone.utc),
                "check_in_method": "qr_scan",
                "attendance_status": "present"
            }
            
            # Add all QR code data to the check-in record
            for key, value in event_info.items():
                if key not in check_in_data:  # Don't overwrite fields we've already set
                    check_in_data[key] = value
                
            # Add to EventCheckIns collection in Firebase
            db.collection('EventCheckIns').add(check_in_data)
            
            # Update user's attendance record using the user ID from QR code
            user_attendance_ref = db.collection('UserAttendance').document(qr_user_id)
            
            # Check if document exists
            user_attendance_doc = user_attendance_ref.get()
            if user_attendance_doc.exists:
                # Update existing document
                attended_events = user_attendance_doc.to_dict().get('attended_events', [])
                if event_id not in attended_events:
                    attended_events.append(event_id)
                    user_attendance_ref.update({
                        'attended_events': attended_events,
                        'last_updated': datetime.now(timezone.utc),
                        'event_details': firestore.ArrayUnion([event_info])  # Store the full event info
                    })
            else:
                # Create new document
                user_attendance_ref.set({
                    'user_id': qr_user_id,
                    'attended_events': [event_id],
                    'event_details': [event_info],  # Store the full event info
                    'last_updated': datetime.now(timezone.utc)
                })
            
            st.success(f"Successfully checked in user '{username}' to event: {event_id}")
            return True
            
        except json.JSONDecodeError:
            st.error("Invalid QR code format")
            return False
        except Exception as e:
            st.error(f"Error processing check-in: {str(e)}")
            return False

    # QR Scanner function
    def scan_qr():
        # Create placeholders for camera feed and status
        frame_placeholder = st.empty()
        status_placeholder = st.empty()
        
        status_placeholder.info("Starting camera... Please wait.")
        
        try:
            # Open camera
            cap = cv2.VideoCapture(0)
            
            # Check if camera opened successfully
            if not cap.isOpened():
                status_placeholder.error("Could not open camera. Please check your permissions and camera connection.")
                return None
            
            # Set resolution
            cap.set(3, 640)  # Width
            cap.set(4, 480)  # Height
            
            status_placeholder.info("Scanning for QR code... (Click outside camera or press 'Stop Scanning' to exit)")
            
            # Add a stop button
            stop_col1, stop_col2, stop_col3 = st.columns([1, 1, 1])
            with stop_col2:
                stop_button = st.button("Stop Scanning")
            
            # Scanning loop
            scan_start_time = time.time()
            scan_timeout = 60  # 60 seconds timeout
            
            while not stop_button and (time.time() - scan_start_time < scan_timeout):
                # Capture frame
                ret, frame = cap.read()
                if not ret:
                    status_placeholder.error("Failed to grab frame from camera")
                    break
                
                # Convert to RGB for display in Streamlit
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Display the frame - FIXED HERE: use_container_width instead of use_column_width
                frame_placeholder.image(frame_rgb, channels="RGB", caption="QR Scanner", use_container_width=True)
                
                # Scan for QR codes
                decoded_objects = decode(frame)
                if decoded_objects:
                    for obj in decoded_objects:
                        if obj.type == 'QRCODE':
                            # Extract QR code data
                            qr_data = obj.data.decode('utf-8')
                            
                            # Close the camera
                            cap.release()
                            
                            # Clear the camera view
                            frame_placeholder.empty()
                            status_placeholder.empty()
                            
                            # Process the QR data
                            return qr_data
                
                # Small delay to prevent high CPU usage
                time.sleep(0.1)
                
                # Check if the button state changed
                if stop_button:
                    break
            
            # Timeout handling
            if time.time() - scan_start_time >= scan_timeout:
                status_placeholder.warning("QR scanning timed out. Please try again.")
        
        except Exception as e:
            status_placeholder.error(f"Error during QR scanning: {str(e)}")
        finally:
            # Clean up
            if 'cap' in locals() and cap.isOpened():
                cap.release()
            
            # Clear placeholders
            frame_placeholder.empty()
            status_placeholder.empty()
        
        return None

    # Handle check-in button click
    def handle_check_in(event_id):
        # Store the current event ID in session state
        st.session_state.current_event_id = event_id
        
        # Display scanning UI
        st.subheader("QR Code Check-in")
        st.write("Please scan the event QR code to confirm your attendance")
        
        # Start QR scanning
        qr_data = scan_qr()
        
        if qr_data:
            # Process the scanned QR data
            process_qr_data(qr_data)

    try:
        # Get events from Firestore
        events = list(db.collection('Events').stream())
        
        if not events:
            st.info("No events found.")
            return
            
        # Create a list of events with their data
        content = []
        for event in events:
            event_data = event.to_dict()
            # Add both the event document and its data to content
            content.append((event, event_data))
        
        # Sort events by event date/time chronologically
        def get_event_datetime(event_data):
            try:
                # First try to use the stored timestamp if available
                if 'Timestamp' in event_data:
                    return event_data['Timestamp']
                
                # If timestamp not available, try to parse from the "Date & Time" string
                date_str = event_data.get('Date & Time', '')
                if date_str:
                    # Extract date and time using regex
                    match = re.search(r'(\d{2} \w+ \d{4}) at (\d{2}:\d{2}:\d{2})', date_str)
                    if match:
                        date_part = match.group(1)
                        time_part = match.group(2)
                        # Parse the datetime string
                        dt = datetime.strptime(f"{date_part} {time_part}", "%d %B %Y %H:%M:%S")
                        # Set timezone (assuming IST)
                        ist = pytz.timezone('Asia/Kolkata')
                        dt = ist.localize(dt)
                        # Return as timestamp
                        return dt.timestamp()
                
                # If we can't get a proper timestamp, use current time as fallback
                return datetime.now(timezone.utc).timestamp()
            except Exception as e:
                # If any error occurs, return current time
                st.warning(f"Error parsing date: {e}")
                return datetime.now(timezone.utc).timestamp()
        
        # Sort events chronologically (earliest first)
        content.sort(key=lambda x: get_event_datetime(x[1]))
        
        # Display sorted events
        for c, (event, event_data) in enumerate(content):
            event_id = event.id
            
            try:
                # Get the timestamp as a string
                formatted_time = event_data.get('Date & Time', 'N/A')
                
                # Get the last context item or handle empty context
                context = event_data.get('Context', ['No description available'])
                context_text = context[-1] if isinstance(context, list) and context else context
                
                # Location with fallback
                location_text = event_data.get('Location', 'N/A')

                # Create a unique key for each event
                event_container = st.container()
                
                with event_container:
                    st.markdown(f"""
                        <div style="padding:10px; border:1px solid #aaa; border-radius:10px; margin-bottom:10px;">
                            <b>Event Name:</b> {event_id}<br>
                            <b>Event Description:</b> {context_text}<br>
                            <b>Location:</b> {location_text}<br>
                            <b>Date & Time:</b> {formatted_time}<br>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Check if user has already checked in to this event
                    user_attendance_ref = db.collection('UserAttendance').document(current_uid).get()
                    already_checked_in = False
                    
                    if user_attendance_ref.exists:
                        attended_events = user_attendance_ref.to_dict().get('attended_events', [])
                        if event_id in attended_events:
                            already_checked_in = True
                    
                    # Show appropriate button based on check-in status
                    if already_checked_in:
                        if st.button(f"On-spot Check-in", key=f"checkin_{c}_{event_id}"):
                            handle_check_in(event_id)
                    else:
                        # Check-in button with unique key
                        if st.button(f"On-spot Check-in", key=f"checkin_{c}_{event_id}"):
                            handle_check_in(event_id)
                    
                    st.markdown("---")
                
            except Exception as e:
                st.warning(f"Could not display event {event_id}: {str(e)}")

    except Exception as e:
        st.error(f"Error loading events: {str(e)}")