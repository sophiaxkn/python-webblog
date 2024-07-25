import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, session
from flask import flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATABASE = 'blog.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT id, title, content FROM posts')
    posts = cur.fetchall()
    return render_template('index.html', posts=posts)


@app.route('/post/<int:post_id>')
def post(post_id):
    db = get_db()
    cur = db.execute('SELECT id, title, content FROM posts WHERE id = ?', (post_id,))
    post = cur.fetchone()
    return render_template('post.html', post=post)


@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db = get_db()
        db.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
        db.commit()
        flash('Post was successfully added!')
        return redirect(url_for('index'))
    return render_template('edit_post.html')


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.execute('SELECT id, title, content FROM posts WHERE id = ?', (post_id,))
    post = cur.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, post_id))
        db.commit()
        flash('Post was successfully updated!')
        return redirect(url_for('post', post_id=post_id))
    return render_template('edit_post.html', post=post)


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    db = get_db()
    db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    db.commit()
    flash('Post was successfully deleted!')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cur = db.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
        user = cur.fetchone()
        if user:
            session['logged_in'] = True
            flash('You were successfully logged in')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were successfully logged out')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
