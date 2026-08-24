# 🔐 Facial Expression Authentication System

A modern, passwordless authentication system that uses **facial recognition** and **emotion detection** to verify user identity. Built with Flask, OpenCV, and DeepFace AI.

---

## 🛠️ Technology Stack

### **Backend**
- **Flask** - Python web framework
- **OpenCV** - Computer vision and image processing
- **DeepFace** - Deep learning facial recognition
- **TensorFlow** - Machine learning backend
- **Pillow** - Image manipulation

### **Frontend**
- **HTML5** - Structure
- **CSS3** - Styling with gradients and animations
- **JavaScript (ES6+)** - Interactive functionality
- **MediaDevices API** - Camera access

### **AI/ML Models**
- **VGG-Face** - Face recognition
- **Emotion Detection Model** - Facial expression analysis

---

## 📥 Installation

### **Prerequisites**
- Python 3.9, 3.10, 3.11, or 3.12 (64-bit)
- Webcam/camera
- Modern web browser (Chrome, Firefox, Edge)

### **Step 1: Clone Repository**
```bash
git clone https://github.com/UtsavBajracharya/Facial-Expression-Authentication.git
cd facial-expression-auth
```

### **Step 2: Create Virtual Environment**
```bash
# Windows
python -m venv facial_auth_env
facial_auth_env\Scripts\activate
```

### **Step 3: Install Dependencies**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### **Step 4: Create Project Structure**
```bash
mkdir -p templates static/css static/js user_data
```

### **Step 5: Run Application**
```bash
python app.py
```

The application will start at: **http://127.0.0.1:5000**

