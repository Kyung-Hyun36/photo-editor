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


def handle_signup(client_socket, client_address):
    # 사용자 정보 수신
    id, address = client_socket.recvfrom(1024)
    name, address = client_socket.recvfrom(1024)
    password, address = client_socket.recvfrom(1024)
    version, address = client_socket.recvfrom(1024)

    # 회원가입 로직
    if id.decode() in user_database:
        client_socket.sendto('이미 가입된 사용자입니다.'.encode(), address)
    else:
        user_database[id.decode()] = {
            'password': password.decode(),
            'name': name.decode(),
            'version': version.decode()
        }
        client_socket.sendto('회원가입이 완료되었습니다.'.encode(), address)


def handle_login(client_socket, client_address):
    # 사용자명과 비밀번호 수신
    id, address = client_socket.recvfrom(1024)
    password, address = client_socket.recvfrom(1024)

    # 로그인 로직
    if id.decode() in user_database and user_database[id.decode()]['password'] == password.decode():
        client_socket.sendto('로그인 성공'.encode(), address)
    else:
        client_socket.sendto('로그인 실패'.encode(), address)


# 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 서버 주소 설정
server_socket.bind((HOST, PORT))

print(f"서버가 실행되었습니다. {HOST}:{PORT}")

while True:
    request, client_address = server_socket.recvfrom(1024)

    if request.decode() == 'signup':
        handle_signup(server_socket, client_address)
    elif request.decode() == 'login':
        handle_login(server_socket, client_address)
    elif request.decode() == "exit":
        break

# 소켓 종료
server_socket.close()
