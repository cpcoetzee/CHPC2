import streamlit as st
import pandas as pd
import altair as alt

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Virology Dashboard", layout="wide")

# --- STYLING ---
st.markdown("""
    <style>
    .main-title {text-align: center; font-size: 2em; font-weight: bold;}
    .subheader {color: #007BFF; font-size: 1.5em;}
    </style>
""", unsafe_allow_html=True)

# --- TITLE & HEADER ---
st.markdown("<div class='main-title'>TYG NHLS Virology Dashboard</div>", unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR ---
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV of Results Data", type="csv")

# --- LOAD DATA ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Ensure dates are parsed correctly
    df["Collection Date"] = pd.to_datetime(df["Collection Date"], errors='coerce')
    df["Year"] = df["Collection Date"].dt.year
    df["Month"] = df["Collection Date"].dt.month
    
    # Sidebar filters
    year_filter = st.sidebar.selectbox("Select Year", sorted(df["Year"].dropna().unique()), index=0)
    month_filter = st.sidebar.selectbox("Select Month", range(1, 13), index=0)
    
    df_filtered = df[(df["Year"] == year_filter) & (df["Month"] == month_filter)]
    
    st.subheader("Filtered Results Data Preview")
    st.dataframe(df_filtered)
    
    # --- HIV POSITIVITY RATE OVER TIME ---
    st.subheader("HIV Positivity Rate Over Time")
    if "WEEK" in df_filtered.columns and "HIVCOS - V0010 - HIV Combo Result" in df_filtered.columns:
        positivity_rate = df_filtered.groupby("WEEK")["HIVCOS - V0010 - HIV Combo Result"].apply(lambda x: (x == 'P').mean())
        chart = alt.Chart(pd.DataFrame({'Week': positivity_rate.index, 'Positivity Rate': positivity_rate.values})).mark_line().encode(
            x='Week:O', y='Positivity Rate:Q', tooltip=['Week', 'Positivity Rate']
        ).properties(title=f"HIV Positivity Rate Per Week ({year_filter})")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("Required columns 'WEEK' and 'HIVCOS - V0010 - HIV Combo Result' not found.")
    
    # --- AGE DISTRIBUTION ---
    st.subheader("Age Distribution of Patients")
    if "Age" in df_filtered.columns:
        chart = alt.Chart(df_filtered).mark_bar().encode(
            x=alt.X('Age:Q', bin=True),
            y='count()',
            tooltip=['Age']
        ).properties(title="Age Distribution of Patients")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("Column 'Age' not found in dataset.")
    
    # --- TURNAROUND TIME (TAT) TRENDS ---
    st.subheader("Turnaround Time (TAT) Trends")
    if "WEEK" in df_filtered.columns and "TOTAL TAT" in df_filtered.columns:
        tat_trends = df_filtered.groupby("WEEK")["TOTAL TAT"].mean()
        chart = alt.Chart(pd.DataFrame({'Week': tat_trends.index, 'Average TAT': tat_trends.values})).mark_line().encode(
            x='Week:O', y='Average TAT:Q', tooltip=['Week', 'Average TAT']
        ).properties(title=f"Average Turnaround Time Per Week ({year_filter})")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("Required columns 'WEEK' and 'TOTAL TAT' not found.")
    
    # --- WEEKLY/MONTHLY TEST VOLUME ---
    st.subheader("Weekly/Monthly Test Volume")
    if "WEEK" in df_filtered.columns:
        weekly_volume = df_filtered["WEEK"].value_counts().sort_index()
        chart = alt.Chart(pd.DataFrame({'Week': weekly_volume.index, 'Test Volume': weekly_volume.values})).mark_bar().encode(
            x='Week:O', y='Test Volume:Q', tooltip=['Week', 'Test Volume']
        ).properties(title=f"Test Volume Per Week ({year_filter})")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("Column 'WEEK' not found in dataset.")
    
    if "MONTH" in df_filtered.columns:
        monthly_volume = df_filtered["MONTH"].value_counts().sort_index()
        chart = alt.Chart(pd.DataFrame({'Month': monthly_volume.index, 'Test Volume': monthly_volume.values})).mark_bar().encode(
            x='Month:O', y='Test Volume:Q', tooltip=['Month', 'Test Volume']
        ).properties(title=f"Test Volume Per Month ({year_filter})")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("Column 'MONTH' not found in dataset.")
    
    st.markdown("---")
    
# --- CONTACT INFO ---
st.subheader("Contact Information")
st.markdown("You can reach **Dr. Chris Coetzee** at [christiaan.coetzee@nhls.ac.za](mailto:christiaan.coetzee@nhls.ac.za)")
