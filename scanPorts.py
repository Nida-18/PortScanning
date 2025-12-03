import socket
import concurrent.futures
import time

# -------- service resolver ----------
def get_service(port):
    try:
        return socket.getservbyport(port)
    except:
        return "unknown"


# -------- scan a single port ---------
def scan_port(ip, port, timeout=0.5):
    """
    Returns True if the port is open.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))  # 0 = success
        sock.close()
        return result == 0
    except:
        return False


# -------- main port scanner ----------
def port_scan(ip, start_port=1, end_port=1024):
    """
    Scans a host and returns a dict:
    {
        port_number: "service_name"
    }
    """
    open_ports = {}

    ports = range(start_port, end_port + 1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        results = executor.map(lambda p: (p, scan_port(ip, p)), ports)

    for port, is_open in results:
        if is_open:
            service = get_service(port)
            open_ports[port] = service

    return open_ports   # <-- this is what main.py uses

