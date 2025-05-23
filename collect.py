import spidev
import time
import yaml
from compute import adc_to_temperature

# SPI setup for MCP3008 ADC
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0
spi.max_speed_hz = 1350000

def read_adc_channel(channel):
    """Read raw ADC value from MCP3008 channel (0-7)."""
    if not 0 <= channel <= 7:
        raise ValueError("ADC channel must be 0-7")
    # MCP3008 SPI protocol: start bit, single-ended mode, channel bits
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    raw_value = ((adc[1] & 3) << 8) + adc[2]
    return raw_value

def load_config(config_path="config.yaml"):
    """Load configuration file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def collect_data(config):
    """Collect data from ADC channels and convert thermistor readings."""
    calibration = config['calibration']['thermistor']
    thermistor_channels = config['sensors']['thermistors']

    # Read thermistor raw ADC values
    temperatures = {}
    for label, channel in thermistor_channels.items():
        adc_val = read_adc_channel(channel)
        temp_c = adc_to_temperature(adc_val, calibration)
        temperatures[label] = temp_c

    # Similarly, read other analog sensors if needed (pressure, power, etc.)
    # For example:
    pressure_channels = config['sensors'].get('pressure', {})
    pressures = {}
    for label, channel in pressure_channels.items():
        adc_val = read_adc_channel(channel)
        # Convert ADC reading to pressure using calibration (not implemented here)
        pressures[label] = adc_val  # Placeholder

    # Optional sensors for heater power and pump power
    heater_power = None
    if 'heater_power' in config['sensors']:
        adc_val = read_adc_channel(config['sensors']['heater_power'])
        # Convert to power as needed
        heater_power = adc_val  # Placeholder

    pump_power = None
    if 'pump_power' in config['sensors']:
        adc_val = read_adc_channel(config['sensors']['pump_power'])
        # Convert to power as needed
        pump_power = adc_val  # Placeholder

    # Combine all readings
    data = {
        **temperatures,
        **pressures,
        'heater_power': heater_power,
        'pump_power': pump_power,
    }
    return data

if __name__ == "__main__":
    config = load_config()
    while True:
        data = collect_data(config)
        print(data)  # Or handle logging/data saving here
        time.sleep(1)


# Define read_all for external use
_config = load_config()

def read_all():
    return collect_data(_config)
