from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import cv2
import numpy as np
import os
from deepface import DeepFace
from datetime import datetime
# import secrets

app = Flask(__name__)
# app.secret.key = secrets.token_hex(16) # Generate secure secret key

# Configuration
USER_DATA_DIR = 'user_data'
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

# Validate if the user already exists 
def user_exists(username):
    return os.path.exists(os.path.join(USER_DATA_DIR, username))


# Homepage - Login
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Registration page
@app.route('/register')
def register():
    return render_template('register.html')

# Register new user with facial data
@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        image_data = data.get('image')

        # Validation
        if not username or not email or not image_data:
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        if user_exists(username):
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        return jsonify({'success': True, 'message': 'Registration successful!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration error: {str(e)}'})
        

if __name__ == '__main__':
    app.run(debug=True)