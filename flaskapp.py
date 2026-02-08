import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

# Use relative paths so this runs on GitHub/Local/AWS without changes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mydatabase.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Create uploads folder if it doesn't exist
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
    # Collect data form input
    data = (
        request.form['username'], request.form['password'],
        request.form['firstname'], request.form['lastname'],
        request.form['email'], request.form['address']
    )
    
    # Handle File Upload
    file = request.files['file']
    word_count = 0
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, 'Limerick.txt')
        file.save(file_path)
        # Calculate word count
        try:
            with open(file_path, 'r') as f:
                word_count = len(f.read().split())
        except Exception as e:
            print(f"Error reading file: {e}")

    # Save user to database
    conn = get_db_connection()
    conn.execute('INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)', data)
    conn.commit()
    conn.close()

    # Redirect to profile to display details
    return render_template('profile.html', user=request.form, word_count=word_count)

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
        return render_template('profile.html', user=user, word_count="N/A (Retrieved)")
    return "Invalid Login"

@app.route('/download')
def download():
    return send_from_directory(UPLOAD_FOLDER, 'Limerick.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
