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

image_data= []

def handle_signup(client_socket, client_address):
    # 사용자 정보 수신
    id, address = client_socket.recvfrom(1024)
    name, address = client_socket.recvfrom(1024)
    password, address = client_socket.recvfrom(1024)

    # 회원가입 로직
    if id.decode() in user_database:
        client_socket.sendto('이미 가입된 사용자입니다.'.encode(), client_address)
    else:
        user_database[id.decode()] = {
            'password': password.decode(),
            'name': name.decode(),
            'version': '1'
        }
        client_socket.sendto('회원가입이 완료되었습니다.'.encode(), client_address)


def handle_login(client_socket, client_address):
    # 사용자명과 비밀번호 수신
    id, address = client_socket.recvfrom(1024)
    password, address = client_socket.recvfrom(1024)

    # 로그인 로직
    if id.decode() in user_database and user_database[id.decode()]['password'] == password.decode():
        client_socket.sendto('로그인 성공'.encode(), client_address)
        client_socket.sendto(user_database[id.decode()]['name'].encode(), client_address)
        client_socket.sendto(user_database[id.decode()]['version'].encode(), client_address)
    else:
        client_socket.sendto('로그인 실패'.encode(), client_address)


def handle_update(client_socket, client_address):
    # 사용자명과 버전 수신
    id, address = client_socket.recvfrom(1024)
    user_database[id.decode()]['version'] = '2'
    msg = user_database[id.decode()]['name'] + "님 안녕하세요.\nPremium 회원이 되어 주셔서 감사합니다."
    client_socket.sendto(msg.encode(), client_address)


# 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 서버 주소 설정
server_socket.bind((HOST, PORT))

while True:
    request, client_address = server_socket.recvfrom(1024)

    if request.decode() == 'signup':
        handle_signup(server_socket, client_address)
    elif request.decode() == 'login':
        handle_login(server_socket, client_address)
    elif request.decode() == 'update':
        handle_update(server_socket, client_address)
    elif request.decode() == "exit":
        break

# 소켓 종료
server_socket.close()
