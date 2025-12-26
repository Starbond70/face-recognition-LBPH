# Face Recognition Attendance System

A robust and user-friendly attendance system that utilizes facial recognition technology. This project offers two interfaces: a modern **Web Application** (FastAPI + HTML/JS) and a **Streamlit Dashboard** (Legacy).

## 🚀 Features

-   **Dashboard**:
    -   View real-time attendance records.
    -   List registered students.
    -   Administrative capabilities (Password protected).
-   **Student Registration**:
    -   Streamlined interface to register new students.
    -   Captures 30 face images for training samples.
    -   Live camera feed integration.
-   **Model Training**:
    -   Train the LBPH (Local Binary Patterns Histograms) Face Recognizer on captured images.
    -   Visual feedback for successful training.
-   **Smart Attendance**:
    -   Real-time face detection and recognition using webcam.
    -   Batch processing for recognizing multiple students.
    -   Session-based attendance tracking before saving.

## 🛠️ Tech Stack

-   **Backend**: Python, [FastAPI](https://fastapi.tiangolo.com/), Uvicorn
-   **Frontend**: HTML, CSS, JavaScript (Vanilla)
-   **Legacy Interface**: [Streamlit](https://streamlit.io/)
-   **Computer Vision**: [OpenCV](https://opencv.org/)
-   **Data Processing**: Pandas, NumPy
-   **Image Handling**: Pillow

## 📂 Project Structure

```
Face_recognition_based_attendance_system/
├── main.py                             # FastAPI Application entry point (Web App)
├── app.py                              # Streamlit Application entry point (Legacy)
├── requirements.txt                    # Project dependencies
├── haarcascade_frontalface_default.xml # Haar Cascade model for face detection
├── static/                             # Frontend assets (HTML, CSS, JS) for Web App
├── src/
│   ├── data_handler.py                 # Data management for Students & Attendance
│   └── face_rec.py                     # Core Face Recognition logic
├── data/
│   └── attendance/                     # Daily attendance CSV logs
└── TrainingImageLabel/                 # Stores trained model (trainer.yml)
```

## ⚙️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Starbond70/face-recognition-LBPH.git
    cd Face_recognition_based_attendance_system
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## 🏃‍♂️ Usage

You can run the system using either the new Web Interface or the Streamlit Dashboard.

### Option 1: Web Application (Recommended)

1.  **Start the Server**
    ```bash
    uvicorn main:app --reload
    ```
    Or simply:
    ```bash
    python main.py
    ```

2.  **Access the App**
    Open your browser and navigate to: `http://localhost:8000`

### Option 2: Streamlit Dashboard (Legacy)

1.  **Run the Streamlit App**
    ```bash
    streamlit run app.py
    ```

2.  **Access the App**
    The app will typically open automatically at `http://localhost:8501`.

## ⚠️ Troubleshooting

-   **Camera Issues**: Ensure no other application is using your webcam. If the video feed is black or throwing errors, restart the server.
-   **"Unknown" Faces**: Poor lighting or limited training data can cause recognition failures. Try re-registering the student with clear, well-lit images.
-   **Dependency Errors**: Make sure all packages in `requirements.txt` are installed in your active virtual environment.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
