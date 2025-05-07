from email.message import EmailMessage
import ssl
import smtplib
import firebase_admin
from firebase_admin import credentials
import streamlit as st
from firebase_admin import firestore
import os
from PIL import Image
import io

if not firebase_admin._apps:
    cred = credentials.Certificate("event-check-in-system-b3de0fb59c7e.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

def send_email_with_qr(email_receiver, event_id, event_name, qr_code_path):
    """
    Send an email with the QR code to the user
    
    Args:
        email_receiver (str): The email address of the receiver
        event_id (str): The ID of the event
        event_name (str): The name of the event
        qr_code_path (str): The path to the QR code image
    """
    try:
        email_sender = 'dkudesiaa.gzb@gmail.com'
        email_password = 'jhdh vvwo nexn dcce'
        
        subject = f'Event Check-in QR Code for: {event_name}'
        body = f"""
        Thank you for checking in to the event: {event_name}
        
        Please find your QR code attached to this email. You can use this QR code to verify your attendance at the event.
        
        Best regards,
        Event Check-in System Team
        """
        
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)
        
        # Attach the QR code image
        with open(qr_code_path, 'rb') as f:
            qr_image_data = f.read()
        
        em.add_attachment(qr_image_data, maintype='image', subtype='png', filename=f'{event_id}_qr.png')
        
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False