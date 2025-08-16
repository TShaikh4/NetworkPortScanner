#!/usr/bin/env python3

import unittest
import sys
import os

def run_all_tests():
    """Run all unit tests for the port scanner"""
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    print("NetworkPortScanner - Unit Test Suite")
    print("=" * 50)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = current_dir
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print(f"Discovering tests in: {start_dir}")
    print(f"Test pattern: test_*.py")
    print("-" * 50)
    
    result = runner.run(suite)
    
    # Print detailed summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests discovered: {result.testsRun}")
    print(f"Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Tests failed: {len(result.failures)}")
    print(f"Tests with errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.split('AssertionError: ')[-1].split(chr(10))[0]}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.split(chr(10))[-2]}")
    
    # Calculate success rate
    total_tests = result.testsRun
    successful_tests = total_tests - len(result.failures) - len(result.errors)
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nSUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All tests passed!")
    elif success_rate >= 90:
        print("✅ Most tests passed - minor issues to fix")
    elif success_rate >= 70:
        print("⚠️  Some tests failed - review needed")
    else:
        print("❌ Many tests failed - significant issues to address")
    
    print("=" * 50)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_name):
    """Run a specific test class or method"""
    
    print(f"Running specific test: {test_name}")
    print("-" * 50)
    
    try:
        # Load specific test
        suite = unittest.TestLoader().loadTestsFromName(test_name)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
    except Exception as e:
        print(f"Error loading test '{test_name}': {e}")
        return 1

def list_available_tests():
    """List all available test classes and methods"""
    
    print("Available test classes:")
    print("-" * 30)
    
    try:
        from test_port_scanner import (
            TestPortScanner,
            TestPortScannerNetworking, 
            TestPortScannerRange,
            TestPortScannerIntegration,
            TestPortScannerEdgeCases
        )
        
        test_classes = [
            TestPortScanner,
            TestPortScannerNetworking,
            TestPortScannerRange, 
            TestPortScannerIntegration,
            TestPortScannerEdgeCases
        ]
        
        for test_class in test_classes:
            print(f"\n{test_class.__name__}:")
            methods = [method for method in dir(test_class) if method.startswith('test_')]
            for method in methods:
                print(f"  - {method}")
                
    except ImportError as e:
        print(f"Error importing test classes: {e}")

def main():
    """Main test runner function"""
    
    if len(sys.argv) == 1:
        # Run all tests
        exit_code = run_all_tests()
    elif sys.argv[1] == "--list":
        # List available tests
        list_available_tests()
        exit_code = 0
    elif sys.argv[1] == "--help":
        # Show help
        print("NetworkPortScanner Test Runner")
        print("Usage:")
        print("  python run_tests.py                    # Run all tests")
        print("  python run_tests.py --list             # List available tests")
        print("  python run_tests.py <test_name>        # Run specific test")
        print("\nExamples:")
        print("  python run_tests.py TestPortScanner")
        print("  python run_tests.py TestPortScanner.test_validate_ip_valid_addresses")
        exit_code = 0
    else:
        # Run specific test
        test_name = sys.argv[1]
        exit_code = run_specific_test(test_name)
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()