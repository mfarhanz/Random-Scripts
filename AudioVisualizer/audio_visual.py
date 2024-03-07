import sounddevice as sd
# from colorama import init
# from termcolor import colored
import numpy as np
import time as tm
import msvcrt
import os

def print_sound(indata, outdata, frames, time, status):
    # print("\n\n\n")
    indata = indata.reshape(16, 34)
    # default_input_device_info = sd.query_devices(kind='input', device=None)
    # print(sd.default.device)
    vol_norm = np.linalg.norm(indata * 2000, axis=0).astype(int)
    vol_norm_d = damper(vol_norm)
    render_matrix(t_cmatrix, vol_norm_d)
    tm.sleep(0.05 if ch == '1' else 0.005)
    os.system('cls') if ch == '1' else os.system('type out.txt')
    if msvcrt.kbhit() and msvcrt.getch() == chr(32).encode():
        raise sd.CallbackAbort


# init()                    # for using colorama
int_multi = 6               # color intensity multiplier
thresh_min = 50             # lower bound for red/green channel
thresh_max = 235            # upper bound for red/green channel
rows, cols = (16, 34)
rgb = np.array([thresh_min, thresh_max, 100])   # change any vals for interesting color gradients
cmatrix = np.full((39, 34), ' ', dtype=object)
t_cmatrix = np.transpose(cmatrix)
ch = input('Choose display mode -'
          '\n1 - Print to console directly (less frames, uses less memory)'
          '\n2 - Write to file and print to console (more frames, uses more memory')
# testarr = np.random.randint(1, cmatrix.shape[0]-1, size=(cmatrix.shape[1],))

def damper(freqs):                  # damping function
    coeffs = np.logspace(0.1, 0.98, 34, base=0.01)
    return np.multiply(freqs, coeffs).astype(int)


def static_matrix(matrix):          # gives the graph for the current frame
    return '\n'.join([' '.join(map(str, row)) for row in [[x for x in row] for row in matrix]])


def render_matrix(matrix, base_arr):
    for i, row in enumerate(matrix):
        for j, x in enumerate(row[::-1][:base_arr[i]]):
            matrix[i][j] = (f'\033[38;2;{rgb[0] + int_multi * j if j < 30 else thresh_max};'
                            f'{rgb[1] - int_multi * j if 10 < j < 60 else thresh_min if rgb[1] - int_multi * j < 0 else rgb[1]};'
                            f'{rgb[2]}m' + '\u20DE' + '\033[0m')       # replace with any other ANSI char for fun
            # matrix[i][j] = colored('\u2588', color='green', attrs=['dark'])    # if using colorama
        matrix[i][base_arr[i]:] = np.full(matrix[i][base_arr[i]:].shape, fill_value=' ', dtype=str)
    half = np.flip(np.transpose(matrix), axis=0)
    if ch == '1':
        print(static_matrix(np.concatenate((np.flip(half, axis=1), half), axis=1)))
    else:
        with open('out.txt', encoding='utf-16', mode='w') as f:
            f.write(static_matrix(np.concatenate((np.flip(half, axis=1), half), axis=1)))

def main():
    with sd.Stream(samplerate=10000, callback=print_sound):
        while True:
            sd.sleep(1000)

if __name__ == '__main__':
    main()

# n = 34
# def trans_func(x, c):          # damper funcs and testing
#    return (c*x**2)/((c**2)*(x**2)+(2*c*x)+1)*(1/10)
# testarr = np.random.randint(1, t_cmatrix.shape[1] - 1, size=(t_cmatrix.shape[0],))
# val_arr = [41, 26, 26, 26, 34, 34, 33, 33, 35, 35, 37, 37, 34, 34, 33, 33, 26, 26, 33, 33, 39, 39, 35, 35, 41, 41, 36, 36, 33, 33, 35, 35, 28, 28]
# test = np.logspace(0.1, 0.98, n, base=0.01)
# # test = np.abs(np.sin(np.arange(0.1, np.pi * 2 * 2, np.pi * 2 * 2 / 34)))
# thresholds = np.array([15, 17, 20, 25, 31, 40, 50, 62, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1200, 1600, 2000, 2500, 3200, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000, 24000])
# # test = np.array([trans_func(val_arr[i], 1/(x*2*np.pi)) for i, x in enumerate(thresholds)])
# test2 = np.multiply(val_arr, test)
# # print(test)
# for x in test2:
#    print(int(x))

# box = u20DE           # cool alternative characters to plot
# filledbox = u220E
# smallbox = u2395
# continuousbar = u2588  #2584 to 2589
# shadedbox = u25A9
