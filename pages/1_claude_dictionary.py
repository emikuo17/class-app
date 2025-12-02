import streamlit as st
import pandas as pd
import json
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Marketing Tactics Classifier",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for dictionaries
if 'dictionaries' not in st.session_state:
    st.session_state.dictionaries = {
        'urgency_marketing': [
            'limited', 'limited time', 'limited run', 'limited edition', 'order now',
            'last chance', 'hurry', 'while supplies last', 'before they\'re gone',
            'selling out', 'selling fast', 'act now', 'don\'t wait', 'today only',
            'expires soon', 'final hours', 'almost gone'
        ],
        'exclusive_marketing': [
            'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
            'members only', 'vip', 'special access', 'invitation only',
            'premium', 'privileged', 'limited access', 'select customers',
            'insider', 'private sale', 'early access'
        ]
    }

if 'classified_data' not in st.session_state:
    st.session_state.classified_data = None

def classify_statement(text, dictionaries):
    """Classify a statement based on marketing tactic dictionaries."""
    if pd.isna(text) or not text:
        return {}
    
    text_lower = str(text).lower()
    results = {}
    
    for tactic, keywords in dictionaries.items():
        matches = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matches.append(keyword)
        
        results[tactic] = {
            'present': len(matches) > 0,
            'count': len(matches),
            'matches': matches
        }
    
    return results

def process_data(df, dictionaries):
    """Process the uploaded data and classify statements."""
    # Find statement column
    statement_col = None
    for col in df.columns:
        if 'statement' in col.lower() or 'text' in col.lower():
            statement_col = col
            break
    
    if statement_col is None:
        statement_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    # Apply classification
    df['classification'] = df[statement_col].apply(lambda x: classify_statement(x, dictionaries))
    
    # Extract results to separate columns
    for tactic in dictionaries.keys():
        df[f'{tactic}_present'] = df['classification'].apply(
            lambda x: x.get(tactic, {}).get('present', False)
        )
        df[f'{tactic}_count'] = df['classification'].apply(
            lambda x: x.get(tactic, {}).get('count', 0)
        )
        df[f'{tactic}_matches'] = df['classification'].apply(
            lambda x: ', '.join(x.get(tactic, {}).get('matches', []))
        )
    
    return df, statement_col

# Header
st.title("📊 Marketing Tactics Classifier")
st.markdown("Upload your dataset and classify marketing statements based on customizable tactic dictionaries.")

# Tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload Data", "📚 Manage Dictionaries", "📊 Results"])

# Tab 1: Upload Data
with tab1:
    st.header("Upload Your Dataset")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ File uploaded successfully! {len(df)} rows loaded.")
        
        st.subheader("Preview of uploaded data")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("🚀 Classify Data", type="primary", use_container_width=True):
            with st.spinner("Classifying statements..."):
                classified_df, statement_col = process_data(df.copy(), st.session_state.dictionaries)
                st.session_state.classified_data = classified_df
                st.session_state.statement_col = statement_col
                st.success("✅ Classification complete! Go to the Results tab to view.")
                st.rerun()

# Tab 2: Manage Dictionaries
with tab2:
    st.header("Manage Marketing Tactic Dictionaries")
    
    # Add new tactic
    col1, col2 = st.columns([3, 1])
    with col1:
        new_tactic = st.text_input("New Tactic Name", placeholder="e.g., scarcity_marketing")
    with col2:
        st.write("")
        st.write("")
        if st.button("➕ Add Tactic"):
            if new_tactic and new_tactic not in st.session_state.dictionaries:
                st.session_state.dictionaries[new_tactic] = []
                st.success(f"Added tactic: {new_tactic}")
                st.rerun()
            elif new_tactic in st.session_state.dictionaries:
                st.error("Tactic already exists!")
    
    st.divider()
    
    # Display and edit existing tactics
    for tactic in list(st.session_state.dictionaries.keys()):
        with st.expander(f"📋 {tactic.replace('_', ' ').title()}", expanded=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                new_keyword = st.text_input(
                    "Add keyword",
                    key=f"keyword_{tactic}",
                    placeholder="Enter a keyword..."
                )
            
            with col2:
                st.write("")
                st.write("")
                if st.button("Add", key=f"add_{tactic}"):
                    if new_keyword and new_keyword not in st.session_state.dictionaries[tactic]:
                        st.session_state.dictionaries[tactic].append(new_keyword)
                        st.rerun()
            
            # Display keywords
            keywords = st.session_state.dictionaries[tactic]
            if keywords:
                st.write(f"**Keywords ({len(keywords)}):**")
                
                # Create a grid of keywords with delete buttons
                cols_per_row = 3
                for i in range(0, len(keywords), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col in enumerate(cols):
                        if i + j < len(keywords):
                            keyword = keywords[i + j]
                            with col:
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.text(keyword)
                                with col2:
                                    if st.button("🗑️", key=f"del_{tactic}_{i+j}"):
                                        st.session_state.dictionaries[tactic].remove(keyword)
                                        st.rerun()
            else:
                st.info("No keywords yet. Add some above!")
            
            # Delete tactic button
            if st.button(f"🗑️ Delete {tactic} tactic", key=f"delete_tactic_{tactic}"):
                del st.session_state.dictionaries[tactic]
                st.rerun()
    
    st.divider()
    
    # Export/Import dictionaries
    st.subheader("Export/Import Dictionaries")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Export Dictionaries (JSON)",
            data=json.dumps(st.session_state.dictionaries, indent=2),
            file_name="marketing_dictionaries.json",
            mime="application/json"
        )
    
    with col2:
        imported_file = st.file_uploader("📤 Import Dictionaries (JSON)", type=['json'])
        if imported_file is not None:
            imported_dict = json.load(imported_file)
            st.session_state.dictionaries = imported_dict
            st.success("✅ Dictionaries imported successfully!")
            st.rerun()

# Tab 3: Results
with tab3:
    st.header("Classification Results")
    
    if st.session_state.classified_data is not None:
        df = st.session_state.classified_data
        
        # Summary statistics
        st.subheader("📈 Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Statements", len(df))
        
        with col2:
            any_tactic = df[[f'{t}_present' for t in st.session_state.dictionaries.keys()]].any(axis=1).sum()
            st.metric("Statements with Any Tactic", any_tactic)
        
        with col3:
            st.metric("Tactics Analyzed", len(st.session_state.dictionaries))
        
        st.divider()
        
        # Tactic-specific statistics
        st.subheader("📊 Tactic Breakdown")
        
        for tactic in st.session_state.dictionaries.keys():
            total_present = df[f'{tactic}_present'].sum()
            percentage = (total_present / len(df) * 100)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(percentage / 100, text=f"{tactic.replace('_', ' ').title()}")
            with col2:
                st.metric("", f"{total_present}/{len(df)} ({percentage:.1f}%)")
        
        st.divider()
        
        # Detailed results
        st.subheader("📋 Detailed Results")
        
        # Filter options
        filter_tactic = st.selectbox(
            "Filter by tactic",
            ["All"] + list(st.session_state.dictionaries.keys())
        )
        
        display_df = df.copy()
        if filter_tactic != "All":
            display_df = display_df[display_df[f'{filter_tactic}_present']]
        
        # Display columns
        display_cols = [col for col in df.columns if col not in ['classification']]
        st.dataframe(display_df[display_cols], use_container_width=True)
        
        # Download results
        csv = display_df[display_cols].to_csv(index=False)
        st.download_button(
            label="📥 Download Results (CSV)",
            data=csv,
            file_name="classified_data.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    else:
        st.info("👆 Upload a dataset in the 'Upload Data' tab and click 'Classify Data' to see results here.")

# Footer
st.divider()
st.markdown("---")
st.markdown("**Marketing Tactics Classifier** | Built with Streamlit")
