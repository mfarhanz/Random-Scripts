# By Bonan Yin, Mohammed Farhan, Liam Lawlor, Michael Adedokun
"""
Driver script file that loads up Sign Detection program.
To run, navigate inside project directory, and run-  python start.py
in the terminal or command prompt
"""
import os
import sys
import time
import msvcrt
import platform
from pathlib import Path, PureWindowsPath

import torch

from models.common import DetectMultiBackend
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadScreenshots, LoadStreams
from utils.general import (LOGGER, Profile, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_boxes, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, smart_inference_mode

import tkinter
from tkinter import *
from PIL import Image, ImageTk
import cv2

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

def run(
        weights=ROOT / 'yolov5s.pt',  # model path or triton URL
        source=ROOT / 'data/images',  # file/dir/URL/glob/screen/0(webcam)
        data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=False,  # show results
        save_txt=False,  # save results to *.txt
        save_conf=False,  # save confidences in --save-txt labels
        save_crop=False,  # save cropped prediction boxes
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        update=False,  # update all models
        project=ROOT / 'runs/detect',  # save results to project/name
        name='exp',  # save results to project/name
        exist_ok=False,  # existing project/name ok, do not increment
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        vid_stride=1,  # video frame-rate stride
):
    source = str(source)
    save_img = not nosave and not source.endswith('.txt')  # save inference images
    is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
    is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
    webcam = source.isnumeric() or source.endswith('.streams') or (is_url and not is_file)
    screenshot = source.lower().startswith('screen')
    if is_url and is_file:
        source = check_file(source)  # download

    save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Load model
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # Dataloader
    bs = 1  # batch_size
    if webcam:
        view_img = check_imshow(warn=True)
        dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
        bs = len(dataset)
    elif screenshot:
        dataset = LoadScreenshots(source, img_size=imgsz, stride=stride, auto=pt)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
    vid_path, vid_writer = [None] * bs, [None] * bs

    # Run inference
    model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # warmup
    seen, windows, dt = 0, [], (Profile(), Profile(), Profile())
    truePath = []
    break_capture = False
    frame_time = 1
    for path, im, im0s, vid_cap, s in dataset:
        with dt[0]:
            im = torch.from_numpy(im).to(model.device)
            im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim

        # Inference
        with dt[1]:
            visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
            pred = model(im, augment=augment, visualize=visualize)

        # NMS
        with dt[2]:
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

        # Second-stage classifier (optional)
        # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)

        # Process predictions
        for i, det in enumerate(pred):  # per image
            seen += 1
            if webcam:  # batch_size >= 1
                p, im0, frame = path[i], im0s[i].copy(), dataset.count
                s += f'{i}: '
            else:
                p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # im.jpg
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # im.txt
            s += '%gx%g ' % im.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            imc = im0.copy() if save_crop else im0  # for save_crop
            annotator = Annotator(im0, line_width=line_thickness, example=str(names))
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, 5].unique():
                    n = (det[:, 5] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                        with open(f'{txt_path}.txt', 'a') as f:
                            f.write(('%g ' * len(line)).rstrip() % line + '\n')

                    if save_img or save_crop or view_img:  # Add bbox to image
                        c = int(cls)  # integer class
                        label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                        annotator.box_label(xyxy, label, color=colors(c, True))
                    if save_crop:
                        save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)

            # Stream results
            im0 = annotator.result()
            if view_img:
                if platform.system() == 'Linux' and p not in windows:
                    windows.append(p)
                    cv2.namedWindow(str(p), cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)  # allow window resize (Linux)
                    cv2.resizeWindow(str(p), im0.shape[1], im0.shape[0])
                cv2.imshow(str(p)+" - Webcam (hit q to stop)", im0)
                key = cv2.waitKey(frame_time)&0xFF
                if key == ord('q'):
                    break_capture = True
                    break

            # Save results (image with detections)
            resPath = ""
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                    print(save_path)
                    resPath = save_path
                else:  # 'video' or 'stream'
                    if vid_path[i] != save_path:  # new video
                        vid_path[i] = save_path
                        if isinstance(vid_writer[i], cv2.VideoWriter):
                            vid_writer[i].release()  # release previous video writer
                        if vid_cap:  # video
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  # stream
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                        save_path = str(Path(save_path).with_suffix('.mp4'))  # force *.mp4 suffix on results videos
                        vid_writer[i] = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer[i].write(im0)
        if break_capture:
            break
        # Print time (inference-only)
        LOGGER.info(f"{s}{'' if len(det) else '(no detections), '}{dt[1].dt * 1E3:.1f}ms")
        if len(det):
            truePath.append(resPath)
    
    if not screenshot:
            print(save_dir)
            resPath = str(save_dir)+'\\'+os.listdir(save_dir)[0]
    
    # Print results
    t = tuple(x.t / seen * 1E3 for x in dt)  # speeds per image
    LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)
    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}{s}")
    if update:
        strip_optimizer(weights[0])  # update model (to fix SourceChangeWarning)
    print(resPath)
    return truePath,resPath
    
def case_static(d):
    global access_path
    if not Entry1.get():
        return
    path = Entry1.get()
    res = run(weights="weights/best.pt", source= path )
    resPath = res[1]
    print(res, resPath)     #testing
    access_path = resPath
    # resPath = Entry1.get()  #testing
    if Entry1.get()[-3:] in IMG_FORMATS:
        img = Image.open(resPath)
        img = img.resize((520,520))
        one = ImageTk.PhotoImage(img)
        app.one = one
        canvas.create_image((0,0), image=one, anchor='nw')

def update_frame(video, photo, fps):
    ret, frame = video.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (520,520))
        image = Image.fromarray(frame)
        photo.paste(image)
    # update again after some time (in milliseconds) (ie. 1000ms/25fps = 40ms)
    app.after(int(1000/fps), update_frame, video, photo, fps)  

# def get_path(d):          #testing function
    # print(access_path)

def get_video(d):
    if not Entry1.get():
        return
    if Entry1.get()[-3:] in VID_FORMATS or Entry1.get() == '0':
        # path = PureWindowsPath(Entry1.get())  #testing
        path = PureWindowsPath(access_path)
        path = str(path.as_posix())
        if path[-3:] in IMG_FORMATS:
            return
        vid = cv2.VideoCapture(path)
        fps = vid.get(cv2.CAP_PROP_FPS)
        ret, frame = vid.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (520,520))
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image)
        app.photo = photo
        img_id = canvas.create_image((0,0), image=photo, anchor='nw')
        update_frame(vid, photo, fps)
        app.mainloop()
        vid.release()

def case_live(d):
    global live_ctr
    live_ctr += 1
    if live_ctr > 1:
        temp_text = 'restarting'
        for i in range(5):
            if i == 0:
                print(temp_text, end="")
            else:
                print('.', end="")
            time.sleep(1)
        os.execv(sys.executable, ['python'] + sys.argv)
    Entry1.delete(0,END)
    Entry1.insert(0,'0')
    case_static(d)    

def window_event(event):
    global window_ctr
    if app.state() == 'zoomed':
        window_ctr = 0
        Button1.pack(padx=(x//2, x//4), pady=(10,20), side=LEFT)
        Button2.pack(padx=(x//2,x//2), pady=(20,20), side=LEFT)
        Button3.pack(padx=(x//4,x//2), pady=(20,10), side=LEFT)
    if app.state() == 'normal' and window_ctr < 1:
        window_ctr += 1
        Button1.pack(padx=(x//5,0), pady=(0,10), side=LEFT)
        Button2.pack(padx=(x//6,x//6), pady=(0,10), side=LEFT)
        Button3.pack(padx=(0,x//3), pady=(0,10), side=LEFT)

app = tkinter.Tk()
window_ctr = 0
live_ctr = 0
access_path = None
sw = app.winfo_screenwidth()
# get windows width
sh = app.winfo_screenheight()
# get windows height
ww = 800
wh = 700
x = (sw - ww) / 2
y = (sh - wh) / 2
app.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
app.config(bg='white')
app.title('Sign Detection')
canvas = Canvas(bg="dark grey", height=520, width=520)
canvas.pack(pady=10, expand=True)
# 按钮
Label2 = tkinter.Label(app, text="Enter the Image/Video root or choose Detect Live", width=70, font=("Terminal", 12))
Label2.pack(pady=0)
Entry1 = Entry(app, width=200, bg='light cyan', font=("Terminal", 9))
Entry1.pack(padx=20, pady=(10,10), ipadx=5, ipady=5)
Button1 = Button(app, text='Detect - Image/Video', width=20, font=("Segoe UI", 11))
Button1.pack(padx=(x//5,0), pady=(0,10), side=LEFT)
Button2 = Button(app, text='Get Video', width=20, font=("Segoe UI", 11))
Button2.pack(padx=(x//6,x//6), pady=(0,10), side=LEFT)
Button3 = Button(app, text='Detect - Live', width=20, font=("Segoe UI", 11))
Button3.pack(padx=(0,x//3), pady=(0,10), side=LEFT)
# binding
Button1.bind("<Button-1>", case_static)  # event binding
Button2.bind("<Button-1>", get_video)  # event binding
Button3.bind("<Button-1>", case_live)  # event binding
app.bind("<Configure>", window_event)
tkinter.mainloop()

