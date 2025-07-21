# habit_tracker

# ✅ My Habit Tracker

A simple, clean and personal **habit tracking app** built with [Streamlit] and [SQLite]

📅 Log your daily habits, track progress over time, and stay motivated with visual feedback!

##  Features

- 👤 Login with your own username (no password needed)
- ✅ Check off daily habits with one click
- ➕ Add or delete custom habits
- 📊 View monthly progress with interactive bar charts
- 💾 Data stored locally in a lightweight SQLite database habits_db

## 🚀 Live Demo

🌐 [Click here to try it on Streamlit Cloud] https://habittracker-cptxusg3qrljqdq5gp7hct.streamlit.app/

## 💾 Data Persistence Notes

This app uses a local **SQLite database** (`habits.db`) to store all habit logs and user data.

- When running **locally**, your data is stored permanently in the file system.
- When deployed on **Streamlit Cloud** and run it using the link above https://habittracker-cptxusg3qrljqdq5gp7hct.streamlit.app/ , the database file is temporary and may be:
  - **Reset** after app updates or long inactivity,
  - **Deleted** on server restarts.
 
## 🛠️ How to Run the App Locally

 1. Make sure you have Python installed. You need Python 3.7 or higher.
 2. Clone or download the GitHub repo
    - If you have Git installed, clone the repo by running in your terminal:
      ```bash
      git clone https://github.com/AntigoniD/habit_tracker.git
      ```
    - Or, you can download the repo as a ZIP file from GitHub and extract it.
 3. Navigate to the project folder, by running to your terminal:
     ```bash
     cd habit_tracker
     ```
 4. (Optional) Create and activate a virtual environment.
     It's a good practice to isolate dependencies.
     **On Windows:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ````
 5. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```
 6. Run the app:
    ```bash
    streamlit run app.py
    ```
 7. Open the app in your browser. Usually at http://localhost:8501




