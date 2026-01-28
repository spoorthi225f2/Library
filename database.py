import sqlite3
import os
from datetime import datetime
import bcrypt

DB_PATH = 'library.db'

def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    if os.path.exists(DB_PATH):
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'member'))
        )
    ''')
    
    # Create books table
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        )
    ''')
    
    # Create borrowed_books table
    cursor.execute('''
        CREATE TABLE borrowed_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrowed_at TIMESTAMP NOT NULL,
            returned_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_data():
    """Seed initial data including default admin user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if admin already exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone():
        conn.close()
        return
    
    # Hash admin password
    admin_password = bcrypt.hashpw(b'admin123', bcrypt.gensalt())
    
    # Insert default admin
    cursor.execute('''
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
    ''', ('admin', admin_password, 'admin'))
    
    # Insert some sample books (Indian fictional titles/authors)
    sample_books = [
        ('The Midnight Kite of Varanasi', 'Arunika Senapati'),
        ('Whispers of the Monsoon', 'Rohan Mehra'),
        ('The Last Stepwell', 'Anaya Iyer'),
        ('Tales of the Banyan Court', 'Devansh Rathore'),
        ('The River\'s Secret of Kaveri', 'Priyanka Deshpande'),
        ('Marigold and Ashes', 'Kavya Nair'),
        ('The Glass Lantern of Jodhpur', 'Samarjeet Bhatia'),
        ('Echoes from the Spice Market', 'Mehul Joshi'),
    ]
    
    for title, author in sample_books:
        cursor.execute('''
            INSERT INTO books (title, author, available)
            VALUES (?, ?, ?)
        ''', (title, author, 1))
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def get_user_by_username(username):
    """Get user by username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Get user by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password, role='member'):
    """Create a new user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', (username, hashed_password, role))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_all_books():
    """Get all books."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    conn.close()
    return books

def get_available_books():
    """Get only available books."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE available = 1')
    books = cursor.fetchall()
    conn.close()
    return books

def get_book_by_id(book_id):
    """Get book by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    conn.close()
    return book

def add_book(title, author):
    """Add a new book."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (title, author, available)
        VALUES (?, ?, 1)
    ''', (title, author))
    conn.commit()
    book_id = cursor.lastrowid
    conn.close()
    return book_id

def update_book(book_id, title, author):
    """Update book details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE books
        SET title = ?, author = ?
        WHERE id = ?
    ''', (title, author, book_id))
    conn.commit()
    conn.close()

def delete_book(book_id):
    """Delete a book."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete from borrowed_books first
    cursor.execute('DELETE FROM borrowed_books WHERE book_id = ?', (book_id,))
    
    # Delete the book
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

def borrow_book(user_id, book_id):
    """Record a book borrow transaction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if book is available
    cursor.execute('SELECT available FROM books WHERE id = ?', (book_id,))
    result = cursor.fetchone()
    if not result or not result['available']:
        conn.close()
        return False
    
    # Record the borrow
    cursor.execute('''
        INSERT INTO borrowed_books (user_id, book_id, borrowed_at)
        VALUES (?, ?, ?)
    ''', (user_id, book_id, datetime.now()))
    
    # Update book availability
    cursor.execute('UPDATE books SET available = 0 WHERE id = ?', (book_id,))
    
    conn.commit()
    conn.close()
    return True

def return_book(user_id, book_id):
    """Record a book return transaction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find the active borrow record
    cursor.execute('''
        SELECT id FROM borrowed_books
        WHERE user_id = ? AND book_id = ? AND returned_at IS NULL
    ''', (user_id, book_id))
    borrow = cursor.fetchone()
    
    if not borrow:
        conn.close()
        return False
    
    # Update the borrow record
    cursor.execute('''
        UPDATE borrowed_books
        SET returned_at = ?
        WHERE id = ?
    ''', (datetime.now(), borrow['id']))
    
    # Update book availability
    cursor.execute('UPDATE books SET available = 1 WHERE id = ?', (book_id,))
    
    conn.commit()
    conn.close()
    return True

def get_borrowed_books_by_user(user_id):
    """Get all borrowed books by a user (active and returned)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, b.title, b.author, bb.borrowed_at, bb.returned_at
        FROM borrowed_books bb
        JOIN books b ON bb.book_id = b.id
        WHERE bb.user_id = ?
        ORDER BY bb.borrowed_at DESC
    ''', (user_id,))
    borrowed = cursor.fetchall()
    conn.close()
    return borrowed

def get_active_borrowed_books_by_user(user_id):
    """Get active borrowed books by a user (not returned)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, b.title, b.author, bb.borrowed_at
        FROM borrowed_books bb
        JOIN books b ON bb.book_id = b.id
        WHERE bb.user_id = ? AND bb.returned_at IS NULL
        ORDER BY bb.borrowed_at DESC
    ''', (user_id,))
    borrowed = cursor.fetchall()
    conn.close()
    return borrowed
