##QR-Based Event Check-In System

This project is a QR code-based event check-in system designed to streamline event management and attendance tracking. Built with Python and Streamlit, it allows administrators to create and manage events, while users can check into events using QR codes, either through email notifications or on-spot scanning. The system integrates with Firebase for authentication and data storage, ensuring secure and efficient operations.
Features

Event Management: Admins can create, update, and delete events with details like name, description, location, date, and time.
QR Code Generation: Automatically generates unique QR codes for events and attendees.
QR Code Scanning: Supports on-spot check-ins via webcam-based QR scanning.
Email Notifications: Sends QR codes to attendees via email upon check-in.
User Authentication: Secure login and registration for admins and users using Firebase Authentication.
Attendance Tracking: Records and displays checked-in events for users and maintains attendance logs.

Prerequisites

Python 3.8+: Ensure you have Python installed.
Firebase Account: Required for authentication and database services.
Webcam Access: Necessary for QR scanning functionality (if running locally).
Internet Connection: Needed for Firebase integration and email sending.

Setup Instructions
Installing Dependencies
Clone the repository and install the required Python packages using pip:
git clone https://github.com/yourusername/QR-Based-Event-Check-In-System.git
cd QR-Based-Event-Check-In-System
pip install streamlit firebase-admin opencv-python pyzbar pillow qrcode

Firebase Setup

Create a Firebase Project:

Visit console.firebase.google.com and create a new project.
Enable Authentication (Email/Password provider) and Firestore Database.


Generate Service Account Key:

Go to Project Settings > Service Accounts.
Click "Generate new private key" and download the JSON file.
Rename it to event-check-in-system-b3de0fb59c7e.json and place it in the project root directory. Do not commit this file to the repository.



Configuring Admin User
The system designates admin@gmail.com as the admin account:

Register this email through the app’s registration interface (auth.py).
Log in with the admin credentials to access the admin dashboard.

Usage
Running the Application
Launch the Streamlit app with:
streamlit run main.py

This opens the app in your default web browser.
Admin Workflow

Login: Use admin@gmail.com and the registered password.
Create Event: From the Admin Dashboard, enter event details (name, description, location, date, time) and click "Post".
Manage Events: View, update, or delete events under "Latest Events".

User Workflow

Register/Login: Create an account or log in via the authentication page.
View Events: Browse available events on the user dashboard.
Check-In: 
Via Email: Click "Check In" to receive a QR code via email.
On-Spot: Use the "On-spot Check-in" button to scan a QR code with your webcam.


View Checked-In Events: See your attendance history under "Checked-In Events".

File Structure
The project is organized as follows:

QR-BASE (root directory)
QR-Event-Management... (truncated name, likely contains additional files or subdirectories related to event management)
_pycache_ (standard Python cache directory containing compiled bytecode files)
Generated QR (truncated name, likely contains files or subdirectories related to generated QR codes)
auth.py (Python script handling authentication logic)
check_in_events.py (Python script for managing or processing check-in events)
email_sender.py (Python script for sending emails, such as notifications or confirmations)
{event-check-in-system...} (truncated name, likely a subdirectory containing core system files; the curly braces may indicate a virtual environment or specific project module)
events.py (Python script with event-related logic or data)
home_admin.py (Python script for the admin interface or backend logic)
home_user.py (Python script for the user interface or backend logic)
main.py (Python script serving as the entry point or main execution file)
QR_Gen.py (Python script responsible for generating QR codes)
qr_scanner.py (Python script handling QR code scanning functionality)


venv (directory for the virtual environment, used to isolate project dependencies)



Note: The truncated names (e.g., QR-Event-Management..., {event-check-in-system...}) indicate that the full directory names are longer and may contain additional descriptive information not visible in the screenshot. The curly braces around {event-check-in-system...} might signify a specific project module or virtual environment.


Security Notes

Firebase Credentials: Keep event-check-in-system-b3de0fb59c7e.json private. Use .gitignore to exclude it from version control.
Email Credentials: In email_sender.py, replace hardcoded credentials (email_sender and email_password) with environment variables for security:export EMAIL_SENDER="your_email@gmail.com"
export EMAIL_PASSWORD="your_app_password"

Update email_sender.py to use os.getenv("EMAIL_SENDER") and os.getenv("EMAIL_PASSWORD").
Password Security: Passwords are hashed using PBKDF2 with a salt in auth.py for secure storage.

Contributing
We welcome contributions! To get started:

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m "Add your feature").
Push to your branch (git push origin feature/your-feature).
Open a pull request.

Please include screenshots or GIFs in your pull request to demonstrate new features.
License
This project is licensed under the MIT License. See the LICENSE file for details. (Note: Add a LICENSE file to your repository if not already present.)
Recommendations

Screenshots/GIFs: Add visuals to this README to showcase the app’s interface and QR scanning process.
Deployment: Consider deploying the app on Streamlit Cloud or a similar platform for broader access.
Testing: Test QR scanning across different devices to ensure webcam compatibility.

