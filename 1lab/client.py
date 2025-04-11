import socket
import struct
import json

def start_client(host='localhost', port=9090):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print("Успешно подключено к серверу.")

        while True:
            print("\nДоступные команды:")
            print("1 - Сменить директорию")
            print("2 - Получить информацию о файлах")
            print("3 - Выход")

            choice = input("Введите номер команды: ")

            if choice == "1":
                new_dir = input("Введите путь до новой директории: ")
                command = f"SET_DIR {new_dir}"
                client_socket.send(command.encode())
                response = client_socket.recv(1024).decode()
                print("Ответ сервера:", response)

            elif choice == "2":
                client_socket.send("GET_INFO".encode())

                # Получаем длину данных
                data_len = client_socket.recv(4)
                data_len = struct.unpack('>I', data_len)[0]

                # Получаем сами данные
                data = b""
                while len(data) < data_len:
                    packet = client_socket.recv(1024)
                    if not packet:
                        break
                    data += packet

                file_structure = json.loads(data.decode())
                print(json.dumps(file_structure, indent=2))

            elif choice == "3":
                client_socket.send("EXIT".encode())
                print("Выход из программы.")
                break

            else:
                print("Неизвестная команда.")

if __name__ == "__main__":
    start_client()