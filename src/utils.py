import streamlit as st

def digit_slider(label, key):
    return st.slider(label, 6, 12, 6, step=1, key=key)

def recent_exclude_ui(default=True, key_prefix=""):
    col1, col2 = st.columns([1, 2])
    with col1:
        exclude = st.checkbox("Exclude ALL latest drawn numbers", value=default, key=f"{key_prefix}_exclude_recent")
    with col2:
        if exclude:
            exclude_n = st.slider("Exclude the latest n draws:", 1, 5, 1, key=f"{key_prefix}_exclude_n_recent")
        else:
            exclude_n = 0
    return exclude, exclude_n

def fill_unique_numbers(generate_func, df, existing, num_digits, **kwargs):
    guess = sorted(set(existing))
    while len(guess) < num_digits:
        extra = generate_func(df, num_digits=num_digits, **kwargs)
        for n in extra:
            if n not in guess:
                guess.append(n)
            if len(guess) == num_digits:
                break
    return sorted(guess)