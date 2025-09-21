import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from omr_core.omr_detect import process_omr
from web_app.db_utils import init_db, save_result, get_all_results, save_review, delete_result

import pandas as pd

init_db()

st.title("Automated OMR Evaluation & Scoring System")

tab1, tab2, tab3 = st.tabs(["Evaluate OMR Sheet", "Dashboard", "Delete Student"])

with tab1:
    st.header("Evaluate OMR Sheet")
    with st.form(key='omr_form'):
        student_name = st.text_input("Student Name")
        student_id = st.text_input("Student ID (roll number)")
        uploaded_file = st.file_uploader("Upload OMR Sheet Image (JPEG/PNG)", type=["png", "jpg", "jpeg"])
        version = st.selectbox("Select OMR Sheet Version", ["version_A", "version_B"])
        submitted = st.form_submit_button("Submit & Evaluate")
        
        if submitted:
            if not student_name or not student_id or not uploaded_file or not version:
                st.warning("Please fill in all fields and upload the image.")
            else:
                img_path = f"temp_{uploaded_file.name}"
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.image(img_path, caption="OMR Sheet", use_container_width=True)
                results = process_omr(img_path, "omr_core/answer_key.json", version)
                st.subheader("Subject-wise Scores")
                for subj in [k for k in results if k.startswith("subject_")]:
                    st.write(f"{subj}: {results[subj]}/20")
                st.write(f"Total: {results['total']}/100")
                save_result(student_id, student_name, version, results)
                os.remove(img_path)
                st.success("Results saved successfully!")

with tab2:
    st.header("Students Performance Dashboard")
    all_results = get_all_results()
    if all_results:
        df = pd.DataFrame(all_results)

        # Ensure required columns exist
        review_col = "review"
        if review_col not in df.columns:
            df[review_col] = ""
        if "student_name" not in df.columns:
            df["student_name"] = ""
        if "student_id" not in df.columns:
            df["student_id"] = ""

        # Ranking
        df = df.sort_values(by="total", ascending=False).reset_index(drop=True)
        df["rank"] = df["total"].rank(method="min", ascending=False).astype(int)

        # Set review column automatically
        df[review_col] = df['total'].apply(lambda x: "Fail" if x < 36 else "Pass")

        # Bar chart for total marks (0–100)
        st.subheader("Total Marks per Student")
        import plotly.express as px
        total_chart = px.bar(
            df,
            x="student_name",
            y="total",
            title="Total Marks (0–100)",
            range_y=[0, 100],
            labels={"total": "Marks", "student_name": "Student"},
            height=400
        )
        st.plotly_chart(total_chart, use_container_width=True)

        # Subject-wise bar chart (0–20)
        subject_cols = [c for c in df.columns if c.startswith("subject_")]
        st.subheader("Subject-wise Marks Distribution")
        subject_df = df[["student_name"] + subject_cols].melt(id_vars="student_name", var_name="Subject", value_name="Marks")
        subject_chart = px.bar(
            subject_df,
            x="student_name",
            y="Marks",
            color="Subject",
            barmode="group",
            title="Subject-wise Marks (0–20)",
            range_y=[0, 20],
            height=400
        )
        st.plotly_chart(subject_chart, use_container_width=True)

        # Data Table
        st.subheader("Students Table & Reviews")
        st.dataframe(df[["rank", "student_name", "student_id", "version", *subject_cols, "total", "review"]].style.highlight_max("total"))

        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button(label="Download Table as CSV", data=csv, file_name="students_results.csv", mime="text/csv")
    else:
        st.info("No student results available yet.")

with tab3:
    st.header("Delete Student Details")
    with st.form(key="delete_student_form"):
        del_student_id = st.text_input("Enter Student ID to Delete")
        del_submit = st.form_submit_button("Delete Student")
        if del_submit:
            if not del_student_id:
                st.warning("Please enter a Student ID to delete.")
            else:
                # Check if student exists
                all_results = get_all_results()
                existing_ids = [str(r["student_id"]) for r in all_results]
                
                if del_student_id not in existing_ids:
                    st.error(f"No student found with ID {del_student_id}. Please check the ID and try again.")
                else:
                    delete_result(del_student_id)
                    st.success(f"Deleted student with ID {del_student_id}. Please check Dashboard tab to confirm.")