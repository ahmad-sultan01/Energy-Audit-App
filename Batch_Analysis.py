import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io # Import io for capturing info() output if needed for debugging

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
        rec.append("✅ **Boiler Efficiency (Avg: {:.2f}%)**: Excellent. Maintain current operation and schedule routine maintenance.".format(be))
    elif 70 <= be <= 85:
        rec.append("⚠️ **Boiler Efficiency (Avg: {:.2f}%)**: Good, but room for improvement. Optimize excess air supply, clean heat transfer surfaces (e.g., soot blowing).".format(be))
    else:
        rec.append("❌ **Boiler Efficiency (Avg: {:.2f}%)**: Inefficient. Check for incomplete combustion, poor coal quality, leaks, and fouling in boiler tubes. Consider retrofitting economizers or better insulation.".format(be))

    # Recommendation for Plant Heat Rate
    hr = metrics.get('Plant Heat Rate (kcal/kWh)', 0)
    # Check for hr > 0 to avoid recommending 'Efficient' for 0 values
    if hr < 2500 and hr > 0:
        rec.append("✅ **Plant Heat Rate (Avg: {:.2f} kcal/kWh)**: Efficient. Maintain load management and keep equipment in tuned condition.".format(hr))
    elif 2500 <= hr <= 3000:
        rec.append("⚠️ **Plant Heat Rate (Avg: {:.2f} kcal/kWh)**: Average. Inspect turbine sealing, condenser vacuum, and reheater losses.".format(hr))
    else: # This covers > 3000 and 0 values (or negative, if any)
        rec.append("❌ **Plant Heat Rate (Avg: {:.2f} kcal/kWh)**: Inefficient. Audit heat exchangers, check turbine performance, condenser vacuum issues, and unaccounted auxiliary consumption.".format(hr))

    # Recommendation for Specific Fuel Consumption
    sfc = metrics.get('Specific Fuel Consumption (kg/kWh)', 0)
    if sfc < 0.6 and sfc > 0:
        rec.append("✅ **Specific Fuel Consumption (Avg: {:.2f} kg/kWh)**: Efficient. Ensure consistent coal quality and maintain feed systems.".format(sfc))
    elif 0.6 <= sfc <= 0.75:
        rec.append("⚠️ **Specific Fuel Consumption (Avg: {:.2f} kg/kWh)**: Acceptable. Verify air-fuel ratio, minimize unburnt carbon.".format(sfc))
    else: # This covers > 0.75 and 0 values
        rec.append("❌ **Specific Fuel Consumption (Avg: {:.2f} kg/kWh)**: High. Recommend coal quality improvement, combustion tuning, and reducing clinker formation.".format(sfc))

    # Recommendation for Flue Gas Loss
    fl = metrics.get('Flue Gas Loss', 0)
    if fl < 5 and fl > 0:
        rec.append("✅ **Flue Gas Loss (Avg: {:.2f}%)**: Optimal flue gas recovery. Keep stack temperature and air ratio monitored.".format(fl))
    elif 5 <= fl <= 10:
        rec.append("⚠️ **Flue Gas Loss (Avg: {:.2f}%)**: Moderate loss. Consider preheating combustion air or recovering heat using economizer.".format(fl))
    else: # This covers > 10 and 0 values
        rec.append("❌ **Flue Gas Loss (Avg: {:.2f}%)**: High heat loss. Suggest urgent flue gas heat recovery installation, reduce excess air, and check for insulation leaks.".format(fl))

    # Recommendation for CO2 Emissions
    co2 = metrics.get('CO2 Emissions (kg/hr)', 0)
    if co2 > 8000:
        rec.append("⚠️ **CO₂ Emissions (Avg: {:.2f} kg/hr)**: High CO₂ emissions. Explore cleaner fuels or carbon capture technologies.".format(co2))
    elif co2 > 0:
        rec.append("✅ **CO₂ Emissions (Avg: {:.2f} kg/hr)**: Monitor CO₂ emissions regularly and explore opportunities for reduction.".format(co2))
    return rec


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

        # Check for missing required columns first
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"❌ CSV must have the following columns: {', '.join(missing_cols)}. Please check your CSV file.")
            st.stop() # Stop execution if critical columns are missing

        # Convert relevant columns to numeric, coercing errors
        for col in required_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows where critical input columns are NaN after coercion
        # This prevents errors in calculate_metrics
        df.dropna(subset=required_columns, inplace=True)

        if df.empty:
            st.warning("No valid data rows remaining after cleaning. Please check your CSV for missing or non-numeric values in critical input columns.")
            st.stop()


        with st.spinner("🔄 Processing..."):
            results = []
            for _, row in df.iterrows():
                r = calculate_metrics(
                    row["Coal Flow"], row["GCV"], row["Steam Flow"],
                    row["Steam Enthalpy"], row["Feedwater Enthalpy"],
                    row["Power Output"], row["Flue Temp"], row["Ambient Temp"]
                )
                results.append(r)

            result_df = pd.DataFrame(results)
            final_df = pd.concat([df.reset_index(drop=True), result_df.reset_index(drop=True)], axis=1) # Reset index before concat


        st.subheader("📊 Audit Results")
        st.dataframe(final_df)

        st.download_button("📥 Download Results", final_df.to_csv(index=False),
                          file_name="audit_results.csv", mime="text/csv")

        st.subheader("📈 Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(10, 8))
        # Ensure only numeric columns are passed to .corr()
        sns.heatmap(final_df.corr(numeric_only=True), ax=ax, annot=True, cmap="coolwarm")
        plt.title("Correlation Heatmap of Metrics") # Added title for clarity
        st.pyplot(fig)
        plt.close(fig) # Close plot to free memory

        # --- Add Recommendations Section ---
        st.subheader("💡 Batch Performance Recommendations")

        # Calculate average metrics from the final_df
        # Ensure only numeric columns are included for mean calculation
        numeric_metrics_cols = [
            "Boiler Efficiency",
            "Plant Heat Rate (kcal/kWh)",
            "Specific Fuel Consumption (kg/kWh)",
            "Flue Gas Loss",
            "CO2 Emissions (kg/hr)"
        ]
        
        # Filter for existing numeric metric columns before calculating mean
        existing_metrics_for_avg = [col for col in numeric_metrics_cols if col in final_df.columns]

        if not existing_metrics_for_avg:
            st.warning("No calculated metrics available to generate recommendations. Please check calculations.")
        else:
            # Calculate the mean of only the existing numeric calculated metric columns
            avg_metrics = final_df[existing_metrics_for_avg].mean().to_dict()

            recommendations_list = generate_recommendations(avg_metrics)

            for rec in recommendations_list:
                st.markdown(rec)

    except Exception as e:
        st.error(f"❌ An error occurred: {e}. Please ensure your CSV format is correct and contains valid data.")

