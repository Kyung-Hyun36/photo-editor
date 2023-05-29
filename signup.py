import tkinter as tk
import tkinter.font
import socket
import login
from tkinter import messagebox

HOST = "127.0.0.1"
PORT = 12345


def signupmain():
    def on_closing():
        win_signup.destroy()
        login.loginmain()

    def signup():
        id = entry_id.get()
        username = entry_username.get()
        password = entry_password.get()
        confirm_password = entry_confirm_password.get()
        version = str(version_var.get())

        if id == "" or username == "" or password == "" or confirm_password == "":
            messagebox.showwarning("회원가입 실패", "빈칸을 모두 기입해 주세요.")
        elif password != confirm_password:
            messagebox.showwarning("회원가입 실패", "비밀번호가 일치하지 않습니다.")
        else:
            # 서버에 가입 요청 전송
            client_socket.sendto('signup'.encode(), (HOST, PORT))

            # 사용자 정보 전송
            client_socket.sendto(id.encode(), (HOST, PORT))
            client_socket.sendto(username.encode(), (HOST, PORT))
            client_socket.sendto(password.encode(), (HOST, PORT))
            client_socket.sendto(version.encode(), (HOST, PORT))

            # 서버로부터 응답 수신
            response, server_address = client_socket.recvfrom(1024)
            if response.decode() == "회원가입이 완료되었습니다.":
                messagebox.showinfo("회원가입 완료", response.decode())
                win_signup.destroy()
                login.loginmain()
            else:
                messagebox.showwarning("회원가입 실패", response.decode())

    # 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Tkinter 윈도우 생성
    win_signup = tk.Tk()
    win_signup.title("Sign Up")
    win_signup.resizable(False, False)

    # 화면의 가로 길이와 세로 길이 구하기
    screen_width = win_signup.winfo_screenwidth()
    screen_height = win_signup.winfo_screenheight()

    # 윈도우의 가로 길이와 세로 길이 구하기
    win_width = 300
    win_height = 250

    # 윈도우를 화면 중앙에 위치시키기
    x = (screen_width - win_width) // 2
    y = (screen_height - win_height) // 2
    win_signup.geometry(f"{win_width}x{win_height}+{x}+{y}")

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

    # 윈도우 종료 시 on_closing 함수 실행
    win_signup.protocol("WM_DELETE_WINDOW", on_closing)

    # Tkinter 이벤트 루프 시작
    win_signup.mainloop()

    # 소켓 종료
    client_socket.close()
