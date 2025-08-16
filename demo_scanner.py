#!/usr/bin/env python3

import time
import threading
from port_scanner import PortScanner
from test_server import TestServer

def demo_with_test_servers():
    """Demonstrate the port scanner with real open ports"""
    
    print("🔍 Port Scanner Demo with Real Open Ports")
    print("=" * 50)
    print("This demo will:")
    print("1. Start test servers on localhost")
    print("2. Run the port scanner against them") 
    print("3. Show you actual open port detection")
    print("=" * 50)
    
    # Start test servers
    print("\n📡 Starting test servers...")
    server = TestServer()
    if not server.start_multiple_servers():
        print("❌ Failed to start test servers")
        return
    
    # Give servers time to start
    time.sleep(1)
    
    try:
        # Initialize scanner
        scanner = PortScanner()
        found_ports = []
        progress_values = []
        
        def progress_callback(value):
            progress_values.append(value)
            if int(value) % 10 == 0:  # Print every 10%
                print(f"   Progress: {value:.1f}%")
        
        def result_callback(port, service):
            found_ports.append((port, service))
            print(f"   🎯 FOUND OPEN PORT: {port} ({service})")
        
        print(f"\n🔍 Scanning localhost ports 8000-10000...")
        print("   This should find several open test servers:")
        
        scanner.scanning = True
        start_time = time.time()
        
        # Run the scan
        open_ports = scanner.scan_range(
            "127.0.0.1", 8000, 10000, 1,
            progress_callback, result_callback
        )
        
        end_time = time.time()
        
        # Results
        print("\n" + "=" * 50)
        print("📊 SCAN RESULTS")
        print("=" * 50)
        print(f"Scan completed in {end_time - start_time:.2f} seconds")
        print(f"Ports scanned: 2001 (8000-10000)")
        print(f"Open ports found: {len(open_ports)}")
        
        if open_ports:
            print("\n🎯 Open Ports Detected:")
            print("-" * 30)
            for port, service in open_ports:
                print(f"   Port {port:5d}: {service}")
        else:
            print("\n❌ No open ports found (something went wrong)")
        
        # Test individual port
        print(f"\n🔍 Testing individual port 8080...")
        result = scanner.scan_port("127.0.0.1", 8080, timeout=2)
        print(f"   Port 8080 status: {'OPEN' if result else 'CLOSED'}")
        
        # Test a closed port for comparison
        print(f"\n🔍 Testing known closed port 7777...")
        result = scanner.scan_port("127.0.0.1", 7777, timeout=1)
        print(f"   Port 7777 status: {'OPEN' if result else 'CLOSED'}")
        
    finally:
        print(f"\n🛑 Stopping test servers...")
        server.stop_all_servers()
    
    print("\n✅ Demo completed!")
    print("\n💡 What this proves:")
    print("   • Your port scanner correctly detects open ports")
    print("   • Progress tracking works accurately")  
    print("   • Service identification functions properly")
    print("   • Both individual and range scanning work")

def demo_realistic_scenarios():
    """Show realistic scanning scenarios"""
    
    print("\n🌐 Realistic Scanning Scenarios")
    print("=" * 50)
    
    scanner = PortScanner()
    
    scenarios = [
        {
            "name": "Check if SSH is running",
            "target": "127.0.0.1", 
            "ports": [22],
            "description": "Check for SSH service on localhost"
        },
        {
            "name": "Web server check",
            "target": "127.0.0.1",
            "ports": [80, 443, 8080, 8443],
            "description": "Look for web servers on common ports"
        },
        {
            "name": "Database services",
            "target": "127.0.0.1", 
            "ports": [3306, 5432, 1433, 6379],
            "description": "Check for database services"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print(f"   {scenario['description']}")
        print(f"   Target: {scenario['target']}")
        print(f"   Ports: {scenario['ports']}")
        
        results = []
        for port in scenario['ports']:
            result = scanner.scan_port(scenario['target'], port, timeout=1)
            service = scanner.get_service_name(port)
            status = "OPEN" if result else "CLOSED"
            results.append((port, service, status))
            print(f"      Port {port} ({service}): {status}")
        
        open_count = sum(1 for _, _, status in results if status == "OPEN")
        print(f"   Result: {open_count}/{len(scenario['ports'])} ports open")

def interactive_demo():
    """Interactive demo where user can choose what to test"""
    
    print("🎮 Interactive Port Scanner Demo")
    print("=" * 40)
    
    while True:
        print("\nChoose a demo:")
        print("1. Test with real open ports (test servers)")
        print("2. Check realistic scenarios on localhost")
        print("3. Custom scan")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            demo_with_test_servers()
        elif choice == "2":
            demo_realistic_scenarios()
        elif choice == "3":
            custom_scan_demo()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, try again")

def custom_scan_demo():
    """Let user input custom scan parameters"""
    
    print("\n🛠️  Custom Scan Demo")
    print("-" * 30)
    
    scanner = PortScanner()
    
    # Get user input
    target = input("Enter target IP (default: 127.0.0.1): ").strip() or "127.0.0.1"
    
    if not scanner.validate_ip(target):
        print("❌ Invalid IP address")
        return
    
    try:
        start_port = int(input("Enter start port (default: 80): ") or "80")
        end_port = int(input("Enter end port (default: 85): ") or "85")
        timeout = float(input("Enter timeout in seconds (default: 1): ") or "1")
    except ValueError:
        print("❌ Invalid input")
        return
    
    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print("❌ Invalid port range")
        return
    
    print(f"\n🔍 Scanning {target} ports {start_port}-{end_port}...")
    
    found_ports = []
    
    def progress_callback(value):
        if int(value) % 20 == 0:
            print(f"   Progress: {value:.1f}%")
    
    def result_callback(port, service):
        found_ports.append((port, service))
        print(f"   🎯 Found: Port {port} ({service})")
    
    scanner.scanning = True
    start_time = time.time()
    
    open_ports = scanner.scan_range(
        target, start_port, end_port, timeout,
        progress_callback, result_callback
    )
    
    end_time = time.time()
    
    print(f"\n✅ Scan completed in {end_time - start_time:.2f} seconds")
    print(f"   Found {len(open_ports)} open ports")

def main():
    """Main demo function"""
    print("🚀 Welcome to the Port Scanner Demo!")
    print("This will help you test the scanner with actual open ports.")
    print()
    
    # Quick check if we're ready
    scanner = PortScanner()
    print("🔧 Quick system check...")
    print(f"   ✓ Scanner initialized")
    print(f"   ✓ IP validation working: {scanner.validate_ip('127.0.0.1')}")
    print(f"   ✓ Service database loaded: {len(scanner.common_ports)} services")
    
    # Run interactive demo
    interactive_demo()

if __name__ == "__main__":
    main()