import streamlit as st
import pandas as pd
import os

# ---------- Page Config
st.set_page_config(page_title="School Response of Gariaband", layout="wide")

# ---------- Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #E0F7FA 0%, #FFEBEE 100%);
        background-attachment: fixed;
        color: #000;
    }
    .big-font {
        font-size: 1.7rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🏫 School Response Status - GAURAV GARIABAND</p>', unsafe_allow_html=True)

# ---------- File Uploads
col1, col2 = st.columns(2)
with col1:
    school_file = st.file_uploader("📘 Upload School List File (must contain SCHOOL & BLOCK_NAME)", type=['csv', 'xlsx'], key="school")
with col2:
    raw_file = st.file_uploader("📄 Upload Raw Data File (must contain SCHOOL)", type=['csv', 'xlsx'], key="raw")

if school_file and raw_file:
    # ---------- Load Data
    df_school = pd.read_csv(school_file) if school_file.name.endswith(".csv") else pd.read_excel(school_file)
    df_raw = pd.read_csv(raw_file) if raw_file.name.endswith(".csv") else pd.read_excel(raw_file)

    df_school.columns = df_school.columns.str.upper()
    df_raw.columns = df_raw.columns.str.upper()

    if 'SCHOOL' not in df_school.columns or 'SCHOOL' not in df_raw.columns:
        st.error("❌ Both files must contain a column named 'SCHOOL'")
    elif 'BLOCK_NAME' not in df_school.columns:
        st.error("❌ School list must contain a 'BLOCK_NAME' column")
    else:
        # ---------- Add RESPONSE column
        df_school['RESPONSE'] = df_school['SCHOOL'].isin(df_raw['SCHOOL']).map({True: 'YES', False: 'NO'})

        st.markdown("### 📝 Updated School List with Response")
        st.dataframe(df_school)

        # ---------- Pivot Table
        pivot = pd.pivot_table(
            df_school,
            values='SCHOOL',
            index='BLOCK_NAME',
            columns='RESPONSE',
            aggfunc='count',
            fill_value=0,
            margins=True,
            margins_name='Total'
        ).reset_index()

        st.markdown("### 📊 Pivot Table - Block vs Response Count")
        st.dataframe(pivot)

        # ---------- Summary Table
        if 'YES' not in pivot.columns:
            pivot['YES'] = 0
        if 'NO' not in pivot.columns:
            pivot['NO'] = 0

        summary = pd.DataFrame()
        summary['BLOCK_NAME'] = pivot['BLOCK_NAME']
        summary['# SCHOOLS'] = pivot['YES'] + pivot['NO']
        summary['RESPONDED'] = pivot['YES']
        summary['PENDING'] = pivot['NO']
        summary['RESPONDED %'] = round((summary['RESPONDED'] / summary['# SCHOOLS']) * 100).astype(str) + '%'

        st.markdown("### ✅ Final Summary Table")
        st.dataframe(summary)

        # ---------- Downloads
        school_csv = df_school.to_csv(index=False).encode('utf-8')
        pivot_csv = pivot.to_csv(index=False).encode('utf-8')
        summary_csv = summary.to_csv(index=False).encode('utf-8')

        st.download_button("⬇️ Download Updated School List CSV", school_csv, file_name="updated_school_list.csv", mime="text/csv")
        st.download_button("⬇️ Download Pivot Table CSV", pivot_csv, file_name="pivot_table.csv", mime="text/csv")
        st.download_button("⬇️ Download Summary Table CSV", summary_csv, file_name="summary_table.csv", mime="text/csv")
else:
    st.info("⬅️ Please upload both the school list and raw data files to proceed.")
