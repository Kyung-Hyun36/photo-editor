import tkinter as tk
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk
import cv2


def load_image():
    global canvas, image_path, image_tk, image_layers, layer_ids, current_image
    # 이미지 파일 선택 대화상자 열기
    file_path = filedialog.askopenfilename(
        title="이미지 파일 선택",
        filetypes=(("JPEG 파일", "*.jpg"), ("PNG 파일", "*.png"))
    )

    if file_path:
        # 이미지 불러오기
        image_path = file_path
        image = Image.open(image_path)

        # 이미지 리사이즈
        max_size = 800
        resized_image = resize_image(image, max_size)

        # 기존 레이어 삭제
        if layer_ids:
            for layer_id in layer_ids:
                canvas.delete("all")

        # 이미지를 표시할 캔버스 생성
        canvas = tk.Canvas(image_frame, width=800, height=800, bg="white")
        canvas.config(width=800, height=800)
        canvas.pack(side="left", padx=10, pady=10)

        # 이미지를 캔버스에 표시
        image_tk = ImageTk.PhotoImage(resized_image)
        image_layer = canvas.create_image(0, 0, anchor="nw", image=image_tk)

        # 레이어 ID 저장
        layer_ids = [image_layer]

        # 현재 이미지 업데이트
        current_image = resized_image

        return file_path


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


def rotate_CCW():
    global image_tk, layer_ids, current_image
    # 현재 이미지 가져오기
    image = current_image

    # 이미지 회전
    angle = 90
    rotated_image = image.rotate(angle)

    # 이미지 리사이즈
    max_size = 800
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
    max_size = 800
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
    max_size = 800
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
    max_size = 800
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
win.geometry("1200x800")  # 윈도우 크기 수정

image_path = None
image_tk = None
layer_ids = []
current_image = None

# 좌측 프레임: 이미지 표시
image_frame = tk.Frame(win, width=500, height=500)
image_frame.pack(side="left")

# 우측 프레임: 버튼
button_frame = tk.Frame(win, width=500, height=500)
button_frame.pack(side="right")

# 버튼 생성
load_button = tk.Button(button_frame, text="이미지 불러오기", command=load_image)
load_button.pack(pady=10)

rotate_CW_button = tk.Button(button_frame, text="시계방향 회전", command=rotate_CW)
rotate_CW_button.pack(pady=10)

rotate_CCW_button = tk.Button(button_frame, text="반시계방향 회전", command=rotate_CCW)
rotate_CCW_button.pack(pady=10)

dark_button = tk.Button(button_frame, text="밝기 감소", command=decrease_brightness)
dark_button.pack(pady=10)

bright_button = tk.Button(button_frame, text="밝기 증가", command=increase_brightness)
bright_button.pack(pady=10)

save_button = tk.Button(button_frame, text="이미지 저장하기", command=save_image)
save_button.pack(pady=10)

save_button2 = tk.Button(button_frame, text="이미지 저장하기", command=save_image)
save_button2.pack(pady=10)

save_button2 = tk.Button(button_frame, text="이미지 저장하기", command=save_image)
save_button2.pack(pady=10)

# 윈도우 실행
win.mainloop()
