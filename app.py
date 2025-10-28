from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import cv2
import numpy as np
from deepface import DeepFace
from datetime import datetime
# import secrets

app = Flask(__name__)
# app.secret.key = secrets.token_hex(16) # Generate secure secret key


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


if __name__ == '__main__':
    app.run(debug=True)