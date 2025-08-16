#!/usr/bin/env python3

from port_scanner import PortScanner

def test_scanner():
    scanner = PortScanner()
    
    print("Testing port scanner functionality...")
    
    # Test localhost port 22 (SSH - likely closed) and 80 (HTTP - likely closed)
    test_ports = [22, 80, 443]
    
    for port in test_ports:
        result = scanner.scan_port("127.0.0.1", port, timeout=0.5)
        service = scanner.get_service_name(port)
        status = "Open" if result else "Closed"
        print(f"Port {port} ({service}): {status}")
    
    # Test IP validation
    print(f"\nIP validation tests:")
    print(f"127.0.0.1 valid: {scanner.validate_ip('127.0.0.1')}")
    print(f"invalid.ip valid: {scanner.validate_ip('invalid.ip')}")
    
    print("\nCore functionality test completed!")

if __name__ == "__main__":
    test_scanner()