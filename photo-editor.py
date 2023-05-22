import tkinter as tk
import tkinter.font
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk
import cv2


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
        filetypes=(("PNG 파일", "*.png"), ("JPEG 파일", "*.jpg"))
    )

    if file_path:
        # 이미지 불러오기
        image_path = file_path
        image = Image.open(image_path)
        update_image(image)

        return file_path


def update_image(new_image):
    global image_tk, layer_ids, current_image, image_size

    # 이미지 리사이즈
    max_size = 600
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


def undo():
    global image_tk, layer_ids, current_image, undo_history
    if len(undo_history) >= 2:
        # 이전 작업 단계의 이미지 가져오기
        previous_image = undo_history[-2]

        # 현재 이미지 업데이트
        current_image = previous_image
        max_size = 600
        resized_image = resize_image(current_image, max_size)
        for layer_id in layer_ids:
            canvas.delete(layer_id)
        image_tk = ImageTk.PhotoImage(resized_image)
        image_layer = canvas.create_image(0, 0, anchor="nw", image=image_tk)
        layer_ids = [image_layer]
        current_image = resized_image

        # 현재 작업 단계를 undo_history에서 제거
        undo_history.pop()
# ...


def mouse_event(canvas, event):
    if event:
        x = event.x
        y = event.y
    else:
        x = canvas.winfo_pointerx() - canvas.winfo_rootx()
        y = canvas.winfo_pointery() - canvas.winfo_rooty()
    return x, y



def mouse_click(event):
    global start_x, start_y
    # 클릭된 좌표를 저장합니다.
    start_x, start_y = event.x, event.y


def check_cursor_position(event, canvas):
    if event:
        x, y = mouse_event(canvas, event)
    else:
        x, y = mouse_event(canvas, None)

    edge_left = 5
    edge_right = image_size[0] + 5
    edge_top = 5
    edge_bottom = image_size[1] + 5

    # 마우스 커서가 가장자리에 닿았는지 확인합니다.
    if edge_left < x < edge_right and edge_top < y < edge_bottom:
        canvas.config(cursor="")  # 가장자리에 닿았을 때의 커서 모양을 변경합니다.
    else:
        canvas.config(cursor="sizing")  # 가장자리를 벗어났을 때의 커서 모양을 원래대로 돌려놓습니다.


def crop_image():
    global current_image, image_tk, layer_ids, start_x, start_y, end_x, end_y
    # 이미지의 좌표 시스템은 tkinter의 캔버스와 다르므로,
    # 캔버스에서 얻은 좌표를 이미지의 좌표로 변환합니다.
    start_x = int(start_x * (current_image.width / canvas.winfo_width()))
    start_y = int(start_y * (current_image.height / canvas.winfo_height()))
    end_x = int(end_x * (current_image.width / canvas.winfo_width()))
    end_y = int(end_y * (current_image.height / canvas.winfo_height()))

    # 좌표 순서가 올바르지 않으면 교환합니다.
    if end_x < start_x:
        start_x, end_x = end_x, start_x
    if end_y < start_y:
        start_y, end_y = end_y, start_y

    # 이미지를 자르고, 새로운 이미지로 업데이트합니다.
    current_image = current_image.crop((start_x, start_y, end_x, end_y))
    max_size = 600
    resized_image = resize_image(current_image, max_size)

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
    check_cursor_position(None)
    mouse_event(None)


def mouse_release(event):
    global start_x, start_y, end_x, end_y
    if event:
        end_x, end_y = event.x, event.y
    else:
        x, y = mouse_event(None)
        event = tk.Event()
        event.x = x
        event.y = y

    # 이미지를 자릅니다.
    if start_x is not None and start_y is not None and end_x is not None and end_y is not None:
        crop_image()
        check_cursor_position(event, canvas)  # crop_image() 실행 후에 check_cursor_position() 함수 호출


def rotate_CCW():
    global image_tk, layer_ids, current_image
    # 현재 이미지 가져오기
    image = current_image

    # 이미지 회전
    angle = 90
    rotated_image = image.rotate(angle)
    update_image(rotated_image)


def rotate_CW():
    global image_tk, layer_ids, current_image
    # 현재 이미지 가져오기
    image = current_image

    # 이미지 회전
    angle = -90
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



# tkinter 윈도우 생성
win_main = tk.Tk()
win_main.title("Photo Editor")
win_main.geometry("1200x700")  # 윈도우 크기 수정

image_path = None
image_tk = None
image_size = (0, 0)
layer_ids = []
current_image = None
undo_history = []
start_x, start_y = None, None
convert = 0

# 좌측 프레임: 이미지 표시
image_frame = tk.Frame(win_main, width=600, height=600)
image_frame.pack(side="left")

# 우측 프레임: 버튼
button_frame = tk.Frame(win_main, width=600, height=600)
button_frame.pack(side="left")

# 이미지 캔버스 생성
canvas = tk.Canvas(image_frame, width=600, height=600, bg="white")
canvas.pack(side="left", padx=10, pady=10)

# 마우스 이벤트를 바인드
canvas.bind("<Motion>", lambda event: check_cursor_position(event, canvas))
canvas.bind("<Button-1>", mouse_click)
canvas.bind("<ButtonRelease-1>", mouse_release)


# 버튼 생성
font = tkinter.font.Font(family="맑은 고딕", size=15, weight="bold")

load_frame = tk.Frame(button_frame)
icon_load = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_load.png"), 80))
load_button = tk.Button(load_frame, image=icon_load, command=load_image)
load_button.grid(row=0, column=0)
load_label = tk.Label(load_frame, text="File Load", font=font)
load_label.grid(row=1, column=0)
load_frame.grid(row=0, column=0)

save_frame = tk.Frame(button_frame)
icon_save = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_save.png"), 80))
save_button = tk.Button(save_frame, image=icon_save, command=save_image)
save_button.grid(row=0, column=0)
save_label = tk.Label(save_frame, text="File Save", font=font)
save_label.grid(row=1, column=0)
save_frame.grid(row=0, column=1)

CW_frame = tk.Frame(button_frame)
icon_CW = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_rotateCW.png"), 80))
rotate_CW_button = tk.Button(CW_frame, image=icon_CW, command=rotate_CW)
rotate_CW_button.grid(row=0, column=0)
CW_label = tk.Label(CW_frame, text="Rotate CW", font=font)
CW_label.grid(row=1, column=0)
CW_frame.grid(row=1, column=0)

CCW_frame = tk.Frame(button_frame)
icon_CCW = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_rotateCCW.png"), 80))
rotate_CCW_button = tk.Button(CCW_frame, image=icon_CCW, command=rotate_CCW)
rotate_CCW_button.grid(row=0, column=0)
CCW_label = tk.Label(CCW_frame, text="Rotate CCW", font=font)
CCW_label.grid(row=1, column=0)
CCW_frame.grid(row=1, column=1)

dark_frame = tk.Frame(button_frame)
icon_brightness = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_brightness.png"), 80))
dark_button = tk.Button(dark_frame, image=icon_brightness, command=decrease_brightness)
dark_button.grid(row=0, column=0)
dark_label = tk.Label(dark_frame, text="Darkness", font=font)
dark_label.grid(row=1, column=0)
dark_frame.grid(row=2, column=0)

bright_frame = tk.Frame(button_frame)
bright_button = tk.Button(bright_frame, image=icon_brightness, command=increase_brightness)
bright_button.grid(row=0, column=0)
bright_label = tk.Label(bright_frame, text="Brightness", font=font)
bright_label.grid(row=1, column=0)
bright_frame.grid(row=2, column=1)

cut_frame = tk.Frame(button_frame)
icon_cut = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_cut.png"), 80))
cut_button = tk.Button(cut_frame, image=icon_cut, command=lambda: mouse_release(None))
cut_button.grid(row=0, column=0)
cut_label = tk.Label(cut_frame, text="Cut", font=font)
cut_label.grid(row=1, column=0)
cut_frame.grid(row=3, column=0)

undo_frame = tk.Frame(button_frame)
icon_undo = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_undo.png"), 80))
undo_button = tk.Button(undo_frame, image=icon_undo, command=undo)
undo_button.grid(row=0, column=0)
undo_label = tk.Label(undo_frame, text="Undo", font=font)
undo_label.grid(row=1, column=0)
undo_frame.grid(row=3, column=1)

add_frame = tk.Frame(button_frame)
icon_add = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_add.png"), 80))
add_button = tk.Button(add_frame, image=icon_add, command=undo)
add_button.grid(row=0, column=0)
add_label = tk.Label(add_frame, text="add", font=font)
add_label.grid(row=1, column=0)
add_frame.grid(row=0, column=2)

bg_remove_frame = tk.Frame(button_frame)
icon_bg_remove = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_bg_remove.png"), 80))
bg_remove_button = tk.Button(bg_remove_frame, image=icon_bg_remove, command=undo)
bg_remove_button.grid(row=0, column=0)
bg_remove_label = tk.Label(bg_remove_frame, text="bg_remove", font=font)
bg_remove_label.grid(row=1, column=0)
bg_remove_frame.grid(row=1, column=2)

blur_frame = tk.Frame(button_frame)
icon_blur = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_blur.png"), 80))
blur_button = tk.Button(blur_frame, image=icon_blur, command=undo)
blur_button.grid(row=0, column=0)
blur_label = tk.Label(blur_frame, text="blur", font=font)
blur_label.grid(row=1, column=0)
blur_frame.grid(row=2, column=2)

convert_frame = tk.Frame(button_frame)
icon_convert = ImageTk.PhotoImage(resize_image(Image.open("icon//icon_convert.png"), 80))
convert_button = tk.Button(convert_frame, image=icon_convert, command=path_convert)
convert_button.grid(row=0, column=0)
convert_label = tk.Label(convert_frame, text="convert", font=font)
convert_label.grid(row=1, column=0)
convert_frame.grid(row=3, column=2)

# 윈도우 실행
win_main.mainloop()
