import spidev
import time
import yaml

# Attempt to initialize SPI devices
spi_0 = spidev.SpiDev()
spi_0.open(0, 0)
spi_0.max_speed_hz = 1350000

try:
    spi_1 = spidev.SpiDev()
    spi_1.open(0, 1)
    spi_1.max_speed_hz = 1350000
    second_chip_available = True
except FileNotFoundError:
    print("Warning: SPI device 0.1 not available. Falling back to single-chip mode.")
    spi_1 = None
    second_chip_available = False


def read_adc_channel(channel: int) -> int | None:
    """
    Read raw ADC value from MCP3008.
    Channels 0–7 use chip 0 (SPI0.0), channels 8–15 use chip 1 (SPI0.1).

    Returns None if channel is on second chip but it isn't connected.
    """
    if not 0 <= channel <= 15:
        raise ValueError("ADC channel must be in range 0–15")

    if channel < 8:
        spi = spi_0
        chip_channel = channel
    else:
        if not second_chip_available:
            return None
        spi = spi_1
        chip_channel = channel - 8

    adc = spi.xfer2([1, (8 + chip_channel) << 4, 0])
    raw_value = ((adc[1] & 3) << 8) + adc[2]
    return raw_value


def load_config(config_path: str = "config.yaml") -> dict:
    """Load YAML configuration file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def collect_data(config: dict) -> dict:
    """
    Collect raw ADC data from thermistors, pressure sensors, and optional power sensors.
    Returns a dictionary with raw ADC values.
    """
    thermistor_channels = config['sensors'].get('thermistors', {})
    pressure_channels = config['sensors'].get('pressure', {})

    temperatures = {
        label: read_adc_channel(channel)
        for label, channel in thermistor_channels.items()
    }

    pressures = {
        label: read_adc_channel(channel)
        for label, channel in pressure_channels.items()
    }

    heater_power = None
    if 'heater_power' in config['sensors']:
        heater_power = read_adc_channel(config['sensors']['heater_power'])

    pump_power = None
    if 'pump_power' in config['sensors']:
        pump_power = read_adc_channel(config['sensors']['pump_power'])

    return {
        **temperatures,
        **pressures,
        'heater_power': heater_power,
        'pump_power': pump_power,
    }


# Load config once and provide `read_all()` for other modules
_config = load_config()

def read_all() -> dict:
    """Convenience function for external use."""
    return collect_data(_config)


# Debug / direct run block
if __name__ == "__main__":
    while True:
        readings = collect_data(_config)
        print(readings)
        time.sleep(1)
