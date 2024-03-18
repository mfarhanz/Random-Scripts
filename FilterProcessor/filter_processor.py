"""
overlaying scanline pngs on green-ed frames of gif = cool af terminal screen filter effect
"""
import sys
from os import path
from psutil import Process
from threading import Thread
from math import log, ceil
from random import randrange
from traceback import format_exc
from time import perf_counter, sleep
from tkinter import Tk, Canvas, NW
from PIL import Image, ImageTk, ImageSequence
from numpy import uint8, array, zeros, zeros_like, dot

class Runner:
    def __init__(self, root):
        self.root = root
        self.canvas = None
        self.FRAME_DELAY = None
        self.FRAME_DELAY2 = None
        self.FRAME_COUNT = 1  # default if image
        self.FILTER_RGB = [15, 165, randrange(50, 100)]
        self.FILTER_WORKER_STATUS = True
        # sys.tracebacklimit = 0
        self.filter_worker = None
        self.filter_timer = None
        self.filter_worker2 = None
        self.filter_timer2 = None
        self.frames = []
        self.frames2 = []
        self.scaled_filtr_frames = None
        self.frame_id = None
        self.frame_id2 = None

    def runtk(self):
        self.canvas = Canvas(self.root, width=1200, height=700, background='black')
        orig_fltr_frames = [Image.open(fp='C:/Users/mfarh/OneDrive/Pictures/Downloads/scanline_f1.png'),
                            Image.open(fp='C:/Users/mfarh/OneDrive/Pictures/Downloads/scanline_f2.png')]
        self.scaled_filtr_frames = [fltr_frm.resize((fltr_frm.size[0] * 3, fltr_frm.size[1] * 3))
                                    .crop((0, 0, 1200, 700)) for fltr_frm in orig_fltr_frames]
        self.frames2[:] = [ImageTk.PhotoImage(pfrm2) for pfrm2 in self.scaled_filtr_frames]
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.resizable(0, 0)
        self.root.iconify()
        self.start_process()
        self.canvas.pack()
        self.root.mainloop()

    def on_close(self, f):
        # global FILTER_WORKER_STATUS, filter_worker, filter_worker2
        self.root.iconify()
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        if isinstance(f, Image.Image):
            self.root.after_cancel(self.filter_timer2)
        else:
            self.root.after_cancel(self.filter_timer)
            self.root.after_cancel(self.filter_timer2)
            self.filter_worker.join()
            self.filter_worker2.join()
        self.root.destroy()
        ch_save = input('\nSave GIF? (Y/N)\t')
        if ch_save in ['Y', 'y', 'yes', 'Yes', 'YES', '']:
            out_path = path.dirname(path.abspath(__file__))
            ch_scanline = input('Remove scanline effect? (Y/N)\t')
            if ch_scanline not in ['Y', 'y', 'yes', 'Yes', 'YES', '']:
                if isinstance(f, Image.Image):
                    print('Saving...')
                    f.save("threshed.gif", append_images=[self.scaled_filtr_frames[0], f, self.scaled_filtr_frames[1]],
                           save_all=True, optimize=False, duration=self.FRAME_DELAY2 - 2, loop=0)
                else:
                    print(f'\033[38;2;15;125;90m'.strip(), end='')
                    gif = [None for _ in range(len(f))]
                    def interlace_frames(arr, thid, thcount):
                        gifpart = []
                        for f_index, frame in enumerate(arr, start=1):
                            sys.stdout.write(f'\rApplying [{"=" * f_index}{" " * (len(arr) - f_index)}]')
                            sys.stdout.flush()
                            frame_lst = array(frame)
                            inter = zeros((*frame.size[::-1], 3))
                            scaled_filtr_lst = array(self.scaled_filtr_frames[(0, 1)[f_index % 2]]
                                                        .crop((0, 0, arr[0].size[0], arr[0].size[1])))
                            filter_alpha1 = scaled_filtr_lst[:, :, 3]
                            scaled_filtr_lst = scaled_filtr_lst[..., 0:3]
                            mask = filter_alpha1 > 160
                            inter[mask] = scaled_filtr_lst[mask]
                            inter[~mask] = frame_lst[~mask]
                            gifpart.append(Image.fromarray(uint8(inter), "RGB"))
                        if thid == thcount-1:
                            gif[(len(gif)//thcount)*thid:] = gifpart
                        else:
                            gif[(len(gif)//thcount)*thid:(len(gif)//thcount)*(thid+1)] = gifpart

                    gifparts, thlst, thcount = [], [], ceil(log(len(f)))
                    for partid in range(thcount):
                        if partid == thcount - 1:
                            gifparts.append(f[partid*(len(f)//thcount):])
                        else:
                            gifparts.append(f[partid*(len(f)//thcount): (len(f)//thcount)*(partid+1)])
                    for thid in range(thcount):
                        thlst.append(Thread(target=interlace_frames, args=(gifparts[thid], thid, thcount)))
                    for thread in thlst:
                        thread.start()
                    for thread in thlst:
                        thread.join()
                    print('\nSaving...')
                    gif[0].save("threshed.gif", save_all=True, append_images=gif[1:],
                                optimize=False, duration=self.FRAME_DELAY2, disposal=0, loop=0)
                print(f'\033[F\033[92mGIF saved at \033[38;2;70;130;180m\033]8;;{out_path}\\threshed.gif'
                      f'\033\\{out_path}\033]8;;\033\\\033[0m')
            else:
                if isinstance(f, Image.Image):
                    f.save("threshed.png", save_all=True, optimize=False)
                    print(f'\033[92mImage saved at \033[38;2;70;130;180m\033]8;;{out_path}\\threshed.png'
                          f'\033\\{out_path}\033]8;;\033\\\033[0m')
                else:
                    print('Saving...')
                    f[0].save("threshed.gif", save_all=True, append_images=f[1:],
                                optimize=False, duration=self.FRAME_DELAY2, disposal=0, loop=0)
                    print(f'\033[F\033[92mGIF saved at \033[38;2;70;130;180m\033]8;;{out_path}\\threshed.gif'
                          f'\033\\{out_path}\033]8;;\033\\\033[0m')

    def image_process(self, index, img):
        if index % 2 == 0:
            print()
        pixels = array(img)
        pixels_new = zeros_like(pixels)
        for i in range(pixels.shape[0]):
            if i % 10 == 0:
                print(f'\rprocessing frame {index}-{index + 2 if index + 2 < self.FRAME_COUNT else self.FRAME_COUNT} '
                      f'\t[ {"=" * int(i / 10)}{" " * int(pixels.shape[0] / 10 - i / 10)}]', end='')
            gray = dot(pixels[i], [0.299, 0.587, 0.114])
            mask = gray > 75
            pixels_new[i][mask] = self.FILTER_RGB
        img2 = Image.fromarray(uint8(pixels_new), "RGB")
        tkimg = ImageTk.PhotoImage(img2)
        return tkimg, img2

    def animate(self, n):
        if self.FILTER_WORKER_STATUS:
            if n < len(self.frames):
                global frame_id, filter_timer
                self.canvas.delete(self.frame_id)
                self.frame_id = self.canvas.create_image(0, 0, image=self.frames[n], anchor=NW)
                n = n + 1 if n != len(self.frames) - 1 else 0
                self.filter_timer = self.root.after(self.FRAME_DELAY, self.animate, n)

    def animate2(self, n):
        if self.FILTER_WORKER_STATUS:
            if n < len(self.frames2):
                global frame_id2, filter_timer2
                self.canvas.delete(self.frame_id2)
                self.frame_id2 = self.canvas.create_image(0, 0, image=self.frames2[n], anchor=NW)
                n = n+1 if n != len(self.frames2)-1 else 0
                self.filter_timer2 = self.root.after(self.FRAME_DELAY2, self.animate2, n)

    def gif_setup(self, f_path):
        pilframes = []
        print(f'\033[38;2;15;125;90m', end='')
        with Image.open(f_path) as gif:
            global FRAME_COUNT
            x, y, self.FRAME_COUNT = None, None, gif.n_frames
            for f_index, frame in enumerate(ImageSequence.Iterator(gif)):
                sys.stdout.write(f'\rloading frames\t[ {"="*f_index}{" "*(self.FRAME_COUNT-f_index)}]')
                sys.stdout.flush()
                pilframe = frame.copy()
                if pilframe.size[0] > pilframe.size[1]:
                    x, y = 1200, int(1200 / (pilframe.size[0]/pilframe.size[1]))
                else:
                    y, x = 700, int(700 / (pilframe.size[1]/pilframe.size[0]))
                pilframes.append(pilframe.resize((x, y)).convert('RGB'))
        return pilframes

    def start_process(self):
        while True:
            f_path = input("\n\nEnter path to image or gif (or quit to exit):\t")
            try:
                if f_path.startswith('"') and f_path.endswith('"'):
                    f_path = f_path[1:-1]
                if f_path in ['Q', 'q', 'exit', 'Exit', 'EXIT', 'quit', 'Quit', 'QUIT']:
                    sys.exit()
                if path.exists(f_path):
                    break
                else:
                    raise FileNotFoundError("\033[0m could not locate file\n")
            except FileNotFoundError:
                print('\033[91m' + format_exc())
        if f_path[-3:] in ['png', 'jpg', 'jpeg', 'jpe']:
            global FRAME_DELAY2, newimg
            self.FRAME_DELAY2 = 30
            img = Image.open(f_path)
            if img.size[0] > img.size[1]:
                x, y = 1200, int(1200 / (img.size[0] / img.size[1]))
            else:
                y, x = 700, int(700 / (img.size[1] / img.size[0]))
            scaled_img = img.resize((x, y))
            print(f'\033[38;2;15;125;90m', end='')
            print('applying filter -', end='')
            newimg, saveimg = self.image_process(0, scaled_img)
            self.canvas.create_image(0, 0, image=newimg, anchor=NW)
            print(' - \033[92mdone\n\033[38;2;15;125;90m(preview in tkinter window)\033[0m')
            self.root.geometry('%dx%d+%d+%d' % (1200, 700, self.root.winfo_screenmmwidth()/4, self.root.winfo_screenmmheight()/4))
            self.animate2(0)
            self.root.protocol("WM_DELETE_WINDOW", lambda data=saveimg: self.on_close(data))
        elif f_path[-3:] == 'gif':
            global FRAME_DELAY, frames, filter_worker, filter_worker2
            self.FRAME_DELAY = 72
            self.FRAME_DELAY2 = 8
            pfrms = self.gif_setup(f_path)
            print('\napplying filter -', end='')
            starttimer = perf_counter()
            self.frames[:], saveframes = zip(*(self.image_process(i, frm) for i, frm in enumerate(pfrms)))
            stoptimer = perf_counter()
            print(f' - \033[92mdone ({round((stoptimer - starttimer) * 1000, 3)}ms)')
            print(f'\033[38;2;15;125;90m(preview in tkinter window)\033[0m')
            self.root.geometry('%dx%d+%d+%d' % (1200, 700, self.root.winfo_screenmmwidth()/4, self.root.winfo_screenmmheight()/4))
            self.filter_worker = Thread(target=self.animate, args=(0,))
            self.filter_worker2 = Thread(target=self.animate2, args=(0,))
            self.filter_worker.start()
            self.filter_worker2.start()
            self.root.protocol("WM_DELETE_WINDOW", lambda data=saveframes: self.on_close(data))
        else:
            pass

class NewFilter:
    def __init__(self):
        self.root = Tk()

    def start(self):
        self.root.title("Preview")
        self.root.geometry('%dx%d+%d+%d' % (1200, 700, self.root.winfo_screenmmwidth() / 4,
                                                        self.root.winfo_screenmmheight() / 4))
        runner = Runner(self.root)
        runner.runtk()

if __name__ == "__main__":
    title_lst = []              # dont judge me, it looks cool
    title = "░▒▓████████▓▒░▒▓█▓▒░▒▓█▓▒░   ░▒▓████████▓▒░▒▓███████▓▒░    ▓███████▓▒░░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓███████▓▒░▒▓███████▓▒░▒▓███████▓▒░   " \
            "░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒    ▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ " \
            "░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒    ▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░     ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ " \
            "░▒▓██████▓▒░ ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░   ░▒▓███████▓▒░    ▒▓███████▓▒░░▒▓███████▓▒░░▒▓█▓▒░       ░▒▓██████▓▒░░▒▓██████▓▒░░▒▓███████▓▒░  " \
            "░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒    ▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░     ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ " \
            "░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒    ▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░     ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ " \
            "░▒▓█▓▒░      ░▒▓█▓▒░▒▓████████▓▒░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒    ▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓███████▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░ "
    for i in range(7):
        title_lst.append(title[i * 137:(i + 1) * 137])
    print('\033[38;2;1;127;5m')
    for r in title_lst:
        print(r)
        sleep(0.02)
    print(f'\n\033[0m\033[3m{" " * 100}Recreate your GIFs in cool filters\033[0m\n')
    process = Process()
    while True:
        newfilter = NewFilter()
        newfilter.start()
        newfilter = None
        print(f'{int(process.memory_info().rss / 1024 ** 2)} MB used')

