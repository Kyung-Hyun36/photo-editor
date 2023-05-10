import tkinter as tk
import tkinter.font

# tkinter 윈도우 생성
win_login = tk.Tk()
win_login.title("Login")
win_login.geometry("300x200")

login_frame = tk.Frame(win_login, pady=20)
tk.Label(login_frame, text="ID").grid(row=0, column=0)
id = tk.Entry(login_frame)
id.grid(row=0, column=1)
tk.Label(login_frame, text="PW").grid(row=1, column=0)
pw = tk.Entry(login_frame, show='*')
pw.grid(row=1, column=1)

tk.Button(login_frame, text="로그인").grid(row=2, columnspan=2)

login_frame.pack()
win_login.mainloop()
