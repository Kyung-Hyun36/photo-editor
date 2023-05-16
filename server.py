import socket

HOST = "127.0.0.1"
PORT = 12345

# 가입된 사용자 정보
user_database = {
    'admin': {
        'password': 'admin123',
        'name': '관리자',
        'version': '2'
    }
}


def handle_registration(client_socket):
    # 사용자명과 비밀번호 수신
    id = client_socket.recv(1024).decode()
    name = client_socket.recv(1024).decode()
    password = client_socket.recv(1024).decode()
    version = client_socket.recv(1024).decode()

    # 회원가입 로직
    if id in user_database:
        client_socket.send('이미 가입된 사용자입니다.'.encode())
    else:
        user_database[id] = {
            'password': password,
            'name': name,
            'version': version
        }
        client_socket.send('회원가입이 완료되었습니다.'.encode())
        print(user_database)


def handle_login(client_socket):
    # 사용자명과 비밀번호 수신
    id = client_socket.recv(1024).decode()
    password = client_socket.recv(1024).decode()

    # 로그인 로직
    if id in user_database and user_database[id] == password:
        client_socket.send('로그인 성공'.encode())
    else:
        client_socket.send('로그인 실패'.encode())


def handle_client(client_socket):
    while True:
        # 클라이언트로부터 요청 수신
        request = client_socket.recv(1024).decode()

        if request == 'register':
            handle_registration(client_socket)
        elif request == 'login':
            handle_login(client_socket)
        elif request == 'exit':
            break

    # 클라이언트 소켓 종료
    client_socket.close()


# 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 서버 주소 설정
server_socket.bind((HOST, PORT))

# 클라이언트 접속 대기
server_socket.listen()

print(f"서버가 실행되었습니다. {HOST}:{PORT}")

while True:
    # 클라이언트 접속 수락
    client_socket, client_address = server_socket.accept()
    print(f"클라이언트가 접속했습니다. {client_address[0]}:{client_address[1]}")

    # 클라이언트 요청 처리 함수 호출
    handle_client(client_socket)
