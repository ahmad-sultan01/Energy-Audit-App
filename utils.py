def calculate_metrics(coal_flow, gcv, steam_flow, h_steam, h_feed,
                      power_output, flue_temp, ambient_temp):
    """
    Calculate boiler and plant performance metrics.

    Parameters:
    - coal_flow: Coal consumption rate (kg/hr)
    - gcv: Gross Calorific Value of coal (kcal/kg)
    - steam_flow: Steam generation rate (kg/hr)
    - h_steam: Enthalpy of steam (kcal/kg)
    - h_feed: Enthalpy of feed water (kcal/kg)
    - power_output: Power generated (kW)
    - flue_temp: Flue gas temperature (°C)
    - ambient_temp: Ambient temperature (°C)

    Returns:
    Dictionary of metrics:
    - Boiler Efficiency (%)
    - Heat Rate (kcal/kWh)
    - Specific Fuel Consumption (kg/kWh)
    - Flue Gas Loss (%)
    - CO2 Emissions (kg/hr)
    """

    heat_input = coal_flow * gcv
    steam_energy = steam_flow * (h_steam - h_feed)

    boiler_efficiency = (steam_energy / heat_input) * 100 if heat_input else 0
    heat_rate = heat_input / power_output if power_output else 0
    sfc = coal_flow / power_output if power_output else 0

    # Constants for flue gas loss calculation
    cp_flue_gas = 0.24  # kcal/kg°C (approximate specific heat capacity of flue gas)
    flue_gas_flow = 1.5 * coal_flow  # Simplified estimation of flue gas mass flow (kg/hr)
    flue_gas_loss = ((flue_temp - ambient_temp) * cp_flue_gas * flue_gas_flow) / heat_input * 100 if heat_input else 0

    # CO2 emissions factor for coal (approximate)
    co2_emissions = coal_flow * 2.32  # kg CO2 per kg coal

    return {
        "Boiler Efficiency (%)": round(boiler_efficiency, 2),
        "Heat Rate (kcal/kWh)": round(heat_rate, 2),
        "Specific Fuel Consumption (kg/kWh)": round(sfc, 4),
        "Flue Gas Loss (%)": round(flue_gas_loss, 2),
        "CO2 Emissions (kg/hr)": round(co2_emissions, 2)
    }


def generate_recommendations(metrics):
    rec = []

    be = metrics.get("Boiler Efficiency (%)", 0)
    if be > 85:
        rec.append("✅ Excellent boiler efficiency.")
    elif be >= 70:
        rec.append("⚠️ Moderate efficiency. Optimize air/fuel ratio.")
    else:
        rec.append("❌ Low efficiency. Improve combustion or insulation.")

    hr = metrics.get("Heat Rate (kcal/kWh)", 0)
    if hr > 3000:
        rec.append("❌ High heat rate. Check turbines & steam conditions.")
    elif hr > 2500:
        rec.append("⚠️ Slightly high heat rate. Review operations.")
    else:
        rec.append("✅ Efficient heat rate.")

    sfc = metrics.get("Specific Fuel Consumption (kg/kWh)", 0)
    if sfc > 0.75:
        rec.append("❌ High fuel usage. Check fuel quality.")
    elif sfc > 0.6:
        rec.append("⚠️ Improve combustion.")
    else:
        rec.append("✅ Efficient fuel use.")

    fl = metrics.get("Flue Gas Loss (%)", 0)
    if fl > 10:
        rec.append("❌ High flue gas loss. Add economizers.")
    elif fl > 5:
        rec.append("⚠️ Consider better insulation.")
    else:
        rec.append("✅ Heat recovery is good.")

    co2 = metrics.get("CO2 Emissions (kg/hr)", 0)
    if co2 > 8000:
        rec.append("⚠️ High CO₂ emissions. Explore cleaner fuels or carbon capture.")

    return "\n\n".join(rec)
