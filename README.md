# NetworkPortScanner
A Python defensive security tool to scan for open ports on your network with a user-friendly GUI interface.

## Overview
This port scanner is designed for defensive security assessment to help you understand what services are running on your own network so you can secure them properly.

## Installation & Usage

### Requirements
- Python 3.x with tkinter support (usually included)
- No additional dependencies required

### Running the Application
```bash
python3 port_scanner.py
```

## Configuration Guide

### Target IP Address
**What it is:** The IP address of the device you want to scan for open ports.

**Common Examples:**
- `127.0.0.1` - Your own computer (safest for testing)
- `192.168.1.1` - Usually your router
- `192.168.1.100` - Another device on your local network

**Why we need to set it:** 
- The scanner needs to know which specific device to check
- Networks can have hundreds of devices
- Scanning every device automatically could be slow and potentially suspicious

### Port Range
**What it is:** Which ports to check (1-65535 are all possible ports)

**Why we select a range:**
- **Speed:** Scanning all 65,535 ports takes hours
- **Relevance:** Most services use common ports (1-1024)
- **Stealth:** Smaller scans are less noticeable

**Recommended Ranges:**
- `1-100`: Basic system services
- `1-1000`: Most common services (default)
- `1-1024`: All well-known ports
- `21,22,23,25,53,80,110,143,443,993,995`: Specific services only

### Timeout
**What it is:** How long to wait for each port to respond (in seconds)

**Speed vs Accuracy tradeoff:**
- `0.1-0.5 seconds`: Very fast, might miss slower services
- `1 second`: Good balance (default)
- `2-3 seconds`: Better for internet scanning
- `5+ seconds`: Slower but catches everything

## Example Scans

### Safe Local Testing
```
Target: 127.0.0.1
Ports: 1-1000
Timeout: 0.5
```

### Check Your Router
```
Target: 192.168.1.1
Ports: 1-100
Timeout: 1
```

### Quick Web Server Check
```
Target: your-domain.com
Ports: 80,443
Timeout: 2
```

## Features
- **GUI Interface**: Clean tkinter-based interface for easy use
- **Port Scanning**: TCP port scanning with configurable timeout
- **Service Identification**: Recognizes common services on standard ports
- **Progress Tracking**: Real-time progress bar and scan status
- **Results Display**: Tabular results showing open ports and services
- **Scan Log**: Detailed logging of scan activities
- **Input Validation**: IP address and port range validation
- **Safety Features**: Confirmation dialog before scanning

## Security & Ethical Use
- **Defensive Purpose Only**: Designed for securing your own networks
- **Permission Required**: Only scan networks you own or have explicit permission to test
- **Built-in Warnings**: Confirmation prompts before scanning
- **Safe Defaults**: Localhost scanning for safe testing

## Service Identification
The scanner recognizes these common services:
- Port 21: FTP
- Port 22: SSH
- Port 23: Telnet
- Port 25: SMTP
- Port 53: DNS
- Port 80: HTTP
- Port 110: POP3
- Port 143: IMAP
- Port 443: HTTPS
- Port 993: IMAPS
- Port 995: POP3S
- Port 1433: MSSQL
- Port 3306: MySQL
- Port 3389: RDP
- Port 5432: PostgreSQL
- Port 5900: VNC
- Port 6379: Redis
- Port 8080: HTTP-Alt
- Port 9200: Elasticsearch

## Testing the Scanner

### Method 1: Test Server (Recommended)
Start local test servers to verify the scanner detects open ports:

```bash
# Start test servers in one terminal
python3 test_server.py

# In another terminal or GUI, scan:
# Target: 127.0.0.1
# Ports: 8000-10000  
# Timeout: 1
```

This creates 6 test servers on ports 8080, 8443, 9000, 9001, 9002, 9999.

### Method 2: Integration Tests
Run automated tests with real servers:

```bash
# Run unit tests (mock testing)
python3 run_tests.py

# Run integration tests (real servers)
python3 test_with_real_ports.py
```

### Method 3: Interactive Demo
Try the guided demo:

```bash
python3 demo_scanner.py
```

### Method 4: Check Your Own Services
Look for services you know are running:

**Common services to check:**
- Web servers: ports 80, 443, 8080, 8000
- SSH: port 22 
- Database: ports 3306 (MySQL), 5432 (PostgreSQL)
- Development servers: ports 3000, 8080, 9000

### Method 5: Public Services (Use Responsibly)
Test against well-known public services with permission:
- `google.com` ports 80, 443 (should be open)
- Your own website/server

**⚠️ Only scan systems you own or have explicit permission to test!**

## Testing Results
When the scanner is working correctly, you should see:
- **Progress bar** advancing from 0% to 100%
- **Open ports** listed in the results table
- **Service names** identified (HTTP, SSH, etc.)
- **Log messages** showing scan progress and findings

If you only see closed ports everywhere, it usually means:
- Good security! Most systems should have minimal open ports
- Use the test server method above to verify the scanner works

## Legal Notice
This tool is intended for defensive security purposes only. Users are responsible for ensuring they have proper authorization before scanning any network or system. Unauthorized network scanning may violate local laws and regulations.
