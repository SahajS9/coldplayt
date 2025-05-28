import numpy as np
import pandas as pd
from typing import Union, Optional

NumberOrSeries = Union[float, pd.Series]


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
    """
    voltage_ref = calibration['voltage_ref']
    adc_max = calibration['calibration']
    voltage_min = calibration['V_min']
    pressure_min = calibration['P_min']
    pressure_max = calibration['V_max']
    voltage_max = calibration['P_max']

    if adc_value == 0 or adc_value >= adc_max:
        return None
    
    voltage = adc_value * (5.0 / adc_max)
    pressure = (voltage - 0.5) * 100
    return pressure


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


def calibrate_df(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Apply all sensor calibrations to raw dataframe.
    """
    therm_cal = config['calibration']['thermistor']

    flow_rate = config['calibration'].get('flow_rate_m3s', 0.0001)

    for t_col in ['T1', 'T2', 'T3', 'fluid_in', 'fluid_out']:
        if t_col in df:
            df[f'{t_col}_C'] = df[t_col].apply(lambda x: temp_from_adc(x, therm_cal) if pd.notna(x) else np.nan)

    if 'P_in' in df.columns and 'P_out' in df.columns:
        df['delta_p'] = df['P_out'] - df['P_in']
        df['pump_power_calc'] = calculate_pump_power(flow_rate, df['delta_p'])
        df['pump_cost_per_day'] = calculate_pump_cost(df['pump_power_calc'])
    else:
        df['delta_p'] = df['pump_power_calc'] = df['pump_cost_per_day'] = np.nan


    m_dot = 0.01  # kg/s
    cp = config.get('fluid_cp', 1090)  # Default: Flutec PP1

    df['Q_dot'] = calculate_heat_transfer(m_dot, cp, df.get('fluid_in_C'), df.get('fluid_out_C'))

    if 'heater_power' in df.columns:
        df['efficiency'] = calculate_efficiency(df['heater_power'], df['Q_dot'])
    else:
        df['efficiency'] = np.nan

    return df
