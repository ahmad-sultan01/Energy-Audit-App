import streamlit as st

st.set_page_config(
    page_title="Coal Power Plant Audit",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Coal Combustion Power Plant\nEnergy Audit Tool")

st.markdown("""
Welcome to the **Coal Energy Audit App**.

Use the sidebar to:

- 🧮 Perform manual audits  
- 📁 Upload CSVs for batch analysis  
- 📊 View performance & emissions  
""")
