from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import role_required, login_required
from database import (
    get_available_books, borrow_book, return_book, get_book_by_id,
    get_active_borrowed_books_by_user, get_borrowed_books_by_user,
    delete_book, get_all_books
)

member_bp = Blueprint('member', __name__, url_prefix='/member')

@member_bp.before_request
def check_member():
    """Check if user is logged in and is a member."""
    if 'user_id' not in session:
        flash('Please login to access this page', 'warning')
        return redirect(url_for('auth.login'))
    
    if session.get('role') != 'member':
        flash('You do not have permission to access this page', 'error')
        return redirect(url_for('auth.login'))

@member_bp.route('/dashboard')
def dashboard():
    """Member dashboard."""
    user_id = session.get('user_id')
    borrowed_books = get_active_borrowed_books_by_user(user_id)
    available_books_count = len(get_available_books())
    
    context = {
        'borrowed_books_count': len(borrowed_books),
        'available_books_count': available_books_count
    }
    
    return render_template('member/dashboard.html', **context)

@member_bp.route('/books', methods=['GET'])
def books():
    """View available books."""
    books = get_available_books()
    user_id = session.get('user_id')
    borrowed_books = get_active_borrowed_books_by_user(user_id)
    borrowed_book_ids = [b['id'] for b in borrowed_books]
    
    return render_template('member/books.html', books=books, borrowed_book_ids=borrowed_book_ids)

@member_bp.route('/borrow/<int:book_id>', methods=['POST'])
def borrow(book_id):
    """Borrow a book."""
    user_id = session.get('user_id')
    book = get_book_by_id(book_id)
    
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('member.books'))
    
    if not book['available']:
        flash('Book is not available', 'error')
        return redirect(url_for('member.books'))
    
    if borrow_book(user_id, book_id):
        flash(f'You have borrowed "{book["title"]}"', 'success')
    else:
        flash('Failed to borrow book', 'error')
    
    return redirect(url_for('member.books'))

@member_bp.route('/return/<int:book_id>', methods=['POST'])
def return_book_page(book_id):
    """Return a book."""
    user_id = session.get('user_id')
    book = get_book_by_id(book_id)
    
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('member.books'))
    
    if return_book(user_id, book_id):
        flash(f'You have returned "{book["title"]}"', 'success')
    else:
        flash('Failed to return book', 'error')
    
    return redirect(url_for('member.books'))

@member_bp.route('/delete/<int:book_id>', methods=['POST'])
def delete_book_page(book_id):
    """Delete a book."""
    book = get_book_by_id(book_id)
    
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('member.books'))
    
    if delete_book(book_id):
        flash(f'Book "{book["title"]}" deleted successfully', 'success')
    else:
        flash('Failed to delete book', 'error')
    return redirect(url_for('member.books'))


