import socket
import datetime
import json
import http.client
import base64
import struct

def decode_payload(hex_string):
    try:
        actual_hex = ''
        for i in range(0, len(hex_string), 2):
            ascii_hex = hex_string[i:i+2]
            # Convert ASCII hex to actual character
            actual_hex += chr(int(ascii_hex, 16))
            
        payload = bytes.fromhex(actual_hex)
        
        header = {
            'start': payload[0],
            'id': struct.unpack('>H', payload[1:3])[0],
            'packet_length': struct.unpack('>H', payload[3:5])[0],
            'flag': payload[5],
            'frame_counter': struct.unpack('>H', payload[6:8])[0],
            'protocol_version': payload[8],
            'software_version': payload[9:13].decode('ascii', errors='replace'),
            'hardware_version': payload[13:17].decode('ascii', errors='replace'),
            'sn': payload[17:33].decode('ascii', errors='replace'),
            'imei': payload[33:48].decode('ascii', errors='replace'),
            'imsi': payload[48:63].decode('ascii', errors='replace'),
            'iccid': payload[63:83].decode('ascii', errors='replace'),
            'signal': payload[83],
            'data_length': struct.unpack('>H', payload[84:86])[0]
        }
        
        data = payload[86:]
        decoded_data = {}
        
        i = 0
        while i < len(data):
            channel = data[i]
            type_ = data[i+1]
            
            if channel == 0x01 and type_ == 0x75:  
                decoded_data['battery'] = data[i+2]
                i += 3
            elif channel == 0x03 and type_ == 0x67: 
                decoded_data['temperature'] = struct.unpack('<h', data[i+2:i+4])[0] / 10
                i += 4
            elif channel == 0x04 and type_ == 0x82: 
                decoded_data['distance'] = struct.unpack('<H', data[i + 2:i + 4])[0] / 10.0
                i += 4
            elif channel == 0x05 and type_ == 0x00:  
                decoded_data['position'] = "Normal" if data[i+2] == 0 else "Tilt"
                i += 3
            else:
                # Unknown channel/type, skip
                i += 1
        
        return {**header, 'sensor_data': decoded_data}
    except Exception as e:
        import traceback
        return {'error': f'Failed to decode payload: {str(e)}\n{traceback.format_exc()}'}

def send_to_webhook(decoded_data):
    try:
        webhook_url = 'somewebsite.com'
        endpoint = '/some-webhook/'
        
        conn = http.client.HTTPSConnection(webhook_url)
        headers = {'Content-Type': 'application/json'}
        json_data = json.dumps(decoded_data)
        
        conn.request("POST", endpoint, body=json_data, headers=headers)
        response = conn.getresponse()
        
        if response.status == 200:
            return True, "Data sent successfully"
        else:
            return False, f"Webhook error: {response.status} - {response.read().decode()}"
    except Exception as e:
        return False, f"Failed to send to webhook: {str(e)}"

def start_udp_server(host='0.0.0.0', port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    
    print(f'UDP Server listening on {host}:{port}')
    
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            timestamp = datetime.datetime.now().isoformat()
            
            # Print raw received data
            print("\n--- New Message Received ---")
            print(f"Time: {timestamp}")
            print(f"From: {addr[0]}:{addr[1]}")
            print(f"Length: {len(data)} bytes")
            
            # Convert received data to string
            hex_data = data.decode('ascii')
            print(f"Raw hex: {hex_data}")
            
            # Show bytes breakdown
            print("Bytes breakdown:")
            for i in range(0, len(hex_data), 32):
                chunk = hex_data[i:i+32]
                print(f"{i//2:04x}: {' '.join(chunk[j:j+2] for j in range(0, len(chunk), 2))}")
            
            try:
                decoded_result = decode_payload(hex_data)
                print("\nDecoded Data:")
                print(json.dumps(decoded_result, indent=2))
                
                # Send to webhook if no error in decoded_result
                if 'error' not in decoded_result:
                    success, message = send_to_webhook(decoded_result)
                    print(f"\nWebhook result: {message}")
                else:
                    print(f"\nSkipping webhook due to decode error")
                
            except Exception as e:
                print(f"\nError processing message: {str(e)}")
            
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        sock.close()

if __name__ == "__main__":
    start_udp_server()