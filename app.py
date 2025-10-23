from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import cv2
import numpy as np
from deepface import DeepFace
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret.key = secrets.token_hex(16) # Genrate secure secret key


# Homepage - Login
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)