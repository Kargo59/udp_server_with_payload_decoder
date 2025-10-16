# UDP Server for NB-IoT Sensors

A Python-based UDP server designed to receive, decode, and forward data from NB-IoT sensors (specifically Milesight distance sensors, can be easily modified to accomodate other sensors).

## Overview

This project provides a simple yet robust UDP server that listens for incoming packets from NB-IoT devices, decodes the sensor data according to the Milesight protocol, and forwards the processed information to a webhook endpoint for further processing or storage.

## Use Cases

- Water level monitoring
- Distance/proximity sensing
- Tank level monitoring
- Industrial IoT applications
- Smart city sensor networks

## Usage

### Running the Server

**Option 1: Direct execution**
```bash
python3 udp_server.py
```

**Option 2: Using screen (persistent session)**
```bash
screen
python3 udp_server.py
# Press Ctrl+A, then D to detach
```

**Option 3: As a systemd service**
```bash
sudo cp udp-server.service /etc/systemd/system/
sudo systemctl enable udp-server
sudo systemctl start udp-server
```

### Viewing Logs

```bash
# For systemd service
sudo journalctl -u udp-server -f

# Or check the log file
tail -f udp_server.log
```

## Payload Format

The server expects data in the following format:

1. **ASCII-encoded hex string** (double-encoded)
2. **Header** (86 bytes):
   - Start byte, ID, packet length, flags
   - Device identifiers (IMEI, IMSI, ICCID, SN)
   - Signal strength, software/hardware versions
3. **Data section**: TLV (Type-Length-Value) encoded sensor readings

### Decoded Output Example

```json
{
  "imei": "867490427550061",
  "imsi": "618685080619307",
  "iccid": "00901405114752456",
  "signal": 82,
  "sensor_data": {
    "battery": 82,
    "temperature": 19.6,
    "distance": 18.4,
    "position": "Normal"
  }
}
```


## License

MIT License
