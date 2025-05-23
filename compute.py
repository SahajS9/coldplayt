import numpy as np
import pandas as pd
from typing import Union, Optional

NumberOrSeries = Union[float, pd.Series]


def adc_to_temperature(adc_value: Union[int, float], calibration: dict) -> Optional[float]:
    """
    Convert an ADC value to temperature (°C) using the Steinhart-Hart equation.

    Parameters:
        adc_value (int or float): Raw ADC value (0 to adc_max).
        calibration (dict): Thermistor calibration settings, including:
        - R_fixed (float): Fixed resistor value in ohms
        - R_nominal (float): Nominal resistance at T_nominal
        - T_nominal (float): Nominal temperature in °C
        - beta (float): Beta coefficient
        - adc_max (int): ADC resolution max (e.g., 1023)

    Returns:
        float or None: Temperature in Celsius or None for invalid readings.
    """
    R_fixed = calibration['R_fixed']
    R_nominal = calibration['R_nominal']
    T_nominal = calibration['T_nominal']
    beta = calibration['beta']
    adc_max = calibration['adc_max']

    if adc_value == 0 or adc_value >= adc_max:
        return None  # Avoid division by zero or invalid input

    resistance = R_fixed / (adc_max / adc_value - 1)
    steinhart = np.log(resistance / R_nominal) / beta
    steinhart += 1.0 / (T_nominal + 273.15)
    temperature_k = 1.0 / steinhart
    return temperature_k - 273.15


def calculate_heat_transfer(
    m_dot: float,
    cp: float,
    temp_in: NumberOrSeries,
    temp_out: NumberOrSeries
) -> NumberOrSeries:
    """
    Compute heat transfer rate using Q̇ = ṁ · cp · ΔT.

    Parameters:
        m_dot (float): Mass flow rate in kg/s
        cp (float): Specific heat capacity in J/kg·K
        temp_in (float or Series): Inlet temperature in °C
        temp_out (float or Series): Outlet temperature in °C

    Returns:
        float or Series: Heat transfer rate in Watts
    """
    return m_dot * cp * (temp_in - temp_out)


def calculate_pump_power(
    flow_rate: float,
    delta_p: NumberOrSeries
) -> NumberOrSeries:
    """
    Compute pump power using P = ΔP · Q.

    Parameters:
        flow_rate (float): Volumetric flow rate in m³/s
        delta_p (float or Series): Pressure differential in Pascals

    Returns:
        float or Series: Pump power in Watts
    """
    return flow_rate * delta_p


def calculate_heating_power(
    voltage: Optional[float],
    current: Optional[float]
) -> Optional[float]:
    """
    Compute electrical heating power.

    Parameters:
        voltage (float): Voltage in volts
        current (float): Current in amperes

    Returns:
        float or None: Power in Watts
    """
    if voltage is None or current is None:
        return None
    return voltage * current


def calculate_efficiency(
    heating_power: NumberOrSeries,
    heat_transferred: NumberOrSeries
) -> NumberOrSeries:
    """
    Calculate thermal efficiency η = Q̇_out / Q̇_in.

    Parameters:
        heating_power (float or Series): Input electrical power
        heat_transferred (float or Series): Output heat rate to fluid

    Returns:
        float or Series: Efficiency ratio (0–1), or NaN where invalid
    """
    heating_power = np.where(heating_power == 0, np.nan, heating_power)
    return heat_transferred / heating_power
