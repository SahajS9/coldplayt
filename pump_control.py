import spidev
import yaml

CONFIG_FILE = 'config.yaml'

class PumpController:
    def __init__(self, spi_bus=0, spi_device=0, max_speed_hz=5000):
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = max_speed_hz
        self.flow_rate = self.load_flow_rate()

    def set_pwm(self, duty_cycle):
        """
        Sets PWM duty cycle (0–100) to control pump speed.
        """
        if not 0 <= duty_cycle <= 100:
            raise ValueError("Duty cycle must be between 0 and 100")
        # Convert to byte and send via SPI
        pwm_value = int(duty_cycle / 100 * 255)
        self.spi.xfer2([pwm_value])

    def save_flow_rate(self, rate):
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
        config['pump_flow_rate'] = rate
        with open(CONFIG_FILE, 'w') as f:
            yaml.safe_dump(config, f)
        self.flow_rate = rate

    def load_flow_rate(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f)
            return config.get('pump_flow_rate', 0.0)
        except FileNotFoundError:
            return 0.0

# This can be used in other files as needed, an example is shown below:
# from pump import PumpController
# pump = PumpController()
# pump.set_pwm(75)  # example duty cycle
# pump.save_flow_rate(1.2)  # example flow rate in L/min
