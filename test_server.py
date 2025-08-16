#!/usr/bin/env python3

import socket
import threading
import time
import sys
from contextlib import contextmanager

class TestServer:
    """A simple test server that opens multiple ports for testing the port scanner"""
    
    def __init__(self):
        self.servers = []
        self.running = False
    
    def start_server(self, port, service_name="Test"):
        """Start a simple TCP server on the specified port"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('127.0.0.1', port))
            server_socket.listen(5)
            
            def handle_connections():
                while self.running:
                    try:
                        server_socket.settimeout(1.0)  # Non-blocking with timeout
                        client_socket, addr = server_socket.accept()
                        # Send a simple response and close
                        response = f"Hello from {service_name} server on port {port}\n"
                        client_socket.send(response.encode())
                        client_socket.close()
                    except socket.timeout:
                        continue  # Continue checking if we should stop
                    except Exception:
                        break
                
                server_socket.close()
            
            thread = threading.Thread(target=handle_connections, daemon=True)
            thread.start()
            
            self.servers.append({
                'port': port,
                'socket': server_socket,
                'thread': thread,
                'service': service_name
            })
            
            print(f"✓ Started {service_name} server on port {port}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to start server on port {port}: {e}")
            return False
    
    def start_multiple_servers(self):
        """Start multiple test servers on different ports"""
        servers_to_start = [
            (8080, "HTTP-Alt"),
            (8443, "HTTPS-Alt"), 
            (9000, "Test-Web"),
            (9001, "Test-API"),
            (9002, "Test-DB"),
            (9999, "Test-Service")
        ]
        
        self.running = True
        started_count = 0
        
        print("Starting test servers...")
        print("-" * 40)
        
        for port, service in servers_to_start:
            if self.start_server(port, service):
                started_count += 1
            time.sleep(0.1)  # Small delay between starts
        
        print("-" * 40)
        print(f"Started {started_count}/{len(servers_to_start)} test servers")
        print(f"Servers running on 127.0.0.1")
        print("\nYou can now run the port scanner with:")
        print("Target: 127.0.0.1")
        print("Ports: 8000-10000")
        print("Timeout: 1")
        
        return started_count > 0
    
    def stop_all_servers(self):
        """Stop all running test servers"""
        print("\nStopping test servers...")
        self.running = False
        
        # Give threads time to finish
        time.sleep(2)
        
        for server in self.servers:
            try:
                server['socket'].close()
                print(f"✓ Stopped server on port {server['port']}")
            except:
                pass
        
        self.servers.clear()
        print("All servers stopped.")
    
    def list_running_servers(self):
        """List all currently running servers"""
        if not self.servers:
            print("No test servers currently running.")
            return
        
        print("Running test servers:")
        print("-" * 30)
        for server in self.servers:
            print(f"Port {server['port']}: {server['service']}")

@contextmanager
def test_servers():
    """Context manager for test servers - automatically starts and stops"""
    server = TestServer()
    try:
        if server.start_multiple_servers():
            yield server
        else:
            print("Failed to start test servers")
            yield None
    finally:
        server.stop_all_servers()

def interactive_mode():
    """Interactive mode for manual testing"""
    server = TestServer()
    
    print("=== Port Scanner Test Server ===")
    print("This will start multiple test servers on localhost")
    print("You can then test your port scanner against them")
    print()
    
    try:
        if not server.start_multiple_servers():
            print("Failed to start servers. Exiting.")
            return
        
        print("\n" + "=" * 50)
        print("TEST SERVERS ARE NOW RUNNING!")
        print("=" * 50)
        print("\nOpen your port scanner and use these settings:")
        print("• Target IP: 127.0.0.1")
        print("• Port Range: 8000-10000")
        print("• Timeout: 1 second")
        print("\nYou should see several open ports detected!")
        print("\nPress Ctrl+C to stop the servers...")
        
        # Keep servers running until user stops
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        server.stop_all_servers()

def quick_test():
    """Quick test to verify servers work"""
    print("Quick test - starting servers for 10 seconds...")
    
    with test_servers() as server:
        if server:
            print("\nTesting connection to port 8080...")
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(2)
                result = test_socket.connect_ex(('127.0.0.1', 8080))
                test_socket.close()
                
                if result == 0:
                    print("✓ Port 8080 is responding - test servers working!")
                else:
                    print("✗ Port 8080 not responding")
            except Exception as e:
                print(f"✗ Test failed: {e}")
            
            print("Servers will run for 10 seconds...")
            time.sleep(10)
        else:
            print("Failed to start test servers")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            quick_test()
        elif sys.argv[1] == "--help":
            print("Test Server for Port Scanner")
            print("Usage:")
            print("  python test_server.py              # Interactive mode")
            print("  python test_server.py --quick      # Quick 10-second test")
            print("  python test_server.py --help       # Show this help")
        else:
            print("Unknown option. Use --help for usage.")
    else:
        interactive_mode()

if __name__ == "__main__":
    main()