import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os

class VideoProcessor:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def calculate_weight_transfer(self, landmarks):
        """
        Calculates weight transfer based on hip center relative to ankles.
        Returns a percentage (0-100) and the raw ratio (0.0-1.0).
        """
        # Get coordinates
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]

        # Calculate midpoints (only X matters for weight transfer in side-on view)
        hip_center_x = (left_hip.x + right_hip.x) / 2
        
        # Determine stace range
        ankle_xs = [left_ankle.x, right_ankle.x]
        min_ankle_x = min(ankle_xs)
        max_ankle_x = max(ankle_xs)
        stance_width = max_ankle_x - min_ankle_x

        if stance_width == 0:
            return 50, 0.5

        # Calculate relative position (0.0 = back foot, 1.0 = front foot)
        # We assume the "front" is the direction of the max x for simplicity
        # or we just map the hip position within the stance interval.
        relative_pos = (hip_center_x - min_ankle_x) / stance_width
        
        # Clamp between 0 and 1
        relative_pos = max(0.0, min(1.0, relative_pos))
        
        return int(relative_pos * 100), relative_pos

    def process_video(self, input_path, output_path, player_name="PLAYER"):
        cap = cv2.VideoCapture(input_path)
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            # Convert the BGR image to RGB
            image.flags.writeable = False
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process pose
            results = self.pose.process(image_rgb)

            # Draw the pose annotation on the image.
            image.flags.writeable = True
            
            # Create a dark overlay for aesthetics (optional, skipping for now to keep video clear)
            # but we will darken the image slightly to make landmarks pop?
            # image = cv2.addWeighted(image, 0.7, np.zeros(image.shape, image.dtype), 0, 0)
            
            if results.pose_landmarks:
                # 1. Draw Skeleton
                # Custom drawing for specifically requested "Green lines, Red joints"
                self.draw_custom_skeleton(image, results.pose_landmarks)
                
                # 2. Calculate Logic
                wt_percent, wt_ratio = self.calculate_weight_transfer(results.pose_landmarks.landmark)
                
                # 3. Draw HUD
                self.draw_hud(image, wt_percent, player_name)

            out.write(image)

        cap.release()
        out.release()
        return output_path

    def draw_custom_skeleton(self, image, landmarks):
        h, w, _ = image.shape
        
        # Define connections (standard pose connections)
        connections = self.mp_pose.POSE_CONNECTIONS
        
        # Draw lines (Green)
        for connection in connections:
            start_idx = connection[0]
            end_idx = connection[1]
            
            start_point = landmarks.landmark[start_idx]
            end_point = landmarks.landmark[end_idx]
            
            # Check visibility
            if start_point.visibility < 0.5 or end_point.visibility < 0.5:
                continue
                
            x1, y1 = int(start_point.x * w), int(start_point.y * h)
            x2, y2 = int(end_point.x * w), int(end_point.y * h)
            
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2) # Green

        # Draw joints (Red)
        for idx, landmark in enumerate(landmarks.landmark):
            if landmark.visibility < 0.5:
                continue
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(image, (cx, cy), 4, (0, 0, 255), -1) # Red

    def draw_hud(self, image, percentage, player_name):
        h, w, _ = image.shape
        
        # --- Top Text ---
        text = f"BALANCE . TIMING . {player_name.upper()}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0 * (w / 1280) # Scale based on width
        thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (w - text_size[0]) // 2
        text_y = int(h * 0.1)
        
        # Shadow
        cv2.putText(image, text, (text_x + 2, text_y + 2), font, font_scale, (0,0,0), thickness)
        # Text
        cv2.putText(image, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)

        # --- Bottom Weight Transfer Bar ---
        bar_width = int(w * 0.6)
        bar_height = int(h * 0.05)
        bar_x = (w - bar_width) // 2
        bar_y = int(h * 0.85)
        
        # Background bar
        cv2.rectangle(image, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        cv2.rectangle(image, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (200, 200, 200), 2)

        # Fill bar
        fill_width = int(bar_width * (percentage / 100))
        # Color gradient logic could go here, but let's stick to a solid color for now (Cyan/Blue)
        cv2.rectangle(image, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), (255, 255, 0), -1) # Cyan

        # Label
        label = f"WEIGHT TRANSFER: {percentage}%"
        label_size = cv2.getTextSize(label, font, font_scale * 0.7, 1)[0]
        label_x = (w - label_size[0]) // 2
        label_y = bar_y - 10
        
        cv2.putText(image, label, (label_x, label_y), font, font_scale * 0.7, (255, 255, 255), 1)

