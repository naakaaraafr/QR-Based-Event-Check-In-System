import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os
import time

# Add the QR-Generator directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
qr_generator_path = os.path.join(parent_dir, 'QR-Generator')
sys.path.append(qr_generator_path)

import QR_Gen as qr_generator
from email_sender import send_email_with_qr

def app():
    st.title(':blue[Event Check-in System]')
    
    # Get Firestore client
    db = firestore.client()
    
    # Get current user info from session state
    current_username = st.session_state.get("username")
    current_uid = st.session_state.get("user_uid")
    user_email = st.session_state.get("useremail")
    
    if not current_uid:
        st.warning("User not logged in.")
        return
    
    st.header("Available Events")
    
    # Create a success message placeholder
    success_placeholder = st.empty()
    
    try:
        # Get all events from Firestore
        events_ref = db.collection('Events').stream()
        
        # Convert to list of tuples (id, data) for easier processing
        events_list = [(event.id, event.to_dict()) for event in events_ref]
        
        if not events_list:
            st.info("No events available at the moment.")
            return
        
        # Display each event with check-in option
        for event_id, event_data in events_list:
            # Create container for each event
            with st.container():
                # Get the last context item or handle empty context
                context = event_data.get('Context', ['No description available'])
                context_text = context[-1] if isinstance(context, list) and context else context
                
                # Check if user is already checked in
                already_checked_in = False
                if 'CheckedIn' in event_data:
                    already_checked_in = current_uid in event_data['CheckedIn']
                
                # Display event details
                st.markdown(f"""
                    <div style="padding:10px; border:1px solid #aaa; border-radius:10px; margin-bottom:10px;">
                        <b>Event Name:</b> {event_id}<br>
                        <b>Description:</b> {context_text}<br>
                        <b>Location:</b> {event_data.get('Location', 'N/A')}<br>
                        <b>Date & Time:</b> {event_data.get('Date & Time', 'N/A')}<br>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show appropriate button based on check-in status
                if already_checked_in:
                    st.success("✅ You are checked in to this event")
                else:
                    if st.button("Check In", key=f"checkin_{event_id}"):
                        try:
                            # Update the CheckedIn list in Firestore
                            event_ref = db.collection('Events').document(event_id)
                            
                            # Get current checked in users
                            checked_in = event_data.get('CheckedIn', [])
                            
                            # Add current user if not already in the list
                            if current_uid not in checked_in:
                                checked_in.append(current_uid)
                                
                                # Update Firestore document
                                event_ref.update({"CheckedIn": checked_in})
                                
                                # Generate QR code for this user and event
                                qr_path = qr_generator.generate_and_save_event_qr(event_id, event_data, current_uid)
                                
                                # Send email with QR code
                                email_sent = send_email_with_qr(user_email, event_id, event_id, qr_path)
                                
                                if email_sent:
                                    success_message = f"✅ Successfully checked in to {event_id}! QR code has been sent to your email."
                                else:
                                    success_message = f"✅ Successfully checked in to {event_id}! But failed to send QR code to your email."
                                
                                success_placeholder.success(success_message)
                                
                                # Force refresh after a short delay
                                time.sleep(2)
                                st.rerun()
                        except Exception as e:
                            st.error(f"Failed to check in: {e}")
                
                st.markdown("---")
    
    except Exception as e:
        st.error(f"Failed to load events: {e}")