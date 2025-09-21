# Automated OMR Evaluation & Scoring System

## Features

- Upload OMR sheets (image files, e.g., JPEG/PNG)
- Automated bubble detection and scoring (per subject, total)
- Supports multiple OMR versions (answer keys in JSON)
- Stores results in SQLite DB (MVP)
- Streamlit dashboard for upload, scoring, and review

## Setup

1. Clone this repo or copy the folder structure.
2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the app:

    ```bash
    streamlit run web_app/app.py
    ```

4. Upload a sample OMR image, enter Student ID, select version, and view results.

## Extending

- Add more answer keys in `omr_core/answer_key.json`
- For Flask or FastAPI backend, move core logic to API views.
- For real OMR sheet layouts, update `detect_bubbles()` for exact grid/bubble positions.
- Export results from SQLite to CSV/Excel as needed.

## Notes

- This is an MVP. For production, add authentication, error handling, real OMR calibration, and ML bubble classifiers for high accuracy.