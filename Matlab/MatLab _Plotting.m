% Real-Time Temperature Plotting

% Clear workspace and close existing figures
clear;
close all;

% Serial port configuration
port = 'COM3'; % Replace with your Arduino's serial port
baudRate = 9600;

% Initialize serial connection
if ~isempty(instrfind)
    fclose(instrfind);
    delete(instrfind);
end
s = serial(port, 'BaudRate', baudRate);
fopen(s);

% Initialize variables
numThermistors = 5; % Number of thermistors
timeWindow = 20; % Time window for the graph (in seconds)
updateInterval = 1; % Update interval for the graph (in seconds)

% Create empty arrays to store data
timeData = [];
temperatureData = zeros(0, numThermistors);

% Create the figure and axes
figure;
hold on;
xlabel('Time (s)');
ylabel('Temperature (°C)');
title('Temperature Over Time');
ylim([0, 100]); % Adjust based on your temperature range
grid on;

% Create lines for each thermistor
lines = gobjects(1, numThermistors);
colors = lines(numThermistors); % Use MATLAB's default colors
for i = 1:numThermistors
    lines(i) = animatedline('Color', colors(i, :), 'DisplayName', ['Thermistor ' num2str(i)]);
end
legend('Location', 'northeast');

% Start real-time plotting
startTime = tic;
while ishandle(gcf)
    % Read data from the serial port
    if s.BytesAvailable > 0
        line = fgetl(s); % Read a line of data
        if ~isempty(line)
            % Parse the comma-separated temperature values
            temperatures = sscanf(line, '%f,', [1, numThermistors]);
            if numel(temperatures) == numThermistors
                % Append new data to the arrays
                timeData(end+1) = toc(startTime);
                temperatureData(end+1, :) = temperatures;

                % Update the plot
                for i = 1:numThermistors
                    addpoints(lines(i), timeData(end), temperatureData(end, i));
                end

                % Adjust the x-axis limits
                xlim([max(0, timeData(end) - timeWindow), max(timeWindow, timeData(end))]);
            end
        end
    end

    % Pause for the update interval
    pause(updateInterval);
end

% Clean up
fclose(s);
delete(s);
clear s;
