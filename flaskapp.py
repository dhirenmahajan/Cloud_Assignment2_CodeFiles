import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

# Use relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mydatabase.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    # Collect data (No file handling here anymore)
    data = (
        request.form['username'], request.form['password'],
        request.form['firstname'], request.form['lastname'],
        request.form['email'], request.form['address']
    )
    
    # Save user to database
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)', data)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

    # Redirect to profile (Word count is None initially)
    return render_template('profile.html', user=request.form, word_count=None)

@app.route('/upload', methods=['POST'])
def upload():
    username = request.form['username']
    file = request.files['file']
    word_count = "N/A"
    
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, 'Limerick.txt')
        file.save(file_path)
        try:
            with open(file_path, 'r') as f:
                word_count = len(f.read().split())
        except Exception as e:
            print(f"Error reading file: {e}")

    # Re-fetch user details to render the profile page correctly
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    return render_template('profile.html', user=user, word_count=word_count)

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    if user:
        # Check if file exists to display current count
        word_count = "N/A (Upload to Calculate)"
        file_path = os.path.join(UPLOAD_FOLDER, 'Limerick.txt')
        if os.path.exists(file_path):
             with open(file_path, 'r') as f:
                word_count = len(f.read().split())
                
        return render_template('profile.html', user=user, word_count=word_count)
    return "Invalid Login"

@app.route('/download')
def download():
    return send_from_directory(UPLOAD_FOLDER, 'Limerick.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
