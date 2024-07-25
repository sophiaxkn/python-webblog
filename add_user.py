import sqlite3

DATABASE = 'blog.db'


def add_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    add_user('admin', 'password123')
    print("User added successfully!")
