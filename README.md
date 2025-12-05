# Network-Health-Checker
# 🌐 Python Network Health Checker

A simple, fast, and automated Python script to check the connectivity and health of network devices by performing Ping tests and scanning essential TCP ports.

---

## 💡 Project Overview

This tool automates the tedious task of manually verifying network connectivity for a list of hosts. It reads target devices from an input file, performs checks, and generates an easy-to-read HTML report.

### Key Features

* **Batch Processing:** Reads multiple target IP addresses or hostnames from a `targets.txt` file.
* **Connectivity Check:** Uses the system's native `ping` command (ICMP) to verify network reachability.
* **Port Scanning:** Utilizes the built-in Python `socket` library to check if essential TCP ports (e.g., 80, 443, 22, 3389) are open.
* **Intelligent Status Reporting:** Automatically overrides a failed Ping result to **UP (Reachable)** if an open TCP port is found, accounting for servers that block ICMP.
* **HTML Report Generation:** Creates a detailed, color-coded HTML file for quick and easy viewing of results.

---

## 🎯 Why This Tool Was Built

Managing network infrastructure often requires regularly checking the status of servers, routers, or other network devices. The problems this script solves are:

1.  **Manual Repetition:** Eliminates the need to manually run `ping` and port check commands for every single device.
2.  **Inaccurate Reporting:** Solves the common issue where a device is reachable (e.g., its web server is running), but standard `ping` fails because the firewall blocks ICMP traffic.
3.  **Lack of Documentation:** Provides a centralized, timestamped, and visual HTML report of the network health status at a specific moment in time.

---

## ⚙️ How It Works (Technical Breakdown)

The script operates in three main stages:

1.  **Target Acquisition (`read_targets`):** The script first reads the list of targets from `targets.txt`, ignoring comments (`#`) and empty lines.
2.  **Health Checks:** For each target, two independent checks are performed:
    * **Ping Check (`ping_check`):** Uses the `subprocess` module to execute the system's `ping` command. **Crucially, it detects the Operating System (Windows/Linux/macOS)** and adjusts the command line flags (`-n` for Windows, `-c` for Linux) to ensure reliable execution across platforms.
    * **Port Check (`port_check`):** Attempts a non-blocking TCP connection using the `socket.connect_ex()` method on the predefined `TARGET_PORTS`. A successful connection indicates the port is **Open**.
3.  **Reporting (`generate_html_report`):** All results are compiled. A final logical check is applied to determine the overall status (if any port is open, the host is marked as **UP**). Finally, an HTML report file is generated with CSS styling for clarity.

---

## 🚀 Getting Started

### Prerequisites

You need a working installation of Python on your system.

* **Python Version:** **Python 3.6+**

No external libraries (like `requests` or `scapy`) are required; the script only uses built-in Python libraries: `subprocess`, `socket`, `datetime`, `os`, and `platform`.

### Installation and Execution

1.  **Clone or Download:** Get the `network_checker.py` script and save it to a local folder.
2.  **Create Input File:** In the same folder, create a file named **`targets.txt`**.
    ```txt
    # targets.txt
    127.0.0.1
    google.com
    server-a.local
    192.168.1.10
    ```
3.  **Run the Script:** Open your terminal or command prompt, navigate to the project folder, and run:

    ```bash
    python network_checker.py
    ```

### Output

The script will print real-time status updates to the console and generate an HTML report file named something like `network_health_report_YYYYMMDD_HHMMSS.html`.
