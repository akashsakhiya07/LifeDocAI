# LifeDocAI 🧠📄

A smart Flask-based web app that allows users to submit their personal details via a form, automatically generates a filled PDF form using that data, stores everything in a database, and sends the completed form via email.

---

## 🚀 Features

- 📋 User Form Submission (Name, Email, Phone, DOB, Aadhaar, Photo)
- 🧾 Auto PDF generation (using a template)
- 📧 Emails sent to both User and Admin with attached PDF
- 🔒 Admin Login for viewing all submissions
- 🖼️ User photo uploads with preview
- 📤 CSV export for all users
- 📝 Edit/Delete functionality for each user
- 🔍 Search users by Name, Email or Phone
- 🧑‍💻 Admin Dashboard with PDF download links

---

## 🛠 Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (via SQLAlchemy)
- **PDF Handling**: pdfrw
- **Email**: Flask-Mail
- **Frontend**: HTML + CSS + Jinja2

---


## ⚙️ Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/LifeDocAI.git
   cd LifeDocAI

   .

📂 Folder Structure

LifeDocAI/
│
├── app.py                # Main Flask app
├── users.db              # SQLite DB (auto-created)
├── filled_forms/         # Generated PDF files
├── static/
│   └── uploads/          # Uploaded user photos
├── templates/
│   ├── index.html        # User form
│   ├── success.html      # Confirmation page
│   ├── admin_login.html  # Admin login
│   ├── view_users.html   # Admin dashboard
│   └── edit_user.html    # Edit form

