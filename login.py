import tkinter as tk
import tkinter.font
import socket
import signup
import photoeditor

HOST = "127.0.0.1"
PORT = 12345


def loginmain():
    def on_closing():
        client_socket.sendto('exit'.encode(), (HOST, PORT))
        win_login.destroy()

    def login():
        # 서버에 로그인 요청 전송
        client_socket.sendto('login'.encode(), (HOST, PORT))

        username = entry_id.get()
        password = entry_password.get()

        # 아이디와 비밀번호 전송
        client_socket.sendto(username.encode(), (HOST, PORT))
        client_socket.sendto(password.encode(), (HOST, PORT))

        # 서버로부터 응답 수신
        response, server_address = client_socket.recvfrom(1024)
        if response.decode() == "로그인 성공":
            open_photoeditor()
        else:
            label_message.config(text=response.decode(), fg="red")

    def open_signup():
        win_login.destroy()
        signup.signupmain()

    def open_photoeditor():
        win_login.destroy()
        photoeditor.photoeditormain()

    # 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Tkinter 윈도우 생성
    win_login = tk.Tk()
    win_login.title("Login")
    win_login.geometry("300x180")

    # 로그인 프레임 생성
    login_frame = tk.Frame(win_login, pady=20)
    login_frame.pack()

    # 사용자명 입력 필드
    label_id = tk.Label(login_frame, text="아이디")
    label_id.grid(row=0, column=0, pady=5)
    entry_id = tk.Entry(login_frame)
    entry_id.grid(row=0, column=1, pady=5)

    # 비밀번호 입력 필드
    label_password = tk.Label(login_frame, text="비밀번호")
    label_password.grid(row=1, column=0, pady=5)
    entry_password = tk.Entry(login_frame, show="*")
    entry_password.grid(row=1, column=1, pady=5)

    # 로그인 버튼
    button_login = tk.Button(login_frame, text="로그인", command=login)
    button_login.grid(row=2, columnspan=2, pady=5)

    # 회원가입 버튼
    button_signup = tk.Button(login_frame, text="회원가입", command=open_signup)
    button_signup.grid(row=3, columnspan=2, pady=5)

    # 메시지 표시 레이블
    label_message = tk.Label(login_frame, text="")
    label_message.grid(row=4, columnspan=2, pady=5)

    # 윈도우 종료 시 on_closing 함수 실행
    win_login.protocol("WM_DELETE_WINDOW", on_closing)

    # Tkinter 이벤트 루프 시작
    win_login.mainloop()


if __name__ == "__main__":
    loginmain()
