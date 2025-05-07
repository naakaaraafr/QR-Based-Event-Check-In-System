import firebase_admin
import streamlit as st
from firebase_admin import credentials, auth, firestore
import hashlib
import os
import hmac

if not firebase_admin._apps:
    cred = credentials.Certificate("event-check-in-system-b3de0fb59c7e.json")
    firebase_admin.initialize_app(cred)

def is_admin():
    """Check if current user is admin without rendering UI elements"""
    return st.session_state.get("is_admin", False)

def hash_password(password, salt=None):
    """
    Hash a password for storing.
    
    Args:
        password (str): The password to hash
        salt (bytes, optional): The salt to use. If None, a new salt is generated.
        
    Returns:
        tuple: (hash, salt)
    """
    if salt is None:
        salt = os.urandom(32)  # 32 bytes = 256 bits
    
    # Use PBKDF2 with HMAC-SHA256, 100,000 iterations
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    
    # Return the salt and key as hex strings
    return key.hex(), salt.hex()

def verify_password(stored_password, stored_salt, provided_password):
    """
    Verify a stored password against a provided password
    
    Args:
        stored_password (str): The stored password hash (hex)
        stored_salt (str): The stored salt (hex)
        provided_password (str): The password to check
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    # Convert hex strings back to bytes
    salt = bytes.fromhex(stored_salt)
    
    # Hash the provided password with the same salt
    new_key, _ = hash_password(provided_password, salt)
    
    # Compare the new hash with the stored hash
    return hmac.compare_digest(stored_password, new_key)

def app(show_ui=True):
    """
    Handle authentication logic
    
    Parameters:
    - show_ui: Whether to render UI elements (set to False when just checking admin status)
    
    Returns:
    - Boolean indicating if user is admin
    """
    # Initialize Firestore client
    db = firestore.client()
    
    # Initialize session state variables if they don't exist
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'user_uid' not in st.session_state:
        st.session_state.user_uid = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
    # If not showing UI, just return admin status
    if not show_ui:
        return st.session_state.get("is_admin", False)
    
    st.title(':violet[Event Check-in System] :sunglasses:')

    def login():
        try:
            # Get user by email
            user = auth.get_user_by_email(email)
            
            # Get the user document from Firestore
            user_doc = db.collection('users').document(user.uid).get()
            
            if not user_doc.exists:
                st.warning("User profile not found")
                return
                
            user_data = user_doc.to_dict()
            username = user_data.get('username', user.uid)
            
            # Check if we're using the new secure password system or legacy plaintext
            if 'password_hash' in user_data and 'password_salt' in user_data:
                # Secure password verification
                stored_hash = user_data.get('password_hash')
                stored_salt = user_data.get('password_salt')
                password_correct = verify_password(stored_hash, stored_salt, password)
            else:
                # Legacy plaintext password verification
                # This allows for backward compatibility during transition
                stored_password = user_data.get('password')
                password_correct = (password == stored_password)
                
                # If using legacy password, update to secure hash on successful login
                if password_correct:
                    # Update to secure password
                    password_hash, password_salt = hash_password(password)
                    db.collection('users').document(user.uid).update({
                        'password_hash': password_hash,
                        'password_salt': password_salt,
                        # Keep the plaintext password for now during transition
                        # Later you can remove it with: 'password': firestore.DELETE_FIELD
                    })
            
            # Admin user check
            if user.email == "admin@gmail.com" and password_correct:
                st.success("Admin Login Successful")
                st.session_state.username = username
                st.session_state.user_uid = user.uid
                st.session_state.useremail = user.email
                st.session_state.is_admin = True
                st.session_state.signedout = True
                st.session_state.signout = True
                st.session_state.authenticated = True
            # Regular user check with password verification
            elif password_correct:
                st.success("Login Successful")
                st.session_state.username = username
                st.session_state.user_uid = user.uid
                st.session_state.useremail = user.email
                st.session_state.is_admin = False
                st.session_state.signedout = True
                st.session_state.signout = True
                st.session_state.authenticated = True
            else:
                st.error("Incorrect password")
                    
        except Exception as e:
            st.warning(f"Login failed: {e}")

    def signout():
        st.session_state.signout = False
        st.session_state.signedout = False   
        st.session_state.username = ''
        st.session_state.user_uid = ''
        st.session_state.useremail = ''
        st.session_state.is_admin = False
        st.session_state.authenticated = False  # Reset the authenticated state

    if not st.session_state.get("signedout", False):
        choice = st.selectbox('Select an option', ['Login', 'Register'], key='auth_option_selector')
        
        if choice == 'Login':
            st.subheader('Login to your account')
            email = st.text_input('Email', key='login_email')
            password = st.text_input('Password', type='password', key='login_password')
            if st.button('Login', key='login_button'):
                login()

        else:
            st.subheader('Create a new account')
            username = st.text_input('Username', key='register_username')
            email = st.text_input('Email', key='register_email')
            password = st.text_input('Password', type='password', key='register_password')
            if st.button('Register', key='register_button'):
                try:
                    # Create user with Firebase Authentication
                    user = auth.create_user(
                        email=email,
                        password=password  # Firebase Auth handles secure password storage
                    )
                    
                    # Hash the password for our own storage
                    password_hash, password_salt = hash_password(password)
                    
                    # Store user data in Firestore users collection
                    db.collection('users').document(user.uid).set({
                        'username': username,
                        'email': email,
                        'password_hash': password_hash,
                        'password_salt': password_salt
                    })
                    
                    st.success("User created successfully")
                    st.markdown("Please login to continue")
                    st.balloons()
                except Exception as e:
                    st.error(f"Registration failed: {e}")

    if st.session_state.get("signout"):
        st.text(f'Username: {st.session_state.username}')
        st.text(f'User ID: {st.session_state.user_uid}')
        st.text(f'Email: {st.session_state.useremail}')
        if st.session_state.is_admin:
            st.text('Account type: Administrator')
        else:
            st.text('Account type: Regular user')
        st.button('Sign out', on_click=signout, key='signout_button')
    
    # Return True if admin, False otherwise
    return st.session_state.get("is_admin", False)