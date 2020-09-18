from flask import Flask, redirect, render_template, request, url_for, flash
from data import Books
from flask_mysqldb import MySQL
from wtforms import Form, StringField, validators, IntegerField, SelectField
from datetime import timedelta, date

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'şifreyok'
app.config['MYSQL_DB'] = 'myLibrary'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
Books = Books()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/books', methods=['GET', 'POST'])
def books():
    search = BookSearchForm(request.form)
    if request.method == 'POST':
        choice = search.select.data
        keyword = search.keyword.data
        print("choice is:", choice)
        print("keyword is:", keyword)
        return redirect(url_for('search_results', choice=choice, keyword=keyword))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM BOOKS")
    books_list = cur.fetchall()
    return render_template('books.html', books=books_list, form=search)


@app.route('/users')
def users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM USERS")
    user_list = cur.fetchall()
    return render_template('users.html', users=user_list)


@app.route('/borrowed')
def borrowed():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM BORROWED")
    borrowed_list = cur.fetchall()
    return render_template('borrowed.html', borrowed=borrowed_list)


@app.route('/search_results/<string:choice>/<string:keyword>')
def search_results(choice, keyword):
    cur = mysql.connection.cursor()
    if choice == 'isbn':
        cur.execute("SELECT * FROM books where isbn = {0}".format(keyword))
    elif choice == 'title' or 'author':
        cur.execute("SELECT * FROM books where {0} like \"%{1}%\"".format(choice, keyword))
    else:
        flash('No results found!', 'danger')
        return redirect('/')
    all_books = cur.fetchall()
    if not all_books:
        flash('No results found!', 'danger')
        return redirect('/books')
    return render_template('search_results.html', books=all_books)


class BookSearchForm(Form):
    choices = [('isbn', 'isbn'),
               ('title', 'title'),
               ('author', 'author')]
    select = SelectField('Search for book:', choices=choices)
    keyword = StringField('Keyword', [validators.Length(min=1, max=64)])


class BookForm(Form):
    title = StringField('title', [validators.Length(min=1, max=100)])
    author = StringField('author', [validators.Length(min=1, max=50)])


class UserForm(Form):
    isbn = IntegerField('isbn')
    tc = IntegerField('tc')


@app.route('/delete_book/<string:isbn>', methods=['POST'])
def delete_book(isbn):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM books WHERE isbn = %s", [isbn])

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('Book Deleted', 'success')

    return redirect(url_for('books'))


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = BookForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        author = form.author.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO books(title, author) VALUES(%s, %s)", (title, author))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Book Created', 'success')
        return redirect(url_for('books'))

    return render_template('add_book.html', form=form)


@app.route('/borrow_book', methods=['GET', 'POST'])
def borrow_book():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        isbn = form.isbn.data
        tc = form.tc.data
        if len(str(tc)) != 11:
            flash('TC number is not valid.', 'danger')
            return redirect(url_for('borrow_book'))

        due_date = date.today() + timedelta(days=14)

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("select distinct isbn from books")
        isbn_books = cur.fetchall()
        isbn_books = list(isbn_books)

        cur.execute("select distinct tc from borrowed")
        tc_numbers = cur.fetchall()
        tc_numbers = list(tc_numbers)
        cur.execute("select total_books from users where tc=" + str(tc))
        book_num = cur.fetchone()
        if book_num is None:
            total_book_num = 0
        else:
            total_book_num = book_num["total_books"]
        cur.execute("select distinct isbn from borrowed")
        isbn_borrowed = cur.fetchall()
        isbn_borrowed = list(isbn_borrowed)

        if {'isbn': isbn} not in isbn_borrowed:
            if {'isbn': isbn} in isbn_books:
                if total_book_num < 8:
                    cur.execute("INSERT INTO borrowed(isbn, tc, due_date) VALUES(%s, %s, %s)", (isbn, tc, due_date))
                    if {'tc': tc} not in tc_numbers:
                        cur.execute("INSERT INTO users(tc) VALUES({0})".format(tc))
                    else:
                        cur.execute("UPDATE users SET total_books = total_books + 1 WHERE tc={0}".format(tc))
                    mysql.connection.commit()
                    flash('Book is borrowed', 'success')
                else:
                    flash('User reached the total borrowed books limit!', 'danger')
            else:
                flash("Book's isbn not found!", 'danger')
        else:
            flash('Book is already borrowed by another user!', 'danger')

        # Close connection
        cur.close()
        return redirect(url_for('books'))

    return render_template('borrow_book.html', form=form)


if __name__ == '__main__':
    app.secret_key = "secret123"
    app.run(debug=True)
