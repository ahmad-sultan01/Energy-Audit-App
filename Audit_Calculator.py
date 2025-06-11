import streamlit as st
import matplotlib.pyplot as plt
from utils import calculate_metrics, generate_recommendations

st.title("🔢 Single Audit Calculator")

with st.form("input_form"):
    st.subheader("Plant Input Parameters")
    col1, col2 = st.columns(2)

    with col1:
        coal_flow = st.number_input("Coal Flow (kg/hr)", min_value=0.0)
        gcv = st.number_input("Coal GCV (kcal/kg)", min_value=0.0)
        power_output = st.number_input("Power Output (kW)", min_value=0.0)
        flue_temp = st.number_input("Flue Gas Temp (°C)", min_value=0.0)

    with col2:
        steam_flow = st.number_input("Steam Flow (kg/hr)", min_value=0.0)
        h_steam = st.number_input("Steam Enthalpy (kcal/kg)", min_value=0.0)
        h_feed = st.number_input("Feedwater Enthalpy (kcal/kg)", min_value=0.0)
        ambient_temp = st.number_input("Ambient Temp (°C)", min_value=0.0)

    submitted = st.form_submit_button("Calculate")

if submitted:
    results = calculate_metrics(coal_flow, gcv, steam_flow, h_steam, h_feed,
                                power_output, flue_temp, ambient_temp)

    st.success("✅ Calculation Complete!")

    st.subheader("📊 Key Metrics")
    st.write(f"**Boiler Efficiency:** {results['boiler_efficiency']:.2f}%")
    st.write(f"**Heat Rate:** {results['heat_rate']:.2f} kcal/kWh")
    st.write(f"**SFC:** {results['sfc']:.2f} kg/kWh")
    st.write(f"**Flue Gas Loss:** {results['flue_gas_loss']:.2f}%")
    st.write(f"**CO₂ Emissions:** {results['co2_emissions']:.2f} kg/hr")

    st.subheader("📌 Recommendations")
    st.write(generate_recommendations(results))

    st.subheader("📉 Visual Overview")
    fig, ax = plt.subplots()
    labels = ['Efficiency (%)', 'Heat Rate', 'SFC', 'Flue Loss']
    values = [results['boiler_efficiency'], results['heat_rate'], results['sfc'], results['flue_gas_loss']]
    ax.bar(labels, values, color=['green', 'orange', 'red', 'blue'])
    ax.set_ylabel("Values")
    st.pyplot(fig)
