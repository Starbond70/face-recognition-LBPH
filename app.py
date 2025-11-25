import streamlit as st
import pandas as pd
import os
from src.data_handler import DataManager
from src.face_rec import FaceRecognitionSystem


st.set_page_config(page_title="Face Attendance System", layout="wide")


data_manager = DataManager()
try:
    face_rec = FaceRecognitionSystem()
except Exception as e:
    st.error(f"Error initializing Face Recognition System: {e}")
    st.stop()

st.title("📷 Face Recognition Attendance System")


page = st.sidebar.selectbox("Navigate", ["Dashboard", "Registration", "Training", "Attendance"])

if page == "Dashboard":
    st.header("📊 Dashboard")
    st.subheader("Today's Attendance")
    df = data_manager.get_attendance_today()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No attendance marked today.")

    st.subheader("Registered Students")
    if os.path.exists(data_manager.student_file):
        students = pd.read_csv(data_manager.student_file)
        st.dataframe(students, use_container_width=True)
    else:
        st.info("No students registered yet.")

    st.markdown("---")
    st.subheader("Danger Zone")
    with st.expander("Clear All Data"):
        password = st.text_input("Enter Password to Clear Data", type="password")
        if st.button("Clear All Student Data"):
            if password == "244001":
                success, msg = data_manager.clear_all_students()
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Incorrect Password!")

elif page == "Registration":
    st.header("📝 New Student Registration")
    
    col1, col2 = st.columns(2)
    with col1:
        student_id = st.text_input("Enter Student ID")
    with col2:
        name = st.text_input("Enter Student Name")
    
    
    if st.button("Start Capture"):
        if student_id and name:

            success, msg = data_manager.add_student(student_id, name)
            if success:
                st.success(msg)
                st.info("Opening camera... Please look at the camera. It will close automatically after capturing 30 images.")
                

                frame_placeholder = st.empty()
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                captured_count = 0
                total_limit = 30
                
                for frame, count, limit in face_rec.capture_frames(student_id, name, limit=total_limit):
                    if frame is None:
                        st.error("Could not open camera.")
                        break
                    
                    frame_placeholder.image(frame, channels="RGB")
                    captured_count = count
                    progress_bar.progress(min(count / limit, 1.0))
                    status_text.text(f"Captured {count}/{limit} images")
                
                if captured_count >= total_limit:
                    st.success(f"Successfully captured {captured_count} images for {name}.")
                    frame_placeholder.empty()
                    status_text.empty()
                    progress_bar.empty()
            else:
                st.error(msg)
        else:
            st.warning("Please enter both ID and Name.")
    
    elif st.checkbox("Open Camera"):
        frame_placeholder = st.empty()
        for frame in face_rec.preview_frames():
            if frame is None:
                st.error("Could not open camera.")
                break
            frame_placeholder.image(frame, channels="RGB")

elif page == "Training":
    st.header("🧠 Train Model")
    st.write("Train the face recognition model with the captured images.")
    
    if st.button("Train Model"):
        with st.spinner("Training model... This may take a few seconds."):
            success, msg = face_rec.train_model()
            if success:
                st.success(msg)
            else:
                st.error(msg)

elif page == "Attendance":
    st.header("✅ Mark Attendance")
    
    if 'recognized_students' not in st.session_state:
        st.session_state.recognized_students = set()

    col1, col2 = st.columns([3, 1])
    
    with col1:
        run_camera = st.checkbox("Start Camera")
        FRAME_WINDOW = st.image([])
    
    with col2:
        st.subheader("Recognized")
        student_list_placeholder = st.empty()
        

        current_names = [data_manager.get_student_name(sid) for sid in st.session_state.recognized_students]
        student_list_placeholder.write("\n".join(current_names))

        col_save, col_clear = st.columns(2)
        with col_save:
            if st.button("Save Attendance"):
                if not st.session_state.recognized_students:
                    st.warning("No students to save.")
                else:
                    count = 0
                    for sid in st.session_state.recognized_students:
                        name = data_manager.get_student_name(sid)
                        success, msg = data_manager.mark_attendance(sid, name)
                        if success:
                            count += 1
                    st.success(f"Saved {count} records.")
                    st.session_state.recognized_students.clear()
                    st.rerun()
        
        with col_clear:
            if st.button("Clear Names"):
                st.session_state.recognized_students.clear()
                st.rerun()

    if run_camera:
        for frame, students in face_rec.generate_frames():
            if frame is None:
                st.error(students)
                break
            
            FRAME_WINDOW.image(frame)
            

            new_students = False
            for s in students:
                if s['id'] not in st.session_state.recognized_students:
                    st.session_state.recognized_students.add(s['id'])
                    new_students = True
            
            if new_students:
                current_names = [data_manager.get_student_name(sid) for sid in st.session_state.recognized_students]
                student_list_placeholder.write("\n".join(current_names))


st.markdown("---")

