import os

import pandas as pd
import plotly.express as px
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="RegLab Tool Starter",
    layout="wide",
)

# --- PROFESSIONAL STYLING ---
# This CSS hides the Streamlit "hamburger" menu and footer for a cleaner look
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Reduce top whitespace so content appears higher on the page */
            .block-container, section[data-testid="stAppViewContainer"] .main .block-container {
                padding-top: 0rem !important;
                margin-top: 0rem !important;
            }
            /* Tighter spacing for the top-level app container */
            section[data-testid="stAppViewContainer"] > div {
                padding-top: 0rem !important;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


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
    # Authentication disabled by user request (option 1)
    return True


# --- APP START ---

if not check_password():
    st.stop()

example_path = "data/metrics_collapsed_vs_not.csv"
if os.path.exists(example_path):
    df_example = pd.read_csv(example_path)

    # --- USER SELECTIONS ---
    # Argument choices with display names
    arg_display_map = {
        "Strategy + prompt": "strategy_prompt",
        "Model": "model",
        "Non-conflicts are related?": "related_nonconflicts",
        "Labels?": "labels",
        "Cross-references?": "cross_refs",
    }

    # Base performance metric choices (we'll show collapsed vs non-collapsed automatically)
    base_metrics = ["precision", "accuracy", "recall", "f1_score"]

    # No sidebar — controls are shown on the main page

    # Main-page visible controls placed near the top so users don't have to open anything
    cols = st.columns([1, 1, 1])
    with cols[0]:
        arg_choice_label = st.selectbox("Select argument (group by)", list(arg_display_map.keys()), key="arg_choice_main")
    with cols[1]:
        metric_choice = st.selectbox("Select performance metric", base_metrics, key="metric_choice_main")
    # Mirror sidebar selections into session state if user used sidebar instead
    if not arg_choice_label:
        arg_choice_label = st.session_state.get("arg_choice_sidebar")
    if not metric_choice:
        metric_choice = st.session_state.get("metric_choice_sidebar")

    arg_col = arg_display_map[arg_choice_label]

    # base metric selected directly
    base_metric = metric_choice

    collapsed_col = f"{base_metric}_c"
    noncollapsed_col = base_metric

    # Validate required columns exist
    missing = [c for c in (arg_col, collapsed_col, noncollapsed_col) if c not in df_example.columns]
    if missing:
        st.error(f"Missing required columns in CSV: {missing}")
    else:
        # Prepare grouped averages
        # Treat the argument column as string/categorical for grouping
        df = df_example.copy()
        df[arg_col] = df[arg_col].astype(str)

        grouped = df.groupby(arg_col).agg(
            collapsed_mean=(collapsed_col, "mean"),
            noncollapsed_mean=(noncollapsed_col, "mean"),
        )
        grouped = grouped.reset_index()

        # Melt into long form for plotting
        plot_df = grouped.melt(
            id_vars=[arg_col],
            value_vars=["collapsed_mean", "noncollapsed_mean"],
            var_name="Type",
            value_name="Value",
        )

        # Rename Type values for display
        plot_df["Type"] = plot_df["Type"].map({
            "collapsed_mean": "Collapsed",
            "noncollapsed_mean": "Non-collapsed",
        })

        # Sort categories for consistent plotting (optional: by total mean)
        try:
            order = (
                grouped.assign(total_mean=(grouped["collapsed_mean"] + grouped["noncollapsed_mean"]) / 2)
                .sort_values("total_mean", ascending=False)[arg_col]
                .tolist()
            )
        except Exception:
            order = grouped[arg_col].tolist()

        # Create a horizontal grouped bar chart: Value on x, category (argument) on y
        color_map = {"Non-collapsed": "#32558f", "Collapsed": "#a1beed"}

        # Determine Type order from the data so legend matches plotted order
        type_order = plot_df["Type"].drop_duplicates().tolist()

        fig = px.bar(
            plot_df,
            x="Value",
            y=arg_col,
            color="Type",
            barmode="group",
            orientation="h",
            category_orders={arg_col: order, "Type": type_order},
            color_discrete_map=color_map,
            labels={
                arg_col: arg_choice_label,
                "Value": f"Average {base_metric} (collapsed vs non-collapsed)",
            },
            title=f"Average {base_metric}: Collapsed vs Non-collapsed by {arg_choice_label}",
        )

        fig.update_layout(xaxis_title=f"Average {base_metric}", yaxis_title=arg_choice_label)

        st.plotly_chart(fig, use_container_width=True)

        # Optionally show the aggregated table below the plot for reference (collapsible)
        with st.expander("Show aggregated numbers"):
            st.dataframe(grouped.rename(columns={"collapsed_mean": collapsed_col, "noncollapsed_mean": noncollapsed_col}))
else:
    st.error("Example file not found.")
