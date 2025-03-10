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
