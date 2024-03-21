"""
image/gif filtering viewer tool
p.s. needs convolve_ops.py as a dependency
"""
from tkinter import Tk, Canvas, NW, Spinbox, StringVar, IntVar, Button, Label, Scale
from PIL import Image, ImageTk, ImageSequence
from os import fsencode, listdir, fsdecode
from tkinter.font import Font, families
from tkinter.ttk import Combobox, Progressbar
from numpy import array, clip, uint8
from math import cos, sin, log
from threading import Thread
from random import uniform
from time import perf_counter
import convolve_ops

color_matrix = {
    'none': lambda _: (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0),
    'rotation': lambda val: (cos(val), -sin(val), 0, 0, sin(val), cos(val), 0, 0, 0, 0, 1, 0),
    'factor': lambda val: (val/25+1, 0, 0, 0, 0, val/25+1, 0, 0, 0, 0, val/25+1, 0),
    'log': lambda val: (log(abs(val)) % 1, 0, 0, 0, 0, log(abs(val)) % 1, 0, 0, 0, 0, log(abs(val)) % 1, 0),
    'sine': lambda val: (sin(val), 0, 0, 0, 0, sin(val), 0, 0, 0, 0, sin(val), 0),
    'cie_xyz': lambda val: (0.412453, 0.357580, 0.180423, val, 0.212671, 0.715160,
                          0.072169, val, 0.019334, 0.119193, 0.950227, val),
    'cmyk': lambda val: (0.4124, 0.3576, 0.1805, val, 0.2126, 0.7152, 0.0722, val, 0.0193, 0.1192, 0.9505, val),
    'lab': lambda val: (0.4124, 0.3576, 0.1805, val, 0.2126, 0.7152, 0.0722, val, 0.0193, 0.1192, 0.9505, val),
    'yuv': lambda val: (0.299, 0.587, 0.114, val, -0.14713, -0.28886, 0.436, val, 0.615, -0.51499, -0.10001, val),
    'gray': lambda val: (0.299, 0.587, 0.114, val, 0.299, 0.587, 0.114, val, 0.299, 0.587, 0.114, val),
    'sepia': lambda val: (0.393, 0.769, 0.189, val, 0.349, 0.686, 0.168, val, 0.272, 0.534, 0.131, val),
    'tint_c_r': lambda val: (1, 0, 0, val, 0, 1, 0, -val, 0, 0, 1, -val),
    'tint_m_g': lambda val: (1, 0, 0, -val, 0, 1, 0, val, 0, 0, 1, -val),
    'tint_y_b': lambda val: (1, 0, 0, -val, 0, 1, 0, -val, 0, 0, 1, val),
    'intensity': lambda val: (1, 0, 0, val*1.2, 0, 1, 0, val*1.2, 0, 0, 1, val*1.2),
    'color_balance': lambda val: (1.5, 0, 0, val, 0, 1, 0, val, 0, 0, 0.8, val),
    'true_color': lambda val: (1.87, -0.79, -0.08, val, -0.20, 1.64, -0.44, val, 0.03, -0.55, 1.52, val),
    'random': lambda val: (uniform(0.5, 0.8)+1/val, 0, 0, 0, 0, uniform(0.5, 0.6)+1/val, 0, 0,
                           0, 0, uniform(0.2, 0.6)+1/val, 0),
    'bluish': lambda val: (-1, -2, -1, val, 1, 0, 0, val, 1, 0, 1, val),
    'hellish': lambda val: (1, 0, 0, val, 0, 1, -1, val, 0, -1, 1, val),
    'hellish2': lambda val: (-1.8, 1, 0.8, val, -1, 0, 0, val, 0, -1, 1, val),
    'hellish3': lambda val: (0.3, -0.3, 0.9, val, 1.8, -1, 0, val, -1, 0, 0.4, val),
    'ghostly': lambda val: (-1, 1, 0, val, -1, 0.5, 1, val, 0, 1, 1, val),
    'evil': lambda val: (-1.8, 1, 0.8, val, -0.1, 0.3, 0, val, 0.5, -1, 1, val),
    'evil2': lambda val: (0, 3, -2, val, -1, 1, 0.2, val, -1, 1.4, -1, val),
    'scary': lambda val: (0, -1, 0, val, 1, -0.45, 0, val, -1, 2, -1, val),
    'scary2': lambda val: (0, 0, 0, val, -2, 1, 0.6, val, -1, 1.4, -1, val),
    'scary2_contrast': lambda val: (0, 0, 0, val, -1, -1, 2, val, -0.1, -0.9, 1.1, val),
    'afterdark': lambda val: (-0.9, 0, 0, val, -0.5, -0.5, 0, val, 0.2, -0.9, 1.06, val),
}

transform_matrix = {
    'blur': ((1/9, 1/9, 1/9), (1/9, 1/9, 1/9), (1/9, 1/9, 1/9)),
    'gaussian_blur': ((1/16, 1/8, 1/16), (1/8, 1/4, 1/8), (1/16, 1/8, 1/16)),
    'motion_blur': ((0, 0, 1/3), (0, 1/3, 0), (1/3, 0, 0)),
    'negative': ((0, 0, 0), (0, -1, 0), (0, 0, 0)),
    'sobel_edge_detect_H': ((-1, 0, 1), (-2, 0, 2), (-1, 0, 1)),
    'sobel_edge_detect_V': ((-1, -2, -1), (0, 0, 0), (1, 2, 1)),
    'prewitt_edge_detect_H': ((-1, -1, -1), (0, 0, 0), (1, 1, 1)),
    'prewitt_edge_detect_V': ((-1, 0, 1), (-1, 0, 1), (-1, 0, 1)),
    'scharr_edge_detect_H': ((-3, 0, 3), (-10, 0, 10), (-3, 0, 3)),
    'scharr_edge_detect_V': ((-3, -10, -3), (0, 0, 0), (3, 10, 3)),
    'high_pass': ((-1, -1, -1), (-1,  8, -1), (-1, -1, -1)),
    'band_pass': ((0, -1,  0), (-1,  4, -1), (0, -1,  0)),
    'laplacian': ((0, 1, 0), (1, -4, 1), (0, 1, 0)),
    'emboss': ((-2, -1, 0), (-1,  1, 1), (0,  1, 2)),
    'sharpen': ((0, -1,  0), (-1,  5, -1), (0, -1,  0)),
}

def animate2(n):
    if FILTER_WORKER_STATUS:
        if n < len(frames2):
            global frame_id2, filter_timer2
            canvas.delete('fltrimg')
            canvas.create_image(0, 0, image=frames2[n], anchor=NW, tags='fltrimg')
            canvas.create_image(frames2[n].width(), 0, image=frames2[n], anchor=NW, tags='fltrimg')
            canvas.create_image(frames2[n].width()*2, 0, image=frames2[n], anchor=NW, tags='fltrimg')
            canvas.create_image(0, frames2[n].height(), image=frames2[n], anchor=NW, tags='fltrimg')
            canvas.create_image(frames2[n].width(), frames2[n].height(), image=frames2[n], anchor=NW, tags='fltrimg')
            canvas.create_image(frames2[n].width()*2, frames2[n].height(), image=frames2[n], anchor=NW, tags='fltrimg')
            n = n + 1 if n != len(frames2) - 1 else 0
            filter_timer2 = root.after(2, animate2, n)

def animate(n):
    if FILTER_WORKER_STATUS:
        if n < len(frames):
            global frame_id, filter_timer, CURR_FRAME
            canvas.delete(frame_id)
            frame_id = canvas.create_image(0, 0, image=frames[n], anchor=NW)
            CURR_FRAME = n + 1 if n != len(frames) - 1 else 0
            filter_timer = root.after(gif.info['duration'], animate, CURR_FRAME)

def toggle_filter():
    global filter_timer2
    print(THREAD_REF)
    if not filter_timer2:
        animate2(0)
    else:
        root.after_cancel(filter_timer2)
        canvas.delete('fltrimg')
        filter_timer2 = None

def toggle_play_gif():
    global filter_timer, CURR_FRAME
    if not filter_timer:
        animate(CURR_FRAME)
    else:
        root.after_cancel(filter_timer)
        filter_timer = None

def toggle_scale(_):
    if norm_method.get() in ['clip', 'modulo']:
        canvas.itemconfigure('threshold', state="hidden")
    else:
        canvas.itemconfigure('threshold', state="normal")

def apply_color_matrix(_):
    global theta, THREAD_REF
    theta = 0
    if THREAD_REF:
        for thid, thd in enumerate(THREAD_REF):
            thd.join()
            THREAD_REF.pop(thid)
    color_matrix_process(_)

def savegif():
    if saveframes:
        saveframes[0].save("filtered.gif", save_all=True, append_images=saveframes[1:],
                       optimize=False, duration=gif.info['duration'], disposal=0, loop=0)
    else:
        scaled_img.save("filtered.png", save_all=True, optimize=False)
    print('saved')

def color_matrix_process(cmd):
    global x, y, theta, img, scaled_img, newtkimg, frames, pilframes, saveframes, EFFECT_ACTIVE
    if cmd == "up":
        theta += 1
    elif cmd == "down":
        theta -= 1
    else:
        pass
    print(f'\r{theta} {curr_color_matrix.get()}')
    if f_path[-3:] == 'gif':
        if curr_color_matrix.get() == 'none':
            EFFECT_ACTIVE = False
            saveframes[:] = [frm.resize((x, y)) for frm in pilframes]
        elif EFFECT_ACTIVE:
            saveframes = [frm.resize((x, y)).convert(mode='RGB', matrix=color_matrix[curr_color_matrix.get()](theta))
                               for frm in saveframes]
        elif not EFFECT_ACTIVE:
            saveframes[:] = [frm.resize((x, y)).convert(mode='RGB', matrix=color_matrix[curr_color_matrix.get()](theta))
                             for frm in pilframes]
        frames[:] = [ImageTk.PhotoImage(frm2) for frm2 in saveframes]
    else:
        canvas.delete("mainimg")
        if curr_color_matrix.get() == 'none':
            EFFECT_ACTIVE = False
            scaled_img = img.resize((x, y)).convert(mode='RGB')
        elif EFFECT_ACTIVE:
            scaled_img = scaled_img.resize((x, y)).convert(mode='RGB', matrix=color_matrix[curr_color_matrix.get()](theta))
        elif not EFFECT_ACTIVE:
            scaled_img = img.resize((x, y)).convert(mode='RGB', matrix=color_matrix[curr_color_matrix.get()](theta))
        newtkimg = ImageTk.PhotoImage(scaled_img)
        canvas.create_image(0, 0, image=newtkimg, anchor=NW, tags='mainimg')

def transform_matrix_process(process_frames):
    global scaled_img, saveframes, frames, newtkimg, EFFECT_ACTIVE
    strt = perf_counter()
    EFFECT_ACTIVE = True
    canvas.delete("mainimg")
    for frame in process_frames:
        imgarr = array(frame)
        imgchannels = [imgarr[:, :, 0], imgarr[:, :, 1], imgarr[:, :, 2]]
        dimx, dimy = imgchannels[0].shape[0], imgchannels[0].shape[1]
        kernel = array(transform_matrix[curr_transform_matrix.get()])
        ret = convolve_ops.channel_op(dimx * dimy + 2 * (dimx + dimy) + 4, imgchannels, kernel).astype(int)
        match norm_method.get():
            case 'clip':
                norm_ret = clip(ret, 0, 255)
            case 'modulo':
                norm_ret = ret % 255
            case 'threshold':
                norm_ret = ret.copy()
                norm_ret[ret <= norm_thresh.get()] = 0
                norm_ret[ret > norm_thresh.get()] = 255
        if f_path[-3:] == 'gif':
            saveframes.append(Image.fromarray(uint8(norm_ret)))
            frames.append(ImageTk.PhotoImage(saveframes[-1]))
        else:
            scaled_img = Image.fromarray(uint8(norm_ret))
            newtkimg = ImageTk.PhotoImage(scaled_img)
            canvas.create_image(0, 0, image=newtkimg, anchor=NW, tags='mainimg')
        stp = perf_counter()
        print(f'{(stp - strt) * 1000}ms')
    progress_bar.stop()
    print(f'\r{curr_transform_matrix.get()}')
    canvas.itemconfigure('progress', state="hidden")
    for wid in [btn1, btn2, menu1, menu2, menu3, scale1, spinner1]:
        if wid in [menu1, menu2, menu3]:
            wid.configure(state='readonly')
        else:
            wid.configure(state='normal')
    if f_path[-3:] == 'gif':
        btn3.configure(state='normal')

def apply_transform_matrix(_):
    global THREAD_REF, scaled_img, pilframes, saveframes
    for wid in [btn1, btn2, menu1, menu2, menu3, scale1, spinner1]:
        wid.configure(state='disabled')
    if f_path[-3:] == 'gif':
        btn3.configure(state='disabled')
        process_frames = [frame for frame in pilframes]
        saveframes[:], frames[:] = [], []
    else:
        process_frames = [scaled_img]
    progress_bar.configure(maximum=100*len(process_frames))
    th1 = Thread(target=transform_matrix_process, args=(process_frames,))
    canvas.itemconfigure('progress', state="normal")
    progress_bar.start(44)
    THREAD_REF.append(th1)
    th1.start()

if __name__ == '__main__':
    FILTER_WORKER_STATUS = True
    LAST_TRANSFORM = None
    EFFECT_ACTIVE = False
    FRAME_COUNT = 1
    CURR_FRAME = 0
    THREAD_REF = []
    theta = 1
    filter_worker2 = None
    filter_timer = None
    filter_timer2 = None
    frame_id = None
    frame_id2 = None
    root = Tk()
    filtframes, pilframes, saveframes, frames = [], [], [], []
    root.title("ImAdjustr")
    f_path = "C:/Users/mfarh/OneDrive/Pictures/Downloads/elizabeth2.gif"
    root.geometry('%dx%d+%d+%d' % (1200, 700, root.winfo_screenmmwidth() / 4, root.winfo_screenmmheight() / 4))
    canvas = Canvas(root, width=1200, height=700, background='black')
    if f_path[-3:] == 'gif':
        with Image.open(f_path) as gif:
            FRAME_COUNT = gif.n_frames
            if gif.size[0] > gif.size[1]:
                x, y = 1200, int(1200 / (gif.size[0] / gif.size[1]))
            else:
                y, x = 700, int(700 / (gif.size[1] / gif.size[0]))
            for f_index, frame in enumerate(ImageSequence.Iterator(gif)):
                tmpfrm = frame.resize((x, y)).convert(mode='RGB')
                pilframes.append(tmpfrm)
                frames.append(ImageTk.PhotoImage(tmpfrm))
    else:
        img = Image.open(fp=f_path)
        if img.size[0] > img.size[1]:
            x, y = 1200, int(1200 / (img.size[0] / img.size[1]))
        else:
            y, x = 700, int(700 / (img.size[1] / img.size[0]))
    print(x, y)
    directory = fsencode("C:/Users/mfarh/OneDrive/Pictures/Downloads/filter_frames/scanline1")
    for file in listdir(directory):
        filename = fsdecode(file)
        filtframes.append(Image.open(fp=f'C:/Users/mfarh/OneDrive/Pictures/Downloads/filter_frames/scanline1/{filename}')
                          .resize((x, y)))
    frames2 = [ImageTk.PhotoImage(ffrm) for ffrm in filtframes]
    if f_path[-3:] in ['png', 'jpeg', 'bmp', 'jpg']:
        scaled_img = img.resize((x, y)).convert(mode='RGB')
        tkimg = ImageTk.PhotoImage(scaled_img)
        canvas.create_image(0, 0, image=tkimg, anchor=NW, tags='mainimg')

    spinner1 = Spinbox(name="change", command=(root.register(color_matrix_process), '%d'), width=0, highlightthickness=4,
                       font=Font(family=families()[3], size=20, weight='bold'), state='readonly',
                       textvariable=StringVar(root, '\u03BA'))
    btn1 = Button(name="save", text="save", width=5, command=savegif)
    btn2 = Button(name="toggle", text="toggle filter", width=10, command=toggle_filter)
    btn3 = Button(name="play_gif", text="play/pause", width=10, command=toggle_play_gif)
    curr_color_matrix = StringVar(root, 'none')
    curr_transform_matrix = StringVar(root, 'none')
    norm_method, norm_thresh = StringVar(root, 'clip'), IntVar(root, 100)
    menu1 = Combobox(root, justify='center', height=5, textvariable=curr_color_matrix,
                     values=list(color_matrix.keys()), state='readonly')
    menu1.bind("<<ComboboxSelected>>", apply_color_matrix)
    menu1label = Label(root, text="theme :")
    menu2label = Label(root, text="effect :")
    menu3label = Label(root, text="normalize :")
    menu2 = Combobox(root, justify='center', height=5, textvariable=curr_transform_matrix,
                     values=list(transform_matrix.keys()), state='readonly')
    menu2.bind("<<ComboboxSelected>>", apply_transform_matrix)
    menu3 = Combobox(root, justify='center', height=5, textvariable=norm_method,
                     values=['clip', 'modulo', 'threshold'], state='readonly', width=10)
    menu3.bind("<<ComboboxSelected>>", toggle_scale)
    scale1 = Scale(root, from_=5, orient="horizontal", to=250, variable=norm_thresh, sliderlength=20)
    progress_bar = Progressbar(root, orient="horizontal", length=100, mode="determinate")
    canvas.create_window(spinner1.winfo_reqwidth() * 2 + 20, 10, anchor="nw", window=spinner1)
    canvas.create_window(spinner1.winfo_reqwidth() * 3 + 35, 10, anchor="nw", window=menu1label)
    canvas.create_window(spinner1.winfo_reqwidth() * 4 + 20, 10, anchor="nw", window=menu1)
    canvas.create_window(spinner1.winfo_reqwidth() * 7 + 40, 10, anchor="nw", window=menu2label)
    canvas.create_window(spinner1.winfo_reqwidth() * 8 + 30, 10, anchor="nw", window=menu2)
    canvas.create_window(spinner1.winfo_reqwidth() * 11 + 52, 10, anchor="nw", window=menu3label)
    canvas.create_window(spinner1.winfo_reqwidth() * 13 + 20, 10, anchor="nw", window=menu3)
    canvas.create_window(canvas.winfo_reqwidth()-btn1.winfo_reqwidth()*3-10, 10, anchor="nw", window=btn1)
    canvas.create_window(canvas.winfo_reqwidth()-btn1.winfo_reqwidth()*2, 10, anchor="nw", window=btn2)
    canvas.create_window(canvas.winfo_reqwidth()-btn1.winfo_reqwidth()*2, 50, anchor="nw", window=btn3,
                         state="normal" if f_path[-3:] == 'gif' else "hidden")
    canvas.create_window(spinner1.winfo_reqwidth() * 15 + 10, 10, anchor="nw", window=scale1, tags='threshold',
                         state="hidden")
    canvas.create_window(spinner1.winfo_reqwidth() * 18 + 10, 10, anchor="nw", window=progress_bar, tags='progress',
                         state="hidden")
    if f_path[-3:] == 'gif':
        animate(0)
    canvas.pack()
    root.mainloop()
