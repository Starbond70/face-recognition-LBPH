# Face Recognition Attendance System

A robust and user-friendly attendance system built with Python and Streamlit. This application uses OpenCV for real-time face detection and recognition to automate the attendance marking process.

## 🚀 Features

- **Dashboard**: 
  - View real-time attendance records for the current day.
  - List all registered students.
  - Administrative options to clear all data (Password protected).
- **Student Registration**: 
  - Easy-to-use interface for registering new students.
  - Automatically captures 30 face images for training.
  - Real-time camera preview embedded in the application.
- **Model Training**: 
  - One-click training of the LBPH (Local Binary Patterns Histograms) Face Recognizer.
  - Visual feedback during the training process.
- **Smart Attendance**: 
  - Real-time face recognition using your webcam.
  - Batch processing: Recognizes multiple students and allows for batch saving.
  - Prevents duplicate entries for the same day.

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Web Framework**: [Streamlit](https://streamlit.io/)
- **Computer Vision**: [OpenCV](https://opencv.org/) (opencv-contrib-python)
- **Data Handling**: Pandas, NumPy
- **Image Processing**: Pillow

## 📂 Project Structure

```
Face_recognition_based_attendance_system/
├── app.py                              # Main Streamlit application entry point
├── requirements.txt                    # Python dependencies
├── haarcascade_frontalface_default.xml # Pre-trained Haar Cascade model
├── src/
│   ├── data_handler.py                 # Handles CSV data operations (Students & Attendance)
│   └── face_rec.py                     # Core logic for Face Detection & Recognition
├── data/                               # Directory for storing CSV records
│   └── attendance/                     # Daily attendance logs
└── TrainingImageLabel/                 # Directory for storing the trained model
```

## ⚙️ Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd Face_recognition_based_attendance_system
   ```

2. **Create a Virtual Environment (Optional but Recommended)**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃‍♂️ Usage

1. **Run the Application**
   ```bash
   streamlit run app.py
   ```

2. **Navigate the App**
   The application is divided into four main sections accessible via the sidebar:

   - **Dashboard**: Check who is present today and view the list of all registered students.
   - **Registration**: 
     - Enter the Student ID and Name.
     - Click "Start Capture" to take 30 photos of the student.
     - Ensure good lighting and face the camera directly.
   - **Training**: 
     - After registering new students, go to this tab.
     - Click "Train Model" to update the recognition system.
   - **Attendance**: 
     - Check "Start Camera" to begin the recognition process.
     - The system will list recognized students on the right.
     - Click "Save Attendance" to commit the records to the daily CSV file.

## ⚠️ Troubleshooting

- **Camera Issues**: Ensure no other application is using your webcam. If the camera doesn't start, try refreshing the page or restarting the Streamlit server.
- **"Unknown" Faces**: If the system fails to recognize a registered student, try re-training the model or registering the student again with better lighting conditions.
- **Haar Cascade Error**: Ensure `haarcascade_frontalface_default.xml` is present in the root directory.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

