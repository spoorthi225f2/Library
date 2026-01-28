from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import role_required
from database import (
    get_all_books, get_book_by_id, add_book, update_book, delete_book,
    get_borrowed_books_by_user
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    """Check if user is logged in and is an admin."""
    if 'user_id' not in session:
        flash('Please login to access this page', 'warning')
        return redirect(url_for('auth.login'))
    
    if session.get('role') != 'admin':
        flash('You do not have permission to access this page', 'error')
        return redirect(url_for('auth.login'))

@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard."""
    books = get_all_books()
    total_books = len(books)
    available_books = sum(1 for book in books if book['available'])
    issued_books = total_books - available_books
    
    context = {
        'total_books': total_books,
        'available_books': available_books,
        'issued_books': issued_books
    }
    
    return render_template('admin/dashboard.html', **context)

@admin_bp.route('/books')
def books():
    """View all books."""
    books = get_all_books()
    return render_template('admin/books.html', books=books)

@admin_bp.route('/books/add', methods=['GET', 'POST'])
def add_book_page():
    """Add a new book."""
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        
        if not title or not author:
            flash('Title and author are required', 'error')
            return redirect(url_for('admin.add_book_page'))
        
        add_book(title, author)
        flash('Book added successfully', 'success')
        return redirect(url_for('admin.books'))
    
    return render_template('admin/add_book.html')

@admin_bp.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book_page(book_id):
    """Edit a book."""
    book = get_book_by_id(book_id)
    
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('admin.books'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        
        if not title or not author:
            flash('Title and author are required', 'error')
            return redirect(url_for('admin.edit_book_page', book_id=book_id))
        
        update_book(book_id, title, author)
        flash('Book updated successfully', 'success')
        return redirect(url_for('admin.books'))
    
    return render_template('admin/edit_book.html', book=book)



@admin_bp.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book_page(book_id):
    """Delete a book."""
    book = get_book_by_id(book_id)
    
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('admin.books'))
    
    delete_book(book_id)
    flash('Book deleted successfully', 'success')
    return redirect(url_for('admin.books'))


