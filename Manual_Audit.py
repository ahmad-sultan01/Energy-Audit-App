import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# json and requests are not strictly needed for this version, but kept as they were in previous versions
import json
import requests

# Assuming calculate_metrics is defined in a utils.py file and imported as follows:
# from utils import calculate_metrics
# For this example, I'll define it here for completeness,
# but if you have it in utils.py, you can keep your import.

def calculate_metrics(coal_flow, gcv, steam_flow, steam_h, feed_h, power_output, flue_temp, amb_temp):
    """
    Calculates key performance and emission metrics for a power plant.

    Args:
        coal_flow (float): Coal flow rate (e.g., kg/hr).
        gcv (float): Gross Calorific Value of coal (e.g., kcal/kg).
        steam_flow (float): Steam flow rate (e.g., kg/hr).
        steam_h (float): Enthalpy of steam (e.g., kcal/kg).
        feed_h (float): Enthalpy of feedwater (e.g., kcal/kg).
        power_output (float): Electrical power output (e.g., kWh).
        flue_temp (float): Flue gas temperature (e.g., °C).
        amb_temp (float): Ambient air temperature (e.g., °C).

    Returns:
        dict: A dictionary containing the calculated metrics.
    """
    # Ensure inputs are numeric and handle potential None/NaN values by coercing to 0 for calculation safety
    coal_flow = pd.to_numeric(coal_flow, errors='coerce') if pd.notna(coal_flow) else 0
    gcv = pd.to_numeric(gcv, errors='coerce') if pd.notna(gcv) else 0
    steam_flow = pd.to_numeric(steam_flow, errors='coerce') if pd.notna(steam_flow) else 0
    steam_h = pd.to_numeric(steam_h, errors='coerce') if pd.notna(steam_h) else 0
    feed_h = pd.to_numeric(feed_h, errors='coerce') if pd.notna(feed_h) else 0
    power_output = pd.to_numeric(power_output, errors='coerce') if pd.notna(power_output) else 0
    flue_temp = pd.to_numeric(flue_temp, errors='coerce') if pd.notna(flue_temp) else 0
    amb_temp = pd.to_numeric(amb_temp, errors='coerce') if pd.notna(amb_temp) else 0

    # Calculate heat input from coal
    energy_input = coal_flow * gcv

    # Calculate useful energy output in steam
    steam_energy = steam_flow * (steam_h - feed_h)

    # Calculate Boiler Efficiency (percentage)
    efficiency = (steam_energy / energy_input) * 100 if energy_input != 0 else 0

    # Calculate Plant Heat Rate (kcal/kWh)
    plant_heat_rate = (energy_input / power_output) if power_output != 0 else 0

    # Calculate Specific Fuel Consumption (kg/kWh)
    specific_fuel_consumption = (coal_flow / power_output) if power_output != 0 else 0

    # Calculate CO2 emissions (kg/hr)
    co2_emissions = coal_flow * 2.29

    # Calculate Flue Gas Loss
    flue_loss = (flue_temp - amb_temp) * 0.25

    return {
        "Boiler Efficiency": efficiency,
        "Plant Heat Rate (kcal/kWh)": plant_heat_rate,
        "Specific Fuel Consumption (kg/kWh)": specific_fuel_consumption,
        "Flue Gas Loss": flue_loss,
        "CO2 Emissions (kg/hr)": co2_emissions
    }

# Define the generate_recommendations function
def generate_recommendations(metrics):
    """
    Generates recommendations based on power plant performance metrics.

    Args:
        metrics (dict): A dictionary containing average calculated metrics.

    Returns:
        list: A list of recommendation strings.
    """
    rec = []

    # Recommendation for Boiler Efficiency
    be = metrics.get('Boiler Efficiency', 0)
    if be > 85:
        rec.append("✅ **Boiler Efficiency ({:.2f}%)**: Excellent. Maintain current operation and schedule routine maintenance.".format(be))
    elif 70 <= be <= 85:
        rec.append("⚠️ **Boiler Efficiency ({:.2f}%)**: Good, but room for improvement. Optimize excess air supply, clean heat transfer surfaces (e.g., soot blowing).".format(be))
    else:
        rec.append("❌ **Boiler Efficiency ({:.2f}%)**: Inefficient. Check for incomplete combustion, poor coal quality, leaks, and fouling in boiler tubes. Consider retrofitting economizers or better insulation.".format(be))

    # Recommendation for Plant Heat Rate
    hr = metrics.get('Plant Heat Rate (kcal/kWh)', 0)
    if hr < 2500 and hr > 0:
        rec.append("✅ **Plant Heat Rate ({:.2f} kcal/kWh)**: Efficient. Maintain load management and keep equipment in tuned condition.".format(hr))
    elif 2500 <= hr <= 3000:
        rec.append("⚠️ **Plant Heat Rate ({:.2f} kcal/kWh)**: Average. Inspect turbine sealing, condenser vacuum, and reheater losses.".format(hr))
    else:
        rec.append("❌ **Plant Heat Rate ({:.2f} kcal/kWh)**: Inefficient. Audit heat exchangers, check turbine performance, condenser vacuum issues, and unaccounted auxiliary consumption.".format(hr))

    # Recommendation for Specific Fuel Consumption
    sfc = metrics.get('Specific Fuel Consumption (kg/kWh)', 0)
    if sfc < 0.6 and sfc > 0:
        rec.append("✅ **Specific Fuel Consumption ({:.2f} kg/kWh)**: Efficient. Ensure consistent coal quality and maintain feed systems.".format(sfc))
    elif 0.6 <= sfc <= 0.75:
        rec.append("⚠️ **Specific Fuel Consumption ({:.2f} kg/kWh)**: Acceptable. Verify air-fuel ratio, minimize unburnt carbon.".format(sfc))
    else:
        rec.append("❌ **Specific Fuel Consumption ({:.2f} kg/kWh)**: High. Recommend coal quality improvement, combustion tuning, and reducing clinker formation.".format(sfc))

    # Recommendation for Flue Gas Loss
    fl = metrics.get('Flue Gas Loss', 0)
    if fl < 5 and fl > 0:
        rec.append("✅ **Flue Gas Loss ({:.2f}%)**: Optimal flue gas recovery. Keep stack temperature and air ratio monitored.".format(fl))
    elif 5 <= fl <= 10:
        rec.append("⚠️ **Flue Gas Loss ({:.2f}%)**: Moderate loss. Consider preheating combustion air or recovering heat using economizer.".format(fl))
    else:
        rec.append("❌ **Flue Gas Loss ({:.2f}%)**: High heat loss. Suggest urgent flue gas heat recovery installation, reduce excess air, and check for insulation leaks.".format(fl))

    # Recommendation for CO2 Emissions
    co2 = metrics.get('CO2 Emissions (kg/hr)', 0)
    if co2 > 8000:
        rec.append("⚠️ **CO₂ Emissions ({:.2f} kg/hr)**: High CO₂ emissions. Explore cleaner fuels or carbon capture technologies.".format(co2))
    elif co2 > 0:
        rec.append("✅ **CO₂ Emissions ({:.2f} kg/hr)**: Monitor CO₂ emissions regularly and explore opportunities for reduction.".format(co2))
    return rec

st.title("🧮 Manual Audit Tool")

# Input fields for the manual audit
coal_flow = st.number_input("Coal Flow (kg/hr)", min_value=0.0, value=100.0, format="%.2f", key="man_coal_flow")
gcv = st.number_input("GCV of Coal (kcal/kg)", min_value=0.0, value=5000.0, format="%.2f", key="man_gcv")
steam_flow = st.number_input("Steam Output (kg/hr)", min_value=0.0, value=400.0, format="%.2f", key="man_steam_flow")
steam_enthalpy = st.number_input("Steam Enthalpy (kcal/kg)", min_value=0.0, value=750.0, format="%.2f", key="man_steam_enthalpy")
feedwater_enthalpy = st.number_input("Feedwater Enthalpy (kcal/kg)", min_value=0.0, value=100.0, format="%.2f", key="man_feedwater_enthalpy")
power_output = st.number_input("Power Output (kW)", min_value=0.0, value=200.0, format="%.2f", key="man_power_output")
flue_temp = st.number_input("Flue Gas Temp (°C)", min_value=0.0, value=150.0, format="%.2f", key="man_flue_temp")
ambient_temp = st.number_input("Ambient Temp (°C)", min_value=0.0, value=25.0, format="%.2f", key="man_amb_temp")

# Session state to store results for persistence across reruns
if 'calculated_result' not in st.session_state:
    st.session_state.calculated_result = None

if st.button("🔍 Run Audit", key="run_manual_audit_btn"):
    # Perform calculations using the inputs
    st.session_state.calculated_result = calculate_metrics(
        coal_flow, gcv, steam_flow,
        steam_enthalpy, feedwater_enthalpy,
        power_output, flue_temp, ambient_temp
    )

if st.session_state.calculated_result:
    st.subheader("✅ Calculated Results")
    # Display results in a structured DataFrame
    results_df = pd.DataFrame([st.session_state.calculated_result]).T.rename(columns={0: "Value"})
    results_df.index.name = "Metric"
    results_df["Value"] = results_df["Value"].round(2)
    st.dataframe(results_df)

    # --- Visualizations Section ---
    st.subheader("📊 Visualizations")
    
    # Prepare data for plotting for the combined bar chart
    plot_data = pd.DataFrame({
        'Metric': list(st.session_state.calculated_result.keys()),
        'Value': [round(v, 2) for v in st.session_state.calculated_result.values()]
    })

    # Create the combined bar chart for all calculated metrics (as you had it)
    fig_combined, ax_combined = plt.subplots(figsize=(10, 6))
    sns.barplot(x='Metric', y='Value', data=plot_data, palette='viridis', ax=ax_combined)
    ax_combined.set_title("Calculated Performance Metrics Overview")
    ax_combined.set_xlabel("Metric")
    ax_combined.set_ylabel("Value")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig_combined)
    plt.close(fig_combined)

    st.markdown("---") # Separator for better visual organization

    # --- Individual Charts to mimic "results report" visuals for single point ---

    # 1. Boiler Efficiency vs. (Conceptually) Coal Flow
    # For a single point, we'll just show the efficiency value
    be_value = st.session_state.calculated_result.get('Boiler Efficiency', 0)
    fig_be, ax_be = plt.subplots(figsize=(6, 4))
    sns.barplot(x=['Boiler Efficiency'], y=[be_value], palette='Blues', ax=ax_be)
    ax_be.set_title("Boiler Efficiency")
    ax_be.set_ylabel("Efficiency (%)")
    ax_be.set_ylim(0, 100) # Efficiency is usually 0-100%
    st.pyplot(fig_be)
    plt.close(fig_be)

    # 2. CO2 Emissions vs. (Conceptually) Power Output
    # For a single point, we'll just show the CO2 emissions value
    co2_value = st.session_state.calculated_result.get('CO2 Emissions (kg/hr)', 0)
    fig_co2, ax_co2 = plt.subplots(figsize=(6, 4))
    sns.barplot(x=['CO2 Emissions'], y=[co2_value], palette='Reds', ax=ax_co2)
    ax_co2.set_title("CO2 Emissions")
    ax_co2.set_ylabel("Emissions (kg/hr)")
    st.pyplot(fig_co2)
    plt.close(fig_co2)

    # 3. Plant Heat Rate Distribution (Conceptually)
    # For a single point, we'll show the Plant Heat Rate value
    phr_value = st.session_state.calculated_result.get('Plant Heat Rate (kcal/kWh)', 0)
    fig_phr, ax_phr = plt.subplots(figsize=(6, 4))
    sns.barplot(x=['Plant Heat Rate'], y=[phr_value], palette='Greens', ax=ax_phr)
    ax_phr.set_title("Plant Heat Rate")
    ax_phr.set_ylabel("Heat Rate (kcal/kWh)")
    st.pyplot(fig_phr)
    plt.close(fig_phr)

    st.markdown("---") # Separator for better visual organization

    # --- Recommendations Section ---
    st.subheader("💡 Performance Recommendations")

    # Generate recommendations based on the single set of calculated metrics
    recommendations_list = generate_recommendations(st.session_state.calculated_result)

    # Display each recommendation
    for rec in recommendations_list:
        st.markdown(rec)

