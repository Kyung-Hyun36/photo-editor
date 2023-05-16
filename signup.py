import tkinter as tk
import tkinter.font

def register():
    username = entry_username.get()
    password = entry_password.get()
    confirm_password = entry_confirm_password.get()

    if password != confirm_password:
        label_message.config(text="비밀번호가 일치하지 않습니다.", fg="red")
    else:
        # 회원가입 로직을 실행하는 코드를 작성합니다.
        label_message.config(text="회원가입이 완료되었습니다.", fg="green")

# Tkinter 윈도우 생성
win_signup = tk.Tk()
win_signup.title("회원가입")
win_signup.geometry("300x200")

# 사용자명 입력 필드
label_username = tk.Label(win_signup, text="사용자명:")
label_username.pack()
entry_username = tk.Entry(win_signup)
entry_username.pack()

# 비밀번호 입력 필드
label_password = tk.Label(win_signup, text="비밀번호:")
label_password.pack()
entry_password = tk.Entry(win_signup, show="*")
entry_password.pack()

# 비밀번호 확인 입력 필드
label_confirm_password = tk.Label(win_signup, text="비밀번호 확인:")
label_confirm_password.pack()
entry_confirm_password = tk.Entry(win_signup, show="*")
entry_confirm_password.pack()

# 회원가입 버튼
button_register = tk.Button(win_signup, text="회원가입", command=register)
button_register.pack()

# 메시지 표시 레이블
label_message = tk.Label(win_signup, text="")
label_message.pack()

# Tkinter 이벤트 루프 시작
win_signup.mainloop()
