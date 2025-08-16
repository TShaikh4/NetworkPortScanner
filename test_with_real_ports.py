#!/usr/bin/env python3

import unittest
import time
import threading
from port_scanner import PortScanner
from test_server import TestServer

class TestPortScannerWithRealPorts(unittest.TestCase):
    """Integration tests using real test servers"""
    
    @classmethod
    def setUpClass(cls):
        """Start test servers before running tests"""
        print("\nSetting up test servers for integration testing...")
        cls.test_server = TestServer()
        cls.test_server.start_multiple_servers()
        time.sleep(1)  # Give servers time to start
    
    @classmethod 
    def tearDownClass(cls):
        """Stop test servers after tests complete"""
        print("\nStopping test servers...")
        cls.test_server.stop_all_servers()
    
    def setUp(self):
        self.scanner = PortScanner()
        self.found_ports = []
        self.progress_updates = []
    
    def progress_callback(self, value):
        self.progress_updates.append(value)
    
    def result_callback(self, port, service):
        self.found_ports.append((port, service))
    
    def test_scan_finds_open_test_servers(self):
        """Test that scanner finds our test servers"""
        self.scanner.scanning = True
        
        # Scan the range where our test servers are running
        open_ports = self.scanner.scan_range(
            "127.0.0.1", 8000, 9999, 1,
            self.progress_callback, self.result_callback
        )
        
        # Should find several open ports
        self.assertGreater(len(open_ports), 0, "Should find at least one open port")
        self.assertGreater(len(self.found_ports), 0, "Callback should be called")
        
        # Check that we found expected ports
        found_port_numbers = [port for port, service in open_ports]
        expected_ports = [8080, 8443, 9000, 9001, 9002, 9999]
        
        found_expected = [p for p in expected_ports if p in found_port_numbers]
        self.assertGreater(len(found_expected), 0, f"Should find some expected ports. Found: {found_port_numbers}")
    
    def test_scan_single_known_open_port(self):
        """Test scanning a single port we know is open"""
        # Test port 8080 specifically
        result = self.scanner.scan_port("127.0.0.1", 8080, timeout=2)
        self.assertTrue(result, "Port 8080 should be open (test server)")
        
        # Test a port we know is closed
        result = self.scanner.scan_port("127.0.0.1", 7777, timeout=1)
        self.assertFalse(result, "Port 7777 should be closed")
    
    def test_service_identification_with_test_servers(self):
        """Test that known services are identified correctly"""
        # These should return "Unknown" since they're not in our common_ports dict
        service = self.scanner.get_service_name(8080)
        self.assertEqual(service, "HTTP-Alt")  # This one is in our dictionary
        
        service = self.scanner.get_service_name(9000)
        self.assertEqual(service, "Unknown")  # This one is not
    
    def test_progress_tracking_with_real_scan(self):
        """Test that progress tracking works during real scan"""
        self.scanner.scanning = True
        
        # Scan a small range
        self.scanner.scan_range(
            "127.0.0.1", 8080, 8085, 0.5,
            self.progress_callback, self.result_callback
        )
        
        # Should have progress updates
        self.assertGreater(len(self.progress_updates), 0, "Should have progress updates")
        
        # Progress should reach 100%
        self.assertAlmostEqual(self.progress_updates[-1], 100.0, places=1)
    
    def test_scan_stop_functionality(self):
        """Test that scanning can be stopped mid-process"""
        self.scanner.scanning = True
        
        def stop_after_delay():
            time.sleep(0.1)  # Let scan start
            self.scanner.scanning = False
        
        # Start stop thread
        stop_thread = threading.Thread(target=stop_after_delay)
        stop_thread.start()
        
        # Run scan (should be stopped early)
        open_ports = self.scanner.scan_range(
            "127.0.0.1", 8000, 8999, 0.1,  # Large range, small timeout
            self.progress_callback, self.result_callback
        )
        
        stop_thread.join()
        
        # Progress should be less than 100% (scan was stopped)
        if self.progress_updates:
            self.assertLess(self.progress_updates[-1], 100.0, "Scan should have been stopped early")

def run_integration_tests():
    """Run integration tests with real servers"""
    print("Running integration tests with real test servers...")
    print("This will start temporary servers on localhost for testing.")
    print("-" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPortScannerWithRealPorts)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All integration tests passed!")
        print("Your port scanner correctly detects open ports!")
    else:
        print("❌ Some integration tests failed")
        if result.failures:
            print("\nFailures:")
            for test, error in result.failures:
                print(f"- {test}: {error.split('AssertionError: ')[-1].split(chr(10))[0]}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_integration_tests()