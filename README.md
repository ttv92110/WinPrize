🏆 WinPrize - Lucky Draw Platform
https://img.freepik.com/free-vector/winner-concept-illustration_114360-3091.jpg

<div align="center">
🎯 Turn 1 Rupee into Thousands!

https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi

https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white

https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black

https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white

https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white

https://img.shields.io/badge/Jinja-B41717?style=for-the-badge&logo=jinja&logoColor=white

</div>
📋 Table of Contents
Overview

✨ Features

📸 Screenshots

🏗️ Architecture

🚀 Live Demo

💻 Tech Stack

⚙️ Installation

📁 Project Structure

👥 User Roles

💳 Payment System

📧 Email Verification

🔐 Security Features

🚀 Deployment

🤝 Contributing

📄 License

📞 Contact

🎯 Overview
WinPrize is a modern, secure, and feature-rich lucky draw platform built with FastAPI. It allows users to participate in daily, weekly, and monthly draws with entries as low as Rs. 1 and win prizes up to Rs. 10,000! The platform includes complete user authentication, email verification, payment tracking, admin panel, and real-time draw management.

✨ Why WinPrize?
🚀 Fast & Responsive: Built with FastAPI for lightning-fast performance

🛡️ Secure: Email verification, secure payments, and admin approval system

🎨 Beautiful UI: Modern, responsive design with smooth animations

📱 Mobile Ready: Works perfectly on all devices

🔔 Real-time Updates: Live countdown timers and status updates

✨ Features
👤 User Features
✅ User Registration with Email Verification (6-digit PIN)

✅ Secure Login with Password

✅ Password Reset via Email

✅ View Active Lucky Draws

✅ Join Draws with Payment

✅ Track Payment Status (Pending/Approved/Rejected)

✅ View Draw Results and Winners

✅ Profile Management

👑 Admin Features
✅ Create/Edit/Delete Lucky Draws

✅ Set Draw Parameters (Entry Fee, Prize, Duration)

✅ Manage Draw Status (Open/Awaiting/Completed)

✅ View and Verify Payments

✅ Approve/Reject Payments with Notes

✅ Run Draws (Random or Manual Winner Selection)

✅ Reopen Completed Draws

✅ View All Users and Manage Status

💳 Payment System
✅ Multiple Bank Options (Easypaisa, Jazzcash, Allied Bank, Meezan Bank)

✅ Transaction ID Tracking

✅ Payment Status: Pending → Paid/Cancel

✅ Admin Approval with Notes

✅ Rejection Reasons Displayed to Users

✅ Payment History for Users

📧 Email Features
✅ Welcome Emails on Registration

✅ 6-digit PIN for Email Verification

✅ Password Reset Links (1-hour expiry)

✅ Payment Status Notifications

✅ Beautiful HTML Email Templates

🎲 Draw Management
✅ Daily, Weekly, Monthly Draws

✅ Automatic Status Updates (Open → Awaiting → Completed)

✅ Real-time Countdown Timers

✅ Participant Count Display

✅ Winner Announcements

✅ Privacy-Protected Winner Display (Masked Emails)

📸 Screenshots
🏠 Home Page
https://img.freepik.com/free-vector/winner-concept-illustration_114360-3091.jpg
Modern hero section with animated elements and platform stats

🎯 Active Draws
https://img.freepik.com/free-vector/lottery-winner-concept-illustration_114360-2251.jpg
Beautifully designed draw cards with live countdown timers

🔐 Login Modal
https://img.freepik.com/free-vector/login-concept-illustration_114360-739.jpg
Secure login with password visibility toggle

📝 Registration with Email Verification
https://img.freepik.com/free-vector/sign-up-concept-illustration_114360-7885.jpg
*Complete registration with 6-digit PIN verification*

✅ PIN Verification
https://img.freepik.com/free-vector/two-factor-authentication-illustration_23-2148624525.jpg
*Enter 6-digit PIN sent to email (expires in 20 minutes)*

💳 Payment Form
https://img.freepik.com/free-vector/online-payments-concept-illustration_114360-2651.jpg
Complete payment details with bank selection

📊 Payment Status Page
https://img.freepik.com/free-vector/payment-information-concept-illustration_114360-2782.jpg
Track all payments with status filters and rejection reasons

👑 Admin Panel
https://img.freepik.com/free-vector/admin-panel-concept-illustration_114360-2498.jpg
Complete draw and payment management

🏆 Winners Page
https://img.freepik.com/free-vector/winner-ceremony-concept-illustration_114360-2528.jpg
View all winners with masked emails for privacy

🏗️ Architecture
text
┌─────────────────────────────────────────────────────────────┐
│                     Client Browser                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  HTML    │  │   CSS    │  │  JavaScript │  │  AOS    │  │
│  │ Templates│  │  Styles  │  │   (ES6)   │  │Animation│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘

                              │
                              ▼

┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │  │   Models     │  │   Services   │     │
│  │ • Auth       │  │ • User       │  │ • FileDB     │     │
│  │ • Draws      │  │ • Draw       │  │ • DrawEngine │     │
│  │ • Admin      │  │ • Payment    │  │ • Email      │     │
│  │ • Payments   │  │ • Enrollment │  │              │     │
│  │ • Password   │  │ • Verification│  │              │     │
│  │ • Verification│  └──────────────┘  └──────────────┘     │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘

                              │
                              ▼

┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              JSON File Database                      │   │
│  │  • users.json          • lucky_draws.json           │   │
│  │  • user_draws.json      • payments.json             │   │
│  │  • password_resets.json  • email_verifications.json │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

🚀 Live Demo
🌐 Live URL: https://winprize.vercel.app

Test Credentials
Role	Email	Password
👑 Admin	admin@example.com	admin123
👤 User	user@example.com	user123
💻 Tech Stack
Backend
FastAPI - Modern Python web framework

Pydantic - Data validation

Jinja2 - Template engine

Python 3.9+ - Core programming language

Frontend
Bootstrap 5 - Responsive design

Font Awesome 6 - Icons

AOS - Scroll animations

JavaScript ES6 - Client-side logic

Email Services
SMTP - Email sending

aiosmtplib - Async SMTP client

Deployment
Vercel - Serverless deployment

Git - Version control

⚙️ Installation
Prerequisites
Python 3.9 or higher

Git

Gmail account (for email services)

Step-by-Step Installation
Clone the repository

bash
git clone https://github.com/yourusername/winprize.git
cd winprize
Create virtual environment

bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
Install dependencies

bash
pip install -r requirements.txt
Create .env file

env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
FROM_EMAIL=noreply@winprize.com
FROM_NAME=WinPrize Support

# App Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
Set up Gmail App Password

Go to your Google Account → Security

Enable 2-Factor Authentication

Go to App Passwords

Create new app password for "Mail" and "WinPrize"

Copy the 16-digit password to .env file

Run the application

bash
python run.py
Access the application

Open browser and go to http://127.0.0.1:8000

📁 Project Structure
text
WinPrize/

├── api/

│   ├── __init__.py

│   ├── main.py                 # FastAPI main application

│   ├── config.py                # Configuration settings

│   ├── startup.py               # Startup events

│   ├── models/

│   │   ├── __init__.py

│   │   ├── draw.py              # Lucky draw models

│   │   ├── enrollment.py        # Enrollment models

│   │   ├── payment.py           # Payment models

│   │   ├── user.py              # User models

│   │   └── verification.py      # Email verification models

│   ├── routes/

│   │   ├── __init__.py

│   │   ├── admin_routes.py      # Admin endpoints

│   │   ├── auth_routes.py       # Authentication endpoints

│   │   ├── draw_routes.py       # Draw endpoints

│   │   ├── payment_routes.py    # Payment endpoints

│   │   ├── password_routes.py   # Password reset endpoints

│   │   └── verification_routes.py # Email verification endpoints

│   ├── schemas/

│   │   ├── __init__.py

│   │   ├── draw_schema.py       # Draw Pydantic schemas

│   │   ├── enrollment_schema.py # Enrollment schemas

│   │   └── user_schema.py       # User schemas

│   ├── services/

│   │   ├── __init__.py

│   │   ├── draw_engine.py       # Draw logic

│   │   └── file_db.py           # JSON file database

│   └── utils/

│       ├── __init__.py

│       ├── auth.py              # Authentication utilities

│       └── email.py             # Email sending utilities

├── static/

│   ├── css/

│   │   └── style.css            # Main stylesheet

│   └── js/

│       ├── admin.js              # Admin panel JavaScript

│       ├── admin-payments.js     # Admin payment management

│       ├── app.js                # Main application JS

│       ├── auth.js               # Authentication JS

│       ├── draws.js              # Draws display JS

│       ├── main.js               # Additional JS

│       ├── payment.js            # Payment form JS

│       └── winner.js             # Winners display JS

├── templates/

│   ├── admin.html                # Admin panel

│   ├── confirm.html              # Payment confirmation

│   ├── index.html                # Home page

│   ├── login.html                # Login page

│   ├── payment-status.html       # Payment status page

│   ├── register.html             # Registration page

│   ├── reset_password.html       # Password reset page

│   ├── reset_password_error.html # Reset error page

│   ├── verify.html               # Email verification page

│   └── winner.html               # Winners page

├── data/                         # JSON database files

│   ├── users.json

│   ├── lucky_draws.json

│   ├── user_draws.json

│   ├── payments.json

│   ├── password_resets.json

│   └── email_verifications.json

├── .env                          # Environment variables

├── .gitignore                    # Git ignore file

├── requirements.txt              # Python dependencies

├── runtime.txt                   # Python version for Vercel

├── vercel.json                   # Vercel configuration

└── run.py                        # Local development server


👥 User Roles
Regular User 👤
Register with email verification

Login to account

View active lucky draws

Join draws by making payments

Track payment status

View draw results

See winners gallery

Reset forgotten password

Admin (Staff) 👑
All user features

Access admin panel

Create new lucky draws

Edit existing draws

Delete draws

Run draws (random/ manual)

Reopen completed draws

View pending payments

Approve/Reject payments with notes

Manage user status

View all users

💳 Payment System
Bank Accounts (Receiving)
Bank	Account Number	Holder Name
Easypaisa	+92340******32	Arshad Ali
Jazzcash	+92340******32	Arshad Ali
Allied Bank	******PA00100***********	Arshad Ali
Meezan Bank	******ZN00003***********	Arshad Ali
Payment Flow
text
User Selects Draw
        ↓
User Fills Payment Form
   • Holder Name
   • From Bank & Account
   • To Bank Selection
   • Transaction ID
        ↓
Payment Status: PENDING
        ↓
Admin Reviews Payment
   • Checks Transaction
   • Verifies Amount
        ↓
      ╱      ╲
    ╱          ╲
APPROVED      REJECTED
   ↓              ↓
Status: PAID    Status: CANCEL
   ↓              ↓
User Enrolled   User Removed
   ↓              ↓
Can Participate  Show Reason
📧 Email Verification
Registration Flow
text
User Signs Up
     ↓
Send 6-digit PIN
     ↓
PIN Expires in 20 mins
     ↓
User Enters PIN
     ↓
Max 5 Attempts
     ↓
PIN Verified → Account Created
     ↓
Send Welcome Email
Password Reset Flow
text
User Requests Reset
     ↓
Generate Unique Token
     ↓
Token Expires in 1 Hour
     ↓
Send Reset Link via Email
     ↓
User Clicks Link
     ↓
Enter New Password
     ↓
Token Marked as Used
     ↓
Password Updated
🔐 Security Features
Authentication
✅ Email verification required

✅ 6-digit PIN (expires in 20 mins)

✅ Password reset with 1-hour expiry

✅ One-time use tokens

✅ Max 5 PIN attempts

Payment Security
✅ Transaction ID tracking

✅ Admin approval required

✅ Rejection reasons stored

✅ User removed on rejection

✅ Payment history maintained

Privacy
✅ Emails masked in winners list

✅ Account numbers partially hidden

✅ No password exposure

✅ Secure session management

Admin Security
✅ Staff status required

✅ All admin actions logged

✅ No unauthorized access

✅ Session validation

🚀 Deployment
Deploy to Vercel
Install Vercel CLI

bash
npm i -g vercel
Login to Vercel

bash
vercel login
Deploy

bash
vercel --prod
Environment Variables on Vercel
Set these in Vercel dashboard:

SMTP_HOST

SMTP_PORT

SMTP_USER

SMTP_PASSWORD

FROM_EMAIL

FROM_NAME

SECRET_KEY

vercel.json Configuration
json
{
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    },
    {
      "src": "static/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/api/main.py"
    }
  ]
}
🤝 Contributing
We welcome contributions! Here's how you can help:

Fork the repository

Create a feature branch

bash
git checkout -b feature/AmazingFeature
Commit your changes

bash
git commit -m 'Add some AmazingFeature'
Push to the branch

bash
git push origin feature/AmazingFeature
Open a Pull Request

Development Guidelines
Follow PEP 8 style guide

Add comments for complex logic

Update documentation

Test thoroughly

Write meaningful commit messages

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

text
MIT License

Copyright (c) 2026 Arshad Ali

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
📞 Contact
Arshad Ali - Lead Developer

📧 Email: arsk92110@gmail.com

📱 Phone: +92 240 1710232

📍 Location: Lahore, Pakistan

💼 GitHub: @arsk92110 or @ttv92110

Support
For support, email ttv92110@gmail.com or create an issue on GitHub.

🙏 Acknowledgments
FastAPI for the amazing framework

Bootstrap for the responsive design

Font Awesome for the beautiful icons

AOS for scroll animations

All contributors and users of WinPrize 

<div align="center">
⭐ If you like this project, please give it a star on GitHub! ⭐
Made with ❤️ in Pakistan

</div>