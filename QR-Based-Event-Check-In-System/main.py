import firebase_admin
import streamlit as st
from streamlit_option_menu import option_menu
from firebase_admin import credentials, auth, firestore
import home_admin, home_user, auth, checked_in_events,events

if not firebase_admin._apps:
    cred = credentials.Certificate("event-check-in-system-b3de0fb59c7e.json")
    firebase_admin.initialize_app(cred)

st.set_page_config(
        page_title="Event Check-in System",
        page_icon=":guardsman:",  # You can use any emoji or icon here
)

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })
    
    def run():
        # Initialize session state variables if they don't exist
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        
        # Check if user is authenticated
        if not st.session_state.authenticated:
            # Only show auth UI and handle login
            is_admin = auth.app(show_ui=True)
            
            # Check if user has successfully authenticated
            if st.session_state.get("signout", False):
                st.session_state.authenticated = True
                # Force a rerun to show the correct dashboard
                st.rerun()
            return
        
        # User is authenticated, now determine if admin
        is_admin_user = auth.is_admin()
        
        # Determine which sidebar to show based on admin status
        if is_admin_user:
            with st.sidebar:        
                app = option_menu(
                    menu_title='Event Check-in System',
                    options=['Home','Events','Account'],
                    icons = ['house-fill', 'award-fill', 'person-circle'],
                    default_index=0,
                    styles={
                        "container": {"padding": "5!important","background-color":'black'},
                        "icon": {"color": "white", "font-size": "23px"}, 
                        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
                        "nav-link-selected": {"background-color": "#02ab21"},
                    },
                    key="admin_sidebar"
                )
            
            # Render admin apps
            if app == "Home":
                home_admin.app()
            elif app == "Account":
                auth.app(show_ui=True)
                # If user signs out, reset authentication state
                if not st.session_state.get("signout", False):
                    st.session_state.authenticated = False
                    st.rerun()
            elif app == "Events":
                events.app()
        else:
            with st.sidebar:        
                app = option_menu(
                    menu_title='Event Check-in System',
                    options=['Home','Checked-In Events','Account'],
                    icons = ['house-fill', 'award-fill', 'person-circle'],
                    default_index=0,
                    styles={
                        "container": {"padding": "5!important","background-color":'black'},
                        "icon": {"color": "white", "font-size": "23px"}, 
                        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
                        "nav-link-selected": {"background-color": "#02ab21"},
                    },
                    key="user_sidebar"
                )
            
            # Render user apps
            if app == "Home":
                home_user.app()
            elif app == "Account":
                auth.app(show_ui=True)
                # If user signs out, reset authentication state
                if not st.session_state.get("signout", False):
                    st.session_state.authenticated = False
                    st.rerun()
            elif app == "Checked-In Events":
                checked_in_events.app()
             
    run()