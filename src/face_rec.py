import cv2
import os
import numpy as np
from PIL import Image
from src.data_handler import DataManager

class FaceRecognitionSystem:
    """
    Handles all Computer Vision tasks for the attendance system.
    
    This class wraps OpenCV functionality to:
    - Capture images from the webcam for training.
    - Train the LBPH face recognition model.
    - specialized generators to stream video frames to the Streamlit UI.
    - Perform real-time face detection and recognition.
    """
    def __init__(self, cascade_path="haarcascade_frontalface_default.xml"):
        self.data_manager = DataManager()
        self.cascade_path = cascade_path
        if not os.path.exists(self.cascade_path):
            raise FileNotFoundError(f"Cascade file not found at {self.cascade_path}")
        self.detector = cv2.CascadeClassifier(self.cascade_path)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

    def capture_images(self, student_id, name, limit=30, cam_index=0):
        """
        Captures images for training.
        Returns: (success, message)
        """
        cam = cv2.VideoCapture(cam_index)
        if not cam.isOpened():
            return False, "Could not open camera."

        sample_num = 0
        try:
            while True:
                ret, img = cam.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.detector.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    sample_num += 1
                    

                    filename = f"{name}.{student_id}.{sample_num}.jpg"
                    path = os.path.join(self.data_manager.training_images_dir, filename)
                    cv2.imwrite(path, gray[y:y+h, x:x+w])
                    
                    cv2.imshow('Capturing Images (Press Q to stop)', img)

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
                

                if sample_num >= limit:
                    break
        finally:
            cam.release()
            cv2.destroyAllWindows()

        return True, f"Captured {sample_num} images for {name}."

    def capture_frames(self, student_id, name, limit=30, cam_index=0):
        """
        Generator that yields frames and progress for Streamlit registration.
        
        Workflow:
        1. Open the camera.
        2. Read frames in a loop.
        3. Detect faces in each frame.
        4. If a face is found, crop and save it to 'training_images' folder with unique filename.
        5. Yield the annotated frame (with rectangle) back to the UI for display.
        6. Stop when 'limit' number of images are captured.
        
        Yields: (frame_rgb, sample_num, total_limit)
        """
        import time
        cam = cv2.VideoCapture(cam_index)
        if not cam.isOpened():
            yield None, 0, limit
            return

        sample_num = 0
        last_capture_time = 0
        capture_interval = 1.0 / 5.0

        try:
            while True:
                ret, img = cam.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.detector.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    
                    current_time = time.time()
                    if current_time - last_capture_time >= capture_interval:
                        sample_num += 1
                        

                        filename = f"{name}.{student_id}.{sample_num}.jpg"
                        path = os.path.join(self.data_manager.training_images_dir, filename)
                        cv2.imwrite(path, gray[y:y+h, x:x+w])
                        
                        last_capture_time = current_time
                

                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                yield img_rgb, sample_num, limit


                if sample_num >= limit:
                    break
        finally:
            cam.release()

    def preview_frames(self, cam_index=0):
        """
        Generator that yields frames for preview (no saving).
        Yields: frame_rgb
        """
        cam = cv2.VideoCapture(cam_index)
        if not cam.isOpened():
            yield None
            return

        try:
            while True:
                ret, img = cam.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.detector.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                

                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                yield img_rgb
        finally:
            cam.release()

    def train_model(self):
        """
        Trains the model using captured images.
        
        Workflow:
        1. Iterate through all .jpg images in 'training_images'.
        2. Extract the Student ID from the filename (format: Name.ID.SampleNum.jpg).
        3. Load the image and convert to numpy array.
        4. Feed all face arrays and corresponding IDs to the LBPH recognizer.
        5. Train the recognizer.
        6. Save the trained model state to 'trainer.yml'.
        """
        path = self.data_manager.training_images_dir
        image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]
        
        if not image_paths:
            return False, "No training images found."

        faces = []
        ids = []

        for image_path in image_paths:
            try:
                pil_image = Image.open(image_path).convert('L')
                image_np = np.array(pil_image, 'uint8')
                

                filename = os.path.split(image_path)[-1]
                parts = filename.split(".")
                if len(parts) >= 3:
                    id_ = int(parts[1])
                    faces.append(image_np)
                    ids.append(id_)
            except Exception as e:
                print(f"Skipping file {image_path}: {e}")

        if not faces:
            return False, "No valid faces found to train."

        self.recognizer.train(faces, np.array(ids))
        self.recognizer.save(self.data_manager.trainer_file)
        return True, "Model trained and saved successfully."

    def generate_frames(self, cam_index=0):
        """
        Generator that yields frames and recognized students for Streamlit.
        
        Workflow:
        1. Load the trained 'trainer.yml' model.
        2. Open camera and read frames.
        3. Detect faces in the frame.
        4. For each face, predict the ID using the recognizer.
        5. If confidence is high (value is low), valid match: retrieve name.
        6. Annotate frame with Name/Unknown.
        7. Yield frame and list of recognized students to UI.
        
        Yields: (frame_rgb, recognized_students_list)
        """
        if not os.path.exists(self.data_manager.trainer_file):
            yield None, "Model not trained. Please train the model first."
            return

        self.recognizer.read(self.data_manager.trainer_file)
        cam = cv2.VideoCapture(cam_index)
        if not cam.isOpened():
            yield None, "Could not open camera."
            return

        font = cv2.FONT_HERSHEY_SIMPLEX
        
        try:
            while True:
                ret, img = cam.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.detector.detectMultiScale(gray, 1.2, 5)

                current_frame_students = []

                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (225, 0, 0), 2)
                    id_, conf = self.recognizer.predict(gray[y:y+h, x:x+w])
                    
                    if conf < 50:
                        name = self.data_manager.get_student_name(id_)
                        current_frame_students.append({"id": id_, "name": name})
                        display_text = f"{name} ({int(conf)})"
                    else:
                        display_text = "Unknown"


                    cv2.putText(img, display_text, (x, y+h), font, 1, (255, 255, 255), 2)


                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                yield img_rgb, current_frame_students

        finally:
            cam.release()
