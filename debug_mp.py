import mediapipe as mp
print(f"MediaPipe Location: {mp.__file__}")
print(f"Dir(mp): {dir(mp)}")
try:
    print(f"mp.solutions: {mp.solutions}")
except AttributeError as e:
    print(f"Error accessing solutions: {e}")

try:
    import mediapipe.python.solutions as solutions
    print("Imported mediapipe.python.solutions directly")
except ImportError as e:
    print(f"Error importing solutions directly: {e}")
