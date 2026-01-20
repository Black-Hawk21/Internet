import json
import os
import socket

LEASES_FILE = os.path.join("dhcp", "leases.json")

DEFAULT_CONFIG = {
    "ip_pool_start": "10.0.0.100",
    "ip_pool_end": "10.0.0.200",
    "subnet_mask": "255.255.255.0",
    "router": "10.0.0.1",
    "dns": "10.0.0.2",
    "lease_time": 3600  # seconds
}


def ip_to_int(ip):
    return sum(int(octet) << (24 - 8 * i) for i, octet in enumerate(ip.split(".")))


def int_to_ip(value):
    return ".".join(str((value >> (24 - 8 * i)) & 0xFF) for i in range(4))


def load_leases():
    if os.path.exists(LEASES_FILE):
        with open(LEASES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_leases(data):
    with open(LEASES_FILE, "w") as f:
        json.dump(data, f, indent=4)


def find_available_ip(leases, config):
    start = ip_to_int(config["ip_pool_start"])
    end = ip_to_int(config["ip_pool_end"])
    used = {ip for ip in leases.values()}
    for ip_int in range(start, end + 1):
        ip = int_to_ip(ip_int)
        if ip not in used:
            return ip
    return None


def create_dhcp_offer(request, config):
    leases = load_leases()
    mac = request.get("mac")
    if mac in leases:
        assigned_ip = leases[mac]
    else:
        assigned_ip = find_available_ip(leases, config)
        if not assigned_ip:
            return {"error": "No available IPs"}
        leases[mac] = assigned_ip
        save_leases(leases)

    return {
        "ip": assigned_ip,
        "subnet_mask": config["subnet_mask"],
        "router": config["router"],
        "dns": config["dns"],
        "lease_time": config["lease_time"]
    }