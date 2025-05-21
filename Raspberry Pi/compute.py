import numpy as np

def adc_to_temperature(adc_value, calibration):
    """
    Convert ADC reading to temperature in Celsius using Steinhart-Hart equation.
    :param adc_value: Raw ADC reading (integer, 0 to adc_max)
    :param calibration: Dict with keys 'R_fixed', 'R_nominal', 'T_nominal', 'beta', 'adc_max'
    :return: Temperature in Celsius or None if invalid reading
    """
    R_fixed = calibration['R_fixed']
    R_nominal = calibration['R_nominal']
    T_nominal = calibration['T_nominal']
    beta = calibration['beta']
    adc_max = calibration['adc_max']

    if adc_value == 0 or adc_value >= adc_max:
        return None  # Avoid division by zero or invalid ADC value

    resistance = R_fixed / (adc_max / adc_value - 1)

    steinhart = resistance / R_nominal
    steinhart = np.log(steinhart)
    steinhart /= beta
    steinhart += 1.0 / (T_nominal + 273.15)
    steinhart = 1.0 / steinhart
    temperature_c = steinhart - 273.15

    return temperature_c

def calculate_heating_power(voltage, current):
    """
    Calculate heating power (W) from voltage (V) and current (A).
    :param voltage: Voltage in volts
    :param current: Current in amperes
    :return: Power in watts
    """
    if voltage is None or current is None:
        return None
    return voltage * current


def calculate_pump_power(flow_rate, delta_p):
    """
    Calculate pump power using P = ΔP * Q.
    Handles scalar or Series delta_p.
    :param flow_rate: volumetric flow rate in m^3/s (scalar)
    :param delta_p: pressure difference in Pascals (scalar or Series)
    :return: pump power in Watts
    """
    if flow_rate is None or delta_p is None:
        return None
    return delta_p * flow_rate  # W = Pa * m^3/s


def calculate_heat_transfer(mass_flow_rate, specific_heat_capacity, temp_in, temp_out):
    """
    Calculate heat transfer rate Q̇ = m·cp·ΔT.
    Handles Series or scalar temperature inputs.
    :param mass_flow_rate: Mass flow rate (kg/s)
    :param specific_heat_capacity: Specific heat capacity (J/kg.K)
    :param temp_in: Fluid inlet temperature (°C)
    :param temp_out: Fluid outlet temperature (°C)
    :return: Heat transfer rate (W) or None
    """
    if any(x is None for x in [mass_flow_rate, specific_heat_capacity, temp_in, temp_out]):
        return None

    delta_T = temp_in - temp_out
    return mass_flow_rate * specific_heat_capacity * delta_T

def calculate_efficiency(heating_power, heat_transferred):
    """
    Calculate thermal efficiency as ratio of useful heat to input power.
    :param heating_power: Electrical heating power (W)
    :param heat_transferred: Heat absorbed by fluid (W)
    :return: Efficiency (0 to 1) or None
    """
    if heating_power is None or heat_transferred is None or heating_power == 0:
        return None
    return heat_transferred / heating_power