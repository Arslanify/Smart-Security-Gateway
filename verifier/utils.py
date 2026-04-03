import os
import cv2
import numpy as np
from django.conf import settings
from deepface import DeepFace

# ==========================================
# 🧠 AI MODEL INITIALIZER
# ==========================================
def get_face_detector():
    """
    T440p ke liye OpenCV backend sab se fast hai.
    """
    return "opencv"

def get_face_model():
    """
    Facenet512 is the most accurate model for 1-on-1 verification.
    """
    return "Facenet512"

# ==========================================
# 📸 IMAGE PROCESSING UTILS
# ==========================================
def save_temp_image(uploaded_file):
    """
    Verification ke waqt jo photo khinchi jaye usay temp folder mein save karna.
    """
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_scans')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return file_path

def cleanup_image(file_path):
    """
    Processing ke baad temp image ko delete karna taake storage full na ho.
    """
    if os.path.exists(file_path):
        os.remove(file_path)

# ==========================================
# 🔍 CORE AI LOGIC (FOR ENTITY)
# ==========================================
def compare_faces(captured_path, reference_path):
    """
    captured_path: Camera se li gayi photo
    reference_path: Database mein mojood photo
    """
    try:
        # Strict threshold 0.3 rakha hai for security
        # 
        result = DeepFace.verify(
            img1_path = captured_path,
            img2_path = reference_path,
            model_name = get_face_model(),
            detector_backend = get_face_detector(),
            distance_metric = "cosine",
            enforce_detection = True,
            align = True
        )
        return result
    except Exception as e:
        print(f"AI Processing Error: {e}")
        return None