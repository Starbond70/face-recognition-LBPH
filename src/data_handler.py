import os
import csv
import pandas as pd
from datetime import datetime


class DataManager:
    """
    Manages data persistence for the application.
    
    This class handles all file system interactions, including:
    - Creating necessary directories (data, attendance, images, models).
    - Managing student registration data (students.csv).
    - Recording daily attendance in CSV files.
    - Cleaning up data when requested.
    """
    def __init__(self, root_dir="."):
        self.root_dir = root_dir
        self.data_dir = os.path.join(root_dir, "data")
        self.student_file = os.path.join(self.data_dir, "students.csv")
        self.attendance_dir = os.path.join(self.data_dir, "attendance")
        self.training_images_dir = os.path.join(self.data_dir, "training_images")
        self.models_dir = os.path.join(self.data_dir, "models")
        self.trainer_file = os.path.join(self.models_dir, "trainer.yml")
        
        self._ensure_directories()
        self._ensure_student_file()

    def _ensure_directories(self):
        """
        Ensure all necessary directories exist.
        
        Workflow:
        1. Define list of required directories.
        2. Itereate through list and create directory if it doesn't exist.
        """
        dirs = [self.data_dir, self.attendance_dir, self.training_images_dir, self.models_dir]
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)

    def _ensure_student_file(self):
        """Ensure the student details CSV exists with headers."""
        if not os.path.exists(self.student_file):
            with open(self.student_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Id', 'Name'])

    def add_student(self, student_id, name):
        """
        Add a new student to the CSV file.
        
        Workflow:
        1. Check if the student CSV file exists.
        2. If it exists, read existing data to ensure the Student ID is unique.
        3. If the ID overlaps, return an error.
        4. If ID is valid, append the new student's ID and Name to the CSV file.
        """

        if os.path.exists(self.student_file):
            df = pd.read_csv(self.student_file)

            df['Id'] = df['Id'].astype(str)
            if str(student_id) in df['Id'].values:
                return False, "Student ID already exists."
        
        with open(self.student_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([student_id, name])
        return True, "Student added successfully."

    def get_student_name(self, student_id):
        """Get student name by ID."""
        if not os.path.exists(self.student_file):
            return "Unknown"
        try:
            df = pd.read_csv(self.student_file)
            df['Id'] = df['Id'].astype(str)
            student = df.loc[df['Id'] == str(student_id)]
            if not student.empty:
                return student['Name'].values[0]
        except Exception as e:
            print(f"Error reading student file: {e}")
        return "Unknown"

    def mark_attendance(self, student_id, name):
        """
        Mark attendance for a student.
        
        Workflow:
        1. Get current date and time.
        2. Determine the attendance file path for the current date (daily files).
        3. Check if the file exists and if the student has already marked attendance today.
        4. If not marked, create/append to the daily CSV file with Timestamp.
        """
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        file_path = os.path.join(self.attendance_dir, f"Attendance_{date_str}.csv")
        

        file_exists = os.path.exists(file_path)
        

        if file_exists:
            try:
                df = pd.read_csv(file_path)
                df['Id'] = df['Id'].astype(str)
                if str(student_id) in df['Id'].values:
                    return False, "Attendance already marked."
            except pd.errors.EmptyDataError:
                pass

        with open(file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Id', 'Name', 'Date', 'Time'])
            writer.writerow([student_id, name, date_str, time_str])
        
        return True, f"Attendance marked for {name} at {time_str}"

    def get_attendance_today(self):
        """
        Get today's attendance records.
        
        Workflow:
        1. Construct the filename for today's attendance.
        2. If file exists, read into a DataFrame.
        3. If not, return an empty DataFrame.
        """
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        file_path = os.path.join(self.attendance_dir, f"Attendance_{date_str}.csv")
        
        if os.path.exists(file_path):
            try:
                return pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                return pd.DataFrame(columns=['Id', 'Name', 'Date', 'Time'])
        return pd.DataFrame(columns=['Id', 'Name', 'Date', 'Time'])

    def clear_all_students(self):
        """
        Clear all student data, including CSV, images, trained model, and attendance records.
        
        Workflow:
        1. Reset 'students.csv' to be empty (headers only).
        2. Delete all images in 'training_images' directory.
        3. Delete the trained model 'trainer.yml'.
        4. Delete all daily attendance CSV files.
        """

        with open(self.student_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Id', 'Name'])
            

        if os.path.exists(self.training_images_dir):
            for f in os.listdir(self.training_images_dir):
                os.remove(os.path.join(self.training_images_dir, f))
                

        if os.path.exists(self.trainer_file):
            os.remove(self.trainer_file)


        if os.path.exists(self.attendance_dir):
            for f in os.listdir(self.attendance_dir):
                os.remove(os.path.join(self.attendance_dir, f))
            
        return True, "All student data and attendance records cleared successfully."
