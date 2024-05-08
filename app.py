from flask import Flask, render_template, request, redirect, jsonify,flash
import sqlite3
app = Flask(__name__)
def connect_db():
    return sqlite3.connect('library.db')
def init_db():
    with sqlite3.connect('library.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS books
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         title TEXT, 
                         author TEXT, 
                         year INTEGER)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS borrowed_books
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         borrower_name TEXT,
                         author TEXT,
                         year TEXT,
                         book_name TEXT,
                         borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
@app.route('/')
def home():
    with sqlite3.connect('library.db') as conn:
        books = conn.execute('SELECT * FROM books').fetchall()
    return render_template('lib.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = int(request.form['year'])
        with sqlite3.connect('library.db') as conn:
            conn.execute('INSERT INTO books (title, author, year) VALUES (?, ?, ?)', (title, author, year))
    return render_template('add.html')

@app.route('/display', methods=['GET', 'POST'])
def display_books():
    if request.method == 'POST':
        search_query = request.form['search_query']
        with sqlite3.connect('library.db') as conn:
            books = conn.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ?', (f'%{search_query}%', f'%{search_query}%')).fetchall()
        return render_template('display.html', bookings=books)
    else:
        with sqlite3.connect('library.db') as conn:
            books = conn.execute('SELECT * FROM books').fetchall()
        return render_template('display.html', bookings=books)

@app.route('/borrowed_display')
def borrowed_display():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, book_name, author, year, borrower_name, borrow_date FROM borrowed_books")
    borrowed_books = cursor.fetchall()
    conn.close()
    return render_template('borrowed_display.html', borrowed_books=borrowed_books)

@app.route('/update', methods=['GET', 'POST'])
def update_booking():
    if request.method == 'POST':
        book_id = int(request.form['id'])
        title = request.form['title']
        author = request.form['author']
        year = int(request.form['year'])
        with sqlite3.connect('library.db') as conn:
            conn.execute('UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?', (title, author, year, book_id))
        return redirect('/display')
    else:
        book_id = request.args.get('id')
        with sqlite3.connect('library.db') as conn:
            booking = conn.execute("SELECT title, author, year FROM books WHERE id = ?", (book_id,)).fetchone()
        return render_template('update.html', booking=booking,book_id=book_id)
    
@app.route('/delete', methods=['POST'])
def delete_booking():
    book_id = int(request.form['id'])
    with sqlite3.connect('library.db') as conn:
        conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    return redirect('/update_display')

@app.route('/update_display')
def bookings1():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id,title,author,year FROM books")
    bookings = cursor.fetchall()
    conn.close()
    return render_template('update_display.html', bookings=bookings)

@app.route('/search', methods=['GET'])
def search_books():
    search_query = request.args.get('query', '')
    with sqlite3.connect('library.db') as conn:
        results = conn.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ?', (f'%{search_query}%', f'%{search_query}%')).fetchall()
    return jsonify(results)

@app.route('/borrow', methods=['GET', 'POST'])
def borrow_book():
    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        borrower_name = request.form['borrower_name']
        with sqlite3.connect('library.db') as conn:
            book_details = conn.execute('SELECT title, author, year FROM books WHERE id = ?', (book_id,)).fetchone()
            if book_details:
                conn.execute('INSERT INTO borrowed_books (borrower_name, book_name, author, year) VALUES (?, ?, ?, ?)', 
                             (borrower_name, book_details[0], book_details[1], book_details[2]))
                conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
                return redirect('/borrowed_display')
    else:
        book_id = request.args.get('id')
        if book_id is not None:
            with sqlite3.connect('library.db') as conn:
                book_details = conn.execute('SELECT title, author, year FROM books WHERE id = ?', (book_id,)).fetchone()
            return render_template('borrow.html', book_details=book_details,book_id=book_id)

@app.route('/return_book', methods=['POST'])
def return_book():
    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        with sqlite3.connect('library.db') as conn:
            borrowed_book = conn.execute('SELECT * FROM borrowed_books WHERE id = ?', (book_id,)).fetchone()
            if borrowed_book:
                conn.execute('INSERT INTO books (title, author, year) VALUES (?, ?, ?)', 
                             (borrowed_book[4], borrowed_book[2], borrowed_book[3]))
                conn.execute('DELETE FROM borrowed_books WHERE id = ?', (book_id,))
                return redirect('/borrowed_display')

if __name__ == '__main__':
    init_db()
    app.run(debug=True,port=9001)