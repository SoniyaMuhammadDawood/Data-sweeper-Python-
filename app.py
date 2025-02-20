import streamlit as st
import pandas as pd
import os
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(page_title="Data-sweeper", layout="wide")

# Custom Styling
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(to right, #73C7C7, #D1F8EF);
            color: black;
        }
       
        .stButton>button {
            background-color: #FFC819E;
            color: black;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px;
            border: none;
        }
        .stDownloadButton>button {
            background-color: #57CC99;
            color: black;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px;
            border: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💿 Data-sweeper Sterling Integrator by Soniya")
st.write("Transform your file between CSV, Excel, JSON & TXT format with built-in data cleaning & visualization.")

# File uploader
uploaded_files = st.file_uploader(
    "Upload your files (CSV, Excel, JSON, TXT):",
    type=["csv", "xlsx", "json", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read file based on type
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            try:
                df = pd.read_excel(file, engine="openpyxl")
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                continue
        elif file_ext == ".json":
            df = pd.read_json(file)
        elif file_ext == ".txt":
            df = pd.read_csv(file, delimiter="\t")  # Tab-separated text files
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # File details
        st.write(f"📂 **File Details:**")
        file_size = len(file.getvalue()) / 1024  # Convert bytes to KB
        st.write(f"- **Name:** {file.name}")
        st.write(f"- **Type:** {file_ext.upper()}")
        st.write(f"- **Size:** {file_size:.2f} KB")
        st.write(f"- **Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")

        # Editable Data Preview
        st.subheader("📝 Editable Data Preview")
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

        # Data cleaning options
        st.subheader("🛠️ Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove duplicates from {file.name}"):
                    edited_df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates removed!")

            with col2:
                if st.button(f"Fill missing values for {file.name}"):
                    numeric_cols = edited_df.select_dtypes(include=["number"]).columns
                    if len(numeric_cols) > 0:
                        edited_df[numeric_cols] = edited_df[numeric_cols].fillna(edited_df[numeric_cols].mean())
                        st.success("✔️ Missing values have been filled!")
                    else:
                        st.warning("⚠️ No numeric columns found to fill missing values.")

            st.subheader("🎯 Select Columns to Keep")
            columns = st.multiselect(f"Choose columns for {file.name}", edited_df.columns, default=edited_df.columns)
            edited_df = edited_df[columns]

        # Data Visualization
        st.subheader("📊 Data Visualizations")
        numeric_cols = edited_df.select_dtypes(include='number').columns

        if len(numeric_cols) == 0:
            st.warning(f"⚠️ No numeric columns found in {file.name} for visualization.")
        else:
            selected_columns = st.multiselect(f"Select columns for visualization ({file.name})", numeric_cols, default=numeric_cols[:2])
            
            if selected_columns:
                st.bar_chart(edited_df[selected_columns])  # Show bar chart
                

        # Conversion options
        st.subheader("🔁 Conversion Option")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel", "JSON", "TXT"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine="openpyxl")
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif conversion_type == "JSON":
                df.to_json(buffer, orient="records")
                file_name = file.name.replace(file_ext, ".json")
                mime_type = "application/json"
            elif conversion_type == "TXT":
                df.to_csv(buffer, index=False, sep="\t")
                file_name = file.name.replace(file_ext, ".txt")
                mime_type = "text/plain"
            
            buffer.seek(0)
            st.download_button(
                label=f"Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("All files processed successfully! 🎉")
