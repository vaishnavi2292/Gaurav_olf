import streamlit as st
import pandas as pd
from io import BytesIO

# --- Set page config ---
try:
    st.set_page_config(page_title="Grade Analysis for Class 11", layout="wide")
except Exception as e:
    st.warning("Page config could not be set. Continuing without it.")

st.title("📘 Grade Analysis for Class 11")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload Excel File", type=[".xlsx", ".xls"])

# --- Helper: Convert df to downloadable Excel ---
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

# --- Main logic ---
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
    else:
        # Expected columns
        expected_cols = [
            'DISTRICT', 'BLOCK', 'CIRCLE', 'SCHOOL',
            'Q_1 कक्षा 11वीं में कुल दर्ज विद्यार्थियों की संख्या',
            'Q_2 कक्षा 11वीं में कुल परीक्षार्थी संख्या'
        ]
        grade_cols = [
            '81% =< 100% प्राप्तांक',
            '60% =< 80% प्राप्तांक',
            '45% =< 59% प्राप्तांक',
            '33% =< 44% प्राप्तांक',
            '< 33% प्राप्तांक'
        ]
        required_columns = expected_cols + grade_cols
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            st.error(f"Missing columns: {', '.join(missing_cols)}")
        else:
            # Rename for internal use
            df.rename(columns={
                'Q_1 कक्षा 11वीं में कुल दर्ज विद्यार्थियों की संख्या': 'Total Enrolled',
                'Q_2 कक्षा 11वीं में कुल परीक्षार्थी संख्या': 'Present',
                '81% =< 100% प्राप्तांक': '81-100%',
                '60% =< 80% प्राप्तांक': '60-80%',
                '45% =< 59% प्राप्तांक': '45-59%',
                '33% =< 44% प्राप्तांक': '33-44%',
                '< 33% प्राप्तांक': '<33%'
            }, inplace=True)

            # Grade assignment
            def get_grade(row):
                scores = {
                    'A': row['81-100%'],
                    'B': row['60-80%'],
                    'C': row['45-59%'],
                    'D': row['33-44%'],
                    'E': row['<33%']
                }
                return max(scores, key=scores.get) if pd.notnull(row['Present']) else pd.NA

            df['Grade'] = df.apply(get_grade, axis=1)

            df['Present'] = df['Present'].replace(0, pd.NA)

            # --- Grade percentages: rounded, whole, with % sign ---
            df['A%'] = ((df['81-100%'] / df['Present']) * 100).round(0).astype('Int64').astype(str) + '%'
            df['B%'] = ((df['60-80%'] / df['Present']) * 100).round(0).astype('Int64').astype(str) + '%'
            df['C%'] = ((df['45-59%'] / df['Present']) * 100).round(0).astype('Int64').astype(str) + '%'
            df['D%'] = ((df['33-44%'] / df['Present']) * 100).round(0).astype('Int64').astype(str) + '%'
            df['E%'] = ((df['<33%'] / df['Present']) * 100).round(0).astype('Int64').astype(str) + '%'

            # --- Show detailed table ---
            st.subheader("📋 Data with Grades and Percentages")
            st.dataframe(df)

            # --- Download full data ---
            df_excel = convert_df_to_excel(df)
            st.download_button(
                label="⬇️ Download Data with Grades and Percentages",
                data=df_excel,
                file_name="Grade_Data_Detailed.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # --- Pivot summary table ---
            pivot = pd.pivot_table(
                df,
                index='BLOCK',
                values=[
                    'SCHOOL', 'Total Enrolled', 'Present',
                    '81-100%', '60-80%', '45-59%', '33-44%', '<33%'
                ],
                aggfunc={
                    'SCHOOL': 'count',
                    'Total Enrolled': 'sum',
                    'Present': 'sum',
                    '81-100%': 'sum',
                    '60-80%': 'sum',
                    '45-59%': 'sum',
                    '33-44%': 'sum',
                    '<33%': 'sum'
                }
            ).reset_index()

            # Rename to Hindi
            pivot.rename(columns={
                'SCHOOL': 'School Count',
                '81-100%': '81% =< 100% प्राप्तांक',
                '60-80%': '60% =< 80% प्राप्तांक',
                '45-59%': '45% =< 59% प्राप्तांक',
                '33-44%': '33% =< 44% प्राप्तांक',
                '<33%': '< 33% प्राप्तांक'
            }, inplace=True)

            # Reorder columns
            first_cols = ['BLOCK', 'Present', 'School Count', 'Total Enrolled']
            remaining_cols = [col for col in pivot.columns if col not in first_cols]
            pivot = pivot[first_cols + remaining_cols]

            st.subheader("📌 Pivot Table Summary by Block")
            st.dataframe(pivot)

            # --- Download pivot summary ---
            pivot_excel = convert_df_to_excel(pivot)
            st.download_button(
                label="⬇️ Download Pivot Table Summary",
                data=pivot_excel,
                file_name="Pivot_Table_Summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # --- Grade count distribution ---
            st.subheader("📊 Grade Distribution by Block")
            grade_pivot = pd.pivot_table(
                df,
                index='BLOCK',
                columns='Grade',
                values='SCHOOL',
                aggfunc='count',
                fill_value=0,
                margins=True,
                margins_name='Grand Total'
            ).reset_index()

            st.dataframe(grade_pivot)

else:
    st.info("Please upload an Excel file to begin analysis.")
