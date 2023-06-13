import tkinter as tk
import tkinter.font
from tkinter import *
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk, ImageGrab
import cv2
import login
import socket
import urllib.request
from datetime import datetime, timedelta

HOST = "127.0.0.1"
PORT = 12345

url = 'https://www.google.com/'
page = urllib.request.urlopen(url)

image_path, image_tk = None, None
image_size = (0, 0)
layer_ids = []
current_image = None
undo_history, redo_history = [], []
start_x, start_y = None, None
convert = 0
crop_start_x, crop_start_y = None, None
crop_end_x, crop_end_y = None, None
current_x, current_y = None, None
image_captured = None
userid, username, userversion = None, None, None
x_offset, y_offset = 0, 0


def photoeditormain(id="admin", name="관리자", version="Premium"):
    global userid, username, userversion
    userid = id
    username = name
    userversion = version

    def ask_exit_cancle():
        # 사용자 정의 대화상자 생성
        dialog = tk.Toplevel(win_main)
        dialog.title("종료")

        # 윈도우의 가로 길이와 세로 길이 구하기
        dialog_width = 300
        dialog_height = 100

        # 윈도우를 화면 중앙에 위치시키기
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # 메시지 표시
        tk.Label(dialog, text="프로그램을 종료하거나 로그아웃하시겠습니까?").pack(pady=20)

        # 버튼1
        def command1():
            dialog.result = True
            dialog.destroy()

        tk.Button(dialog, text="종료", command=command1).place(x=100, y=60)

        # 버튼2
        def command2():
            dialog.result = False
            dialog.destroy()

        tk.Button(dialog, text="로그아웃", command=command2).place(x=150, y=60)

        # 대화상자를 modal로 설정하여 다른 창을 클릭할 수 없게 함
        dialog.transient(win_main)
        dialog.grab_set()
        win_main.wait_window(dialog)

        # 대화상자가 닫힐 때 result 값을 반환
        return dialog.result

    def on_closing():
        result = ask_exit_cancle()
        win_main.destroy()
        if not result:
            login.loginmain()

    def payment():
        # 사용자 정의 대화상자 생성
        dialog = tk.Toplevel(win_main)
        dialog.title("Premium")
        dialog.resizable(False, False)

        # 윈도우의 가로 길이와 세로 길이 구하기
        dialog_width = 280
        dialog_height = 450

        # 윈도우를 화면 중앙에 위치시키기
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        premium_img = ImageTk.PhotoImage(resize_image(Image.open("icon/premium.png"), 500))
        tk.Label(dialog, image=premium_img).place(x=0, y=0)

        # 버튼1
        def command1():
            global userversion
            userversion = "Premium"
            label_userversion["text"] = userversion
            client_socket.sendto('update'.encode(), (HOST, PORT))
            client_socket.sendto(userid.encode(), (HOST, PORT))
            response, server_address = client_socket.recvfrom(1024)
            messagebox.showinfo("결제 완료", response.decode())
            dialog.destroy()

        pay_img = ImageTk.PhotoImage(resize_image(Image.open("icon/payment.png"), 220))
        tk.Button(dialog, image=pay_img, command=command1).place(x=30, y=380)

        # 대화상자를 modal로 설정하여 다른 창을 클릭할 수 없게 함
        dialog.transient(win_main)
        dialog.grab_set()
        win_main.wait_window(dialog)

    def update_btn_state():
        if len(undo_history) >= 2:
            btn_undo['state'] = NORMAL
        else:
            btn_undo['state'] = DISABLED

        if redo_history:
            btn_redo['state'] = NORMAL
        else:
            btn_redo['state'] = DISABLED

    def temp_save():
        global image_captured
        utc_time = datetime.strptime(page.headers['Date'], '%a, %d %b %Y %H:%M:%S %Z')
        kst_time = utc_time + timedelta(hours=9)

        # canvas의 이미지 캡쳐
        canvas_x = canvas.winfo_rootx()
        canvas_y = canvas.winfo_rooty()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        image_captured = ImageGrab.grab((canvas_x, canvas_y, canvas_x + canvas_width, canvas_y + canvas_height))

        # canvas_image = canvas.postscript(colormode="color")
        # base64_encoded_image = base64.b64encode(canvas_image.encode()).decode("utf-8")
        # print(base64_encoded_image)

        # client_socket.sendto('save'.encode(), (HOST, PORT))
        # client_socket.sendto(base64_encoded_image.encode(), (HOST, PORT))

        temp_time['text'] = kst_time

        temp_image = ImageTk.PhotoImage(resize_image(image_captured, 100))
        canvas_temp.create_image(0, 0, anchor="nw", image=temp_image)
        canvas_temp.image = temp_image  # 이미지 객체를 캔버스의 속성으로 유지

    def temp_load():
        # client_socket.sendto('save'.encode(), (HOST, PORT))
        # image, address = client_socket.recvfrom(1024)
        update_image(image_captured)
        redo_history.clear()
        update_btn_state()

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
            redo_history.clear()
            update_btn_state()
            return file_path

    def center_image_on_canvas(canvas, image_tk):
        global x_offset, y_offset
        # 캔버스의 크기 가져오기
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # 이미지의 크기 가져오기
        image_width = image_tk.width()
        image_height = image_tk.height()

        # 이미지를 화면 가운데로 이동하기 위한 좌표 계산
        x = (canvas_width - image_width) // 2
        y = (canvas_height - image_height) // 2

        # 이미지를 캔버스 중앙에 배치
        canvas.coords(image_layer, x, y)
        x_offset = -x
        y_offset = -y

    def update_image(new_image):
        global image_tk, layer_ids, current_image, image_size, image_layer

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

        center_image_on_canvas(canvas, image_tk)

        # 레이어 ID 업데이트
        layer_ids = [image_layer]

        # 현재 이미지 업데이트
        current_image = resized_image

        # 작업 이력에 현재 이미지 추가
        undo_history.append(current_image.copy())

    def undo():
        global image_tk, layer_ids, current_image, undo_history, image_layer
        if len(undo_history) >= 2:
            # 이전 작업 단계의 이미지 가져오기
            last = undo_history.pop()
            redo_history.append(last)
            previous_image = undo_history[-1]

            # 현재 이미지 업데이트
            current_image = previous_image
            max_size = 700
            resized_image = resize_image(current_image, max_size)
            for layer_id in layer_ids:
                canvas.delete(layer_id)
            image_tk = ImageTk.PhotoImage(resized_image)
            image_layer = canvas.create_image(0, 0, anchor="nw", image=image_tk)
            center_image_on_canvas(canvas, image_tk)
            layer_ids = [image_layer]
            current_image = resized_image

        update_btn_state()

    def redo():
        global image_tk, layer_ids, current_image, undo_history, image_layer
        if len(redo_history) >= 1:
            # 이전 작업 단계의 이미지 가져오기
            last = redo_history.pop()
            undo_history.append(last)

            # 현재 이미지 업데이트
            current_image = last
            max_size = 700
            resized_image = resize_image(current_image, max_size)
            for layer_id in layer_ids:
                canvas.delete(layer_id)
            image_tk = ImageTk.PhotoImage(resized_image)
            image_layer = canvas.create_image(0, 0, anchor="nw", image=image_tk)
            center_image_on_canvas(canvas, image_tk)
            layer_ids = [image_layer]
            current_image = resized_image

        update_btn_state()

    # ...
    def mouse_event(canvas, event):
        if event is not None:
            return (event.x, event.y)
        else:
            return (canvas.winfo_pointerx() - canvas.winfo_rootx(),
                    canvas.winfo_pointery() - canvas.winfo_rooty())

    def draw_rectangle():
        global crop_start_x, crop_start_y, current_x, current_y
        if crop_start_x is not None and crop_start_y is not None and current_x is not None and current_y is not None:
            # 기존에 그려진 사각형 삭제
            canvas.delete("rectangle")
            # 사각형 그리기
            canvas.create_rectangle(crop_start_x, crop_start_y, current_x, current_y, outline='black', tags='rectangle')

    def drag(event):
        global crop_start_x, crop_start_y, current_x, current_y
        # 현재 마우스 위치 저장
        current_x, current_y = event.x, event.y
        draw_rectangle()

    def clicked(event):
        global crop_start_x, crop_start_y
        canvas.delete("rectangle")
        crop_start_x, crop_start_y = event.x, event.y
        check_cursor_position(event)  # 커서 모양 업데이트

    def check_cursor_position(event):
        global x_offset, y_offset
        image_x, image_y = 0, 0
        image_width, image_height = image_size[0], image_size[1]

        if event:
            x, y = mouse_event(canvas, event)
        else:
            x, y = mouse_event(canvas, None)

        # 이미지 영역에 마우스 커서가 닿았는지 확인합니다.
        if x + x_offset >= image_x and x + x_offset <= image_x + image_width and y + y_offset>= image_y and y + y_offset <= image_y + image_height:
            canvas.config(cursor="crosshair")
        else:
            canvas.config(cursor="")

    def released(event):
        global crop_end_x, crop_end_y
        crop_end_x, crop_end_y = event.x, event.y

    def image_crop():
        global crop_start_x, crop_start_y, crop_end_x, crop_end_y, x_offset, y_offset
        if crop_start_x is not None and crop_start_y is not None and crop_end_x is not None and crop_end_y is not None:
            min_x = min(crop_start_x, crop_end_x)
            max_x = max(crop_start_x, crop_end_x)
            min_y = min(crop_start_y, crop_end_y)
            max_y = max(crop_start_y, crop_end_y)

            min_x += x_offset
            max_x += x_offset
            min_y += y_offset
            max_y += y_offset

            cropped_image = current_image.crop((min_x, min_y, max_x, max_y))
            update_image(cropped_image)

        canvas.delete("rectangle")
        redo_history.clear()
        update_btn_state()

    def rotate_90CCW():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = current_image

        # 이미지 회전
        angle = 90
        rotated_image = image.rotate(angle)
        update_image(rotated_image)
        redo_history.clear()
        update_btn_state()

    def rotate_90CW():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = current_image

        # 이미지 회전
        angle = -90
        rotated_image = image.rotate(angle)
        update_image(rotated_image)
        redo_history.clear()
        update_btn_state()

    def rotate_45CCW():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = current_image

        # 이미지 회전
        angle = 45
        rotated_image = image.rotate(angle)
        update_image(rotated_image)
        redo_history.clear()
        update_btn_state()

    def rotate_45CW():
        global image_tk, layer_ids, current_image
        # 현재 이미지 가져오기
        image = current_image

        # 이미지 회전
        angle = -45
        rotated_image = image.rotate(angle)
        update_image(rotated_image)
        redo_history.clear()
        update_btn_state()

    def rotate_user():
        global image_tk, layer_ids, current_image
        if userversion == "Premium":
            # 현재 이미지 가져오기
            image = current_image

            # 이미지 회전
            angle = int(angle_entry.get())
            rotated_image = image.rotate(-angle)
            update_image(rotated_image)
            redo_history.clear()
            update_btn_state()
        else:
            payment()

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
        redo_history.clear()
        update_btn_state()

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
        redo_history.clear()
        update_btn_state()

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
        image = np.array(current_image)
        gray_matrix = np.array([[0.333, 0.333, 0.333],
                                [0.333, 0.333, 0.333],
                                [0.333, 0.333, 0.333]])
        gray_image = cv2.transform(image, gray_matrix)
        gray_image = Image.fromarray(gray_image.astype('uint8'))
        update_image(gray_image)
        redo_history.clear()
        update_btn_state()

    def canny_edge():
        global image_tk, layer_ids, current_image
        canny = np.array(current_image.convert("RGBA"))
        canny = cv2.cvtColor(canny, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(canny, (5, 5), 0)
        canny_image = cv2.Canny(blurred, 50, 150)
        canny_image = Image.fromarray(canny_image)
        update_image(canny_image)
        redo_history.clear()
        update_btn_state()

    def gaus_blur():
        global image_tk, layer_ids, current_image
        image = current_image
        Np_image = np.array(image)
        blur_image = cv2.GaussianBlur(Np_image, (5, 5), 0)
        blur_image = Image.fromarray(blur_image)
        update_image(blur_image)
        redo_history.clear()
        update_btn_state()

    def selected_blur():
        global image, cursor
        if crop_start_x is not None and crop_start_y is not None and crop_end_x is not None and crop_end_y is not None:
            min_x = min(crop_start_x, crop_end_x)
            max_x = max(crop_start_x, crop_end_x)
            min_y = min(crop_start_y, crop_end_y)
            max_y = max(crop_start_y, crop_end_y)

            min_x += x_offset
            max_x += x_offset
            min_y += y_offset
            max_y += y_offset

            # 영역 선택
            x, y, width, height = min_x, min_y, max_x - min_x, max_y - min_y

            image = np.array(current_image)
            selected_region = image[y:y + height, x:x + width]
            selected_region = cv2.blur(selected_region, (30, 30))  # 블러(모자이크) 처리
            image[y:y + height, x:x + width] = selected_region  # 원본 이미지에 적용
            image = Image.fromarray(image)
            update_image(image)

        redo_history.clear()
        update_btn_state()

    def red_filter():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)
        red_matrix = np.array([[1.2, 0, 0],
                               [0, 0.8, 0],
                               [0, 0, 0.8]])
        red_image = cv2.transform(image, red_matrix)
        red_image = Image.fromarray(red_image.astype('uint8'))
        update_image(red_image)
        redo_history.clear()
        update_btn_state()

    def orange_filter():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)
        orange_matrix = np.array([[0.9, 0.4, 0.0],
                                  [0.4, 0.7, 0.0],
                                  [0.0, 0.0, 0.7]])
        red_image = cv2.transform(image, orange_matrix)
        red_image = Image.fromarray(red_image.astype('uint8'))
        update_image(red_image)
        redo_history.clear()
        update_btn_state()

    def yellow_filter():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)
        yellow_matrix = np.array([[0.7, 0.4, 0.0],
                                  [0.4, 0.7, 0.0],
                                  [0.0, 0.0, 0.5]])
        red_image = cv2.transform(image, yellow_matrix)
        red_image = Image.fromarray(red_image.astype('uint8'))
        update_image(red_image)
        redo_history.clear()
        update_btn_state()

    def green_filter():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)
        green_matrix = np.array([[0.8, 0, 0],
                                 [0, 1.2, 0],
                                 [0, 0, 0.8]])
        green_image = cv2.transform(image, green_matrix)
        green_image = Image.fromarray(green_image.astype('uint8'))
        update_image(green_image)
        redo_history.clear()
        update_btn_state()

    def blue_filter():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)
        blue_matrix = np.array([[0.8, 0, 0],
                                [0, 0.8, 0],
                                [0, 0, 1.2]])
        blue_image = cv2.transform(image, blue_matrix)
        blue_image = Image.fromarray(blue_image.astype('uint8'))
        update_image(blue_image)
        redo_history.clear()
        update_btn_state()

    def purple_filter():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)
        purple_matrix = np.array([[0.6, 0.0, 0.5],
                                  [0.0, 0.4, 0.6],
                                  [0.6, 0.6, 0.8]])
        red_image = cv2.transform(image, purple_matrix)
        red_image = Image.fromarray(red_image.astype('uint8'))
        update_image(red_image)
        redo_history.clear()
        update_btn_state()

    def remove_background():
        global image_tk, layer_ids, current_image
        image = np.array(current_image)

        # 이미지 데이터 타입 및 채널 수 변경
        image = image.astype(np.uint8)
        image = image[:, :, :3]  # 알파 채널 제거

        # 이미지를 RGB로 변환
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 초기 마스크 생성
        mask = np.zeros(image.shape[:2], np.uint8)

        # 관심 영역 지정
        rect = (50, 50, 600, 600)

        # GrabCut 알고리즘 적용을 위한 flags 설정
        flags = cv2.GC_INIT_WITH_RECT

        # 배경인지 확실하지 않은 픽셀을 제거
        mask, bgd_model, fgd_model = cv2.grabCut(image, mask, rect, None, None, 5, flags)

        # 배경인지 확실하지 않은 픽셀을 제거한 마스크 생성
        mask = np.where((mask == cv2.GC_PR_BGD) | (mask == cv2.GC_BGD), 0, 1).astype('uint8')

        # 마스크를 이용하여 배경 제거
        result = image * mask[:, :, np.newaxis]

        # 색상 복원
        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

        update_image(Image.fromarray(result))
        redo_history.clear()
        update_btn_state()

    def create_button(root, icon_path, icon_size, command, x, y):
        # 이미지 로드
        image = resize_image(Image.open(icon_path), icon_size)
        icon = ImageTk.PhotoImage(image)

        # 버튼 생성
        button = tk.Button(root, image=icon, command=command, background="white", borderwidth=0, highlightthickness=0)
        button.image = icon  # 사진에 대한 참조 유지
        button.place(x=x, y=y)
        return button

    def create_title(root, title, y):
        font_title = tkinter.font.Font(family="맑은 고딕", size=12, weight="bold")
        tk.Label(root, text=title, font=font_title, background="white").place(x=20, y=y)

    def create_line(root, y):
        tk.Label(root, width=41, height=1, background="gray").place(x=20, y=y)
        tk.Label(root, width=41, height=1, background="white").place(x=20, y=y + 2)


    def Non_Selected_Blur():
        global image, cursor
        if crop_start_x is not None and crop_start_y is not None and crop_end_x is not None and crop_end_y is not None:
            min_x = min(crop_start_x, crop_end_x)
            max_x = max(crop_start_x, crop_end_x)
            min_y = min(crop_start_y, crop_end_y)
            max_y = max(crop_start_y, crop_end_y)

            min_x += x_offset
            max_x += x_offset
            min_y += y_offset
            max_y += y_offset

            # 영역 선택
            x, y, width, height = min_x, min_y, max_x - min_x, max_y - min_y

            image = np.array(current_image)
            selected_region = image[y:y + height, x:x + width]
            N_selected_region = cv2.blur(image, (50, 50))  # 블러(모자이크) 처리
            N_selected_region[y:y + height, x:x + width] = selected_region  # 원본 이미지에 적용
            image = Image.fromarray(N_selected_region)
            update_image(image)

        redo_history.clear()
        update_btn_state()

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
    label_userversion = tk.Label(user_frame, text=userversion, font=font_user, background="white")
    label_userversion.place(x=1300, y=7)

    # 이미지 캔버스 생성
    canvas = tk.Canvas(image_frame, width=700, height=700, bg="white")
    canvas.place(x=0, y=0)
    canvas.bind("<Motion>", check_cursor_position)
    canvas.bind("<ButtonPress-1>", clicked)  # 마우스 왼쪽 버튼을 눌렀을 때 crop 시작 좌표를 기록합니다.
    canvas.bind("<B1-Motion>", drag)  # 마우스 움직임에 따라 사각형 영역을 그립니다.
    canvas.bind("<ButtonRelease-1>", released)  # 마우스 왼쪽 버튼을 놓았을 때 crop 종료 좌표를 기록합니다.

    # 버튼 생성
    create_button(user_frame, "icon//icon_load.png", 90, load_image, 1000, 0)
    create_button(user_frame, "icon//icon_save.png", 90, save_image, 1100, 0)

    create_title(button1_frame, "Rotate", 3)
    create_line(button1_frame, 27)
    create_button(button1_frame, "icon//icon_rotate45CW.png", 90, rotate_45CW, 25, 35)
    create_button(button1_frame, "icon//icon_rotate45CCW.png", 90, rotate_45CCW, 125, 35)
    create_button(button1_frame, "icon//icon_rotate90CW.png", 90, rotate_90CW, 25, 135)
    create_button(button1_frame, "icon//icon_rotate90CCW.png", 90, rotate_90CCW, 125, 135)
    create_button(button1_frame, "icon//icon_rotateuser.png", 95, rotate_user, 225, 75)
    angle_entry = Entry(button1_frame, width=10, background="gray")
    angle_entry.place(x=233, y=180)

    create_title(button1_frame, "Adjust Brightness", 233)
    create_line(button1_frame, 257)
    create_button(button1_frame, "icon//icon_brightness.png", 90, increase_brightness, 25, 265)
    create_button(button1_frame, "icon//icon_darkness.png", 90, decrease_brightness, 125, 265)

    create_title(button1_frame, "Blur", 363)
    create_line(button1_frame, 387)
    create_button(button1_frame, "icon//icon_blur.png", 90, gaus_blur, 25, 395)
    create_button(button1_frame, "icon//icon_blur.png", 90, selected_blur, 125, 395)
    create_button(button1_frame, "icon//icon_blur.png", 90, Non_Selected_Blur, 225, 395)

    create_title(button1_frame, "Etc.", 493)
    create_line(button1_frame, 517)
    create_button(button1_frame, "icon//icon_removeBG.png", 90, remove_background, 25, 525)
    create_button(button1_frame, "icon//icon_convert.png", 90, path_convert, 125, 525)

    create_title(button2_frame, "Undo & Redo", 3)
    create_line(button2_frame, 27)
    btn_undo = create_button(button2_frame, "icon//icon_undo.png", 90, undo, 25, 35)
    btn_undo['state'] = DISABLED
    btn_redo = create_button(button2_frame, "icon//icon_redo.png", 90, redo, 125, 35)
    btn_redo['state'] = DISABLED

    create_title(button2_frame, "Add & Crop", 133)
    create_line(button2_frame, 157)
    create_button(button2_frame, "icon//icon_add.png", 90, undo, 25, 165)
    create_button(button2_frame, "icon//icon_crop.png", 90, image_crop, 125, 165)

    create_title(button2_frame, "Filter", 263)
    create_line(button2_frame, 287)
    create_button(button2_frame, "icon//icon_grayscale.png", 250, grayscale, 25, 295)
    create_button(button2_frame, "icon//icon_cannydege.png", 250, canny_edge, 25, 375)

    create_title(button2_frame, "Color Palette", 400)
    create_line(button2_frame, 424)
    create_button(button2_frame, "icon//icon_red.png", 40, red_filter, 25, 435)
    create_button(button2_frame, "icon//icon_orange.png", 40, orange_filter, 75, 435)
    create_button(button2_frame, "icon//icon_yellow.png", 40, yellow_filter, 125, 435)
    create_button(button2_frame, "icon//icon_green.png", 40, green_filter, 175, 435)
    create_button(button2_frame, "icon//icon_blue.png", 40, blue_filter, 225, 435)
    create_button(button2_frame, "icon//icon_purple.png", 40, purple_filter, 275, 435)

    create_title(button2_frame, "TempSave", 553)
    create_line(button2_frame, 577)
    canvas_temp = tk.Canvas(button2_frame, width=100, height=100, bg="white", borderwidth=1, relief="solid")
    canvas_temp.place(x=25, y=585)
    create_button(button2_frame, "icon//icon_save.png", 80, temp_save, 140, 585)
    create_button(button2_frame, "icon//icon_load.png", 80, temp_load, 230, 585)

    font_time = tkinter.font.Font(family="맑은 고딕", size=12)
    temp_time = tk.Label(button2_frame, text="", background="white", font=font_time)
    temp_time.place(x=145, y=630)

    # 윈도우 종료 시 on_closing 함수 실행
    win_main.protocol("WM_DELETE_WINDOW", on_closing)

    # 윈도우 실행
    win_main.mainloop()

    # 소켓 종료
    client_socket.close()


if __name__ == "__main__":
    photoeditormain()