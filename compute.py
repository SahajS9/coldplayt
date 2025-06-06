import numpy as np
import pandas as pd
from typing import Union, Optional

NumberOrSeries = Union[float, pd.Series]

# -----------------------------------------------------------------------------
# Converts raw ADC sensor readings to calibrated values
# -----------------------------------------------------------------------------
def temp_from_adc(adc_value: Union[int, float], calibration: dict) -> Optional[float]:
    """
    Convert an ADC value to temperature (°C) using the Steinhart-Hart equation.
    """
    R_fixed = calibration['R_fixed']
    R_nominal = calibration['R_nominal']
    T_nominal = calibration['T_nominal']
    beta = calibration['beta']
    adc_max = calibration['adc_max']

    if adc_value == 0 or adc_value >= adc_max:
        return None

    resistance = R_fixed / (adc_max / adc_value - 1)
    steinhart = np.log(resistance / R_nominal) / beta
    steinhart += 1.0 / (T_nominal + 273.15)
    temperature_k = 1.0 / steinhart
    return temperature_k - 273.15


def pressure_from_adc(adc_value: Union[int, float], calibration: dict) -> Optional[float]:
    """
    Convert an ADC value to PSI by adjusting for voltage.
    Pressure in the lab is about 14.6 psi fo reference.
    
    Parameters:
        adc_value: Raw ADC integer (0–1023 for 10-bit)
        adc_max: Max ADC value (default: 1023)
        V_ref: ADC reference voltage (default: 5.0V)
        p_range: Pressure range (default: 0–200 PSI)
        V_min: Minimum sensor output voltage (default: 0.5V)
        V_max: Maximum sensor output voltage (default: 4.5V)

    Returns:
        Pressure in PSI (float), or NaN if invalid
    """
    voltage_ref = calibration['V_ref']
    adc_max = calibration['adc_max']
    voltage_min = calibration['V_min']
    pressure_min = calibration['P_min']
    pressure_max = calibration['P_max']
    voltage_max = calibration['V_max']

    if adc_value is None or not (0 <= adc_value <= adc_max):
        return float('nan')

    voltage = (adc_value / adc_max) * voltage_ref
    if voltage < voltage_min:
        return pressure_min  # Below range
    elif voltage > voltage_max:
        return pressure_max  # Above range
    else:
        return ((voltage - voltage_min) / (voltage_max - voltage_min)) * pressure_max


# -----------------------------------------------------------------------------
# Calculations
# -----------------------------------------------------------------------------
def calculate_heat_transfer(m_dot: float, cp: float, temp_in: NumberOrSeries, temp_out: NumberOrSeries) -> NumberOrSeries:
    """
    Compute heat transfer rate using Q̇ = ṁ · cp · ΔT.
    """
    return m_dot * cp * (temp_in - temp_out)


def calculate_pump_power(flow_rate: float, delta_p: NumberOrSeries) -> NumberOrSeries:
    """
    Compute pump power using P = ΔP · Q.
    """
    return flow_rate * delta_p


def calculate_pump_cost(pump_power: NumberOrSeries, electricity_rate: float = 0.12) -> NumberOrSeries:
    """
    Calculate cost of pump operation in $/day.
    """
    energy_kWh_per_s = pump_power / 1000.0
    return energy_kWh_per_s * 3600 * 24 * electricity_rate


def calculate_heating_power(voltage: Optional[float], current: Optional[float]) -> Optional[float]:
    """
    Compute electrical heating power.
    """
    if voltage is None or current is None:
        return None
    return voltage * current

# def calculate_heating_power_if_not_present() -> None:
#     return Q_dot = calculate_heat_transfer(m_dot, cp, df.get('fluid_in_F'), df.get('fluid_out_F'))
#         # df['Q_dot'] = calculate_heat_transfer(m_dot, cp, df.get('fluid_in_F'), df.get('fluid_out_F'))


def calculate_efficiency(heating_power: NumberOrSeries, heat_transferred: NumberOrSeries) -> NumberOrSeries:
    """
    Calculate thermal efficiency η = Q̇_out / Q̇_in.
    """
    heating_power = np.where(heating_power == 0, np.nan, heating_power)
    return heat_transferred / heating_power


def calculate_heat_flux(temp_top: NumberOrSeries, temp_bottom: NumberOrSeries, thickness: float, thermal_conductivity: float) -> NumberOrSeries:
    """
    Calculate heat flux using Fourier's Law: q = -k*(dT/dx).
    """
    return thermal_conductivity * (temp_top - temp_bottom) / thickness


# -----------------------------------------------------------------------------
# Main function, does calibration then calculations
# -----------------------------------------------------------------------------
def calibrate_df(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Apply all sensor calibrations to raw dataframe.
    """
    thermistor_cal = config['calibration']['thermistor']
    pressure_cal = config['calibration']['pressure_transducer']
    flow_rate = config['calibration'].get('flow_rate_m3s', 0.0001)
    pump_power = config['calibration'].get('pump_power')

    for t_col in ['T1', 'T2', 'T3', 'fluid_in', 'fluid_out']:
        if t_col in df:
            df[f'{t_col}_F'] = df[t_col].apply(lambda x: temp_from_adc(x, thermistor_cal) if pd.notna(x) else np.nan)
    
    for P_col in ['P_in', 'P_out']:
        if P_col in df:
            df[f'{P_col}_psi'] = df[P_col].apply(lambda x: pressure_from_adc(x, pressure_cal) if pd.notna(x) else np.nan)

    if 'P_in' in df.columns and 'P_out' in df.columns:
        df['delta_p'] = df['P_out'] - df['P_in']
        df['pump_power_calc'] = calculate_pump_power(flow_rate, df['delta_p'])
        df['pump_cost_per_day'] = calculate_pump_cost(df['pump_power_calc'])
        if 'heater_power' in df.columns:
            df['Q_dot'] = calculate_heat_transfer(m_dot, cp, df.get('fluid_in_F'), df.get('fluid_out_F'))
            df['efficiency'] = calculate_efficiency(df['heater_power'], df['Q_dot'])
    else:
        df['delta_p'] = df['pump_power_calc'] = df['pump_cost_per_day'] = np.nan

    m_dot = 0.01  # kg/s
    cp = config.get('fluid_cp', 1090)  # Default: Flutec PP1

    if 'fluid_in' in df.columns and 'fluid_out' in df.columns:
        df['Q_dot'] = calculate_heat_transfer(m_dot, cp, df.get('fluid_in_F'), df.get('fluid_out_F'))

    if 'pump_power' in df.columns:
        df['pump_power_calc'] = pump_power
        print(df['pump_power_calc'])
        
    # if 'heater_power' in df.columns:
    #     df['efficiency'] = calculate_efficiency(df['heater_power'], df['Q_dot'])
    # else:
    #     # calculate_heating_power_if_not_present()
    #     df['efficiency'] = calculate_efficiency(df['heater_power'], df['Q_dot'])
    #     # df['efficiency'] = calculate_efficiency(df.get('heater_power_calc', np.nan), df['Q_dot'])

    return df
