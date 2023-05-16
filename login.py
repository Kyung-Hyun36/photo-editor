import tkinter as tk


def login():
    username = entry_id.get()
    password = entry_password.get()

    if username == "admin" and password == "admin123":
        label_message.config(text="로그인 성공", fg="green")
    else:
        label_message.config(text="로그인 실패", fg="red")


# Tkinter 윈도우 생성
win_login = tk.Tk()
win_login.title("Login")
win_login.geometry("300x150")

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

# 메시지 표시 레이블
label_message = tk.Label(login_frame, text="")
label_message.grid(row=3, columnspan=2, pady=5)

# Tkinter 이벤트 루프 시작
win_login.mainloop()
