import io
import tkinter as tk
import tkinter.font
from tkinter import *
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk, ImageGrab
import cv2
import login
import socket
import base64

HOST = "127.0.0.1"
PORT = 12345

image_path, image_tk = None, None
image_size = (0, 0)
layer_ids = []
current_image = None
undo_history = []
start_x, start_y = None, None
convert = 0
dot_positions = []
crop_start_x, crop_start_y = None, None
crop_end_x, crop_end_y = None, None
current_x, current_y = None, None
undo = -1
update_count = 0
image_captured = None


def photoeditormain(username="admin", userversion="Premium"):
    def custom_askyesno(title, message, text1="종료", text2="로그아웃"):
        # 사용자 정의 대화상자 생성
        dialog = tk.Toplevel(win_main)
        dialog.title(title)

        # 윈도우의 가로 길이와 세로 길이 구하기
        dialog_width = 300
        dialog_height = 100

        # 윈도우를 화면 중앙에 위치시키기
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # 메시지 표시
        tk.Label(dialog, text=message).pack(pady=20)

        # 버튼1
        def command1():
            dialog.result = True
            dialog.destroy()

        tk.Button(dialog, text=text1, command=command1).place(x=100, y=60)

        # 버튼2
        def command2():
            dialog.result = False
            dialog.destroy()

        tk.Button(dialog, text=text2, command=command2).place(x=150, y=60)

        # 대화상자를 modal로 설정하여 다른 창을 클릭할 수 없게 함
        dialog.transient(win_main)
        dialog.grab_set()
        win_main.wait_window(dialog)

        # 대화상자가 닫힐 때 result 값을 반환
        return dialog.result

    def on_closing():
        result = custom_askyesno("종료", "프로그램을 종료하거나 로그아웃하시겠습니까?", "종료", "로그아웃")
        win_main.destroy()
        if not result:
            login.loginmain()

    def temp_save():
        global image_captured

        # canvas의 이미지 캡쳐
        canvas_x = canvas.winfo_rootx()
        canvas_y = canvas.winfo_rooty()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        image_captured = ImageGrab.grab((canvas_x, canvas_y, canvas_x + canvas_width, canvas_y + canvas_height))

        temp_image = ImageTk.PhotoImage(resize_image(image_captured, 100))
        canvas_temp.create_image(0, 0, anchor="nw", image=temp_image)
        canvas_temp.image = temp_image  # 이미지 객체를 캔버스의 속성으로 유지

    def temp_load():
        update_image(image_captured)

    def resize_image(image, max_size):
        # 프레임 크기에 맞게 이미지 사이즈 재조정
        width, height = image.size
        if width == 0 or height == 0:
            return image
        if width > height:
            ratio = max_size / width
            new_width = max_size
            new_height = int(height * ratio)
        else:
            ratio = max_size / height
            new_height = max_size
            new_width = int(width * ratio)
        return image.resize((new_width, new_height))

    def load_image():
        global image_path

        # 이미지 파일 선택 대화상자 열기
        file_path = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=(("JPG 파일", "*.jpg"), ("PNG 파일", "*.png"))
        )

        if file_path:
            # 이미지 불러오기
            image_path = file_path
            image = Image.open(image_path)
            update_image(image)

            return file_path

    def update_image(new_image):
        global image_tk, layer_ids, current_image, image_size, update_count

        # 이미지 리사이즈
        max_size = 700
        resized_image = resize_image(new_image, max_size)
        image_size = resized_image.size

        # 모든 이미지 레이어 삭제
        for layer_id in layer_ids:
            canvas.delete(layer_id)

        # 새로운 이미지 레이어 추가
        image_tk = ImageTk.PhotoImage(resized_image)
        image_layer = canvas.create_image(0, 0, anchor="nw", image=image_tk)

        # 레이어 ID 업데이트
        layer_ids = [image_layer]

        # 현재 이미지 업데이트
        current_image = resized_image

        # 작업 이력에 현재 이미지 추가
        undo_history.append(current_image.copy())
        update_count += 1

    def undo():
        global image_tk, layer_ids, current_image, undo_history, undo, update_count
        if update_count <= 1:
            pass
        else:
            if len(undo_history) >= 2:
                update_count -= 1
                undo -= 1
                # 이전 작업 단계의 이미지 가져오기
                previous_image = undo_history[undo]

                # 현재 이미지 업데이트
                current_image = previous_image
                max_size = 700
                resized_image = resize_image(current_image, max_size)
                for layer_id in layer_ids:
                    canvas.delete(layer_id)
                image_tk = ImageTk.PhotoImage(resized_image)
                image_layer = canvas.create_image(0, 0, anchor="nw", image=image_tk)
                layer_ids = [image_layer]
                current_image = resized_image

    def redo():
        global image_tk, layer_ids, current_image, undo_history, undo, update_count
        if len(undo_history) >= 1 and undo < len(undo_history) - 1 and undo < -1:
            update_count += 1
            undo += 1
            # 이전 작업 단계의 이미지 가져오기
            next_image = undo_history[undo]

            # 현재 이미지 업데이트
            current_image = next_image
            max_size = 700
            resized_image = resize_image(current_image, max_size)
            for layer_id in layer_ids:
                canvas.delete(layer_id)
            image_tk = ImageTk.PhotoImage(resized_image)
            image_layer = canvas.create_image(0, 0, anchor="nw", image=image_tk)
            layer_ids = [image_layer]
            current_image = resized_image

    # ...
    def mouse_event(canvas, event):
        if event is not None:
            return (event.x, event.y)
        else:
            return (canvas.winfo_pointerx() - canvas.winfo_rootx(),
                    canvas.winfo_pointery() - canvas.winfo_rooty())

    def make_dot():
        global dot_positions

        a, b = image_size
        radius = 5  # 원의 반지름 설정

        # 각 꼭지점의 좌표 계산
        coordinates = [
            (radius + 3, radius + 3),  # 좌측 상단
            (a // 2, radius + 3),  # 중앙 상단
            (a - 3, radius + 3),  # 우측 상단
            (radius + 3, b // 2),  # 좌측 중앙
            (a - 3, b // 2),  # 우측 중앙
            (radius + 3, b - 3),  # 좌측 하단
            (a // 2, b - 3),  # 중앙 하단
            (a - 3, b - 3),  # 우측 하단
        ]

        dot_positions = []

        # 각 꼭지점에 원 그리기
        for x, y in coordinates:
            dot_positions.append((x - radius, y - radius, x + radius, y + radius))
            canvas.create_rectangle(x - radius, y - radius, x + radius, y + radius, fill='white', outline='black')

    def check_cursor_position(event):
        image_x, image_y = 0, 0
        image_width, image_height = image_size[0], image_size[1]

        if event:
            x, y = mouse_event(canvas, event)
        else:
            x, y = mouse_event(canvas, None)

        # 이미지 영역에 마우스 커서가 닿았는지 확인합니다.
        if x >= image_x and x <= image_x + image_width and y >= image_y and y <= image_y + image_height:
            canvas.config(cursor="crosshair")
        else:
            canvas.config(cursor="")

    def image_crop():
        global crop_start_x, crop_start_y, crop_end_x, crop_end_y
        if crop_start_x is not None and crop_start_y is not None and crop_end_x is not None and crop_end_y is not None:
            cropped_image = current_image.crop((crop_start_x, crop_start_y, crop_end_x, crop_end_y))
            update_image(cropped_image)

    def draw_rectangle():
        global crop_start_x, crop_start_y, current_x, current_y
        if crop_start_x is not None and crop_start_y is not None and current_x is not None and current_y is not None:
            # 기존에 그려진 사각형 삭제
            canvas.delete("rectangle")

            # 사각형 그리기
            canvas.create_rectangle(crop_start_x, crop_start_y, current_x, current_y, outline='black', tags='rectangle')

    def drag(event):
        global dot_positions, crop_start_x, crop_start_y, current_x, current_y
        # 현재 마우스 위치 저장
        current_x, current_y = event.x, event.y
        draw_rectangle()

    def clicked(event):
        global crop_start_x, crop_start_y
        crop_start_x, crop_start_y = event.x, event.y

    def released(event):
        global crop_end_x, crop_end_y
        crop_end_x, crop_end_y = event.x, event.y
        canvas.delete("rectangle")
        image_crop()

    def bind_event():
        canvas.bind("<B1-Motion>", drag)  # 마우스 움직임 이벤트에 check_cursor_position 함수를 바인딩합니다.
        canvas.bind("<ButtonPress-1>", clicked)  # 마우스 왼쪽 버튼을 눌렀을 때 crop 시작 좌표를 기록합니다.
        canvas.bind("<ButtonRelease-1>", released)  # 마우스 왼쪽 버튼을 놓았을 때 crop 종료 좌표를 기록하고, 해당 영역을 잘라냅니다.
        canvas.bind("<Motion>", check_cursor_position)

    def rotate_90CCW():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = current_image

        # 이미지 회전
        angle = 90
        rotated_image = image.rotate(angle)
        update_image(rotated_image)

    def rotate_90CW():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = current_image

        # 이미지 회전
        angle = -90
        rotated_image = image.rotate(angle)
        update_image(rotated_image)

    def rotate_45CCW():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = current_image

        # 이미지 회전
        angle = 45
        rotated_image = image.rotate(angle)
        update_image(rotated_image)

    def rotate_45CW():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = current_image

        # 이미지 회전
        angle = -45
        rotated_image = image.rotate(angle)
        update_image(rotated_image)

    def rotate_user():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = current_image

        # 이미지 회전
        angle = int(angle_entry.get())
        rotated_image = image.rotate(angle)
        update_image(rotated_image)

    def decrease_brightness():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = np.array(current_image)

        # 밝기 조정
        image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        image[:, :, 2] -= 5
        image[:, :, 2] = np.clip(image[:, :, 2], 1, 255)  # v값 255 이상일 경우 최대값인 255로 고정
        image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
        update_image(Image.fromarray(image))

    def increase_brightness():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = np.array(current_image)

        # 밝기 조정
        image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        image[:, :, 2] += 5
        image[:, :, 2] = np.clip(image[:, :, 2], 1, 255)  # v값 255 이상일 경우 최대값인 255로 고정
        image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
        update_image(Image.fromarray(image))

    def save_image():
        global current_image, image_path, convert
        # 파일 형식 얻기
        if convert < 1:
            file_format = image_path.split('.')[-1].lower()
        else:
            file_format = convert_path.split('.')[-1].lower()

        # 파일 저장 경로 및 이름 설정
        save_path = filedialog.asksaveasfilename(defaultextension=f'.{file_format}')
        if not save_path:
            return
        # RGBA to RGB if necessary
        if current_image.mode in ("RGBA", "P"):
            background = Image.new("RGB", current_image.size, (255, 255, 255))
            background.paste(current_image, mask=current_image.split()[3])  # 3 is the alpha channel
            current_image = background
        # 이미지 저장
        current_image.save(save_path)

    def path_convert():
        global current_image, image_path, convert, convert_path

        # 파일 형식 얻기
        file_format = image_path.split('.')[-1].lower()

        if file_format == "png":
            # 파일 경로에서 .png 제거 후 .jpg 추가
            convert_path = image_path.rsplit('.', 1)[0] + '.jpg'
            convert = 1
        elif file_format == "jpg":
            # 파일 경로에서 .jpg 제거 후 .png 추가
            convert_path = image_path.rsplit('.', 1)[0] + '.png'
            convert = 1

    def grayscale():
        global image_tk, layer_ids, current_image
        image_cv2 = np.array(current_image.convert("RGBA"))
        image_cv2 = cv2.cvtColor(image_cv2, cv2.COLOR_RGB2GRAY)
        image_gray = Image.fromarray(image_cv2)
        update_image(image_gray)

    def canny_edge():
        global image_tk, layer_ids, current_image
        canny = np.array(current_image.convert("RGBA"))
        canny = cv2.cvtColor(canny, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(canny, (5, 5), 0)
        canny_image = cv2.Canny(blurred, 50, 150)
        canny_image = Image.fromarray(canny_image)
        update_image(canny_image)

    def gaus_blur():
        global image_tk, layer_ids, current_image
        image = current_image
        Np_image = np.array(image)
        blur_image = cv2.GaussianBlur(Np_image, (5, 5), 0)
        blur_image = Image.fromarray(blur_image)
        update_image(blur_image)

    def sepia_filter():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)
        sepia_matrix = np.array([[0.393, 0.769, 0.189],
                                 [0.349, 0.686, 0.168],
                                 [0.272, 0.534, 0.131]])
        sepia_image = cv2.transform(image, sepia_matrix)
        sepia_image = Image.fromarray(sepia_image.astype('uint8'))
        update_image(sepia_image)

    def red_filter():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)
        red_matrix = np.array([[1.2, 0, 0],
                               [0, 0.8, 0],
                               [0, 0, 0.8]])
        red_image = cv2.transform(image, red_matrix)
        red_image = Image.fromarray(red_image.astype('uint8'))
        update_image(red_image)

    def green_filter():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)
        green_matrix = np.array([[0.8, 0, 0],
                                 [0, 1.2, 0],
                                 [0, 0, 0.8]])
        green_image = cv2.transform(image, green_matrix)
        green_image = Image.fromarray(green_image.astype('uint8'))
        update_image(green_image)

    def blue_filter():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)
        blue_matrix = np.array([[0.8, 0, 0],
                                [0, 0.8, 0],
                                [0, 0, 1.2]])
        blue_image = cv2.transform(image, blue_matrix)
        blue_image = Image.fromarray(blue_image.astype('uint8'))
        update_image(blue_image)

    def create_button(root, icon_path, command, x, y):
        # 이미지 로드
        image = resize_image(Image.open(icon_path), 90)
        icon = ImageTk.PhotoImage(image)

        # 버튼 생성
        button = tk.Button(root, image=icon, command=command, background="white", borderwidth=0, highlightthickness=0)
        button.image = icon  # 사진에 대한 참조 유지
        button.place(x=x, y=y)

    def create_title(root, title, y):
        font_title = tkinter.font.Font(family="맑은 고딕", size=12, weight="bold")
        tk.Label(root, text=title, font=font_title, background="white").place(x=20, y=y)

    def create_line(root, y):
        tk.Label(root, width=41, height=1, background="gray").place(x=20, y=y)
        tk.Label(root, width=41, height=1, background="white").place(x=20, y=y + 2)

    # 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # tkinter 윈도우 생성
    win_main = tk.Tk()
    win_main.title("Photo Editor")
    win_main.resizable(False, False)
    win_main.configure(background="white")

    # 화면의 가로 길이와 세로 길이 구하기
    screen_width = win_main.winfo_screenwidth()
    screen_height = win_main.winfo_screenheight()

    # 윈도우의 가로 길이와 세로 길이 구하기
    win_width = 1400
    win_height = 748

    # 윈도우를 화면 중앙에 위치시키기
    x = (screen_width - win_width) // 2
    y = (screen_height - win_height) // 2
    win_main.geometry(f"{win_width}x{win_height}+{x}+{y}")

    # 상단 프레임: 유저 정보 표시
    user_frame = tk.Frame(win_main, width=1400, height=40, background="white")
    user_frame.place(x=0, y=0)

    # 좌측 프레임: 버튼1
    button1_frame = tk.Frame(win_main, width=345, height=710, background="white", highlightbackground="gray",
                             highlightthickness=2)
    button1_frame.place(x=2, y=40)

    scrollbar1 = tk.Scrollbar(button1_frame)
    scrollbar1.place()

    # 중앙 프레임: 이미지
    image_frame = tk.Frame(win_main, width=710, height=710, background="white", highlightbackground="gray",
                           highlightthickness=2)
    image_frame.place(x=345, y=40)

    # 우측 프레임: 버튼2
    button2_frame = tk.Frame(win_main, width=345, height=710, background="white", highlightbackground="gray",
                             highlightthickness=2)
    button2_frame.place(x=1053, y=40)

    # 유저 정보 생성
    font_user = tkinter.font.Font(family="Tahoma", size=12, weight="bold")

    tk.Label(user_frame, text=username, font=font_user, background="white").place(x=1220, y=7)
    tk.Label(user_frame, text=userversion, font=font_user, background="white").place(x=1300, y=7)

    # 이미지 캔버스 생성
    canvas = tk.Canvas(image_frame, width=700, height=700, bg="white")
    canvas.place(x=0, y=0)
    # bind_event()

    # 버튼 생성
    create_button(user_frame, "icon//icon_load.png", load_image, 1000, 0)
    create_button(user_frame, "icon//icon_save.png", save_image, 1100, 0)

    create_title(button1_frame, "Rotate", 3)
    create_line(button1_frame, 27)
    create_button(button1_frame, "icon//icon_rotate45CW.png", rotate_45CW, 25, 35)
    create_button(button1_frame, "icon//icon_rotate45CCW.png", rotate_45CCW, 125, 35)
    create_button(button1_frame, "icon//icon_rotate90CW.png", rotate_90CW, 25, 135)
    create_button(button1_frame, "icon//icon_rotate90CCW.png", rotate_90CCW, 125, 135)
    create_button(button1_frame, "icon//icon_rotate90CCW.png", rotate_user, 225, 75)
    angle_entry = Entry(button1_frame, width=10, background="gray")
    angle_entry.place(x=233, y=170)

    create_title(button1_frame, "Adjust Brightness", 233)
    create_line(button1_frame, 257)
    create_button(button1_frame, "icon//icon_brightness.png", decrease_brightness, 25, 265)
    create_button(button1_frame, "icon//icon_brightness.png", increase_brightness, 125, 265)

    create_title(button1_frame, "Blur", 363)
    create_line(button1_frame, 387)
    create_button(button1_frame, "icon//icon_blur.png", gaus_blur, 25, 395)
    create_button(button1_frame, "icon//icon_blur.png", gaus_blur, 125, 395)
    create_button(button1_frame, "icon//icon_blur.png", gaus_blur, 225, 395)

    create_title(button1_frame, "Etc.", 493)
    create_line(button1_frame, 517)
    create_button(button1_frame, "icon//icon_crop.png", bind_event, 25, 525)
    create_button(button1_frame, "icon//icon_convert.png", path_convert, 125, 525)

    create_title(button2_frame, "Undo & Redo", 3)
    create_line(button2_frame, 27)
    create_button(button2_frame, "icon//icon_undo.png", undo, 25, 35)
    create_button(button2_frame, "icon//icon_redo.png", redo, 125, 35)

    create_title(button2_frame, "Add & Remove", 133)
    create_line(button2_frame, 157)
    create_button(button2_frame, "icon//icon_add.png", undo, 25, 165)
    create_button(button2_frame, "icon//icon_removeBG.png", undo, 125, 165)

    create_title(button2_frame, "Filter", 263)
    create_line(button2_frame, 287)
    create_button(button2_frame, "icon//icon_removeBG.png", grayscale, 25, 295)
    create_button(button2_frame, "icon//icon_removeBG.png", canny_edge, 125, 295)
    create_button(button2_frame, "icon//icon_removeBG.png", sepia_filter, 225, 295)
    create_button(button2_frame, "icon//icon_removeBG.png", red_filter, 25, 395)
    create_button(button2_frame, "icon//icon_removeBG.png", blue_filter, 125, 395)
    create_button(button2_frame, "icon//icon_removeBG.png", green_filter, 225, 395)
    # create_button(button1_frame, "icon//icon_grayscale.png", image_grayscale, 0, 4)

    create_title(button2_frame, "TempSave", 493)
    create_line(button2_frame, 517)
    canvas_temp = tk.Canvas(button2_frame, width=100, height=100, bg="white", borderwidth=1, relief="solid")
    canvas_temp.place(x=110, y=525)
    create_button(button2_frame, "icon//icon_save.png", temp_save, 75, 635)
    create_button(button2_frame, "icon//icon_load.png", temp_load, 175, 635)

    # 윈도우 종료 시 on_closing 함수 실행
    win_main.protocol("WM_DELETE_WINDOW", on_closing)

    # 윈도우 실행
    win_main.mainloop()

    # 소켓 종료
    client_socket.close()


if __name__ == "__main__":
    photoeditormain()
