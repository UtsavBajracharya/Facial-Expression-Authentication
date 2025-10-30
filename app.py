from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import cv2
import numpy as np
import base64
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


# Convert base64 string to OpenCV image
def decode_base64_image(base64_string):
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.unit8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

# Detect facial emotion from image

def detect_emotion(image):
    try:
        result = DeepFace.analyze(image, actions=['emotion'], enforce_detection=False)

        # Hangle both list and dict results
        if isinstance(result, list):
            result=result[0]
        
        dominant_emotion = result['dominant_emotion']
        return dominant_emotion
    
    except Exception as e:
        print(f'Error detecting emotion: {e}')
        return None
    

 
# Save user face
def save_user_face(username, image):
    user_dir = os.path.join(USER_DATA_DIR, username)
    if not os.path.exists(user_dir):
          os.makedirs(user_dir)

    face_path = os.path.join(user_dir, 'reference_face.jpg')
    cv2.imwrite(face_path, image)
    return face_path


# Save user information    
def save_user_info(username, email):
    user_file = os.path.join(USER_DATA_DIR, username, 'info.json')
    user_info = {
        'username': username,
        'email': email,
        'registered_at': datetime.now().isoformat()
    }        
    with open(user_file, 'W') as f:
        json.dump(user_info, f)




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

        # Decode image

        image = decode_base64_image(image_data)
        if image is None:
            return jsonify({'success' : False, 'message' : 'Invalid image data'}) 

        # Save user data
        save_user_face(username, image)   
        save_user_info(username, email)   
        
        return jsonify({'success': True, 'message': 'Registration successful!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration error: {str(e)}'})
        

if __name__ == '__main__':
    app.run(debug=True)