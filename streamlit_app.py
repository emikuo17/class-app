import streamlit as st
import pandas as pd
import json

# -------------------------------------------------------------------
# Default marketing keyword dictionaries
# -------------------------------------------------------------------
DEFAULT_DICTIONARIES = {
    'urgency_marketing': {
        'limited', 'limited time', 'limited run', 'limited edition', 'order now',
        'last chance', 'hurry', 'while supplies last', "before they're gone",
        'selling out', 'selling fast', 'act now', "don't wait", 'today only',
        'expires soon', 'final hours', 'almost gone'
    },
    'exclusive_marketing': {
        'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
        'members only', 'vip', 'special access', 'invitation only',
        'premium', 'privileged', 'limited access', 'select customers',
        'insider', 'private sale', 'early access'
    }
}

# -------------------------------------------------------------------
# Helper classification function
# -------------------------------------------------------------------
def classify_statement(text: str, dictionaries: dict) -> list[str]:
    text_lower = text.lower()
    matched = []
    for label, keywords in dictionaries.items():
        if any(kw in text_lower for kw in keywords):
            matched.append(label)
    return matched

# -------------------------------------------------------------------
# Streamlit App
# -------------------------------------------------------------------
def main():
    st.title("📊 Marketing Statement Classifier")
    st.write("Upload a CSV file and modify the keyword dictionaries to classify marketing statements.")

    # --- Sidebar dictionary editor ----------------------------------------
    st.sidebar.header("📝 Keyword Dictionaries")

    # store dictionaries in session_state
    if "dictionaries" not in st.session_state:
        st.session_state.dictionaries = {k: list(v) for k, v in DEFAULT_DICTIONARIES.items()}

    # editable dictionary UI
    for label in list(st.session_state.dictionaries.keys()):
        with st.sidebar.expander(f"Edit: {label}", expanded=False):
            keywords_text = st.text_area(
                f"Enter keywords for **{label}** (one per line):",
                value="\n".join(st.session_state.dictionaries[label]),
                key=f"dict_{label}"
            )
            # Save back to session state
            st.session_state.dictionaries[label] = [
                kw.strip() for kw in keywords_text.split("\n") if kw.strip()
            ]

    st.sidebar.write("---")
    st.sidebar.write("Add new category:")
    new_cat = st.sidebar.text_input("New category name:")
    if st.sidebar.button("Add category"):
        if new_cat and new_cat not in st.session_state.dictionaries:
            st.session_state.dictionaries[new_cat] = []
        else:
            st.sidebar.warning("Category already exists or name is empty.")

    # --- File upload --------------------------------------------------------
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("### 🔍 Preview of uploaded data:")
        st.write(df.head())

        if "Statement" not in df.columns:
            st.error("❌ The uploaded CSV must contain a column named **'Statement'**.")
            return

        # --- Classification -------------------------------------------------
        dictionaries = {k: set(v) for k, v in st.session_state.dictionaries.items()}

        df["labels"] = df["Statement"].astype(str).apply(
            lambda x: classify_statement(x, dictionaries)
        )

        # One-hot encoding columns
        for label in dictionaries:
            df[label] = df["labels"].apply(lambda cats, lbl=label: lbl in cats)

        st.write("### ✅ Classified Data Preview:")
        st.dataframe(df)

        # --- Download -------------------------------------------------------
        csv_output = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Classified CSV",
            csv_output,
            file_name="classified_output.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
