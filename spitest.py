import spidev
import time

def read_spi(channel, spi):
    if channel is None or not isinstance(channel, int):
        return None
    if channel < 0 or channel > 7:
        raise ValueError("Channel must be 0–7")

    # MCP3008 SPI command format
    command = [1, (8 + channel) << 4, 0]
    response = spi.xfer2(command)
    raw_val = ((response[1] & 3) << 8) | response[2]
    return raw_val

def main():
    spi = spidev.SpiDev()
    spi.open(0, 0)  # Bus 0, Device 0
    spi.max_speed_hz = 1350000  # Reasonable speed for MCP3008

    print("Reading raw SPI values. Press Ctrl+C to stop.")
    try:
        while True:
            for ch in range(8):  # MCP3008 has 8 channels: 0–7
                value = read_spi(ch, spi)
                print(f"Channel {ch}: {value}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        spi.close()

if __name__ == "__main__":
    main()
