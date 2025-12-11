from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import cv2
import numpy as np
import base64
import os
import json
from deepface import DeepFace
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) # Generate secure secret key

# Configuration
USER_DATA_DIR = 'user_data'
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

# Emotion mapping for authentication
REQUIRED_EXPRESSIONS = ['happy', 'surprise', 'neutral']

# Convert base64 string to OpenCV image
def decode_base64_image(base64_string):
    """Convert base64 string to OpenCV image"""
    try:
        print(f"[DEBUG] Received base64 string length: {len(base64_string)}")
        
        # Remove data URL prefix if present
        if 'base64,' in base64_string:
            base64_string = base64_string.split('base64,')[1]
            print(f"[DEBUG] After removing prefix, length: {len(base64_string)}")
        elif ',' in base64_string:
            base64_string = base64_string.split(',')[1]
            print(f"[DEBUG] After removing prefix (comma), length: {len(base64_string)}")
        
        # Add padding if needed
        missing_padding = len(base64_string) % 4
        if missing_padding:
            base64_string += '=' * (4 - missing_padding)
            print(f"[DEBUG] Added padding, new length: {len(base64_string)}")
        
        # Decode base64
        img_data = base64.b64decode(base64_string)
        print(f"[DEBUG] Decoded image data size: {len(img_data)} bytes")
        
        if len(img_data) < 100:
            print("[ERROR] Image data too small")
            return None
        
        # Convert to numpy array
        nparr = np.frombuffer(img_data, np.uint8)
        print(f"[DEBUG] Numpy array shape: {nparr.shape}")
        
        # Decode to image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is not None:
            print(f"[DEBUG] Successfully decoded image with shape: {img.shape}")
        else:
            print("[ERROR] cv2.imdecode returned None - trying alternative method")
            # Try using PIL as alternative
            try:
                from PIL import Image
                import io
                pil_img = Image.open(io.BytesIO(img_data))
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                print(f"[DEBUG] Successfully decoded with PIL, shape: {img.shape}")
            except Exception as pil_error:
                print(f"[ERROR] PIL also failed: {pil_error}")
                return None
        
        return img
    except Exception as e:
        print(f"[ERROR] Error decoding image: {e}")
        import traceback
        traceback.print_exc()
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

        
# Verify if the face matches stored reference
def verify_face(username, image):
    user_dir = os.path.join(USER_DATA_DIR, username)
    reference_path = os.path.join(user_dir, 'reference_face.jpg')

    if not os.path.exists(reference_path):
        return False
    
    try:
        # Save temporary image
        temp_path = os.path.join(user_dir, 'temp_verify.jpg')
        cv2.imwrite(temp_path, image)

        # Verify faces
        result = DeepFace.verify(temp_path, reference_path, enforce_detection=False)

        # Clean up temp file
        os.remove(temp_path)

        return result['verified']
    except Exception as e:
        print(f"Error verifyling face: {e}")
        return False

def save_user_info(username, email):
    user_file = os.path.join(USER_DATA_DIR, username, 'info.json')
    user_info = {
        'username': username,
        'email': email,
        'registered_at': datetime.now().isoformat()
    }
    with open(user_file, 'w') as f:
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
        print("[DEBUG] Registration request received")
        data = request.json
        username = data.get('username')
        email = data.get('email')
        image_data = data.get('image')
        
        print(f"[DEBUG] Username: {username}, Email: {email}")
        print(f"[DEBUG] Image data present: {image_data is not None}")
        
        if image_data:
            print(f"[DEBUG] Image data length: {len(image_data)}")
            print(f"[DEBUG] Image data starts with: {image_data[:50]}")
        
        # Validation
        if not username or not email or not image_data:
            print("[DEBUG] Missing required fields")
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        if user_exists(username):
            print(f"[DEBUG] Username {username} already exists")
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        # Decode image
        print("[DEBUG] Attempting to decode image...")
        image = decode_base64_image(image_data)
        
        if image is None:
            print("[ERROR] Failed to decode image - returning error")
            return jsonify({
                'success': False, 
                'message': 'Invalid image data - could not decode. Check terminal for details.'
            })
        
        print(f"[DEBUG] Image decoded successfully, shape: {image.shape}")
        
        # Validate image has reasonable dimensions
        if image.shape[0] < 100 or image.shape[1] < 100:
            print("[ERROR] Image dimensions too small")
            return jsonify({
                'success': False,
                'message': f'Image too small: {image.shape}. Need at least 100x100.'
            })
        
        # Save user data
        print("[DEBUG] Saving user data...")
        save_user_face(username, image)
        save_user_info(username, email)
        
        print(f"[DEBUG] Registration successful for user: {username}")
        return jsonify({'success': True, 'message': 'Registration successful!'})
    
    except Exception as e:
        print(f"[ERROR] Registration exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

    
# Authenticate the user with facial expression
@app.route('/api/authenticate', methods=['POST'])
def api_authenticate():
    try:
        data = request.json
        username = data.get('username')
        image_data = data.get('image')
        required_emotion = data.get('emotion')

        if not username or not image_data or not required_emotion:
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        if not user_exists(username):
            return jsonify({'success': False, 'message': 'User not found'})
        
        # Decode image
        image = decode_base64_image(image_data)
        if image is None:
            return jsonify({'success': False, 'message': 'Invalid image data'})
        
        # Verify face matches stored reference
        face_verified = verify_face(username, image)
        if not face_verified:
            return jsonify({'success': False, 'message': 'Face verification failed'})
        

        # Detect emotion
        detected_emotion = detect_emotion(image)
        if detected_emotion is None:
            return jsonify({'success': False, 'message': 'Could not detect facial expression'})
        
        # Check if emotion matches
        if detected_emotion.lower() == required_emotion.lower():
            session['username'] = username
            return jsonify({
                'success' : True,
                'message' : 'Authentication successful!',
                'emotion' : detected_emotion
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Wrong expression. Expected: {required_emotion}, Got: {detected_emotion}' ,
                'detected_emotion': detected_emotion
            })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Authentication error: {str(e)}'})

# Detect emotion from the image    
@app.route('/api/detect_emotion', methods=['POST'])
def api_detect_emotion():
    try:
        data = request.json
        image_data = data.get('image')

        if not image_data:
            return jsonify({'success': False, 'message': 'No image provided'})
        
        image = decode_base64_image(image_data)
        if image is None:
            return jsonify({'success': False, 'message': 'Ivalid image data'})
        
        emotion = detect_emotion(image)
        if emotion:
            return jsonify({'success': True, 'emotion': emotion})
        else:
            return jsonify({'success': False, 'message': 'No face detected'})
         
    except Exception as e:    
        return jsonify({'success': False, 'message': str(e)})
        


if __name__ == '__main__':
    app.run(debug=True)