import os

import pandas as pd
import plotly.express as px
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="RegLab Tool Starter",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- PROFESSIONAL STYLING ---
# This CSS hides the Streamlit "hamburger" menu and footer for a cleaner look
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Force sidebar to stay open using JavaScript injection
st.components.v1.html(
    """
<script>
(function() {
    function disableSidebarCollapse() {
        // Find and remove all possible collapse buttons
        const selectors = [
            'button[aria-label*="sidebar"]',
            'button[title*="sidebar"]',
            '[data-testid*="sidebar"][data-testid*="collapse"]',
            '[data-testid*="Collapse"]',
            'button:has(svg[viewBox*="0 0"])',
        ];
        
        selectors.forEach(selector => {
            try {
                document.querySelectorAll(selector).forEach(el => {
                    if (el.textContent?.toLowerCase().includes('close') || 
                        el.getAttribute('aria-label')?.toLowerCase().includes('sidebar') ||
                        el.getAttribute('title')?.toLowerCase().includes('sidebar')) {
                        el.style.display = 'none';
                        el.remove();
                    }
                });
            } catch(e) {}
        });
        
        // Force sidebar to be visible
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.display = 'block';
            sidebar.style.visibility = 'visible';
        }
    }
    
    // Run on load and continuously
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', disableSidebarCollapse);
    } else {
        disableSidebarCollapse();
    }
    
    // Check periodically
    setInterval(disableSidebarCollapse, 200);
})();
</script>
""",
    height=0,
)


# --- AUTHENTICATION ---
def get_secret(key):
    """Helper to get secrets from Streamlit secrets or Environment Variables."""
    try:
        # 1. Try Streamlit Secrets (local secrets.toml or Streamlit Cloud)
        if key in st.secrets:
            return st.secrets[key]
        if key.upper() in st.secrets:
            return st.secrets[key.upper()]
    except Exception:
        pass

    # 2. Fallback to Environment Variables (Railway, Render, etc.)
    return os.environ.get(key) or os.environ.get(key.upper())


def check_password():
    """Returns `True` if the user had the correct password."""
    master_password = get_secret("password")

    if not master_password:
        return True

    # If already authenticated, just return True
    if st.session_state.get("password_correct"):
        return True

    # Show the login form
    st.subheader("🔒 Password Required")
    user_password = st.text_input("Please enter the password", type="password")

    if user_password:
        if str(user_password).strip() == str(master_password).strip():
            st.session_state["password_correct"] = True
            st.rerun()  # Refresh the app to show the content
        else:
            st.error("😕 Password incorrect")

    return False


# --- APP START ---

# 1. AUTHENTICATION CHECK
# We use our helper to check for the password
if not check_password():
    st.stop()

# 2. HEADER SECTION
st.title("🧪 Researcher's Web App Starter")
st.markdown("""
Welcome! This app is a template to help you turn your data scripts into interactive tools.
Edit `app.py` to customize this.
""")

# 3. SIDEBAR - INPUTS
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV or JSON file", type=["csv", "json"])

    st.info("💡 **Pro-tip:** Use `st.sidebar` to keep controls organized.")

# 4. MAIN CONTENT - DATA LOADING
if uploaded_file is not None:
    # Determine file type and load accordingly
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_json(uploaded_file)

    st.subheader("Data Overview")

    # 5. DATA DISPLAY (Command: st.dataframe)
    st.write(f"Showing {len(df)} rows:")
    st.dataframe(df, use_container_width=True)

    # 6. FILTERING (Command: st.selectbox, st.slider)
    st.divider()
    st.subheader("Interactive Analysis")

    col1, col2 = st.columns(2)

    with col1:
        if "Category" in df.columns:
            categories = df["Category"].unique()
            selected_cat = st.multiselect(
                "Filter by Category", options=categories, default=categories
            )
            filtered_df = df[df["Category"].isin(selected_cat)]
        else:
            filtered_df = df
            st.warning("No 'Category' column found for filtering.")

    with col2:
        if "Value" in df.columns:
            min_val, max_val = int(df["Value"].min()), int(df["Value"].max())
            val_range = st.slider(
                "Filter by Value Range", min_val, max_val, (min_val, max_val)
            )
            filtered_df = filtered_df[
                (filtered_df["Value"] >= val_range[0])
                & (filtered_df["Value"] <= val_range[1])
            ]

    # 7. VISUALIZATION (Command: st.plotly_chart)
    st.write(f"Filtered results: {len(filtered_df)} rows")

    tab1, tab2, tab3 = st.tabs(["📊 Chart", "🗺️ Map", "📈 Statistics"])

    with tab1:
        if not filtered_df.empty:
            fig = px.bar(
                filtered_df,
                x=filtered_df.index,
                y="Category",
                color="Date",
                title="Values by Category",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available for the current filters.")

    with tab2:
        if "Latitude" in df.columns and "Longitude" in df.columns:
            # 8. MAP (Command: st.map)
            st.map(filtered_df, latitude="Latitude", longitude="Longitude")
        else:
            st.info(
                "To see a map, ensure your data has 'Latitude' and 'Longitude' columns."
            )

    with tab3:
        st.write("Summary Statistics:")
        st.write(filtered_df.describe())

else:
    st.info(
        "Please upload a file to get started. You can find sample data in the `sample_data` folder."
    )

    # Show example of how to load local data
    if st.checkbox("Show Example Data"):
        example_path = "sample_data/example.csv"
        if os.path.exists(example_path):
            df_example = pd.read_csv(example_path)
            st.write("This is what `example.csv` looks like:")
            st.dataframe(df_example.head())
            if "Latitude" in df_example.columns and "Longitude" in df_example.columns:
                st.map(df_example, latitude="Latitude", longitude="Longitude")
            else:
                st.warning("No 'Latitude' or 'Longitude' columns found for mapping.")
        else:
            st.error("Example file not found.")

# --- FOOTER ---
st.divider()
st.caption("Built with Streamlit • 2025 Researcher Workshop")

# --- SUMMARY OF COMMON COMMANDS ---
# 1. st.write() - The Swiss Army knife: prints text, dataframes, objects.
# 2. st.dataframe() - Displays interactive tables.
# 3. st.selectbox() / st.multiselect() - For dropdown menus.
# 4. st.slider() - For numeric range input.
# 5. st.file_uploader() - To let users upload their own data.
# 6. st.columns() - To layout your app side-by-side.
# 7. st.sidebar - To put controls in the left panel.
# 8. st.plotly_chart() - For beautiful interactive charts.
# 9. st.map() - For quick geospatial visualization.
# 10. st.secrets - For accessing API keys or passwords securely.
