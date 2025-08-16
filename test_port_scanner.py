#!/usr/bin/env python3

import unittest
import socket
import threading
import time
from unittest.mock import patch, MagicMock
from port_scanner import PortScanner

class TestPortScanner(unittest.TestCase):
    
    def setUp(self):
        self.scanner = PortScanner()
    
    def test_init(self):
        """Test PortScanner initialization"""
        self.assertIsInstance(self.scanner.common_ports, dict)
        self.assertFalse(self.scanner.scanning)
        self.assertIsInstance(self.scanner.scan_results, list)
        self.assertEqual(len(self.scanner.scan_results), 0)
    
    def test_common_ports_contains_expected_services(self):
        """Test that common ports dictionary contains expected services"""
        expected_ports = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 443: "HTTPS", 3306: "MySQL", 3389: "RDP"
        }
        
        for port, service in expected_ports.items():
            self.assertIn(port, self.scanner.common_ports)
            self.assertEqual(self.scanner.common_ports[port], service)
    
    def test_get_service_name_known_port(self):
        """Test service name retrieval for known ports"""
        self.assertEqual(self.scanner.get_service_name(80), "HTTP")
        self.assertEqual(self.scanner.get_service_name(443), "HTTPS")
        self.assertEqual(self.scanner.get_service_name(22), "SSH")
        self.assertEqual(self.scanner.get_service_name(21), "FTP")
    
    def test_get_service_name_unknown_port(self):
        """Test service name retrieval for unknown ports"""
        self.assertEqual(self.scanner.get_service_name(12345), "Unknown")
        self.assertEqual(self.scanner.get_service_name(99999), "Unknown")
    
    def test_validate_ip_valid_addresses(self):
        """Test IP validation with valid addresses"""
        valid_ips = [
            "127.0.0.1",
            "192.168.1.1",
            "10.0.0.1",
            "8.8.8.8",
            "172.16.0.1",
            "0.0.0.0",
            "255.255.255.255",
            "::1",  # IPv6 localhost
            "2001:db8::1"  # IPv6 example
        ]
        
        for ip in valid_ips:
            with self.subTest(ip=ip):
                self.assertTrue(self.scanner.validate_ip(ip), f"Failed to validate {ip}")
    
    def test_validate_ip_invalid_addresses(self):
        """Test IP validation with invalid addresses"""
        invalid_ips = [
            "256.256.256.256",
            "192.168.1",
            "192.168.1.1.1",
            "not.an.ip.address",
            "localhost",
            "google.com",
            "",
            "192.168.1.-1",
            "192.168.1.256"
        ]
        
        for ip in invalid_ips:
            with self.subTest(ip=ip):
                self.assertFalse(self.scanner.validate_ip(ip), f"Incorrectly validated {ip}")

class TestPortScannerNetworking(unittest.TestCase):
    
    def setUp(self):
        self.scanner = PortScanner()
    
    @patch('socket.socket')
    def test_scan_port_open(self, mock_socket):
        """Test scanning an open port"""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        mock_sock.connect_ex.return_value = 0  # Success
        
        result = self.scanner.scan_port("127.0.0.1", 80, timeout=1)
        
        self.assertTrue(result)
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_sock.settimeout.assert_called_once_with(1)
        mock_sock.connect_ex.assert_called_once_with(("127.0.0.1", 80))
        mock_sock.close.assert_called_once()
    
    @patch('socket.socket')
    def test_scan_port_closed(self, mock_socket):
        """Test scanning a closed port"""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        mock_sock.connect_ex.return_value = 1  # Connection failed
        
        result = self.scanner.scan_port("127.0.0.1", 12345, timeout=1)
        
        self.assertFalse(result)
        mock_sock.close.assert_called_once()
    
    @patch('socket.socket')
    def test_scan_port_exception(self, mock_socket):
        """Test scanning when socket raises exception"""
        mock_socket.side_effect = socket.error("Network error")
        
        result = self.scanner.scan_port("127.0.0.1", 80, timeout=1)
        
        self.assertFalse(result)
    
    @patch('socket.socket')
    def test_scan_port_timeout_exception(self, mock_socket):
        """Test scanning when socket times out"""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        mock_sock.connect_ex.side_effect = socket.timeout("Timeout")
        
        result = self.scanner.scan_port("127.0.0.1", 80, timeout=0.1)
        
        self.assertFalse(result)
    
    def test_scan_port_localhost_real(self):
        """Test real scan of localhost (should be safe)"""
        # Test a port that's likely closed
        result = self.scanner.scan_port("127.0.0.1", 12345, timeout=0.1)
        self.assertIsInstance(result, bool)

class TestPortScannerRange(unittest.TestCase):
    
    def setUp(self):
        self.scanner = PortScanner()
        self.progress_values = []
        self.found_ports = []
    
    def progress_callback(self, value):
        """Mock progress callback"""
        self.progress_values.append(value)
    
    def result_callback(self, port, service):
        """Mock result callback"""
        self.found_ports.append((port, service))
    
    @patch.object(PortScanner, 'scan_port')
    def test_scan_range_no_open_ports(self, mock_scan_port):
        """Test range scanning with no open ports"""
        mock_scan_port.return_value = False
        self.scanner.scanning = True
        
        result = self.scanner.scan_range(
            "127.0.0.1", 80, 82, 1,
            self.progress_callback, self.result_callback
        )
        
        self.assertEqual(len(result), 0)
        self.assertEqual(len(self.found_ports), 0)
        self.assertEqual(len(self.progress_values), 3)  # 3 ports scanned
        self.assertAlmostEqual(self.progress_values[-1], 100.0, places=1)
    
    @patch.object(PortScanner, 'scan_port')
    def test_scan_range_with_open_ports(self, mock_scan_port):
        """Test range scanning with some open ports"""
        # Port 80 open, 81-82 closed
        mock_scan_port.side_effect = lambda target, port, timeout: port == 80
        self.scanner.scanning = True
        
        result = self.scanner.scan_range(
            "127.0.0.1", 80, 82, 1,
            self.progress_callback, self.result_callback
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (80, "HTTP"))
        self.assertEqual(len(self.found_ports), 1)
        self.assertEqual(self.found_ports[0], (80, "HTTP"))
    
    @patch.object(PortScanner, 'scan_port')
    def test_scan_range_stopped_early(self, mock_scan_port):
        """Test range scanning stopped by user"""
        mock_scan_port.return_value = False
        self.scanner.scanning = False  # Simulate stop
        
        result = self.scanner.scan_range(
            "127.0.0.1", 80, 85, 1,
            self.progress_callback, self.result_callback
        )
        
        # Should stop immediately
        self.assertEqual(len(result), 0)
        self.assertEqual(len(self.progress_values), 0)
    
    def test_scan_range_progress_calculation(self):
        """Test that progress is calculated correctly"""
        self.scanner.scanning = True
        
        with patch.object(self.scanner, 'scan_port', return_value=False):
            self.scanner.scan_range(
                "127.0.0.1", 1, 10, 0.01,  # 10 ports, very fast timeout
                self.progress_callback, self.result_callback
            )
        
        # Should have 10 progress updates
        self.assertEqual(len(self.progress_values), 10)
        # Progress should go from 10% to 100%
        self.assertAlmostEqual(self.progress_values[0], 10.0, places=1)
        self.assertAlmostEqual(self.progress_values[-1], 100.0, places=1)

class TestPortScannerIntegration(unittest.TestCase):
    
    def setUp(self):
        self.scanner = PortScanner()
    
    def test_complete_workflow(self):
        """Test a complete scanning workflow"""
        # Start with a fresh scanner
        self.assertFalse(self.scanner.scanning)
        
        # Set scanning to true (simulating GUI start)
        self.scanner.scanning = True
        self.assertTrue(self.scanner.scanning)
        
        # Test IP validation workflow
        self.assertTrue(self.scanner.validate_ip("127.0.0.1"))
        self.assertFalse(self.scanner.validate_ip("invalid"))
        
        # Test service identification workflow
        self.assertEqual(self.scanner.get_service_name(80), "HTTP")
        self.assertEqual(self.scanner.get_service_name(99999), "Unknown")
        
        # Stop scanning
        self.scanner.scanning = False
        self.assertFalse(self.scanner.scanning)

class TestPortScannerEdgeCases(unittest.TestCase):
    
    def setUp(self):
        self.scanner = PortScanner()
    
    def test_scan_port_edge_cases(self):
        """Test edge cases for port scanning"""
        # Test with minimum port
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            mock_sock.connect_ex.return_value = 0
            
            result = self.scanner.scan_port("127.0.0.1", 1, timeout=1)
            self.assertTrue(result)
        
        # Test with maximum port
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            mock_sock.connect_ex.return_value = 1
            
            result = self.scanner.scan_port("127.0.0.1", 65535, timeout=1)
            self.assertFalse(result)
    
    def test_validate_ip_edge_cases(self):
        """Test edge cases for IP validation"""
        # Test boundary values
        self.assertTrue(self.scanner.validate_ip("0.0.0.0"))
        self.assertTrue(self.scanner.validate_ip("255.255.255.255"))
        
        # Test IPv6
        self.assertTrue(self.scanner.validate_ip("::1"))
        self.assertTrue(self.scanner.validate_ip("fe80::1"))
    
    def test_get_service_name_edge_cases(self):
        """Test edge cases for service name retrieval"""
        # Test port 0 (not typically used)
        self.assertEqual(self.scanner.get_service_name(0), "Unknown")
        
        # Test negative port (shouldn't happen in real usage)
        self.assertEqual(self.scanner.get_service_name(-1), "Unknown")
        
        # Test very high port
        self.assertEqual(self.scanner.get_service_name(100000), "Unknown")

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPortScanner,
        TestPortScannerNetworking,
        TestPortScannerRange,
        TestPortScannerIntegration,
        TestPortScannerEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")