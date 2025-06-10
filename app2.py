# app.py - Simple Python app with one SQL injection vulnerability
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, username, email) VALUES (1, 'admin', 'admin@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, email) VALUES (2, 'user', 'user@example.com')")
    conn.commit()
    conn.close()

# VULNERABILITY: SQL Injection
@app.route('/user/<user_id>')
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # BAD: Direct string formatting - SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    
    if result:
        return jsonify({
            'id': result[0][0],
            'username': result[0][1], 
            'email': result[0][2]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the user API', 'endpoint': '/user/<id>'})

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='127.0.0.1', port=5000)