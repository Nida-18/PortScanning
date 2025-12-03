from icmplib import ping
from ipaddress import ip_network
import concurrent.futures
import sys


# ---- ICMP ping a single host --------------------
def ping_host(ip):
    """
    Returns True if the host responds to ICMP echo.
    Using icmplib for better reliability.
    """
    try:
        result = ping(
            ip,
            count=1,
            timeout=1,
            interval=0.2,
            privileged=True    # Requires CAP_NET_RAW or sudo
        )
        return result.is_alive
    except Exception:
        return False


# ---- handle single IP or subnet ------------------
def get_ip_list(target):
    """
    Returns list of IPs:
    - single IP -> list with 1 element
    - CIDR -> list of all hosts
    """
    try:
        network = ip_network(target, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError:
        return [target]


# ---- main scanning function ----------------------
def scan(target):
    ip_list = get_ip_list(target)

    print(f"[*] Scanning {len(ip_list)} hosts using ICMP...\n")

    alive_hosts = []

    # Thread pool for fast scanning
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        results = executor.map(ping_host, ip_list)

    # Pair results with IPs
    for ip, status in zip(ip_list, results):
        if status:
            print(f"[+] Host UP: {ip}")
            alive_hosts.append(ip)

    print("\n[*] Scan complete.")
    print(f"[*] Total UP hosts: {len(alive_hosts)}")

    return alive_hosts


# ---- CLI entry point -----------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 hostsUp.py <IP or CIDR>")
        sys.exit(1)

    target = sys.argv[1]
    scan(target)

