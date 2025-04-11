import socket
import os
import json
import struct

# Функция для получения структуры файлов и папок
def get_directory_structure(root_dir):
    file_structure = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        relative_path = os.path.relpath(dirpath, root_dir)
        file_structure[relative_path] = {
            'directories': dirnames,
            'files': filenames
        }
    return file_structure

# Основной класс сервера
class FileServer:
    def __init__(self, host='localhost', port=9090):
        self.host = host
        self.port = port
        self.root_dir = os.getcwd()  # Текущая директория как стартовая

    def start(self): # TCP сокет
        print(f"Сервер запущен на {self.host}:{self.port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))#привязка к айпи
            server_socket.listen(1)#Подключение 1
            conn, addr = server_socket.accept()
            print(f"Подключился клиент: {addr}")
            
            with conn:#Ожидание команды от клиента
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                        break

                    print(f"Получена команда: {data}")

                    if data.startswith("SET_DIR"):#Смена директории
                        _, new_dir = data.split(maxsplit=1)
                        if os.path.isdir(new_dir):
                            self.root_dir = new_dir
                            response = "OK"
                        else:
                            response = "ERROR: Directory not found"
                        conn.send(response.encode())

                    elif data == "GET_INFO":
                        structure = get_directory_structure(self.root_dir)
                        json_data = json.dumps(structure, indent=2)

                        # Отправляем длину данных сначала
                        data_len = struct.pack('>I', len(json_data))
                        conn.send(data_len)
                        conn.send(json_data.encode())

                    elif data == "EXIT":
                        print("Клиент отключился.")
                        break

if __name__ == "__main__":
    server = FileServer()
    server.start()