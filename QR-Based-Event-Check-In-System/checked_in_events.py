from datetime import datetime
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os
from PIL import Image
import io

# Add the QR-Generator directory to the path to import the QR-Gen module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
qr_generator_path = os.path.join(parent_dir, 'QR-Generator')
sys.path.append(qr_generator_path)

import QR_Gen as qr_generator

def app():
    st.title(':green[Your Checked-in Events]')
    db = firestore.client()

    # Get current user info from session
    current_username = st.session_state.get("username")
    current_uid = st.session_state.get("user_uid")
    user_email = st.session_state.get("useremail")

    if not current_uid:
        st.warning("User not logged in.")
        return

    try:
        events_ref = db.collection('Events').stream()

        checked_in_events = []
        for event in events_ref:
            event_data = event.to_dict()
            if 'CheckedIn' in event_data and current_uid in event_data['CheckedIn']:
                # Add event to the list
                checked_in_events.append((event.id, event_data))

        if not checked_in_events:
            st.info("You haven't checked into any events yet.")
            return
        
        # Sort events by datetime
        def get_event_datetime(event_tuple):
            _, event_data = event_tuple
            date_time_str = event_data.get('Date & Time', '')
            
            try:
                # Handle your specific format: "06 May 2025 at 09:45:00 IST"
                if 'at' in date_time_str:
                    # Remove timezone indicator and parse
                    date_part, time_part = date_time_str.split(' at ')
                    time_part = time_part.split(' ')[0]  # Remove IST or other timezone
                    full_datetime_str = f"{date_part} {time_part}"
                    dt = datetime.strptime(full_datetime_str, '%d %b %Y %H:%M:%S')
                    return dt
                else:
                    # Fallback for other formats
                    return datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
            except (ValueError, TypeError) as e:
                st.warning(f"Date parsing error for: {date_time_str}")
                # If parsing fails, return a minimum date to sort these events last
                return datetime.min
        
        # Sort the events by their date and time (chronological order)
        sorted_events = sorted(checked_in_events, key=get_event_datetime)
        
        # Create a placeholder for the QR code popup
        qr_placeholder = st.empty()
        
        # Display the events in chronological order
        for event_id, event_data in sorted_events:
            # Get the last context item or handle empty context
            context = event_data.get('Context', ['No description available'])
            context_text = context[-1] if isinstance(context, list) and context else context
            
            # Create a container for each event to keep button associated with the event
            with st.container():
                st.markdown(f"""
                    <div style="padding:10px; border:1px solid #aaa; border-radius:10px; margin-bottom:10px;">
                        <b>Event Name:</b> {event_id}<br>
                        <b>Description:</b> {context_text}<br>
                        <b>Location:</b> {event_data.get('Location', 'N/A')}<br>
                        <b>Date & Time:</b> {event_data.get('Date & Time', 'N/A')}<br>
                    </div>
                """, unsafe_allow_html=True)
                
                # Add Show QR button
                if st.button("Show QR", key=f"qr_button_{event_id}"):
                    # Generate and save QR code
                    try:
                        # Generate QR code specific to this user and event
                        qr_path = qr_generator.generate_and_save_event_qr(event_id, event_data, current_uid)
                        
                        # Display QR code in a popup-like UI
                        with qr_placeholder.container():
                            col1, col2, col3 = st.columns([1, 3, 1])
                            with col2:
                                st.subheader(f"QR Code for {event_id}")
                                # Display the QR code image
                                st.image(qr_path, caption=f"QR Code for {event_id}")
                                # Add a close button
                                if st.button("Close", key=f"close_qr_{event_id}"):
                                    qr_placeholder.empty()
                    except Exception as e:
                        st.error(f"Failed to generate QR code: {e}")
                
                st.markdown("---")
            
    except Exception as e:
        st.error(f"Failed to load events: {e}")