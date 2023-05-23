import tkinter as tk
import tkinter.font
import socket
import login

HOST = "127.0.0.1"
PORT = 12345


def signupmain():
    def signup():
        # 서버에 가입 요청 전송
        client_socket.send('register'.encode())

        id = entry_id.get()
        username = entry_username.get()
        password = entry_password.get()
        confirm_password = entry_confirm_password.get()
        version = str(version_var.get())

        if id == "" or username == "" or password == "" or confirm_password == "":
            label_message.config(text="빈칸을 모두 기입해 주세요.", fg="red")
        elif password != confirm_password:
            label_message.config(text="비밀번호가 일치하지 않습니다.", fg="red")
        else:

            # 사용자 정보 전송
            client_socket.send(id.encode())
            client_socket.send(username.encode())
            client_socket.send(password.encode())
            client_socket.send(version.encode())

            # 서버로부터 응답 수신
            response = client_socket.recv(1024).decode()
            if response == "회원가입이 완료되었습니다.":
                client_socket.send('exit'.encode())
                win_signup.destroy()
                login.loginmain()
            else:
                label_message.config(text=response, fg="red")


    # 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 서버에 연결
    client_socket.connect((HOST, PORT))

    # Tkinter 윈도우 생성
    win_signup = tk.Tk()
    win_signup.title("Sign Up")
    win_signup.geometry("300x250")
    win_signup.resizable(False, False)

    # 회원가입 프레임 생성
    signup_frame = tk.Frame(win_signup, pady=20)
    signup_frame.pack()

    # 아이디 입력 필드
    label_id = tk.Label(signup_frame, text="아이디")
    label_id.grid(row=0, column=0, pady=5)
    entry_id = tk.Entry(signup_frame)
    entry_id.grid(row=0, column=1, pady=5)

    # 사용자명 입력 필드
    label_username = tk.Label(signup_frame, text="이름")
    label_username.grid(row=1, column=0, pady=5)
    entry_username = tk.Entry(signup_frame)
    entry_username.grid(row=1, column=1, pady=5)

    # 비밀번호 입력 필드
    label_password = tk.Label(signup_frame, text="비밀번호")
    label_password.grid(row=2, column=0, pady=5)
    entry_password = tk.Entry(signup_frame, show="*")
    entry_password.grid(row=2, column=1, pady=5)

    # 비밀번호 확인 입력 필드
    label_confirm_password = tk.Label(signup_frame, text="비밀번호 확인")
    label_confirm_password.grid(row=3, column=0, pady=5)
    entry_confirm_password = tk.Entry(signup_frame, show="*")
    entry_confirm_password.grid(row=3, column=1, pady=5)

    # Premium 선택 버튼
    version_var = tk.IntVar()
    button_free = tk.Radiobutton(signup_frame, text="Free", value=1, variable=version_var)
    button_free.grid(row=4, column=0, pady=5)
    button_free.select()
    button_premium = tk.Radiobutton(signup_frame, text="Premium", value=2, variable=version_var)
    button_premium.grid(row=4, column=1, pady=5)

    # 회원가입 버튼
    button_register = tk.Button(signup_frame, text="회원가입", command=signup)
    button_register.grid(row=5, columnspan=2, pady=5)

    # 메시지 표시 레이블
    label_message = tk.Label(signup_frame, text="")
    label_message.grid(row=6, columnspan=2, pady=5)

    # Tkinter 이벤트 루프 시작
    win_signup.mainloop()

    # 소켓 종료
    client_socket.close()
