# 👟 SoleStride — Shoe Store E-Commerce Website

SoleStride is a full-stack shoe-selling web application built with Python and Django. It provides an online shopping experience where users can explore shoes, view product details, manage their shopping cart, and proceed through the checkout flow.

## Features

- 🏠 Home page and shoe store catalogue
- 👟 Shoe product details and images
- 🛒 Shopping cart
- 🔐 User registration and login
- 👤 User profile
- 🛍️ Checkout and order success pages
- 📦 Order tracking interface
- ℹ️ About and customer helpline pages

*Note: Feature availability depends on the current implementation of the project.*

## Technologies Used

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Tools:** Git, GitHub, Visual Studio Code

## Project Structure

```text
chandru-AI-web/
├── manage.py
├── seed_data.py
├── solestride/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shop/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   └── migrations/
├── templates/
├── static/
├── media/
└── README.md
```

## Getting Started

### Prerequisites

- Python installed
- Git installed

### 1. Clone the repository

```bash
git clone https://github.com/chandru11kc/chandru-AI-web.git
cd chandru-AI-web
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

If a `requirements.txt` file is included:

```bash
pip install -r requirements.txt
```

Otherwise, install the project's required packages after checking its imports and configuration.

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Live Demo

Coming soon.

## Source Code

[View the GitHub Repository](https://github.com/chandru11kc/chandru-AI-web)

## Developer

**Chandru K.**

- GitHub: [chandru11kc](https://github.com/chandru11kc)
- LinkedIn: [Chandru K.](https://www.linkedin.com/in/chandru-k11092001/)

## Project Goal

To develop a full-stack e-commerce application and gain practical experience in Django, database management, frontend development, and web application deployment.