
try:
    import streamlit
    print("Streamlit imported successfully")
    import mediapipe
    print("Mediapipe imported successfully")
    import cv2
    print("OpenCV imported successfully")
    import numpy
    print("Numpy imported successfully")
    
    # Check processor import
    from processor import VideoProcessor
    print("VideoProcessor module imported successfully")
    
    # Check app import (just structure, not running)
    # We can't import app easily because it runs streamlit code on import usually (or at least top level)
    # But let's try to just ensure the file is syntactically correct
    with open('app.py', 'r') as f:
        compile(f.read(), 'app.py', 'exec')
    print("app.py syntax check passed")

except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Verification failed: {e}")
