import tkinter as tk
import tkinter.font
import socket
import signup
import photoeditor
from tkinter import messagebox

HOST = "127.0.0.1"
PORT = 12345


def loginmain():
    def on_closing():
        win_login.destroy()

    def open_signup():
        win_login.destroy()
        signup.signupmain()

    def open_photoeditor(userid, username, userversion):
        win_login.destroy()
        photoeditor.photoeditormain(userid, username, userversion)

    def login():
        # 서버에 로그인 요청 전송
        client_socket.sendto('login'.encode(), (HOST, PORT))

        userid = entry_id.get()
        password = entry_password.get()

        # 아이디와 비밀번호 전송
        client_socket.sendto(userid.encode(), (HOST, PORT))
        client_socket.sendto(password.encode(), (HOST, PORT))

        # 서버로부터 응답 수신
        response, server_address = client_socket.recvfrom(1024)
        if response.decode() == "로그인 성공":
            messagebox.showinfo(response.decode(), response.decode())
            username, server_address = client_socket.recvfrom(1024)
            userversion, server_address = client_socket.recvfrom(1024)
            if userversion.decode() == "2":
                userversion = "Premium"
            else:
                userversion = "Free"
            open_photoeditor(userid, username.decode(), userversion)
        else:
            messagebox.showwarning(response.decode(), "아이디와 비밀번호를 확인해 주세요.")

    # 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Tkinter 윈도우 생성
    win_login = tk.Tk()
    win_login.title("Login")
    win_login.resizable(False, False)

    # 화면의 가로 길이와 세로 길이 구하기
    screen_width = win_login.winfo_screenwidth()
    screen_height = win_login.winfo_screenheight()

    # 윈도우의 가로 길이와 세로 길이 구하기
    win_width = 300
    win_height = 160

    # 윈도우를 화면 중앙에 위치시키기
    x = (screen_width - win_width) // 2
    y = (screen_height - win_height) // 2
    win_login.geometry(f"{win_width}x{win_height}+{x}+{y}")

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

    # 윈도우 종료 시 on_closing 함수 실행
    win_login.protocol("WM_DELETE_WINDOW", on_closing)

    # Tkinter 이벤트 루프 시작
    win_login.mainloop()

    # 소켓 종료
    client_socket.close()


if __name__ == "__main__":
    loginmain()
