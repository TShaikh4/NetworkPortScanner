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

## Legal Notice
This tool is intended for defensive security purposes only. Users are responsible for ensuring they have proper authorization before scanning any network or system. Unauthorized network scanning may violate local laws and regulations.
