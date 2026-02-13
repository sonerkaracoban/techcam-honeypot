import socket
import threading
import datetime
import time
import csv
import os

LOG_FILE = "captured_attackers.csv"

def save_log(ip, username, password):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "IP Address", "Username", "Password"])
        writer.writerow([timestamp, ip, username, password])
    
    print(f"[*] New record added: {ip} | {username} : {password}")

def secure_receive(client_socket, max_bytes=1024, max_chars=50):
    try:
        data = client_socket.recv(max_bytes).decode('utf-8', errors='ignore').strip()
        
        if not data:
            return "[EMPTY INPUT]"
            
        if len(data) > max_chars:
            return data[:max_chars] + "...[TRUNCATED]"
            
        return data
        
    except socket.timeout:
        return "[TIMEOUT]"
    except Exception:
        return "[ERROR / DISCONNECTED]"

def handle_connection(client_socket, addr):
    ip = addr[0]
    print(f"[+] New connection detected: {ip}")
    
    client_socket.settimeout(10.0)
    
    try:
        banner = "TechCam Pro IP Network Camera v4.0.1\n\n"
        client_socket.send(banner.encode('utf-8'))
        
        client_socket.send("Login: ".encode('utf-8'))
        username = secure_receive(client_socket)
        
        client_socket.send("Password: ".encode('utf-8'))
        password = secure_receive(client_socket)
        
        save_log(ip, username, password)
        
        time.sleep(1)
        client_socket.send("\nAccess Denied.\n".encode('utf-8'))
        
    except socket.timeout:
        print(f"[-] Connection timed out, dropped: {ip}")
    except Exception as e:
        print(f"[-] Unexpected connection error ({ip}): {e}")
    finally:
        client_socket.close()

def start_honeypot():
    PORT = 23
    HOST = "0.0.0.0"
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[*] Honeypot active. Listening on port {PORT} (Security Measures Active)...")
        
        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_connection, args=(client_socket, addr))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n[*] Shutting down honeypot safely...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_honeypot()