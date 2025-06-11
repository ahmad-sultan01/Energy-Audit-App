import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io # Import io for capturing info() output

# Define the calculate_metrics function
# This function calculates various power plant performance and emission metrics
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
    # Calculate heat input from coal
    energy_input = coal_flow * gcv

    # Calculate useful energy output in steam
    steam_energy = steam_flow * (steam_h - feed_h)

    # Calculate Boiler Efficiency (percentage)
    # Avoid division by zero by checking if energy_input is not zero
    efficiency = (steam_energy / energy_input) * 100 if energy_input != 0 else 0

    # Calculate Plant Heat Rate (kcal/kWh)
    # Avoid division by zero by checking if power_output is not zero
    plant_heat_rate = (energy_input / power_output) if power_output != 0 else 0

    # Calculate Specific Fuel Consumption (kg/kWh)
    # Avoid division by zero by checking if power_output is not zero
    specific_fuel_consumption = (coal_flow / power_output) if power_output != 0 else 0

    # Calculate CO2 emissions (kg/hr) based on coal flow
    # Assuming 2.29 kg CO2 per kg of bituminous coal (approximate factor)
    co2_emissions = coal_flow * 2.29

    # Calculate Flue Gas Loss (simplified placeholder formula)
    # A more accurate calculation would involve actual flue gas mass and specific heat capacity (Cp)
    flue_loss = (flue_temp - amb_temp) * 0.25 # This is a placeholder; needs refinement for real-world accuracy

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
    if hr < 2500 and hr != 0: # Ensure not zero, which could happen if power_output was zero
        rec.append("✅ **Plant Heat Rate (Avg: {:.2f} kcal/kWh)**: Efficient. Maintain load management and keep equipment in tuned condition.".format(hr))
    elif 2500 <= hr <= 3000:
        rec.append("⚠️ **Plant Heat Rate (Avg: {:.2f} kcal/kWh)**: Average. Inspect turbine sealing, condenser vacuum, and reheater losses.".format(hr))
    else: # This covers > 3000 and the zero case if power_output was zero
        rec.append("❌ **Plant Heat Rate (Avg: {:.2f} kcal/kWh)**: Inefficient. Audit heat exchangers, check turbine performance, condenser vacuum issues, and unaccounted auxiliary consumption.".format(hr))

    # Recommendation for Specific Fuel Consumption
    sfc = metrics.get('Specific Fuel Consumption (kg/kWh)', 0)
    if sfc < 0.6 and sfc != 0: # Ensure not zero
        rec.append("✅ **Specific Fuel Consumption (Avg: {:.2f} kg/kWh)**: Efficient. Ensure consistent coal quality and maintain feed systems.".format(sfc))
    elif 0.6 <= sfc <= 0.75:
        rec.append("⚠️ **Specific Fuel Consumption (Avg: {:.2f} kg/kWh)**: Acceptable. Verify air-fuel ratio, minimize unburnt carbon.".format(sfc))
    else: # This covers > 0.75 and the zero case
        rec.append("❌ **Specific Fuel Consumption (Avg: {:.2f} kg/kWh)**: High. Recommend coal quality improvement, combustion tuning, and reducing clinker formation.".format(sfc))

    # Recommendation for Flue Gas Loss
    fl = metrics.get('Flue Gas Loss', 0)
    if fl < 5 and fl != 0: # Ensure not zero
        rec.append("✅ **Flue Gas Loss (Avg: {:.2f}%)**: Optimal flue gas recovery. Keep stack temperature and air ratio monitored.".format(fl))
    elif 5 <= fl <= 10:
        rec.append("⚠️ **Flue Gas Loss (Avg: {:.2f}%)**: Moderate loss. Consider preheating combustion air or recovering heat using economizer.".format(fl))
    else: # This covers > 10 and the zero case
        rec.append("❌ **Flue Gas Loss (Avg: {:.2f}%)**: High heat loss. Suggest urgent flue gas heat recovery installation, reduce excess air, and check for insulation leaks.".format(fl))

    # Recommendation for CO2 Emissions (optional, based on your previous examples)
    co2 = metrics.get('CO2 Emissions (kg/hr)', 0)
    if co2 > 8000: # Example threshold
        rec.append("⚠️ **CO₂ Emissions (Avg: {:.2f} kg/hr)**: High CO₂ emissions. Explore cleaner fuels or carbon capture technologies.".format(co2))
    elif co2 > 0: # General message if not extremely high but still present
        rec.append("✅ **CO₂ Emissions (Avg: {:.2f} kg/hr)**: Monitor CO₂ emissions regularly and explore opportunities for reduction.".format(co2))

    return rec

# Streamlit UI
st.title("📊 Performance & Emissions Dashboard")

uploaded_file = st.file_uploader("Upload Power Plant Data CSV", type=["csv"])

if uploaded_file:
    # Read the uploaded CSV into a pandas DataFrame
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Preview of Raw Data")
    st.dataframe(df.head())

    # Ensure all numerical columns are indeed numeric
    # This step is crucial for calculations and prevents errors from mixed types
    numeric_cols = [
        'Coal Flow', 'GCV', 'Steam Flow', 'Steam Enthalpy',
        'Feedwater Enthalpy', 'Power Output', 'Flue Temp', 'Ambient Temp'
    ]
    for col in numeric_cols:
        if col in df.columns:
            # Convert to numeric, coerce errors will turn invalid parsing into NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            st.error(f"Missing expected column in CSV: **{col}**. Please ensure your CSV has all required columns.")
            st.stop() # Stop execution if a critical column is missing

    # Drop rows where any of the critical input columns are NaN after coercion
    df.dropna(subset=numeric_cols, inplace=True)

    if df.empty:
        st.warning("No valid data rows remaining after cleaning. Please check your CSV for missing or non-numeric values in critical columns.")
        st.stop()

    # --- Apply the calculate_metrics function to each row of the DataFrame ---
    calculated_metrics_df = df.apply(
        lambda row: calculate_metrics(
            coal_flow=row['Coal Flow'],
            gcv=row['GCV'],
            steam_flow=row['Steam Flow'],
            steam_h=row['Steam Enthalpy'],
            feed_h=row['Feedwater Enthalpy'],
            power_output=row['Power Output'],
            flue_temp=row['Flue Temp'],
            amb_temp=row['Ambient Temp']
        ),
        axis=1
    ).apply(pd.Series) # Explicitly convert the Series of dictionaries to a DataFrame

    # Concatenate the original DataFrame with the new calculated metrics DataFrame
    df_with_metrics = pd.concat([df, calculated_metrics_df], axis=1)

    st.subheader("✨ Calculated Metrics Preview")
    st.dataframe(df_with_metrics.head())

    # Add detailed DataFrame info for debugging
    st.subheader("🔬 DataFrame Info (for Debugging)")
    buffer = io.StringIO()
    df_with_metrics.info(buf=buffer)
    st.text(buffer.getvalue())

    if df_with_metrics.empty:
        st.warning("The DataFrame is empty after calculations. No plots or recommendations can be generated.")
    else:
        # --- Plotting Section ---

        # Plotting Boiler Efficiency vs Coal Flow
        has_boiler_eff_coal_flow = 'Boiler Efficiency' in df_with_metrics.columns and 'Coal Flow' in df_with_metrics.columns
        st.write(f"Debug: 'Boiler Efficiency' and 'Coal Flow' columns exist: {has_boiler_eff_coal_flow}")
        if has_boiler_eff_coal_flow:
            st.write("Debug: Attempting to plot Boiler Efficiency vs Coal Flow")
            st.subheader("🔥 Boiler Efficiency vs Coal Flow")
            try:
                fig1, ax1 = plt.subplots(figsize=(10, 6))
                sns.scatterplot(data=df_with_metrics, x="Coal Flow", y="Boiler Efficiency", ax=ax1)
                ax1.set_title("Boiler Efficiency vs. Coal Flow")
                ax1.set_xlabel("Coal Flow (kg/hr)")
                ax1.set_ylabel("Boiler Efficiency (%)")
                st.pyplot(fig1)
                plt.close(fig1)
            except Exception as e:
                st.error(f"Error plotting Boiler Efficiency vs Coal Flow: {e}")
        else:
            st.warning("Cannot plot Boiler Efficiency vs Coal Flow: Required columns not found.")

        # Plotting CO2 Emissions vs Power Output
        has_co2_power_output = 'CO2 Emissions (kg/hr)' in df_with_metrics.columns and 'Power Output' in df_with_metrics.columns
        st.write(f"Debug: 'CO2 Emissions (kg/hr)' and 'Power Output' columns exist: {has_co2_power_output}")
        if has_co2_power_output:
            st.write("Debug: Attempting to plot CO2 Emissions vs Power Output")
            st.subheader("🌫 CO₂ Emissions vs Power Output")
            try:
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                sns.scatterplot(data=df_with_metrics, x="Power Output", y="CO2 Emissions (kg/hr)", ax=ax2)
                ax2.set_title("CO₂ Emissions vs. Power Output")
                ax2.set_xlabel("Power Output (kWh)")
                ax2.set_ylabel("CO₂ Emissions (kg/hr)")
                st.pyplot(fig2)
                plt.close(fig2)
            except Exception as e:
                st.error(f"Error plotting CO2 Emissions vs Power Output: {e}")
        else:
            st.warning("Cannot plot CO₂ Emissions vs Power Output: Required columns not found.")

        # Plotting Plant Heat Rate Distribution
        has_plant_heat_rate = 'Plant Heat Rate (kcal/kWh)' in df_with_metrics.columns
        st.write(f"Debug: 'Plant Heat Rate (kcal/kWh)' column exists: {has_plant_heat_rate}")
        if has_plant_heat_rate:
            st.write("Debug: Attempting to plot Plant Heat Rate Distribution")
            st.subheader("🔁 Plant Heat Rate Distribution")
            try:
                fig3, ax3 = plt.subplots(figsize=(10, 6))
                sns.histplot(data=df_with_metrics, x="Plant Heat Rate (kcal/kWh)", kde=True, ax=ax3)
                ax3.set_title("Distribution of Plant Heat Rate")
                ax3.set_xlabel("Plant Heat Rate (kcal/kWh)")
                ax3.set_ylabel("Frequency")
                st.pyplot(fig3)
                plt.close(fig3)
            except Exception as e:
                st.error(f"Error plotting Plant Heat Rate Distribution: {e}")
        else:
            st.warning("Cannot plot Plant Heat Rate Distribution: Required column not found.")

        # --- Recommendations Section ---
        st.subheader("💡 Performance Recommendations")

        # Calculate average metrics for recommendations
        avg_metrics = {
            "Boiler Efficiency": df_with_metrics['Boiler Efficiency'].mean(),
            "Plant Heat Rate (kcal/kWh)": df_with_metrics['Plant Heat Rate (kcal/kWh)'].mean(),
            "Specific Fuel Consumption (kg/kWh)": df_with_metrics['Specific Fuel Consumption (kg/kWh)'].mean(),
            "Flue Gas Loss": df_with_metrics['Flue Gas Loss'].mean(),
            "CO2 Emissions (kg/hr)": df_with_metrics['CO2 Emissions (kg/hr)'].mean()
        }

        recommendations_list = generate_recommendations(avg_metrics)

        for rec in recommendations_list:
            st.markdown(rec) # Use markdown to render emojis and bold text

    # Optional: Display a summary of all calculated metrics
    st.subheader("📊 Full Data with Calculated Metrics")
    st.dataframe(df_with_metrics)

