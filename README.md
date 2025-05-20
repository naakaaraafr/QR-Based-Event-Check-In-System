# QR-Based Event Check-In System

This project is a QR code-based event check-in system designed to streamline event management and attendance tracking. Built with Python and Streamlit, it allows administrators to create and manage events, while users can check into events using QR codes—either through email notifications or on-spot scanning. The system integrates with Firebase for authentication and data storage, ensuring secure and efficient operations.

---

## 🚀 Features

### Event Management

* Admins can create, update, and delete events with details like name, description, location, date, and time

### QR Code Integration

* Automatically generates unique QR codes for events and attendees
* Real-time on-spot check-in support via webcam-based QR scanning using OpenCV and PyZbar

### Email Notifications

* Sends QR codes to attendees via email upon successful check-in

### User Authentication

* Secure login and registration for admins and users using Firebase Authentication
* Role-based access with admin-only features

### Attendance Tracking

* Logs and displays checked-in events for users
* Maintains historical attendance records

---

## 🛠 Prerequisites

* Python 3.8+
* Firebase account with Firestore and Email/Password Auth enabled
* Webcam access for QR scanning functionality (if running locally)
* Internet connection for Firebase integration and email delivery

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/naakaarafr/QR-Based-Event-Check-In-System.git
cd QR-Based-Event-Check-In-System
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Firebase Setup

* Visit [Firebase Console](https://console.firebase.google.com) and create a project
* Enable Authentication (Email/Password) and Firestore
* Go to Project Settings → Service Accounts → Generate New Private Key
* Rename the downloaded key file to `event-check-in-system-b3de0fb59c7e.json` and place it in the project root (add to `.gitignore`)

### 4. Configure Admin User

* Register `admin@gmail.com` through the app’s interface (auth.py)
* Log in using this account to access the Admin Dashboard

### 5. Email Credentials

In `email_sender.py`, replace hardcoded values with environment variables:

```bash
export EMAIL_SENDER="your_email@gmail.com"
export EMAIL_PASSWORD="your_app_password"
```

Use `os.getenv("EMAIL_SENDER")` and `os.getenv("EMAIL_PASSWORD")` in your code.

---

## 🚦 Running the Application

```bash
streamlit run main.py
```

This will open the application in your default browser.

---

## 🧪 Usage

### Admin Workflow

1. Login with `admin@gmail.com`
2. Create events using the Admin Dashboard
3. View, update, or delete events listed under "Latest Events"

### User Workflow

1. Register or log in
2. Browse available events
3. Check-in via:

   * **Email**: Click "Check In" to receive QR via email
   * **On-Spot**: Scan QR with your webcam
4. View attendance history under "Checked-In Events"

---

## 📂 File Structure

```
├── auth.py                # Handles user authentication and hashing
├── checked_in_events.py   # Displays user event history
├── email_sender.py        # Sends QR codes via email
├── event-check-in-system-b3de0fb59c7e.json  # Firebase credentials (ignored)
├── events.py              # CRUD operations for events
├── home_admin.py          # Admin dashboard UI
├── home_user.py           # User dashboard UI
├── main.py                # Main Streamlit app controller
├── QR_Gen.py              # QR code generation logic
├── qr_scanner.py          # QR code scanner using webcam
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (not committed)
```

---

## 🔐 Security Notes

* Never commit Firebase credentials to version control
* Use environment variables for email credentials to avoid hardcoding
* Passwords are hashed using PBKDF2 for secure storage

---

## 📸 Recommendations

* Add screenshots/GIFs to visually showcase the UI and QR scanning
* Deploy to [Streamlit Cloud](https://streamlit.io/cloud) for easy access
* Test QR compatibility across various webcams and lighting conditions

---

## 🤝 Contributing

We welcome contributions! To get started:

```bash
git checkout -b feature/your-feature
```

1. Make your changes
2. Commit with a descriptive message
3. Push and open a pull request
4. Include screenshots or GIFs if relevant

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Happy check-ins!*
