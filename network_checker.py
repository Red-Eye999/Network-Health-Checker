import subprocess
import socket
import datetime
import os
import platform # New import to detect the operating system
from typing import List, Dict, Any

# ====================================================================
# Tool Configuration Settings
# ====================================================================

INPUT_FILE = "targets.txt"
TARGET_PORTS = [80, 443, 22, 3389, 21] 
PORT_TIMEOUT = 1  
OUTPUT_FILE = f"network_health_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

# ====================================================================
# Core Functions
# ====================================================================

def read_targets(filename: str) -> List[str]:
    """Reads the list of targets (IP/Hostname) from a text file."""
    print(f"✅ Reading targets from: {filename}")
    try:
        with open(filename, 'r') as f:
            targets = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        return targets
    except FileNotFoundError:
        print(f"❌ Error: Input file {filename} not found.")
        return []

def ping_check(target: str) -> bool:
    """Performs a Ping connectivity test for a specific device, adjusting for OS."""
    
    # 1. Determine the correct ping command based on the OS
    current_os = platform.system().lower()
    
    if current_os == "windows":
        # Windows command: -n 1 (count 1), -w 1000 (timeout 1000ms)
        ping_command = ["ping", "-n", "1", "-w", "1000", target]
    else:
        # Linux/macOS command: -c 1 (count 1), -W 1 (timeout 1s)
        ping_command = ["ping", "-c", "1", "-W", "1", target]
    
    # 2. Execute the command
    try:
        # The returncode is what matters (0 = success)
        result = subprocess.run(
            ping_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2  # General command timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except FileNotFoundError:
        print("Warning: Ping command not found. Skipping Ping check.")
        return False


def port_check(target: str, port: int, timeout: int) -> bool:
    """Checks if a specific Port is open using the socket library."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((target, port))
        # result 0 means connection was successful (Open)
        return result == 0
    except socket.gaierror:
        return False
    except socket.error:
        return False
    finally:
        sock.close()


def generate_html_report(results: List[Dict[str, Any]], filename: str):
    """Generates an HTML report file."""
    print(f"📝 Generating HTML report to: {filename}")
    
    css_style = """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }
        h1 { color: #333; border-bottom: 2px solid #ccc; padding-bottom: 10px; }
        .info { background-color: #e9e9ff; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); background-color: white; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #007bff; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .status-ok { background-color: #d4edda; color: #155724; font-weight: bold; }
        .status-fail { background-color: #f8d7da; color: #721c24; font-weight: bold; }
        .port-open { color: green; font-weight: bold; }
        .port-closed { color: red; }
    </style>
    """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Network Health Checker Report</title>
        {css_style}
    </head>
    <body>
        <h1>Network Health Checker Report</h1>
        <div class="info">
            <p><strong>Date and Time Generated:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Number of Devices Scanned:</strong> {len(results)}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Device (IP / Hostname)</th>
                    <th>Connectivity Status (Ping)</th>
                    <th>Scanned Ports ({', '.join(map(str, TARGET_PORTS))})</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for result in results:
        # Status determined by the logic in main()
        is_up = result['ping_success'] 
        ping_status = "UP (Reachable)" if is_up else "DOWN (Unreachable)"
        ping_class = "status-ok" if is_up else "status-fail"
        
        ports_html = []
        for port, is_open in result['ports'].items():
            port_class = "port-open" if is_open else "port-closed"
            status_text = "Open" if is_open else "Closed"
            ports_html.append(f'<span class="{port_class}">Port {port}: {status_text}</span>')

        ports_cell = "<br>".join(ports_html)
        
        html_content += f"""
                <tr>
                    <td>{result['target']}</td>
                    <td class="{ping_class}">{ping_status}</td>
                    <td>{ports_cell}</td>
                </tr>
        """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"✅ Successfully finished generating the report.")


def main():
    """Main function to run the tool."""
    # 1. Read the list of targets
    targets = read_targets(INPUT_FILE)
    if not targets:
        print("⚠️ No targets found to scan. Please check your targets.txt file.")
        return

    all_results = []
    
    print(f"\n🔄 Starting scan of {len(targets)} devices...\n")
    
    # 2. Iterate through each device and perform checks
    for i, target in enumerate(targets):
        print(f"[{i+1}/{len(targets)}] Scanning device: {target}...")
        
        result_entry = {'target': target, 'ping_success': False, 'ports': {}}
        
        # A. Initial Ping Check (Can fail due to ICMP blocking)
        is_up_by_ping = ping_check(target)
        # result_entry['ping_success'] initially takes the Ping result
        result_entry['ping_success'] = is_up_by_ping
        
        # B. Port Scan
        ports_status = {}
        found_open_port = False # Flag to track if any port is open

        for port in TARGET_PORTS:
            is_open = port_check(target, port, PORT_TIMEOUT)
            ports_status[port] = is_open
            
            if is_open:
                found_open_port = True # Set flag if an open port is found

        result_entry['ports'] = ports_status

        # C. LOGIC FIX: Re-evaluate the overall status based on Port Scan
        # If the port scan is successful, the device MUST be reachable, regardless of the Ping result.
        if found_open_port:
            if not result_entry['ping_success']:
                # Override DOWN status only if the Ping was DOWN but an open port was found
                print("   - Ping failed, but an open port was found. Overriding status.")
            
            result_entry['ping_success'] = True # Set the final status to UP

        # D. Console Output
        final_status = 'UP' if result_entry['ping_success'] else 'DOWN'
        print(f"   - Connectivity Status (Ping check result): {'UP' if is_up_by_ping else 'DOWN'}")
        print(f"   - Final Overall Status (for report): {final_status}")

        all_results.append(result_entry)
        print("-" * 30)

    # 3. Generate the Report
    generate_html_report(all_results, OUTPUT_FILE)
    print(f"\n🎉 Network scan complete! Please open the file {os.path.abspath(OUTPUT_FILE)} to view the results.")

if __name__ == "__main__":
    main()