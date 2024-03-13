"""
adding filter to window specified in frames array
also cool af terminal screen filter effect
"""
from sys import stdout
from os import path
import tkinter as tk
import numpy as np
from time import perf_counter
from random import randrange
from PIL import Image, ImageTk, ImageSequence
from threading import Thread
from traceback import format_exc

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
        self.canvas = tk.Canvas(self.root, width=1200, height=700, background='black')
        orig_fltr_frames = [Image.open(fp='C:/Users/mfarh/OneDrive/Pictures/Downloads/scanline_f1.png'),
                            Image.open(fp='C:/Users/mfarh/OneDrive/Pictures/Downloads/scanline_f2.png')]
        scaled_filtr_frames = [fltr_frm.resize((fltr_frm.size[0] * 3, fltr_frm.size[1] * 3)).crop((0, 0, 1200, 700))
                               for fltr_frm in orig_fltr_frames]
        self.scaled_filtr_frames = scaled_filtr_frames
        self.frames2[:] = [ImageTk.PhotoImage(pfrm2) for pfrm2 in scaled_filtr_frames]
        self.root.iconify()
        self.start_process()
        self.canvas.pack()
        self.root.mainloop()

    def on_close(self, f):
        # global FILTER_WORKER_STATUS, filter_worker, filter_worker2
        self.root.iconify()
        save = input('\nSave GIF? (Y/N)\t')
        if save[0] in ['Y', 'y']:
            if isinstance(f, Image.Image):
                print(self.filter_timer2)
                # self.root.after_cancel(self.filter_timer2)
                self.root.destroy()
                f.save("threshed.gif", append_images=[self.scaled_filtr_frames[0], f, self.scaled_filtr_frames[1]],
                       save_all=True, optimize=False, duration=self.FRAME_DELAY2 - 2, loop=0)
            else:
                self.FILTER_WORKER_STATUS = False
                self.root.after_cancel(self.filter_timer)
                self.root.after_cancel(self.filter_timer2)
                self.filter_worker.join()
                self.filter_worker2.join()
                print(f'\033[38;2;15;125;90m'.strip(), end='')
                gif = []
                for f_index, frame in enumerate(f, start=1):
                    stdout.write(f'\rSaving [{"=" * f_index}{" " * (len(f) - f_index)}]')
                    stdout.flush()
                    frame_lst = np.array(frame)
                    inter = np.zeros((*frame.size[::-1], 3))
                    scaled_filtr_lst = np.array(self.scaled_filtr_frames[(0, 1)[f_index % 2]]
                                                .crop((0, 0, f[0].size[0], f[0].size[1])))
                    filter_alpha1 = scaled_filtr_lst[:, :, 3]
                    scaled_filtr_lst = scaled_filtr_lst[..., 0:3]
                    mask = filter_alpha1 > 160
                    inter[mask] = scaled_filtr_lst[mask]
                    inter[~mask] = frame_lst[~mask]
                    gif.append(Image.fromarray(np.uint8(inter), "RGB"))
                gif[0].save("threshed.gif", save_all=True, append_images=gif[1:],
                            optimize=False, duration=self.FRAME_DELAY2, disposal=0, loop=0)
            if not isinstance(f, Image.Image):
                self.root.destroy()
                print()
            out_path = path.dirname(path.abspath(__file__))
            print(f'\033[92mGIF saved at \033[38;2;70;130;180m\033]8;;{out_path}\033\\{out_path}\033]8;;\033\\\033[0m')
        else:
            if isinstance(f, Image.Image):
                self.root.after_cancel(self.filter_timer2)
            else:
                self.root.after_cancel(self.filter_timer)
                self.root.after_cancel(self.filter_timer2)
                self.filter_worker.join()
                self.filter_worker2.join()
            self.root.destroy()

    def image_process(self, index, img):
        # global FILTER_RGB
        if index % 2 == 0:
            print()
        pixels = np.array(img)
        pixels_new = np.zeros_like(pixels)
        for i in range(pixels.shape[0]):
            if i % 10 == 0:
                print(f'\rprocessing frame {index}-{index + 2 if index + 2 < self.FRAME_COUNT else self.FRAME_COUNT} '
                      f'\t[ {"=" * int(i / 10)}{" " * int(pixels.shape[0] / 10 - i / 10)}]', end='')
            gray = np.dot(pixels[i], [0.299, 0.587, 0.114])
            mask = gray > 75
            pixels_new[i][mask] = self.FILTER_RGB
        # for i in range(pixels.shape[0]):
        #     if i % 50 == 0:
        #         pass
        #         print(f'\rprocessing frame {index}-{index+3 if index+3 < FRAME_COUNT else FRAME_COUNT} '
        #               f'\t[ {"=" * int(i/50)}{" " * int(pixels.shape[0]/50 - i/50)}]', end='')
        #     for j in range(pixels.shape[1]):
        #         gray = int(0.299 * pixels[i, j][0] +
        #                    0.587 * pixels[i, j][1] +
        #                    0.114 * pixels[i, j][2])
        #         pixels_new[i, j] = (
        #             FILTER_RGB[0] if gray > 75 else 0,     # 27 5
        #             FILTER_RGB[1] if gray > 75 else 0,     # 189 130
        #             FILTER_RGB[2] if gray > 75 else 0,     # 100-150 50-100
        #         )
        img2 = Image.fromarray(np.uint8(pixels_new), "RGB")
        tkimg = ImageTk.PhotoImage(img2)
        return tkimg, img2

    def animate(self, n):
        if self.FILTER_WORKER_STATUS:
            if n < len(self.frames):
                global frame_id, filter_timer
                self.canvas.delete(self.frame_id)
                self.frame_id = self.canvas.create_image(0, 0, image=self.frames[n], anchor=tk.NW)
                n = n + 1 if n != len(self.frames) - 1 else 0
                self.filter_timer = self.root.after(self.FRAME_DELAY, self.animate, n)

    def animate2(self, n):
        if self.FILTER_WORKER_STATUS:
            if n < len(self.frames2):
                global frame_id2, filter_timer2
                self.canvas.delete(self.frame_id2)
                self.frame_id2 = self.canvas.create_image(0, 0, image=self.frames2[n], anchor=tk.NW)
                n = n+1 if n != len(self.frames2)-1 else 0
                self.filter_timer2 = root.after(self.FRAME_DELAY2, self.animate2, n)

    def gif_setup(self, f_path):
        pilframes = []
        print(f'\033[38;2;15;125;90m', end='')
        with Image.open(f_path) as gif:
            global FRAME_COUNT
            x, y, self.FRAME_COUNT = None, None, gif.n_frames
            for f_index, frame in enumerate(ImageSequence.Iterator(gif)):
                stdout.write(f'\rloading frames\t[ {"="*f_index}{" "*(self.FRAME_COUNT-f_index)}]')
                stdout.flush()
                pilframe = frame.copy()
                if pilframe.size[0] > pilframe.size[1]:
                    x, y = 1200, int(1200 / (pilframe.size[0]/pilframe.size[1]))
                else:
                    y, x = 700, int(700 / (pilframe.size[1]/pilframe.size[0]))
                pilframes.append(pilframe.resize((x, y)).convert('RGB'))
        return pilframes

    def start_process(self):
        while True:
            f_path = input("Enter path to image or gif:\t")
            try:
                if path.exists(f_path):
                    break
                else:
                    raise FileNotFoundError("\033[0m could not locate file\n"
                                            "remove quotes "" from start and end of path if present")
            except FileNotFoundError as err:
                print('\033[91m'+format_exc())
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
            self.canvas.create_image(0, 0, image=newimg, anchor=tk.NW)
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
            self.frames, saveframes = zip(*(self.image_process(i, frm) for i, frm in enumerate(pfrms)))
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


# global root, canvas
# FRAME_DELAY = None
# FRAME_DELAY2 = None
# FRAME_COUNT = 1     # default if image
# FILTER_RGB = [15, 165, randrange(50, 100)]
# FILTER_WORKER_STATUS = True
# # sys.tracebacklimit = 0
# filter_worker = None
# filter_timer = None
# filter_worker2 = None
# filter_timer2 = None
# frames = None
# frames2 = []
# frame_id = None
# frame_id2 = None
# # thd = Thread(target=runtk)
# # thd.daemon = True
# # thd.start()
# root = tk.Tk()
# root.title("Preview")
# root.geometry('%dx%d+%d+%d' % (1200, 700, root.winfo_screenmmwidth()/4, root.winfo_screenmmheight()/4))
# canvas = tk.Canvas(root, width=1200, height=700, background='black')
# orig_fltr_frames = [Image.open(fp='C:/Users/mfarh/OneDrive/Pictures/Downloads/scanline_f1.png'),
#                     Image.open(fp='C:/Users/mfarh/OneDrive/Pictures/Downloads/scanline_f2.png')]
# scaled_filtr_frames = [fltr_frm.resize((fltr_frm.size[0]*3, fltr_frm.size[1]*3)).crop((0, 0, 1200, 700))
#                        for fltr_frm in orig_fltr_frames]
# frames2[:] = [ImageTk.PhotoImage(pfrm2) for pfrm2 in scaled_filtr_frames]
# root.iconify()
# start_process()
# canvas.pack()
# root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Preview")
    root.geometry('%dx%d+%d+%d' % (1200, 700, root.winfo_screenmmwidth() / 4, root.winfo_screenmmheight() / 4))
    runner = Runner(root)
    runner.runtk()



