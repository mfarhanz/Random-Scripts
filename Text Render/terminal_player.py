import sys
import numpy as np
from random import choice
from time import sleep
from os import path, system
from PIL import Image, ImageSequence

def showhist(lst):                      # only for checking grayscale value distribution
    import matplotlib.pyplot as plt
    counts, bins = np.histogram(lst)
    bins = bins.astype(int)
    plt.stairs(counts, bins)
    plt.show()

def getframes():
    ret = []
    with Image.open(f_path) as gif:
        print(gif.info)
        try:
            if gif.info['duration']:
                delay = gif.info['duration']
        except KeyError:
            delay = 72
        for f_index, frame in enumerate(ImageSequence.Iterator(gif)):
            if frame.size[0] > frame.size[1]:
                x, y = 360, int(190 / (frame.size[0] / frame.size[1]))
            else:
                y, x = 100, int(170 / (frame.size[1] / frame.size[0]))
            global txt_w, txt_h
            txt_w, txt_h = y, x
            ret.append(frame.resize((x, y)).convert('RGB'))
    return ret, delay

def getmasks(pils):
    masks = []
    for i in range(len(pils)):
        iml = np.array(pils[i])
        gray = np.mean(iml, axis=-1, dtype=int)
        pil = Image.fromarray(np.uint8(gray), "L").resize((iml.shape[1], iml.shape[0]))
        # gray_vals, count_vals = np.unique(gray, return_counts=True)
        # thresh = gray_vals[count_vals > np.mean(count_vals)]    # both ways are similar, but give the wrong thresh idk
        # thresh = gray_vals[np.argmax(count_vals)]
        thresh = min(range(np.min(gray) + 1, np.max(gray)),       # otsu/automatic thresholding
                     key=lambda th: np.nansum([np.mean(cls) * np.var(gray, where=cls)
                                               for cls in [gray >= th, gray < th]], dtype=int))
        mask = gray <= thresh
        masks.append(mask)
        sys.stdout.write(f'\rSaving [{"=" * i}{" " * (len(pils) - i)}]')
        sys.stdout.flush()
    return masks

def player(txtfrm, pils, masks, i):
    static_txt_frm = np.copy(txtfrm)  # neat way to hold prev state/try it disable
    if len(pils) > 1:
        while True:
            txtfrm = static_txt_frm.copy()
            txtfrm[masks[i]] = fg
            txtfrm[:, -1] = '\n'
            print(*(''.join(r) for r in txtfrm))
            sleep(fdelay / 1000)
            i = i + 1 if i < len(pils) - 1 else 0  # infinite to make gif loop; hit Ctrl+C to stop
            system('cls')
    else:
        txtfrm[masks[0]] = fg
        txtfrm[:, -1] = '\n'
        print(*(''.join(r) for r in txtfrm))

if __name__ == '__main__':
    ctr = 0
    txt_w, txt_h = None, None
    bg, fg = 'E', '.'
    system('cls')
    sys.tracebacklimit = 0
    title_lst = []
    title = "  ...................                                                     ...............                                                                            " \
            " ...................                                                     .....    ......                                                                             " \
            "       .....     ..........  .....         ......     .............     .....    .....        ..........  .....         ....   ........       ..........  .........  " \
            "      .....     .........      ....      ......      .............     .....   ....          ..........  .... ..       ....   ....   ....    ..........  ....   .... " \
            "     .....     ...               ....   ....             ....         .....   .....         ...         ....  ...     ....   ....    ....   ...         ....   ...   " \
            "    .....     .......             ........              ....         ..... .....           .......     ....    ..    ....   ....     ...   .......     ....  ...     " \
            "   .....     .......               ......              ....         .....    .....        .......     ....      ..  ....   ....     ...   .......     .... ....      " \
            "  .....     ...                  ..... ...            ....         .....      .....      ...         ....        ......   ....     ...   ...         ....   ....     " \
            " .....     ..........         ......     ....        ....         .....        .....    ..........  ....          ....   ....    ...    ..........  ....     ....    " \
            ".....     ..........        .....         .....     ....         .....          ...... ..........  ....           ...   .........      ..........  ....       .....  "
    for i in range(10):
        title_lst.append(title[i*165:(i+1)*165].replace('.', '='))
    print('\033[38;2;115;70;180m')
    for r in title_lst:
        print(r)
        sleep(0.02)
    print(f'\n\033[0m\033[3m{" "*140}Render GIF/Images in ASCII\033[0m\n')
    print("Works best on a Terminal, fullscreen,\n"
          "with the font size changed to 5 pt. for proper rendering. Hit CTRL+C to stop script\n")
    try:
        f_path = input("Enter path for Image/GIF:  ")
        if f_path.startswith('"') and f_path.endswith('"'):
            f_path = f_path[1:-1]
        if path.exists(f_path):
            print(f"\r\033[FEnter path for Image/GIF:  {f_path}  \033[92m- located\033[0m")
        else:
            raise FileNotFoundError
    except FileNotFoundError as err:
        print('File not found!')
    pils_ref, fdelay = getframes()
    print(f'Current background symbol: {bg}')
    print(f'Current foreground symbol: {fg}')
    ch_invert = input("Invert render? (Y/N)  ")
    if ch_invert in ['Y', 'y', '1', 'yes', 'Yes', 'YES', 'True']:
        bg, fg = '.', 'E'
    # print(pils_ref[0].size, len(pils_ref))
    txt_frm = np.full((txt_w, txt_h), bg)
    txt_frm[:, -1] = '\n'
    frm_masks = getmasks(pils_ref)
    player(txt_frm, pils_ref, frm_masks, ctr)

