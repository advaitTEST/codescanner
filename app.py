# app.py - Intentionally vulnerable Python code for CodeQL testing
from flask import Flask, request, jsonify
import sqlite3
import subprocess
import os
import pickle

app = Flask(__name__)

# VULNERABILITY 1: SQL Injection
@app.route('/user/<user_id>')
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # BAD: Direct string formatting - SQL injection risk
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return jsonify(result)

# VULNERABILITY 2: Path Traversal
@app.route('/file/<filename>')
def get_file(filename):
    # BAD: No path validation - directory traversal risk
    file_path = f"./uploads/{filename}"
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "File not found", 404

# VULNERABILITY 3: Command Injection
@app.route('/ping', methods=['POST'])
def ping_host():
    data = request.get_json()
    host = data.get('host', '')
    # BAD: Unsanitized user input in command - command injection risk
    command = f"ping -c 4 {host}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return jsonify({
        'stdout': result.stdout,
        'stderr': result.stderr
    })

# VULNERABILITY 4: Hardcoded credentials
SECRET_KEY = "hardcoded_secret_123"
DATABASE_PASSWORD = "admin123"
API_TOKEN = "abc123def456ghi789"

@app.route('/admin')
def admin_panel():
    token = request.headers.get('Authorization')
    # BAD: Hardcoded secret comparison
    if token == API_TOKEN:
        return jsonify({'message': 'Welcome admin', 'secret': SECRET_KEY})
    return "Unauthorized", 401

# VULNERABILITY 5: Unsafe deserialization
@app.route('/load-data', methods=['POST'])
def load_data():
    data = request.data
    # BAD: Unsafe pickle deserialization - code execution risk
    try:
        obj = pickle.loads(data)
        return jsonify({'loaded': str(obj)})
    except Exception as e:
        return f"Error: {str(e)}", 400

# VULNERABILITY 6: Weak random number generation
import random

@app.route('/generate-token')
def generate_token():
    # BAD: Using weak random for security-sensitive operation
    token = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    return jsonify({'token': token})

# VULNERABILITY 7: Information disclosure
@app.route('/debug')
def debug_info():
    # BAD: Exposing sensitive system information
    return jsonify({
        'env_vars': dict(os.environ),
        'current_dir': os.getcwd(),
        'files': os.listdir('.')
    })

# VULNERABILITY 8: Eval injection
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression', '')
    # BAD: Using eval with user input - code injection risk
    try:
        result = eval(expression)
        return jsonify({'result': result})
    except Exception as e:
        return f"Error: {str(e)}", 400

# VULNERABILITY 9: Insecure file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file provided", 400
    
    file = request.files['file']
    filename = file.filename
    # BAD: No file type validation - malicious file upload risk
    file.save(f"./uploads/{filename}")
    return f"File {filename} uploaded successfully"

if __name__ == '__main__':
    # BAD: Running in debug mode in production
    app.run(debug=True, host='0.0.0.0', port=5000)