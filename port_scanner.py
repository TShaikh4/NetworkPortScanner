#!/usr/bin/env python3

import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import ipaddress

class PortScanner:
    def __init__(self):
        self.common_ports = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 993: "IMAPS",
            995: "POP3S", 1433: "MSSQL", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
            5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt", 
            9000: "Test-Web", 9001: "Test-API", 9002: "Test-DB", 9200: "Elasticsearch",
            9999: "Test-Service"
        }
        self.scanning = False
        self.scan_results = []
    
    def scan_port(self, target, port, timeout=1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            return result == 0
        except (socket.error, OSError):
            return False
    
    def get_service_name(self, port):
        return self.common_ports.get(port, "Unknown")
    
    def validate_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def scan_range(self, target, start_port, end_port, timeout, progress_callback, result_callback):
        open_ports = []
        total_ports = end_port - start_port + 1
        
        for i, port in enumerate(range(start_port, end_port + 1)):
            if not self.scanning:
                break
                
            if self.scan_port(target, port, timeout):
                service = self.get_service_name(port)
                open_ports.append((port, service))
                result_callback(port, service)
            
            progress = ((i + 1) / total_ports) * 100
            progress_callback(progress)
        
        return open_ports

class PortScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Port Scanner - Defensive Security Tool")
        self.root.geometry("800x600")
        
        self.scanner = PortScanner()
        self.scan_thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Target IP Address:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_entry = ttk.Entry(main_frame, width=20)
        self.ip_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.ip_entry.insert(0, "127.0.0.1")
        
        ttk.Label(main_frame, text="Port Range:").grid(row=1, column=0, sticky=tk.W, pady=5)
        port_frame = ttk.Frame(main_frame)
        port_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.start_port_entry = ttk.Entry(port_frame, width=10)
        self.start_port_entry.grid(row=0, column=0, padx=(0, 5))
        self.start_port_entry.insert(0, "1")
        
        ttk.Label(port_frame, text="to").grid(row=0, column=1, padx=5)
        
        self.end_port_entry = ttk.Entry(port_frame, width=10)
        self.end_port_entry.grid(row=0, column=2, padx=(5, 0))
        self.end_port_entry.insert(0, "1000")
        
        ttk.Label(main_frame, text="Timeout (seconds):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.timeout_entry = ttk.Entry(main_frame, width=10)
        self.timeout_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.timeout_entry.insert(0, "1")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.scan_button = ttk.Button(button_frame, text="Start Scan", command=self.start_scan)
        self.scan_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Results", command=self.clear_results)
        self.clear_button.grid(row=0, column=2, padx=(5, 0))
        
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(main_frame, text="Ready to scan")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        results_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding="5")
        results_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        main_frame.rowconfigure(6, weight=1)
        
        columns = ("Port", "Service", "Status")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        log_frame = ttk.LabelFrame(main_frame, text="Scan Log", padding="5")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        main_frame.rowconfigure(7, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_progress(self, value):
        self.progress['value'] = value
        self.status_label.config(text=f"Scanning... {value:.1f}%")
        self.root.update_idletasks()
    
    def add_result(self, port, service):
        self.results_tree.insert("", tk.END, values=(port, service, "Open"))
        self.log_message(f"Open port found: {port} ({service})")
    
    def validate_inputs(self):
        try:
            target = self.ip_entry.get().strip()
            if not self.scanner.validate_ip(target):
                messagebox.showerror("Error", "Invalid IP address")
                return None
            
            start_port = int(self.start_port_entry.get())
            end_port = int(self.end_port_entry.get())
            timeout = float(self.timeout_entry.get())
            
            if start_port < 1 or end_port > 65535 or start_port > end_port:
                messagebox.showerror("Error", "Invalid port range (1-65535)")
                return None
            
            if timeout <= 0:
                messagebox.showerror("Error", "Timeout must be positive")
                return None
            
            return target, start_port, end_port, timeout
        except ValueError:
            messagebox.showerror("Error", "Invalid input values")
            return None
    
    def start_scan(self):
        inputs = self.validate_inputs()
        if not inputs:
            return
        
        target, start_port, end_port, timeout = inputs
        
        if not messagebox.askyesno("Confirm Scan", 
                                 f"Scan {target} ports {start_port}-{end_port}?\n\n"
                                 "Only scan networks you own or have permission to test."):
            return
        
        self.scanner.scanning = True
        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.progress['value'] = 0
        self.status_label.config(text="Starting scan...")
        
        self.log_message(f"Starting scan of {target} ports {start_port}-{end_port}")
        
        self.scan_thread = threading.Thread(
            target=self.run_scan,
            args=(target, start_port, end_port, timeout)
        )
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def run_scan(self, target, start_port, end_port, timeout):
        try:
            open_ports = self.scanner.scan_range(
                target, start_port, end_port, timeout,
                self.update_progress, self.add_result
            )
            
            if self.scanner.scanning:
                self.log_message(f"Scan completed. Found {len(open_ports)} open ports.")
                self.status_label.config(text=f"Scan completed - {len(open_ports)} open ports found")
            else:
                self.log_message("Scan stopped by user.")
                self.status_label.config(text="Scan stopped")
                
        except Exception as e:
            self.log_message(f"Scan error: {str(e)}")
            self.status_label.config(text="Scan failed")
        finally:
            self.scan_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.scanner.scanning = False
    
    def stop_scan(self):
        self.scanner.scanning = False
        self.log_message("Stopping scan...")
    
    def clear_results(self):
        self.results_tree.delete(*self.results_tree.get_children())
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.status_label.config(text="Results cleared")

def main():
    root = tk.Tk()
    app = PortScannerGUI(root)
    
    def on_closing():
        if hasattr(app.scanner, 'scanning') and app.scanner.scanning:
            app.scanner.scanning = False
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()