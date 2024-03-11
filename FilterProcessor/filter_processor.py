"""
adding filter to window specified in frames array
also cool af terminal screen filter effect
"""
import tkinter as tk
from os import path
from PIL import Image, ImageTk, ImageSequence
from random import randrange
from threading import Thread
# from ctypes import windll

# def place_image_on_top():
#     image_label = tk.Label(root, image=image, borderwidth=0)
#     image_label.image = image  # Keep a reference to the image to prevent garbage collection
#     image_label.place(x=0, y=0)  # Adjust the coordinates as needed
#     set_opacity(image_label, 0.3)
#     canvas.create_image(200, 200, image=image)

# def set_opacity(widget, value: float):  # this was for making tkinter widget transparent
#     widget = widget.winfo_id()
#     value = int(255*value)      # value from 0 to 1
#     wnd_exstyle = windll.user32.GetWindowLongA(widget, -20)
#     new_exstyle = wnd_exstyle | 0x00080000
#     windll.user32.SetWindowLongA(widget, -20, new_exstyle)
#     windll.user32.SetLayeredWindowAttributes(widget, 0, value, 2)

def on_close():
    global FILTER_WORKER_STATUS, filter_worker, filter_worker2
    FILTER_WORKER_STATUS = False
    filter_worker.join()
    filter_worker2.join()
    root.destroy()

def image_process(index, img, pixels):
    img2 = Image.new("RGBA", img.size)
    pixels_new = img2.load()
    if index == -1:
        print('Processing')
    elif index % 5 == 0:
        print(f" processing frame {index}-{index+5}")
    else:
        print('.', end='', flush=True)
    for i in range(img.size[0]):
        if i % 250 == 0:
            print('.', end='', flush=True)
        for j in range(img.size[1]):
            # gray = sum(pixels[i, j][:-1])//3
            gray = int(0.2126 * pixels[i, j][0] +
                       0.7152 * pixels[i, j][1] +
                       0.0722 * pixels[i, j][2])
            pixels_new[i, j] = (
                randrange(140, 190) if gray < 57 else 0,
                228 if gray < 57 else 0,
                108 if gray < 57 else 0,
                # pixels[i, j][3] + randrange(-20, -5) if pixels[i, j][3] > 30 else 0
            )
    tkimg = ImageTk.PhotoImage(img2)
    return tkimg

def animate(n):
    if FILTER_WORKER_STATUS:
        if (n < len(frames)):
            global frame_id
            canvas.delete(frame_id)
            frame_id = canvas.create_image(0, 0, image=frames[n], anchor=tk.NW)
            n = n+1 if n != len(frames)-1 else 0
            root.after(FRAME_DELAY, animate, n)

def animate2(n):
    if FILTER_WORKER_STATUS:
        if (n < len(frames2)):
            global frame_id2
            canvas.delete(frame_id2)
            frame_id2 = canvas.create_image(0, 0, image=frames2[n], anchor=tk.NW)
            n = n+1 if n != len(frames2)-1 else 0
            root.after(FRAME_DELAY2, animate2, n)

def gif_setup(file_path):
    pilframes = []
    with Image.open(file_path) as gif:
        for frame in ImageSequence.Iterator(gif):
            print('.', end='', flush=True)
            pilframe = frame.copy()
            pilframes.append(pilframe.resize((int(pilframe.size[0] / (pilframe.size[0] / 1180)),
                                              int(pilframe.size[1] / (pilframe.size[1] / 680)))).convert('RGB'))
    framemaps = [pf.load() for pf in pilframes]
    print('.', end='', flush=True)
    print(' frames loaded')
    return pilframes, framemaps

FRAME_DELAY = None
FRAME_DELAY2 = None
FILTER_WORKER_STATUS = True
frames = []
frames2 = []
frame_id = None
frame_id2 = None
root = tk.Tk()
root.title("Image on Top")
root.geometry('%dx%d+%d+%d' % (1200, 700, root.winfo_screenmmwidth()/4, root.winfo_screenmmheight()/4))
# root.resizable(False, False)
# root.attributes('-alpha', 0.4)
# root.attributes('-transparent', 'white')
canvas = tk.Canvas(root, width=1200, height=700, background='black')
# btn2 = tk.Button(text='Button', height=4, width=4)
# button = tk.Button(text="Image on Top")
# rectangle3 = canvas.create_rectangle(150, 150, 220, 220, fill="#A7E46C")

frames2[:] = [tk.PhotoImage(file='scanline_f1.png').zoom(3, 3),
               tk.PhotoImage(file='scanline_f2.png').zoom(3, 3)]
f_path = input("Enter path to image or gif:\t")
while not path.exists(f_path):
    print('error: file not found')
    print('       remove quotes "" from start and end of path if present')
    f_path = input("Enter path to image or gif:\t")
# user_ch = input("Type pic for image filter or gif for gif filter-------\n")
# while user_ch not in ['pic', 'img', 'gif', 'PIC', 'IMG', 'GIF', 'Pic', 'Img', 'Gif']:
#     user_ch = input("Type pic for image filter or gif for gif filter-------\n")
# if user_ch in ['pic', 'img', 'Pic', 'Img', 'PIC', 'IMG']:
if f_path[-3:] in ['png', 'jpg', 'jpeg', 'jpe']:
    FRAME_DELAY2 = 30
    img = Image.open(f_path)
    print(img.size)
    # scaled_img = img.resize((int(img.size[0] * 1.2), int(img.size[1] * 1.2)))
    scaled_img = img.resize((int(img.size[0] / (img.size[0] / 1180)), int(img.size[1] / (img.size[1] / 680))))
    pixelMap = scaled_img.load()
    newimg = image_process(-1, scaled_img, pixelMap)
    canvas.create_image((600, 350), image=newimg)
    print(' Done')
    animate2(0)
# elif user_ch in ['gif', 'Gif', 'GIF']:
elif f_path[-3:] == 'gif':
    FRAME_DELAY = 72
    FRAME_DELAY2 = 3
    # frames = [tk.PhotoImage(file='C:/Users/mfarh/OneDrive/Pictures/Downloads/crysis3_1.gif', # old method, less efficient
    #                         format="gif -index %i" % i).zoom(2, 2) for i in range(FRAMES)]
    pfrms, fmps = gif_setup(f_path)
    print('\napplying filter')
    frames[:] = [image_process(i, frm, mp) for i, (frm, mp) in enumerate(zip(pfrms, fmps))]
    print(' Done')
    filter_worker = Thread(target=animate, args=(0,))
    filter_worker2 = Thread(target=animate2, args=(0,))
    filter_worker.start()
    filter_worker2.start()
    root.protocol("WM_DELETE_WINDOW", on_close)
else:
    pass

# canvas.create_window(60, 60, anchor='nw', window=btn2)
# canvas.create_window(300, 300, anchor='nw', window=button)
canvas.pack()
root.mainloop()
