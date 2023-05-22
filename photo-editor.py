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


def create_button(root, icon_path, icon_name, command, row, column):
    self_frame = tk.Frame(root)
    self_frame.grid(row=row, column=column)

    # 이미지 로드
    image = resize_image(Image.open(icon_path), 80)
    icon = ImageTk.PhotoImage(image)

    # 버튼 생성
    button = tk.Button(self_frame, image=icon, command=command)
    button.image = icon  # 사진에 대한 참조 유지
    button.grid(row=0, column=0)

    # 라벨 생성
    label = tk.Label(self_frame, text=icon_name, font=font)
    label.grid(row=1, column=0)


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

create_button(button_frame, "icon//icon_load.png", "File Load", load_image, 0, 0)
create_button(button_frame, "icon//icon_save.png", "File Save", save_image, 0, 1)
create_button(button_frame, "icon//icon_add.png", "Add", undo, 0, 2)
create_button(button_frame, "icon//icon_rotateCW.png", "Rotate CW", rotate_CW, 1, 0)
create_button(button_frame, "icon//icon_rotateCCW.png", "Rotate CCW", rotate_CCW, 1, 1)
create_button(button_frame, "icon//icon_removeBG.png", "BG Remove", undo, 1, 2)
create_button(button_frame, "icon//icon_brightness.png", "Darkness", decrease_brightness, 2, 0)
create_button(button_frame, "icon//icon_brightness.png", "Brightness", increase_brightness, 2, 1)
create_button(button_frame, "icon//icon_blur.png", "Blur", undo, 2, 2)
create_button(button_frame, "icon//icon_cut.png", "Cut", lambda: mouse_release(None), 3, 0)
create_button(button_frame, "icon//icon_undo.png", "Undo", undo, 3, 1)
create_button(button_frame, "icon//icon_convert.png", "Convert", path_convert, 3, 2)

# 윈도우 실행
win_main.mainloop()
