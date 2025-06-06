import RPi.GPIO as GPIO
import yaml
import sys
import time

CONFIG_FILE = 'config.yaml'
PWM_GPIO_PIN = 12  # BCM numbering
PWM_FREQUENCY = 1000  # 1kHz

class PumpController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PWM_GPIO_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(PWM_GPIO_PIN, PWM_FREQUENCY)
        self.pwm.start(0)
        self.flow_rate = self.load_flow_rate()

    def set_pwm(self, duty_cycle):
        if not 0 <= duty_cycle <= 100:
            raise ValueError("Duty cycle must be between 0 and 100")
        self.pwm.ChangeDutyCycle(duty_cycle)

    def save_flow_rate(self, rate):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            config = {}
        config['flow_rate_m3s'] = rate
        with open(CONFIG_FILE, 'w') as f:
            yaml.safe_dump(config, f)
        self.flow_rate = rate

    def load_flow_rate(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f)
            return config.get('flow_rate_m3s', 0.0)
        except FileNotFoundError:
            return 0.0

    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()

# --- Run from command line ---
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python pump_control.py [duty_cycle 0–100]")
        sys.exit(1)

    try:
        duty = float(sys.argv[1])
    except ValueError:
        print("Error: duty_cycle must be a number between 0 and 100.")
        sys.exit(1)

    pump = PumpController()
    try:
        pump.set_pwm(duty)
        pump.save_flow_rate(duty)  # Optional: save speed as flow rate
        print(f"Pump speed set to {duty}% duty cycle.")
        time.sleep(10)  # Let it run briefly (you can change/remove this)
    finally:
        pump.cleanup()
