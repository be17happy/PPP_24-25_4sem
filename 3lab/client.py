import asyncio
import json
import requests
import websockets
import threading

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws?token={}"

connected_event = threading.Event()  # 👈 Флаг подключения

def login():
    email = input("Email: ")
    password = input("Password: ")
    print("📨 Отправляем запрос на логин...")

    response = requests.post(f"{BASE_URL}/login/", json={"email": email, "password": password})
    if response.status_code == 200:
        data = response.json()
        print("✅ Успешная авторизация")
        return email, data["token"]
    else:
        print("❌ Ошибка:", response.text)
        return None, None

def run_task(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/tsp/solve/", headers=headers)
    if response.status_code == 200:
        print("🚀 Задача запущена:", response.json()["task_id"])
    else:
        print("❌ Ошибка запуска задачи:", response.text)

async def listen_ws(token):
    uri = WS_URL.format(token)
    try:
        async with websockets.connect(uri) as websocket:
            print("🟣 Подключено к WebSocket. Ожидаем уведомления...\n")
            connected_event.set()  # 👈 Установить флаг подключения
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print("📩", json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Ошибка WebSocket: {e}")

def main():
    email, token = login()
    if not token:
        return

    loop = asyncio.get_event_loop()
    ws_task = loop.create_task(listen_ws(token))

    # 👇 Ждём подключения WebSocket прежде чем разрешить команды
    connected_event.wait()

    print("\nКоманды:\n  run — запустить задачу\n  exit — выход\n")

    def command_loop():
        while True:
            cmd = input("> ").strip()
            if cmd == "exit":
                ws_task.cancel()
                break
            elif cmd == "run":
                run_task(token)
            else:
                print("Неизвестная команда")

    threading.Thread(target=command_loop, daemon=True).start()

    try:
        loop.run_until_complete(ws_task)
    except asyncio.CancelledError:
        print("🛑 WebSocket закрыт.")


if __name__ == "__main__":
    main()
