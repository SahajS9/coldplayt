% MATLAB script to calculate clamping force and pressure

function [clamping_force, clamping_pressure] = torque_to_clamping(torque, diameter, torque_coefficient, outer_diameter, inner_diameter)
    % Calculate the clamping force
    clamping_force = (torque * 12) / (diameter * torque_coefficient); % Convert ft-lbf to in-lbf
    
    % Calculate the bearing surface area
    bearing_area = (pi / 4) * (outer_diameter^2 - inner_diameter^2);
    
    % Calculate the clamping pressure
    if bearing_area > 0
        clamping_pressure = clamping_force / bearing_area;
    else
        clamping_pressure = 0;
    end
end

% Example input
torque = 100; % ft-lbf
diameter = 0.5; % inches
torque_coefficient = 0.2; % Assumed
outer_diameter = 0.875; % Washer outer diameter in inches
inner_diameter = diameter; % Inner diameter is typically bolt diameter

% Calculate values
[clamping_force, clamping_pressure] = torque_to_clamping(torque, diameter, torque_coefficient, outer_diameter, inner_diameter);

% Output results
fprintf('Clamping Force: %.2f lbf\n', clamping_force);
fprintf('Clamping Pressure: %.2f PSI\n', clamping_pressure);

