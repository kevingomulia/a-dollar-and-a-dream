import streamlit as st
import pandas as pd
from guess import (
    generate_random_guess,
    generate_smart_guess,
    get_number_frequencies,
    generate_clustered_guess,
    get_recent_numbers
)
from utils import digit_slider, recent_exclude_ui, fill_unique_numbers

from pathlib import Path
import os
from datetime import datetime

# --- Load Draw Data ---
def load_data(file_path_or_buffer):
    df = pd.read_csv(file_path_or_buffer)
    win_cols = ["Winning Number 1", "2", "3", "4", "5", "6"]
    df["Winning Numbers"] = df[win_cols].values.tolist()
    return df

# --- Default Data Loader ---
def get_default_data():
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    default_path = DATA_DIR / "ToTo.csv"
    if os.path.exists(default_path):
        return load_data(default_path)
    return None

# --- Append New Draw ---
def append_new_draw(new_row):
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    file_path = DATA_DIR / "ToTo.csv"
    df = pd.read_csv(file_path)
    df = pd.concat([pd.DataFrame([new_row]), df], ignore_index=True)
    df.to_csv(file_path, index=False)

# --- Streamlit Config ---
st.set_page_config(page_title="A Dollar and A Dream", layout="wide", page_icon="🎰")
st.title("Singapore TOTO Number Generator")
st.warning("Please gamble responsibly. This is for entertainment purposes only.")
tabs = st.tabs(["🎲 Random Guess", "📈 Smart Guess (Weighted)", "🔥 Hot-Warm-Cold Strategy", "📅 Add New Draw"])

# --- Tab 1: Random Guess ---
with tabs[0]:
    st.header("One Dollar and A Dream")
    num_digits = digit_slider("How many numbers per set?", "num_digits")
    num_guesses = st.slider("Number of sets to generate", 1, 10, 1)
    if st.button("HUAT AH! Generate Random Guesses"):
        for i in range(num_guesses):
            st.write(f"Set {i+1}: {generate_random_guess(num_digits)}")

# --- Tab 2: Smart Guess ---
with tabs[1]:
    st.header("Smart Guess Based on Historical Draws")
    default_df = get_default_data()
    uploaded_file = st.file_uploader("Upload TOTO Past Draws CSV (optional)", type="csv")
    df = load_data(uploaded_file) if uploaded_file else default_df
    if df is None:
        st.error("No data available.")
        st.stop()

    st.info(f"Using draw data up to: **{df.iloc[0]['Date']}**")
    with st.expander("🎯 Smart Guess Settings"):
        strategy = st.radio("Strategy", ["frequent", "rare"])
        exclude_recent, exclude_n_recent = recent_exclude_ui(key_prefix="smart")
        col1, col2 = st.columns([1, 2])
        with col1:
            weight_strength = st.slider("Weight strength", 0.0, 3.0, 1.0, 0.1)
        with col2:
            st.info("0 = random\n3 = strong bias")

    num_digits = digit_slider("How many numbers per set?", "smart_num_digits")
    num_smart_guesses = st.slider("Number of smart guesses", 1, 10, 1)

    if exclude_recent and exclude_n_recent > 0:
        st.info(f"Excluded numbers from recent draws: {get_recent_numbers(df, exclude_n_recent)}")

    if st.button("Generate Weighted HUAT Guesses"):
        for i in range(num_smart_guesses):
            raw_guess = generate_smart_guess(
                df,
                strategy=strategy,
                exclude_recent=exclude_recent,
                exclude_n_recent=exclude_n_recent,
                weight_strength=weight_strength,
                num_digits=num_digits
            )
            final_guess = fill_unique_numbers(
                generate_func=generate_smart_guess,
                df=df,
                existing=raw_guess,
                num_digits=num_digits,
                strategy=strategy,
                exclude_recent=exclude_recent,
                exclude_n_recent=exclude_n_recent,
                weight_strength=weight_strength
            )
            st.write(f"Smart Set {i+1}: {final_guess}")

    if st.checkbox("Stats for nerds"):
        freq = get_number_frequencies(df)
        freq_df = pd.DataFrame(freq.items(), columns=["Number", "Frequency"]).sort_values("Frequency", ascending=False)
        st.dataframe(freq_df.reset_index(drop=True), use_container_width=True, hide_index=True)

# --- Tab 3: Clustered Guess ---
with tabs[2]:
    st.header("Hot-Warm-Cold Frequency Strategy")
    if df is None:
        st.warning("No data loaded.")
        st.stop()

    st.info(f"Using draw data up to: **{df.iloc[0]['Date']}**")
    with st.expander("🎯 Clustered Guess Settings"):
        exclude_recent, exclude_n_recent = recent_exclude_ui(key_prefix="cluster")
        if exclude_recent and exclude_n_recent > 0:
            st.info(f"Excluded numbers from recent draws: {get_recent_numbers(df, exclude_n_recent)}")

    num_digits = digit_slider("How many numbers per set?", "cluster_num_digits")
    num_cluster_guesses = st.slider("Number of guesses", 1, 10, 1, key="cluster_slider")
    if st.button("Generate Clustered HUAT Guesses"):
        for i in range(num_cluster_guesses):
            guess = generate_clustered_guess(
                df,
                exclude_recent=exclude_recent,
                exclude_n_recent=exclude_n_recent,
                num_digits=num_digits
            )
            st.write(f"Clustered Set {i+1}: {guess}")

    st.info("""
        - Groups numbers by how often they appear: Hot (appears frequently), Warm, or Cold (appears rarely).
        - Picks equal numbers from each group for each guess.
        - Excludes recently drawn numbers if selected.""")

# --- Tab 4: Add New Draw ---
with tabs[3]:
    password = st.text_input("Enter admin password to submit draws", type="password")
    correct_password = st.secrets["auth"]["submission_password"]

    if password != correct_password:
        st.warning("Enter the correct password to unlock submission form.")
        st.stop()

    st.header("Add New TOTO Draw Result")
    df = get_default_data()
    if df is not None:
        last_draw = int(df.iloc[0]["Draw"])
        new_draw_num = last_draw + 1
        st.write(f"**New Draw Number:** {new_draw_num}")
        new_date = st.date_input("Draw Date", value=datetime.today())

        numbers = []
        cols = st.columns(6)
        for i in range(6):
            with cols[i]:
                num = st.number_input(f"Number {i+1}", min_value=1, max_value=49, step=1, key=f"num_{i}")
                numbers.append(int(num))

        add_num = st.number_input("Additional Number", min_value=1, max_value=49, step=1, key="add_num")

        if st.button("Submit New Draw"):
            low = min(numbers)
            high = max(numbers)
            odd = len([n for n in numbers if n % 2 == 1])
            even = 6 - odd
            r1 = sum(1 for n in numbers if 1 <= n <= 10)
            r2 = sum(1 for n in numbers if 11 <= n <= 20)
            r3 = sum(1 for n in numbers if 21 <= n <= 30)
            r4 = sum(1 for n in numbers if 31 <= n <= 40)
            r5 = sum(1 for n in numbers if 41 <= n <= 50)

            previous_numbers = set(df.iloc[0]["Winning Numbers"])
            from_last = ",".join([str(n) for n in numbers if n in previous_numbers])

            row = {
                "Draw": new_draw_num,
                "Date": new_date.strftime("%Y-%m-%d"),
                "Winning Number 1": numbers[0],
                "2": numbers[1],
                "3": numbers[2],
                "4": numbers[3],
                "5": numbers[4],
                "6": numbers[5],
                "Additional Number": add_num,
                "From Last": from_last,
                "Low": low,
                "High": high,
                "Odd": odd,
                "Even": even,
                "1-10": r1,
                "11-20": r2,
                "21-30": r3,
                "31-40": r4,
                "41-50": r5,
                "Division 1 Winners": 0,
                "Division 1 Prize": "0.00",
                "Division 2 Winners": 0,
                "Division 2 Prize": "0.00",
                "Division 3 Winners": 0,
                "Division 3 Prize": "0.00",
                "Division 4 Winners": 0,
                "Division 4 Prize": "0.00",
                "Division 5 Winners": 0,
                "Division 5 Prize": "0.00",
                "Division 6 Winners": 0,
                "Division 6 Prize": "0.00",
                "Division 7 Winners": 0,
                "Division 7 Prize": "0.00"
            }
            append_new_draw(row)
            st.success("New draw added successfully!")