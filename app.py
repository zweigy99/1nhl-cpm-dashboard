
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Load data from Excel
uploaded_file = st.file_uploader("Upload the Canadian NHL CPM Excel File", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name='CPM Entry')

    # Convert relevant columns
    df['Audience'] = pd.to_numeric(df['Audience'], errors='coerce')
    df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce')
    df['CPM'] = pd.to_numeric(df['CPM'], errors='coerce')

    # Sidebar filters
    st.sidebar.header("Filter by")
    selected_team = st.sidebar.selectbox("Team", options=["All"] + sorted(df['Team'].dropna().unique().tolist()))
    selected_category = st.sidebar.selectbox("Asset Category", options=["All"] + sorted(df['Asset Category'].dropna().unique().tolist()))
    selected_asset = st.sidebar.selectbox("Asset Type", options=["All"] + sorted(df['Asset Type'].dropna().unique().tolist()))

    # Filter logic
    df_filtered = df.copy()
    if selected_team != "All":
        df_filtered = df_filtered[df_filtered['Team'] == selected_team]
    if selected_category != "All":
        df_filtered = df_filtered[df_filtered['Asset Category'] == selected_category]
    if selected_asset != "All":
        df_filtered = df_filtered[df_filtered['Asset Type'] == selected_asset]

    st.title("Canadian NHL Team CPM Dashboard")

    # Entry/adjustment of values
    st.markdown("### Adjust Inputs")
    for idx, row in df_filtered.iterrows():
        st.markdown(f"#### {row['Team']} - {row['Asset Type']}")
        audience = st.number_input(f"Audience ({idx})", min_value=0, value=int(row['Audience']) if not pd.isna(row['Audience']) else 0, step=1000)
        cpm = st.number_input(f"CPM ({idx})", min_value=0.0, value=float(row['CPM']) if not pd.isna(row['CPM']) else 0.0, step=0.1)
        discount = st.number_input(f"Discount (%) ({idx})", min_value=0.0, value=float(row['Discount']) if not pd.isna(row['Discount']) else 0.0, step=1.0)
        df_filtered.at[idx, 'Audience'] = audience
        df_filtered.at[idx, 'CPM'] = cpm
        df_filtered.at[idx, 'Discount'] = discount

    # Calculated fields
    df_filtered['Adjusted CPM'] = df_filtered.apply(lambda x: (x['CPM'] / x['Audience'] * 1000) if pd.notna(x['CPM']) and pd.notna(x['Audience']) and x['Audience'] > 0 else np.nan, axis=1)
    df_filtered['Estimated Spend'] = df_filtered.apply(lambda x: (x['CPM'] * x['Audience'] / 1000) if pd.notna(x['CPM']) and pd.notna(x['Audience']) else np.nan, axis=1)

    # Display
    st.markdown("---")
    st.subheader("Filtered Data Table")
    st.dataframe(df_filtered)

    st.subheader("CPM by Team")
    if not df_filtered.empty:
        bar_chart = alt.Chart(df_filtered).mark_bar().encode(
            x=alt.X('Team:N', sort='-y'),
            y='CPM:Q',
            color='Team:N',
            tooltip=['Team', 'Asset Type', 'CPM']
        ).properties(height=400)
        st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("---")
    st.markdown("**Note:** Adjust audience, CPM, and discount inputs to see real-time effects on spend and adjusted CPM.")
else:
    st.info("Please upload a valid Excel file with the 'CPM Entry' sheet.")
