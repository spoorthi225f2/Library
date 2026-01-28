# Library Management Web Application

A secure, server-rendered web application for library management built with Flask, implementing JWT-based authentication and role-based authorization.

## Table of Contents
- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Database Schema](#database-schema)
- [Authentication & Authorization](#authentication--authorization)
- [User Roles](#user-roles)
- [API/Routes](#routes)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [Security Features](#security-features)
- [Default Credentials](#default-credentials)

## Overview

The Library Management Web Application is a server-rendered Flask application designed to manage library operations with two distinct user roles:

- **Admin**: Full control over the library catalog (add, edit, delete books) and access to borrowing history
- **Member**: Browse and borrow books, manage personal borrowing history

The application implements:
- Secure JWT-based authentication
- Role-based access control (RBAC)
- SQLite3 persistent storage
- Session-based authorization
- Password hashing with bcrypt
- Server-rendered HTML templates with Jinja2

## Technology Stack

- **Backend**: Flask 2.3.3
- **Authentication**: Flask-JWT-Extended 4.5.2
- **Password Hashing**: bcrypt 4.0.1
- **Database**: SQLite3 (raw SQL)
- **Templating**: Jinja2
- **Frontend**: HTML5 + CSS3 (no frontend frameworks)

## Features

### Authentication
- User registration with password validation (minimum 6 characters)
- Secure login with hashed password verification
- JWT token generation and session management
- Logout functionality
- Protected routes requiring authentication

### Authorization
- Admin-only pages with role enforcement
- Member-only pages with role enforcement
- Backend authorization checks (not just UI-level)
- Flash messages for unauthorized access attempts

### Library Management (Admin)
- Dashboard with statistics (total, available, issued books)
- Add new books
- Edit existing book information
- Delete books
- View all books with availability status
- View complete borrow history for all users

### Member Functions
- Dashboard showing borrowed count and available books
- Browse available books
- Borrow books
- Return books
- View personal borrowing history

### Database
- SQLite3 with three main tables: users, books, borrowed_books
- Foreign key relationships
- Timestamp tracking for borrow/return dates
- Efficient queries with proper indexing

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone/Download the Project
```bash
cd library-web-app
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will be available at: **http://localhost:5000**

### Step 5: Database Initialization
The database is automatically initialized on first run with:
- Default admin user (username: `admin`, password: `admin123`)
- 5 sample books

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'member'))
);
```

### Books Table
```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    available INTEGER NOT NULL DEFAULT 1
);
```

### Borrowed Books Table
```sql
CREATE TABLE borrowed_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrowed_at TIMESTAMP NOT NULL,
    returned_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

## Authentication & Authorization

### Authentication Flow

1. **Registration**: New users register with username and password
   - Passwords are hashed using bcrypt
   - Username must be unique
   - Users register as members by default

2. **Login**: Users authenticate with credentials
   - Username and password validated
   - JWT token created with user metadata (id, username, role)
   - Token stored in Flask session
   - User redirected to appropriate dashboard based on role

3. **Session Management**: User state maintained in session
   - Session variables: `user_id`, `username`, `role`, `access_token`
   - All protected routes check session for authentication
   - Logout clears session

### Authorization Mechanism

**Backend Checks**:
- Every protected route validates user authentication in `@before_request` hooks
- Role-based access control via `@role_required` decorator
- Unauthorized users receive 403 or redirect to login

**Security Features**:
- HTTP-only session storage (cookies)
- Backend verification on every request
- No reliance on client-side security
- Flash messages for failed authorization attempts

## User Roles

### Admin Role
**Permissions**:
- Login to admin dashboard
- View all books (available and issued)
- Add new books
- Edit book information
- Delete books
- View system-wide borrow history

**Protected Routes**:
- `/admin/dashboard` - Admin dashboard
- `/admin/books` - All books
- `/admin/books/add` - Add book form
- `/admin/books/edit/<id>` - Edit book form
- `/admin/books/delete/<id>` - Delete book (POST)
- `/admin/borrow-history` - Full borrow history

### Member Role
**Permissions**:
- Login to member dashboard
- Browse available books only
- Borrow books
- Return books
- View personal borrow history

**Protected Routes**:
- `/member/dashboard` - Member dashboard
- `/member/books` - Available books
- `/member/borrow/<id>` - Borrow book (POST)
- `/member/return/<id>` - Return book (POST)
- `/member/borrow-history` - Personal history

## Routes

### Public Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/login` | GET, POST | Login page |
| `/register` | GET, POST | User registration |
| `/logout` | GET | Logout and clear session |

### Admin Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/admin/dashboard` | GET | Admin dashboard with stats |
| `/admin/books` | GET | View all books |
| `/admin/books/add` | GET, POST | Add new book |
| `/admin/books/edit/<id>` | GET, POST | Edit book |
| `/admin/books/delete/<id>` | POST | Delete book |
| `/admin/borrow-history` | GET | View all borrow history |

### Member Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/member/dashboard` | GET | Member dashboard |
| `/member/books` | GET | Available books |
| `/member/borrow/<id>` | POST | Borrow a book |
| `/member/return/<id>` | POST | Return a book |
| `/member/borrow-history` | GET | Personal borrow history |

## Project Structure

```
library-web-app/
├── app.py                 # Main Flask application
├── auth.py               # Authentication logic and decorators
├── admin.py              # Admin routes
├── member.py             # Member routes
├── database.py           # Database operations and helpers
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/
│   ├── base.html        # Base template with navigation
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── admin/
│   │   ├── dashboard.html       # Admin dashboard
│   │   ├── books.html           # Books list
│   └── member/
│       ├── dashboard.html       # Member dashboard
│       ├── books.html           # Available books
└── static/
    └── style.css        # CSS styling
```

## Usage Guide

### Step 1: Initial Login
1. Navigate to http://localhost:5000/login
2. Use default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`

### Step 2: Admin - Managing Books
1. Click "Books" in navigation
2. **Add Book**: Click "Add New Book" button
3. **Edit Book**: Click "Edit" on any book row
4. **Delete Book**: Click "Delete" on any book row

### Step 3: Admin - View History
1. Click "Borrow History" to see all member borrowing activities
2. View who borrowed what, when, and if it's been returned

### Step 4: Member - Register
1. Click "Register" on login page
2. Enter username and password (min 6 characters)
3. Login with new credentials

### Step 5: Member - Borrow Books
1. Go to "Available Books"
2. Click "Borrow" on desired book
3. Book appears in member's borrowed list

### Step 6: Member - Return Books
1. Go to "Available Books"
2. Books you borrowed show a "Return" button
3. Click "Return" to return the book

### Step 7: Member - View History
1. Click "My Books" in navigation
2. See all borrowed books (active and returned)
3. Check borrow and return dates

## Security Features

### Password Security
- Bcrypt hashing with salt generation
- Minimum 6-character password requirement
- Passwords never stored in plain text

### Session Security
- Session data stored server-side
- User ID tracked in session
- Logout clears all session data
- No sensitive data in JWT claims for display

### Authorization
- Backend validation on every protected route
- Role enforcement before processing requests
- Flash messages indicate unauthorized attempts
- Proper HTTP status codes (403 for forbidden)

### Database Security
- Parameterized queries prevent SQL injection
- Foreign key constraints maintain data integrity
- Timestamps track all borrow/return activities

### CSRF Protection
- Forms use Flask sessions
- No explicit CSRF tokens needed for server-rendered forms

## Default Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`

**Note**: Change these credentials in production!

## Production Deployment Notes

Before deploying to production:

1. **Change Secret Keys**:
   ```python
   app.config['SECRET_KEY'] = 'generate-new-secure-random-key'
   app.config['JWT_SECRET_KEY'] = 'generate-new-secure-random-key'
   ```

2. **Set DEBUG Mode**:
   ```python
   app.run(debug=False)  # Never use debug=True in production
   ```

3. **Use Production WSGI Server**:
   - Use Gunicorn, uWSGI, or similar
   - Not Flask development server

4. **Secure Database**:
   - Use proper file permissions on library.db
   - Consider moving to production database (PostgreSQL, MySQL)

5. **HTTPS**:
   - Always use HTTPS in production
   - Use SSL/TLS certificates

6. **Environment Variables**:
   - Store secrets in environment variables
   - Use .env file (not committed to version control)

## Troubleshooting

### Database Already Exists
If you want to reset the database, delete `library.db` and restart the application.

### Login Issues
- Ensure username and password are correct
- Check that user role is set correctly in database
- Verify session is enabled in Flask config

### Permission Denied Errors
- Confirm you're logged in
- Check your user role matches the required role for the page
- Admins cannot access member pages and vice versa

## API Response Codes

- **200**: Success
- **302**: Redirect (after successful login/logout)
- **403**: Forbidden (unauthorized role access)
- **404**: Page not found
- **500**: Server error

## License

This project is created for educational purposes.

## Support

For issues or questions, ensure:
1. All dependencies are installed correctly
2. Python version is 3.7 or higher
3. Virtual environment is activated
4. Database file has proper read/write permissions
