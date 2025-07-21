import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

DB_FILE = "habits.db"

# --- Function Definitions ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Table for habit logs (username, habit, date)
    c.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            username TEXT NOT NULL,
            habit TEXT NOT NULL,
            date TEXT NOT NULL,
            PRIMARY KEY (username, habit, date)
        )
    ''')
    # Table for user's habit list
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_habits (
            username TEXT NOT NULL,
            habit TEXT NOT NULL,
            PRIMARY KEY (username, habit)
        )
    ''')
    conn.commit()
    conn.close()

def log_habit(username, habit, date_):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO habits (username, habit, date) VALUES (?, ?, ?)", (username, habit, date_))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # already logged
    conn.close()

def remove_habit(username, habit, date_):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM habits WHERE username = ? AND habit = ? AND date = ?", (username, habit, date_))
    conn.commit()
    conn.close()

def get_all_logs(username):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM habits WHERE username = ?", conn, params=(username,))
    conn.close()
    return df

def get_user_habits(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT habit FROM user_habits WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_user_habit(username, habit):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO user_habits (username, habit) VALUES (?, ?)", (username, habit))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # habit already exists
    conn.close()

def remove_user_habit(username, habit):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM user_habits WHERE username = ? AND habit = ?", (username, habit))
    conn.commit()
    conn.close()

def get_last_three_months_summary(df, habit):
    if df.empty:
     return None

    df = df[df["habit"] == habit].copy()
    
    # Force date to have only the date part (no time)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    today = pd.Timestamp.today().date()
    first_day_of_current_month = today.replace(day=1)
    two_months_ago = first_day_of_current_month - relativedelta(months=2)
    next_month = first_day_of_current_month + relativedelta(months=1)

    # Filter only relevant dates
    mask = (df["date"] >= two_months_ago) & (df["date"] < next_month)
    df_filtered = df[mask].copy()

    # Add year-month column for grouping
    df_filtered["year_month"] = pd.to_datetime(df_filtered["date"]).dt.to_period("M").astype(str)
    monthly_counts = df_filtered.groupby("year_month").size()

    # Build expected keys: prev-prev month, prev month, current month
    month_keys = [
        two_months_ago.strftime("%Y-%m"),
        (first_day_of_current_month - relativedelta(months=1)).strftime("%Y-%m"),
        first_day_of_current_month.strftime("%Y-%m"),
    ]

    # Create a series with counts (default to 0 if month missing)
    result = pd.Series({m: monthly_counts.get(m, 0) for m in month_keys})

    # Format index to 'Jul 2025', 'Jun 2025', etc.
    result.index = pd.to_datetime(result.index).strftime("%b %Y")
    
    # Set categorical index with correct order for plotting
    months_order = result.index.tolist()
    result.index = pd.CategoricalIndex(result.index, categories=months_order, ordered=True)

    return result


# CSS styling
st.markdown("""
<style>
    .title {
        font-size: 36px;
        font-weight: 700;
        color: #2C6E49;
        text-align: center;
        margin-bottom: 20px;
    }
    .habit-checkbox label {
        font-size: 18px;
        padding: 10px 0;
    }
    .progress-container {
        margin-top: 30px;
        margin-bottom: 30px;
        text-align: center;
        font-weight: 600;
        font-size: 20px;
        color: #2C6E49;
    }
    .habit-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize DB ---
init_db()

# --- Sidebar: User login ---
st.sidebar.header("👤 Login")

if "username" not in st.session_state or not st.session_state.username:
    username_input = st.sidebar.text_input("Enter your username", key="username_input")
    if username_input:
        st.session_state.username = username_input
        st.rerun()
    st.stop()

username = st.session_state.username

# --- Load or initialize user's habits ---
if "habits" not in st.session_state:
    habits_from_db = get_user_habits(username)
    if habits_from_db:
        st.session_state.habits = habits_from_db
    else:
        default_habits = ["Drink 1L Water", "Exercise", "Read", "Meditate", "Work on project", "Sleep early"]
        for habit in default_habits:
            add_user_habit(username, habit)
        st.session_state.habits = default_habits

# --- Main ---
today = date.today().isoformat()
df_logs = get_all_logs(username)

st.markdown('<div class="title">✅ My Habit Tracker</div>', unsafe_allow_html=True)
st.markdown(f"### Welcome, {username}!")

habit_emojis = {
    "Exercise": "🏃‍♂️",
    "Read": "📚",
    "Meditate": "🧘‍♀️",
    "Work on project": "💻",
    "Sleep early": "🌙",
    "Drink 1L Water": "💧",
}

# Habits with checkboxes and delete buttons
for habit in st.session_state.habits:
    checked = ((df_logs["habit"] == habit) & (df_logs["date"] == today)).any()
    label = f"{habit_emojis.get(habit, '✅')} {habit}"

    cols = st.columns([0.8, 0.2])
    with cols[0]:
        checked_new = st.checkbox(label, value=checked, key=f"chk_{habit}")
    with cols[1]:
        if st.button("Delete", key=f"del_{habit}"):
            remove_user_habit(username, habit)
            # Also delete all logs for that habit
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM habits WHERE username = ? AND habit = ?", (username, habit))
            conn.commit()
            conn.close()
            st.session_state.habits.remove(habit)
            st.rerun()

    # Handle checkbox changes
    if checked_new and not checked:
        log_habit(username, habit, today)
        st.rerun()
    if not checked_new and checked:
        remove_habit(username, habit, today)
        st.rerun()

# Daily completion progress
completed = df_logs[df_logs["date"] == today]["habit"].nunique()
total = len(st.session_state.habits)
progress = completed / total if total > 0 else 0
st.markdown(f'<div class="progress-container">Daily Completion: {completed} / {total} habits</div>', unsafe_allow_html=True)
st.progress(progress)

# Add new habit input
st.markdown("## ➕ Add a New Habit")
new_habit = st.text_input("New habit name", key="new_habit_input")
add_clicked = st.button("Add Habit")

if add_clicked:
    new_habit_clean = new_habit.strip()
    if new_habit_clean:
        if new_habit_clean not in st.session_state.habits:
            add_user_habit(username, new_habit_clean)
            st.session_state.habits.append(new_habit_clean)
            st.success(f"Added habit: {new_habit_clean}")
            st.rerun()
        else:
            st.warning(f"Habit '{new_habit_clean}' already exists")
    else:
        st.error("Please enter a valid habit name")

# --- Monthly summary plot code (optional, unchanged) ---
st.markdown("---")
st.markdown("### 📊 Last 2 Months Habit Completions")

selected_habit = st.selectbox("Select habit to plot", st.session_state.habits)

monthly_data = get_last_three_months_summary(df_logs, selected_habit)

if monthly_data is not None:
    st.bar_chart(monthly_data)
else:
    st.write("No data available for this habit yet.")