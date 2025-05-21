import spidev
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_adc(channel):
    adc = spi.xfer2([1, (8+channel)<<4, 0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data / 1023.0 * config['calibration']['voltage_ref']

def read_all():
    readings = {}
    for sensor_type in config['sensors']:
        for name, channel in config['sensors'][sensor_type].items():
            voltage = read_adc(channel)
            readings[name] = voltage
    return readings