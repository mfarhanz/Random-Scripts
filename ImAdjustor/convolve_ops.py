from multiprocessing import Process, Array
from numpy import pad, einsum, frombuffer, stack, float64

def convolve(arr, fltr, output_arr):
    padded_arr = pad(arr, 1, mode='symmetric')
    for x1 in range(1, padded_arr.shape[0] - 1):
        for y1 in range(1, padded_arr.shape[1] - 1):
            output_arr[x1*padded_arr.shape[1]+y1] = einsum('ij,ij', padded_arr[x1 - 1:x1 + 2, y1 - 1:y1 + 2], fltr)
    return output_arr

def channel_op(size, channels, kernel):
    cnvlvdchannels = [Array('d', size) for _ in range(3)]
    processes = []
    for i in range(3):
        p = Process(target=convolve, args=(channels[i], kernel, cnvlvdchannels[i]))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    cnvlvdchannels[:] = [frombuffer(arr.get_obj(), dtype=float64)
                         .reshape((channels[0].shape[0]+2, channels[0].shape[1]+2))[1:-1, 1:-1]
                         for arr in cnvlvdchannels]
    return stack(cnvlvdchannels, axis=2)
