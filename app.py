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
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container, section[data-testid="stAppViewContainer"] .main .block-container {
                padding-top: 0.5rem !important;
                margin-top: 0rem !important;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- APP START ---

example_path = "data/metrics_collapsed_vs_not.csv"
if os.path.exists(example_path):
    df_example = pd.read_csv(example_path)

    # --- USER SELECTIONS ---
    # Added "Individual Runs" to the map
    arg_display_map = {
        "Individual Runs (All Metadata)": "all_metadata",
        "Strategy + prompt": "strategy_prompt",
        "Model": "model",
        "Non-conflicts are related?": "related_nonconflicts",
        "Labels?": "labels",
        "Cross-references?": "cross_refs",
    }

    base_metrics = ["precision", "accuracy", "recall", "f1_score"]

    cols = st.columns([1, 1, 1])
    with cols[0]:
        arg_choice_label = st.selectbox("Select display mode", list(arg_display_map.keys()), key="arg_choice_main")
    with cols[1]:
        metric_choice = st.selectbox("Select performance metric", base_metrics, key="metric_choice_main")

    arg_col = arg_display_map[arg_choice_label]
    base_metric = metric_choice
    collapsed_col = f"{base_metric}_c"
    noncollapsed_col = base_metric

    # Prepare the dataframe
    df = df_example.copy()

    # --- LOGIC FOR "ALL METADATA" LABELING ---
    if arg_col == "all_metadata":
        # Construct the detailed label string requested
        # Format: prompt / model / related_nonconflicts {val} / labels {val} / cross_refs {val}
        df[arg_col] = (
            df['strategy_prompt'].astype(str) + " / " +
            df['model'].astype(str) + " / " +
            "related_nonconflicts " + df['related_nonconflicts'].astype(str) + " / " +
            "labels " + df['labels'].astype(str) + " / " +
            "cross_refs " + df['cross_refs'].astype(str)
        )
        # Since these are individual runs, "grouping" just takes the raw values
        grouped = df[[arg_col, collapsed_col, noncollapsed_col]].rename(columns={
            collapsed_col: "collapsed_mean",
            noncollapsed_col: "noncollapsed_mean"
        })
    else:
        # Standard grouping logic
        df[arg_col] = df[arg_col].astype(str)
        grouped = df.groupby(arg_col).agg(
            collapsed_mean=(collapsed_col, "mean"),
            noncollapsed_mean=(noncollapsed_col, "mean"),
        ).reset_index()

    # Melt into long form for plotting
    plot_df = grouped.melt(
        id_vars=[arg_col],
        value_vars=["collapsed_mean", "noncollapsed_mean"],
        var_name="Type",
        value_name="Value",
    )

    plot_df["Type"] = plot_df["Type"].map({
        "collapsed_mean": "Collapsed",
        "noncollapsed_mean": "Non-collapsed",
    })

    # Sort categories by performance (descending)
    order = (
        grouped.assign(total_mean=(grouped["collapsed_mean"] + grouped["noncollapsed_mean"]) / 2)
        .sort_values("total_mean", ascending=False)[arg_col]
        .tolist()
    )

    color_map = {"Non-collapsed": "#32558f", "Collapsed": "#a1beed"}
    type_order = ["Non-collapsed", "Collapsed"]

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
            arg_col: "Metadata Configuration" if arg_col == "all_metadata" else arg_choice_label,
            "Value": f"Value: {base_metric}",
        },
        title=f"{base_metric} comparison: collapsed vs non-collapsed",
        height=400 + (len(order) * 25) # Dynamically scale height for many individual rows
    )

    # Clean up axis layout
    fig.update_layout(
        xaxis_title=f"Average {base_metric}", 
        yaxis_title=None,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    # Force Y-axis labels to be readable even if long
    fig.update_yaxes(tickfont=dict(size=10))

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show raw data table"):
        st.dataframe(grouped.rename(columns={"collapsed_mean": collapsed_col, "noncollapsed_mean": noncollapsed_col}))
else:
    st.error(f"File not found at: {example_path}")