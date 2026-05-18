import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CSV Analytics Dashboard",
    layout="wide"
)

st.title("📊 Interactive CSV Analytics Dashboard")
st.write("Upload your CSV file and explore complete dataset insights.")

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

show_raw_data = st.sidebar.checkbox("Show Raw Dataset", True)
show_clean_data = st.sidebar.checkbox("Show Cleaned Dataset", True)

# ---------------- MAIN APP ----------------
if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully ✅")

    # ---------------- CLEANING ----------------
    df_clean = df.copy()

    for col in df_clean.columns:

        if pd.api.types.is_numeric_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
        else:
            df_clean[col] = df_clean[col].fillna("Unknown")

    df_clean = df_clean.drop_duplicates()

    # ---------------- OVERVIEW ----------------
    st.header("📌 Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())

    # ---------------- RAW DATA ----------------
    if show_raw_data:
        st.subheader("📋 Raw Dataset")
        st.dataframe(df.fillna("").astype(str), use_container_width=True)

    # ---------------- CLEAN DATA ----------------
    if show_clean_data:
        st.subheader("🧹 Cleaned Dataset")
        st.dataframe(df_clean.fillna("").astype(str), use_container_width=True)

    # ---------------- DATA INFO ----------------
    st.header("ℹ️ Dataset Information")

    info_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing Values": df.isnull().sum().values
    })

    st.dataframe(info_df, use_container_width=True)

    # ---------------- SUMMARY STATISTICS ----------------
    st.header("📈 Summary Statistics")

    st.dataframe(df.describe(include="all"), use_container_width=True)

    # ---------------- AUTO INSIGHTS ----------------
    st.header("💡 Auto Insights")

    total_missing = df.isnull().sum().sum()
    most_missing_col = df.isnull().sum().idxmax()

    numeric_cols = df.select_dtypes(include="number")

    col1, col2 = st.columns(2)

    col1.info(f"📌Total Missing Values: {total_missing}")
    col2.info(f"📌Most Missing Column: {most_missing_col}")

    if not numeric_cols.empty:
        st.success("Numeric columns detected")

        st.dataframe(numeric_cols.mean().to_frame("Mean Values"))

    else:
        st.warning("No numeric columns found")

    # ---------------- FILTER DATA ----------------
    st.header("🔍 Filter Dataset")

    filter_column = st.selectbox("Select Column", df.columns)
    filter_value = st.text_input("Enter value to filter")

    if filter_value:

        filtered_df = df[
            df[filter_column]
            .astype(str)
            .str.contains(filter_value, case=False, na=False)
        ]

        st.subheader("Filtered Results")
        st.dataframe(filtered_df.fillna("").astype(str), use_container_width=True)

    # ---------------- COLUMN ANALYSIS ----------------
    st.header("📊 Column Analysis")

    selected_column = st.selectbox("Choose Column", df.columns, key="col_analysis")

    if pd.api.types.is_numeric_dtype(df[selected_column]):

        st.subheader("📈 Statistical Insights")

        col1, col2, col3 = st.columns(3)

        col1.metric("Mean", round(df[selected_column].mean(), 2))
        col2.metric("Max", df[selected_column].max())
        col3.metric("Min", df[selected_column].min())

        fig, ax = plt.subplots()
        ax.hist(df[selected_column].dropna(), bins=10)
        ax.set_title(selected_column)
        st.pyplot(fig)

    else:

        st.subheader(" Category Distribution")

        value_counts = df[selected_column].value_counts()

        st.dataframe(value_counts)

        fig, ax = plt.subplots()
        value_counts.plot(kind="bar", ax=ax)
        ax.set_title(selected_column)
        st.pyplot(fig)

    # ---------------- CORRELATION ----------------
    st.header("🔗 Correlation Analysis")

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] > 1:
        st.dataframe(numeric_df.corr(), use_container_width=True)
    else:
        st.warning("Not enough numeric columns for correlation analysis.")

    # ---------------- DOWNLOAD ----------------
    st.header("⬇ Download Cleaned Dataset")

    csv = df_clean.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv"
    )

else:
    st.info("👈 Please upload a CSV file to start analysis.")