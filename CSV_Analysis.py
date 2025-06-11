import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from utils import calculate_metrics

st.title("📂 CSV Audit - Batch Mode")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

required_columns = [
    "Coal Flow", "GCV", "Steam Flow", "Steam Enthalpy", 
    "Feedwater Enthalpy", "Power Output", "Flue Temp", "Ambient Temp"
]

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        st.subheader("📋 Uploaded Data")
        st.dataframe(df.head())

        # Validate required columns
        if not all(col in df.columns for col in required_columns):
            st.error(f"❌ Uploaded CSV must contain these columns:\n{', '.join(required_columns)}")
        else:
            with st.spinner("🔄 Processing data..."):
                results = []
                for _, row in df.iterrows():
                    r = calculate_metrics(
                        row["Coal Flow"], row["GCV"], row["Steam Flow"],
                        row["Steam Enthalpy"], row["Feedwater Enthalpy"],
                        row["Power Output"], row["Flue Temp"], row["Ambient Temp"]
                    )
                    results.append(r)

                result_df = pd.DataFrame(results)
                final_df = pd.concat([df, result_df], axis=1)

            st.subheader("📊 Audit Results")
            st.dataframe(final_df)

            st.download_button("📥 Download Result CSV", data=final_df.to_csv(index=False),
                               file_name="audit_results.csv", mime="text/csv")

            st.subheader("📈 Correlation Heatmap")
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(final_df.corr(numeric_only=True), ax=ax, cmap="coolwarm", annot=True)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
