import json
import socket
from dhcp import core

HOST = "127.0.0.1"
PORT = 6767

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"📡 DHCP Server running on {HOST}:{PORT}")

while True:
    try:
        data, addr = sock.recvfrom(1024)
        request = json.loads(data.decode())
        print(f"📥 Request from {addr}: {request}")

        if "mac" not in request:
            response = {"error": "MAC address required"}
        else:
            response = core.create_dhcp_offer(request, core.DEFAULT_CONFIG)

        sock.sendto(json.dumps(response).encode(), addr)
        print(f"📤 Response: {response}")
    except KeyboardInterrupt:
        print("🛑 Shutting down DHCP server.")
        break
    except Exception as e:
        print(f"❌ Error: {e}")