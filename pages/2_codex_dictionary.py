import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="📊 Codex Keyword Classifier",
    page_icon="📊",
    layout="wide",
)

# Default keyword lists
DEFAULT_URGENCY = [
    "limited time",
    "last chance",
    "hurry",
    "act now",
    "today only",
    "expires soon",
    "final hours",
]
DEFAULT_EXCLUSIVE = [
    "exclusive",
    "members only",
    "vip",
    "special access",
    "invitation only",
    "early access",
]


def _initialize_state():
    """Ensure editable text areas keep user input between reruns."""
    if "urgency_text" not in st.session_state:
        st.session_state.urgency_text = "\n".join(DEFAULT_URGENCY)
    if "exclusive_text" not in st.session_state:
        st.session_state.exclusive_text = "\n".join(DEFAULT_EXCLUSIVE)
    if "classified_df" not in st.session_state:
        st.session_state.classified_df = None
    if "statement_column" not in st.session_state:
        st.session_state.statement_column = "Statement"


def _parse_keywords(block: str) -> list[str]:
    """Convert newline-delimited textarea input into a list of keywords."""
    if not block:
        return []
    return [line.strip() for line in block.splitlines() if line.strip()]


def _detect_statement_column(df: pd.DataFrame) -> str | None:
    """Locate the Statement column (case-insensitive)."""
    for col in df.columns:
        if col.lower() == "statement":
            return col
    return None


def _apply_classification(df: pd.DataFrame, column: str, keyword_map: dict[str, list[str]]):
    """Add dictionary flag columns to the provided DataFrame."""
    working_df = df.copy()
    statements = working_df[column].fillna("").astype(str)

    for tactic, words in keyword_map.items():
        lowered_keywords = [word.lower() for word in words if word.strip()]

        def has_match(text: str) -> int:
            text_lower = text.lower()
            return int(any(keyword in text_lower for keyword in lowered_keywords))

        working_df[f"{tactic}_flag"] = statements.apply(has_match)

    return working_df


_initialize_state()

st.title("📊 Codex Keyword Classifier")
st.markdown(
    "Upload a CSV that contains a `Statement` column, fine-tune the keyword dictionaries, "
    "and generate urgency/exclusive marketing flags in one click."
)

# Sidebar controls
st.sidebar.header("Upload CSV")
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV with a Statement column", type=["csv"], accept_multiple_files=False
)

st.sidebar.header("Keyword Dictionaries")
urgency_keywords_raw = st.sidebar.text_area(
    "urgency_marketing keywords (one per line)",
    key="urgency_text",
    height=150,
)
exclusive_keywords_raw = st.sidebar.text_area(
    "exclusive_marketing keywords (one per line)",
    key="exclusive_text",
    height=150,
)

run_clicked = st.sidebar.button("Run classification", type="primary")

if run_clicked:
    if uploaded_file is None:
        st.sidebar.error("Please upload a CSV file before running the classifier.")
    else:
        try:
            uploaded_file.seek(0)
            input_df = pd.read_csv(uploaded_file)
        except Exception as exc:
            st.sidebar.error(f"Unable to read CSV: {exc}")
            input_df = None

        if input_df is not None:
            statement_col = _detect_statement_column(input_df)
            if statement_col is None:
                st.sidebar.error("No `Statement` column found. Please add one to your CSV.")
            else:
                keywords = {
                    "urgency_marketing": _parse_keywords(urgency_keywords_raw),
                    "exclusive_marketing": _parse_keywords(exclusive_keywords_raw),
                }
                classified_df = _apply_classification(input_df, statement_col, keywords)
                st.session_state.classified_df = classified_df
                st.session_state.statement_column = statement_col
                st.success("Classification complete! See the results below.")

# Main content
if uploaded_file:
    uploaded_file.seek(0)
    preview_df = pd.read_csv(uploaded_file)
    st.subheader("Uploaded data preview")
    st.dataframe(preview_df.head(20), use_container_width=True)
else:
    st.info("Upload a CSV file from the sidebar to preview your data and enable classification.")

st.divider()
st.subheader("Classification results")

if st.session_state.classified_df is not None:
    st.dataframe(st.session_state.classified_df, use_container_width=True)
    csv_bytes = st.session_state.classified_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download classified CSV",
        data=csv_bytes,
        file_name="codex_keyword_classification.csv",
        mime="text/csv",
    )
else:
    st.info("Run the classifier to generate urgency and exclusive marketing flags.")
