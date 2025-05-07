import time
import streamlit as st
from firebase_admin import firestore
from datetime import datetime, timezone
import pytz  # For timezone handling
import re  # For parsing date strings

def delete_event(event_id):
    """
    Delete an event from the Firestore database.
    
    Args:
        event_id: The ID of the event document to delete
    """
    try:
        # Delete the event document from Firestore
        st.session_state.db.collection('Events').document(event_id).delete()

        # Use a placeholder to show the success message for longer
        message = st.empty()
        message.success(f"Event '{event_id}' deleted successfully!")
        time.sleep(5)
        message.empty()

        # Force a rerun to refresh the page and show updated list
        st.rerun()

    except Exception as e:
        st.error(f"Error deleting event: {str(e)}")

    except Exception as e:
        st.error(f"Error deleting event: {str(e)}")

def app():
    # Initialize session state variables for form fields if they don't exist
    for key in ['event_name', 'post', 'location']:
        if key not in st.session_state:
            st.session_state[key] = ""
    
    # Initialize refresh flag if needed
    if 'need_refresh' not in st.session_state:
        st.session_state.need_refresh = False
    
    # Handle refresh if needed - using st.rerun() directly instead of experimental_rerun
    if st.session_state.need_refresh:
        st.session_state.need_refresh = False
        st.rerun()
        
    # Firestore client setup
    if 'db' not in st.session_state:
        st.session_state.db = firestore.client()
        
    # Function to handle form submission and clear fields
    def post_event():
        # Get values from session state
        event_name = st.session_state.event_name
        post = st.session_state.post
        location = st.session_state.location
        event_date = st.session_state.event_date
        event_time = st.session_state.event_time
        
        if event_name.strip() != '' and post.strip() != '' and location.strip() != '':
            try:
                # Get the local timezone
                local_tz = pytz.timezone('Asia/Kolkata')  # Adjust to your timezone if needed
                
                # Combine date/time and format with timezone
                naive_datetime = datetime.combine(event_date, event_time)
                event_datetime = local_tz.localize(naive_datetime)
                
                # Store timestamp as a string for display
                timestamp = event_datetime.strftime('%d %B %Y at %H:%M:%S %Z')
                
                # Store event time as a Unix timestamp for sorting
                unix_timestamp = int(event_datetime.timestamp())
                
                doc_ref = st.session_state.db.collection('Events').document(event_name)
                
                if doc_ref.get().exists:
                    doc_ref.update({
                        'Context': firestore.ArrayUnion([post]),
                        'Date & Time': timestamp,
                        'Timestamp': unix_timestamp,
                        'Location': location
                    })
                else:
                    doc_ref.set({
                        'Context': [post],
                        'Date & Time': timestamp,
                        'Timestamp': unix_timestamp,
                        'Location': location
                    })
                
                # Clear the form by resetting session state values
                st.session_state.event_name = ""
                st.session_state.post = ""
                st.session_state.location = ""
                
                # Set success message in session state
                st.session_state.success_message = "Event posted successfully!"
                
                # Set refresh flag
                st.session_state.need_refresh = True
                
            except Exception as e:
                st.session_state.error_message = f"Error posting event: {e}"
        else:
            st.session_state.warning_message = "Please fill all fields"

    db = st.session_state.db
    st.title(':violet[ADMIN DASHBOARD]', anchor='top')
    st.markdown('---')
    st.header(' :blue[New Event] ')
    
    # Display any messages from the previous run
    if 'success_message' in st.session_state:
        st.success(st.session_state.success_message)
        del st.session_state.success_message
    
    if 'error_message' in st.session_state:
        st.error(st.session_state.error_message)
        del st.session_state.error_message
        
    if 'warning_message' in st.session_state:
        st.warning(st.session_state.warning_message)
        del st.session_state.warning_message
    
    # Input fields with explicit keys and values from session state
    st.text_input(
        label=' :green[+ New Event]', 
        placeholder="Enter event name", 
        key='event_name', 
        value=st.session_state.event_name
    )
    
    st.text_area(
        label=' :orange[+ Event Description]', 
        placeholder='Post new event details here...', 
        height=None, 
        max_chars=500, 
        key='post',
        value=st.session_state.post
    )
    
    st.text_input(
        label=' :red[+ Event Location]', 
        placeholder="Enter event location", 
        key='location',
        value=st.session_state.location
    )
    
    # Date/Time inputs - let Streamlit handle their session state internally
    st.date_input(label=' :grey[+ Event Date]', key='event_date')
    st.time_input(label=' :grey[+ Event Time]', key='event_time')
    
    st.markdown('---')

    # Button that triggers the post_event function when clicked
    if st.button('Post', use_container_width=True, on_click=post_event):
        pass  # The actual work is done in the post_event callback

    st.header(' :violet[Latest Events] ')
    
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

                st.markdown(f"""
                    <div style="padding:10px; border:1px solid #aaa; border-radius:10px; margin-bottom:10px; position: relative;">
                        <b>Event Name:</b> {event_id}<br>
                        <b>Event Description:</b> {context_text}<br>
                        <b>Location:</b> {location_text}<br>
                        <b>Date & Time:</b> {formatted_time}<br>
                        <div style="position: absolute; bottom: 10px; right: 10px;">
                """, unsafe_allow_html=True)

                # Unique button key with index
                delete_key = f"delete_event_{event_id}_{c}"
                if st.button('Delete Event', key=delete_key):
                    delete_event(event_id)
                
                st.markdown("</div></div>", unsafe_allow_html=True)

            except Exception as e:
                st.warning(f"Could not display event {event_id}: {str(e)}")

    except Exception as e:
        st.error(f"Error loading events: {str(e)}")


# Add this at the end of your file
if __name__ == "__main__":
    app()