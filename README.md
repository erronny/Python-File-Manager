# Python-File-Manager

# 🔥 Web-Based File Manager (cPanel Style) – Flask

A powerful **web-based file manager** built using Python Flask, inspired by cPanel.
It allows you to manage your server files directly from the browser with advanced features like editing, uploading, compressing, and more.

---

## ✨ Features

* 📂 File & Folder Management (Create, Delete, Rename)
* ⬆️ File Upload
* ⬇️ File Download
* 🗑 Trash System (Safe Delete)
* 🔁 Back / Forward Navigation (History)
* 🔍 Search Files
* 📝 Built-in Code Editor (Monaco Editor - VS Code style)
* 📦 Compress (ZIP) & Extract Files
* 📋 Copy & Move Files
* 🧠 Bulk Actions (Delete, Download, Compress)
* 🖱 Right-click Context Menu (Editor)
* 🔐 Safe Path Handling (Prevents unauthorized access)

---

## 🛠 Tech Stack

* Python (Flask)
* HTML + Tailwind CSS
* JavaScript
* Monaco Editor (VS Code Editor)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/erronny/Python-File-Manager.git
cd Python-File-Manager
```

### 2. Install Dependencies

```bash
pip install flask
```

### 3. Run the Server

```bash
python file_manager.py
```

### 4. Open in Browser

```
http://localhost:5000
```

---

## 📁 Project Structure

```
file-manager/
│
├── file_organizer.py   # Main Flask App
├── .trash/             # Trash Folder
└── README.md
```

---

## ⚠️ Important Notes

* This project is designed for **learning and personal use**
* Do NOT expose directly to the public internet without:

  * Authentication
  * Security improvements
* Always run inside a secure server environment

---

## 🔐 Security Warning

This app allows full file system access within the defined base directory.
Make sure to:

* Restrict access (use login system)
* Run behind a firewall or private server
* Avoid running as root user

---

## 🚀 Future Improvements

* 🔑 Login & Authentication System
* 📁 Drag & Drop Upload
* 🧠 File Preview (Images, PDFs)
* 🌐 Multi-user support
* ⚡ API-based architecture (React frontend)

---

## 🤝 Contributing

Feel free to fork this repo and improve it!
Pull requests are welcome 🚀

---

## 📜 License

This project is open-source and free to use.

---

## 👨‍💻 Author

Made with ❤️ by codewithronny.com and techorbeet.com
