import tkinter as tk
import tkinter.font
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk
import cv2


def resize_image(image, max_size):
    width, height = image.size
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
    global image_path, image_tk, layer_ids, current_image
    # 이미지 파일 선택 대화상자 열기
    file_path = filedialog.askopenfilename(
        title="이미지 파일 선택",
        filetypes=(("PNG 파일", "*.png"), ("JPEG 파일", "*.jpg"))
    )

    if file_path:
        # 이미지 불러오기
        image_path = file_path
        image = Image.open(image_path)

        # 이미지 리사이즈
        max_size = 600
        resized_image = resize_image(image, max_size)

        # 기존 레이어 삭제
        if layer_ids:
            for layer_id in layer_ids:
                canvas.delete("all")

        # 캔버스에 이미지 표시
        image_tk = ImageTk.PhotoImage(resized_image)
        image_layer = canvas.create_image(0, 0, anchor="nw", image=image_tk)

        # 레이어 ID 저장
        layer_ids = [image_layer]

        # 현재 이미지 업데이트
        current_image = resized_image

        return file_path


def rotate_CCW():
    global image_tk, layer_ids, current_image
    # 현재 이미지 가져오기
    image = current_image

    # 이미지 회전
    angle = 90
    rotated_image = image.rotate(angle)

    # 이미지 리사이즈
    max_size = 600
    resized_image = resize_image(rotated_image, max_size)

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


def rotate_CW():
    global image_tk, layer_ids, current_image
    # 현재 이미지 가져오기
    image = current_image

    # 이미지 회전
    angle = -90
    rotated_image = image.rotate(angle)

    # 이미지 리사이즈
    max_size = 600
    resized_image = resize_image(rotated_image, max_size)

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


def decrease_brightness():
    global image_tk, layer_ids, current_image
    # 현재 이미지 가져오기
    image = np.array(current_image)

    # 밝기 조정
    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    image[:, :, 2] -= 5
    image[:, :, 2] = np.clip(image[:, :, 2], 1, 255)  # v값 255 이상일 경우 최대값인 255로 고정
    image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
    if np.all(image[:, :, 2] <= 1):
        dark_button.configure(state='disabled')

    # 이미지 리사이즈
    max_size = 600
    resized_image = resize_image(Image.fromarray(image), max_size)

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


def increase_brightness():
    global image_tk, layer_ids, current_image
    # 현재 이미지 가져오기
    image = np.array(current_image)

    # 밝기 조정
    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    image[:, :, 2] += 5
    image[:, :, 2] = np.clip(image[:, :, 2], 1, 255)  # v값 255 이상일 경우 최대값인 255로 고정
    image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
    if np.all(image[:, :, 2] >= 255):
        bright_button.configure(state='disabled')

    # 이미지 리사이즈
    max_size = 600
    resized_image = resize_image(Image.fromarray(image), max_size)

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


def save_image():
    global current_image, image_path

    # 파일 형식 얻기
    file_format = image_path.split('.')[-1].lower()

    # 파일 저장 경로 및 이름 설정
    save_path = filedialog.asksaveasfilename(defaultextension=f'.{file_format}')
    if not save_path:
        return
    # 이미지 저장
    current_image.save(save_path)


# tkinter 윈도우 생성
win = tk.Tk()
win.title("Photo Editor")
win.geometry("1200x600")  # 윈도우 크기 수정

image_path = None
image_tk = None
layer_ids = []
current_image = None

# 좌측 프레임: 이미지 표시
image_frame = tk.Frame(win, width=600, height=600)
image_frame.pack(side="left")

# 우측 프레임: 버튼
button_frame = tk.Frame(win, width=600, height=600)
button_frame.pack(side="left")

# 이미지 캔버스 생성
canvas = tk.Canvas(image_frame, width=600, height=600, bg="white")
canvas.pack(side="left", padx=10, pady=10)

# 버튼 생성
font = tkinter.font.Font(family="맑은 고딕", size=15, weight="bold")

load_frame = tk.Frame(button_frame)
icon_load = ImageTk.PhotoImage(resize_image(Image.open("icon\\icon_load.png"), 80))
load_button = tk.Button(load_frame, image=icon_load, command=load_image)
load_button.grid(row=0, column=0)
load_label = tk.Label(load_frame, text="File Load", font=font)
load_label.grid(row=1, column=0)
load_frame.grid(row=0, column=0)

save_frame = tk.Frame(button_frame)
icon_save = ImageTk.PhotoImage(resize_image(Image.open("icon\\icon_save.png"), 80))
save_button = tk.Button(save_frame, image=icon_save, command=save_image)
save_button.grid(row=0, column=0)
save_label = tk.Label(save_frame, text="File Save", font=font)
save_label.grid(row=1, column=0)
save_frame.grid(row=0, column=1)

CW_frame = tk.Frame(button_frame)
icon_CW = ImageTk.PhotoImage(resize_image(Image.open("icon\\icon_rotateCW.png"), 80))
rotate_CW_button = tk.Button(CW_frame, image=icon_CW, command=rotate_CW)
rotate_CW_button.grid(row=0, column=0)
CW_label = tk.Label(CW_frame, text="Rotate CW", font=font)
CW_label.grid(row=1, column=0)
CW_frame.grid(row=1, column=0)

CCW_frame = tk.Frame(button_frame)
icon_CCW = ImageTk.PhotoImage(resize_image(Image.open("icon\\icon_rotateCCW.png"), 80))
rotate_CCW_button = tk.Button(CCW_frame, image=icon_CCW, command=rotate_CCW)
rotate_CCW_button.grid(row=0, column=0)
CCW_label = tk.Label(CCW_frame, text="Rotate CCW", font=font)
CCW_label.grid(row=1, column=0)
CCW_frame.grid(row=1, column=1)

dark_frame = tk.Frame(button_frame)
icon_brightness = ImageTk.PhotoImage(resize_image(Image.open("icon\\icon_brightness.png"), 80))
dark_button = tk.Button(dark_frame, image=icon_brightness, command=decrease_brightness)
dark_button.grid(row=0, column=0)
dark_label = tk.Label(dark_frame, text="Brightness", font=font)
dark_label.grid(row=1, column=0)
dark_frame.grid(row=2, column=0)

bright_frame = tk.Frame(button_frame)
bright_button = tk.Button(bright_frame, image=icon_brightness, command=increase_brightness)
bright_button.grid(row=0, column=0)
bright_label = tk.Label(bright_frame, text="Brightness", font=font)
bright_label.grid(row=1, column=0)
bright_frame.grid(row=2, column=1)

# 윈도우 실행
win.mainloop()
