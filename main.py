import sys
import concurrent.futures

# Import your existing functions
from hostsUp import scan as host_discovery
from scanPorts import port_scan


def main():
    if len(sys.argv) not in [2, 4]:
        print("Usage:")
        print("  python3 main.py <IP or CIDR>")
        print("  python3 main.py <IP or CIDR> <start_port> <end_port>")
        sys.exit(1)

    target = sys.argv[1]

    # Port range
    if len(sys.argv) == 4:
        start_port = int(sys.argv[2])
        end_port = int(sys.argv[3])
    else:
        start_port = 1
        end_port = 1024

    print("\n=== STEP 1: Host Discovery ===")
    alive_hosts = host_discovery(target)

    if not alive_hosts:
        print("\nNo alive hosts found. Exiting.")
        sys.exit(0)

    print("\n=== STEP 2: Port Scanning ===")

    results = {}

    # Scan all alive hosts in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_host = {
            executor.submit(port_scan, host, start_port, end_port): host
            for host in alive_hosts
        }

        for future in concurrent.futures.as_completed(future_to_host):
            host = future_to_host[future]
            try:
                open_ports = future.result()
                results[host] = open_ports
            except Exception as e:
                print(f"[!] Error scanning {host}: {e}")

    print("\n=== FINAL RESULTS ===")
    for host, ports in results.items():
        print(f"\nHost: {host}")
        if ports:
            for p in ports:
                print(f"  Port {p}")
        else:
            print("  No open ports")

    print("\nScan complete.")


if __name__ == "__main__":
    main()

