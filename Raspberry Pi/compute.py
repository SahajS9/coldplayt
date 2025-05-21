import numpy as np

def steinhart(voltage, R0=10000, T0=298.15, B=3950, Vref=3.3):
    R = R0 * (voltage / (Vref - voltage))
    return 1 / (1/T0 + (1/B) * np.log(R/R0)) - 273.15

def pressure_from_voltage(voltage, scale=0.1):
    return voltage / scale

def heat_transfer_rate(m_dot, cp, T_in, T_out):
    return m_dot * cp * (T_out - T_in)

def pump_power(flow_rate, delta_p):
    return flow_rate * delta_p

def thermal_flux(power, area):
    return power / area