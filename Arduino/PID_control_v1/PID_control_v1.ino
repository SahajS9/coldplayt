#include <PID_v1.h>

// Pin Definitions
const int heaterPin = 9;                       // PWM pin for heater control
const int thermistorPin = A0;                  // Analog pin for thermistor
const int pressureSensorPin = A1;              // Analog pin for pressure transducer
const int thermistorPins[] = {A2, A3, A4, A5}; // Additional thermistors for heat flux

// PID Parameters
double setpoint = 57.0; // Desired temperature in Celsius
double input, output;
double Kp = 2.0, Ki = 5.0, Kd = 1.0; // PID tuning parameters
PID myPID(&input, &output, &setpoint, Kp, Ki, Kd, DIRECT);

// Pressure Transducer Parameters
const float pipeDiameter = 0.1;  // Pipe diameter in meters
const float fluidDensity = 1000; // Fluid density in kg/m^3 (water)
const float energyCost = 0.15;   // Energy cost in $/kWh

// Thermistor Parameters
const float R0 = 10000.0;  // Thermistor resistance at 25°C
const float T0 = 298.15;   // Reference temperature in Kelvin (25°C)
const float beta = 3950.0; // Beta coefficient of the thermistor

// Heat Flux Calculation
const float plateArea = 0.01;           // Area of the cold plate in m^2
const float thermalConductivity = 50.0; // Thermal conductivity of the plate material in W/m·K

void setup()
{
  Serial.begin(9600);

  // Initialize PID
  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(0, 255); // PWM range

  // Initialize pins
  pinMode(heaterPin, OUTPUT);
  pinMode(thermistorPin, INPUT);
  pinMode(pressureSensorPin, INPUT);
  for (int i = 0; i < 4; i++)
  {
    pinMode(thermistorPins[i], INPUT);
  }
}

void loop()
{
  // Read temperature from the main thermistor
  float temperature = readThermistor(thermistorPin);
  input = temperature;

  // Compute PID output
  myPID.Compute();

  // Control the heater
  analogWrite(heaterPin, output);

  // Read pressure and calculate flow rate
  float pressure = readPressure(pressureSensorPin);
  float flowRate = calculateFlowRate(pressure, pipeDiameter);
  float powerCost = calculatePowerCost(flowRate, pressure);

  // Read additional thermistors for heat flux calculation
  float heatFlux = calculateHeatFlux();

  // Print results
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print(" °C, Heater Output: ");
  Serial.print(output);
  Serial.print(", Flow Rate: ");
  Serial.print(flowRate);
  Serial.print(" m^3/s, Power Cost: $");
  Serial.print(powerCost);
  Serial.print(", Heat Flux: ");
  Serial.print(heatFlux);
  Serial.println(" W/m^2");

  delay(1000); // Adjust delay as needed
}
// hello world

// Function to read temperature from a thermistor
float readThermistor(int pin)
{
  int adcValue = analogRead(pin);
  float R = R0 * (1023.0 / adcValue - 1.0);        // Calculate thermistor resistance
  float T = 1.0 / (1.0 / T0 + log(R / R0) / beta); // Calculate temperature in Kelvin
  return T - 273.15;                               // Convert to Celsius
}

// Function to read pressure from the transducer
float readPressure(int pin)
{
  int adcValue = analogRead(pin);
  float voltage = adcValue * (5.0 / 1023.0); // Convert ADC to voltage
  float pressure = (voltage - 0.5) * 100.0;  // Convert voltage to pressure (kPa)
  return pressure;
}

// Function to calculate flow rate using Bernoulli's equation
float calculateFlowRate(float pressure, float diameter)
{
  float area = PI * pow(diameter / 2.0, 2);                    // Cross-sectional area of the pipe
  float velocity = sqrt((2 * pressure * 1000) / fluidDensity); // Velocity in m/s
  return area * velocity;                                      // Flow rate in m^3/s
}

// Function to calculate power cost
float calculatePowerCost(float flowRate, float pressure)
{
  float power = flowRate * pressure * 1000; // Power in Watts
  float energy = power * (1.0 / 3600.0);    // Energy in kWh (per second)
  return energy * energyCost;               // Cost in $
}

// Function to calculate heat flux
float calculateHeatFlux()
{
  /// still haven't found an equation to accurately model the two phase convection
  float temperatures[4];
  for (int i = 0; i < 4; i++)
  {
    temperatures[i] = readThermistor(thermistorPins[i]);
  }

  // Calculate temperature gradient
  float dT = temperatures[3] - temperatures[0]; // Temperature difference across the plate
  float dx = 0.1;                               // Distance between thermistors in meters (adjust as needed)

  // Calculate heat flux using Fourier's law
  float heatFlux = -thermalConductivity * (dT / dx);
  return heatFlux;
}
// Define the analog pin connected to the pressure transducer
const int pressureSensorPin = A0;

// Define the voltage range and pressure range
const float voltageMin = 0.5;  // Minimum voltage output (0 PSI)
const float voltageMax = 4.5;  // Maximum voltage output (200 PSI)
const float pressureMin = 0;   // Minimum pressure (PSI)
const float pressureMax = 200; // Maximum pressure (PSI)


// reading the pressure transducer readings
void setup() {
  // Initialize serial communication for debugging
  Serial.begin(9600);
}

void loop() {
  // Read the analog value from the pressure transducer
  int sensorValue = analogRead(pressureSensorPin);

  // Convert the analog reading to voltage (0V to 5V)
  float voltage = sensorValue * (5.0 / 1023.0);

  // Map the voltage to the pressure range
  float pressure = mapPressure(voltage, voltageMin, voltageMax, pressureMin, pressureMax);

  // Print the pressure value to the Serial Monitor
  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.println(" PSI");

  // Wait for a short period before the next reading
  delay(500);
}

// Function to map voltage to pressure
float mapPressure(float voltage, float voltageMin, float voltageMax, float pressureMin, float pressureMax) {
  // Ensure the voltage is within the expected range
  voltage = constrain(voltage, voltageMin, voltageMax);

  // Map the voltage to the pressure range
  return (voltage - voltageMin) * (pressureMax - pressureMin) / (voltageMax - voltageMin) + pressureMin;
}
//reading in arduino 
// Define analog pins for the thermistors
const int thermistorPins[] = {A0, A1, A2, A3, A4};
const int numThermistors = 5;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
}

void loop() {
  // Read temperature from each thermistor
  for (int i = 0; i < numThermistors; i++) {
    int sensorValue = analogRead(thermistorPins[i]);
    float voltage = sensorValue * (5.0 / 1023.0); // Convert analog reading to voltage
    float temperature = readTemperature(voltage); // Convert voltage to temperature
    Serial.print(temperature); // Send temperature to serial
    if (i < numThermistors - 1) {
      Serial.print(","); // Separate values with a comma
    }
  }
  Serial.println(); // End of line
  delay(1000); // Wait for 1 second before the next reading
}

// Function to convert voltage to temperature (example for a 10k NTC thermistor)
float readTemperature(float voltage) {
  // Thermistor parameters (adjust based on your thermistor specifications)
  float R1 = 10000; // Resistance of the fixed resistor in the voltage divider
  float Beta = 3950; // Beta value of the thermistor
  float T0 = 298.15; // Reference temperature in Kelvin (25°C)
  float R0 = 10000; // Resistance of the thermistor at T0

  // Calculate thermistor resistance
  float Rt = R1 * (5.0 / voltage - 1.0);

  // Calculate temperature using the Steinhart-Hart equation
  float T = 1.0 / (1.0/T0 + (1.0/Beta) * log(Rt/R0)); // Temperature in Kelvin
  float Tc = T - 273.15; // Convert to Celsius
  return Tc;
}