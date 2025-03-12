import math

def calculate_clamping_force(torque, diameter, torque_coefficient=0.2):
    """
    Calculate the clamping force based on torque.
    
    :param torque: Applied torque in lbf-ft
    :param diameter: Nominal bolt diameter in inches
    :param torque_coefficient: Torque coefficient (default 0.2 for dry threads)
    :return: Clamping force in lbf
    """
    return (torque * 12) / (diameter * torque_coefficient) # Convert ft-lbf to in-lbf

def calculate_clamping_pressure(force, outer_diameter, inner_diameter):
    """
    Calculate the clamping pressure in PSI.
    
    :param force: Clamping force in lbf
    :param outer_diameter: Outer diameter of the washer/nut bearing surface in inches
    :param inner_diameter: Inner diameter (typically bolt diameter) in inches
    :return: Clamping pressure in PSI
    """
    bearing_area = (math.pi / 4) * (outer_diameter**2 - inner_diameter**2)
    return force / bearing_area if bearing_area > 0 else 0

# Example input
torque = 100  # ft-lbf
diameter = 0.5  # inches
torque_coefficient = 0.2  # Assumed
o_diameter = 0.875  # Washer outer diameter in inches
i_diameter = diameter  # Inner diameter is typically bolt diameter

# Calculate values
clamping_force = calculate_clamping_force(torque, diameter, torque_coefficient)
clamping_pressure = calculate_clamping_pressure(clamping_force, o_diameter, i_diameter)

# Output results
print(f"Clamping Force: {clamping_force:.2f} lbf")
print(f"Clamping Pressure: {clamping_pressure:.2f} PSI")