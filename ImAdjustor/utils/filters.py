from math import cos, sin, log
from random import uniform

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
    'blur': {
        'kernel': ((0.1111, 0.1111, 0.1111), (0.1111, 0.1111, 0.1111), (0.1111, 0.1111, 0.1111)),
        'type': 'convolution'
    },
    'triangle_blur': {
        'kernel': ((0.0625, 0.125, 0.0625), (0.125, 0.25, 0.125), (0.0625, 0.125, 0.0625)),
        'type': 'convolution'
    },
    'gaussian_blur': {
        'kernel': ((0.00390625, 0.015625, 0.0234375, 0.015625, 0.00390625),
                   (0.015625, 0.0625, 0.09375, 0.0625, 0.015625),
                   (0.0234375, 0.09375, 0.140625, 0.09375, 0.0234375),
                   (0.015625, 0.0625, 0.09375, 0.0625, 0.015625),
                   (0.00390625, 0.015625, 0.0234375, 0.015625, 0.00390625)),
        'type': 'convolution'
    },
    'motion_blur': {
        'kernel': ((0, 0, 0.3333), (0, 0.3333, 0), (0.3333, 0, 0)),
        'type': 'convolution'
    },
    'negative': {
        'kernel': ((0, 0, 0), (0, -1, 0), (0, 0, 0)),
        'type': 'convolution'
    },
    'sobel_edge_detect_H': {
        'kernel': ((-1, 0, 1), (-2, 0, 2), (-1, 0, 1)),
        'type': 'convolution'
    },
    'sobel_edge_detect_V': {
        'kernel': ((-1, -2, -1), (0, 0, 0), (1, 2, 1)),
        'type': 'convolution'
    },
    'prewitt_edge_detect_H': {
        'kernel': ((-1, -1, -1), (0, 0, 0), (1, 1, 1)),
        'type': 'convolution'
    },
    'prewitt_edge_detect_V': {
        'kernel': ((-1, 0, 1), (-1, 0, 1), (-1, 0, 1)),
        'type': 'convolution'
    },
    'scharr_edge_detect_H': {
        'kernel': ((-3, 0, 3), (-10, 0, 10), (-3, 0, 3)),
        'type': 'convolution'
    },
    'scharr_edge_detect_V': {
        'kernel': ((-3, -10, -3), (0, 0, 0), (3, 10, 3)),
        'type': 'convolution'
    },
    'frei_chen_edge_detect_H': {
        'kernel': ((-1, -1.4142, -1), (0, 0, 0), (1, 1.4142, 1)),
        'type': 'convolution'
    },
    'frei_chen_edge_detect_V': {
        'kernel': ((-1, 0, 1), (-1.4142, 0, 1.4142), (-1, 0, 1)),
        'type': 'convolution'
    },
    'kirsch_compass_N': {
        'kernel': ((-3, -3, 5), (-3, 0, 5), (-3, -3, 5)),
        'type': 'convolution'
    },
    'kirsch_compass_NW': {
        'kernel': ((-3, 5, 5), (-3, 0, 5), (-3, -3, -3)),
        'type': 'convolution'
    },
    'kirsch_compass_W': {
        'kernel': ((5, 5, 5), (-3, 0, -3), (-3, -3, -3)),
        'type': 'convolution'
    },
    'kirsch_compass_SW': {
        'kernel': ((5, 5, -3), (5, 0, -3), (-3, -3, -3)),
        'type': 'convolution'
    },
    'kirsch_compass_S': {
        'kernel': ((5, -3, -3), (5, 0, -3), (5, -3, -3)),
        'type': 'convolution'
    },
    'kirsch_compass_SE': {
        'kernel': ((-3, -3, -3), (5, 0, -3), (5, 5, -3)),
        'type': 'convolution'
    },
    'kirsch_compass_E': {
        'kernel': ((-3, -3, -3), (-3, 0, -3), (5, 5, 5)),
        'type': 'convolution'
    },
    'kirsch_compass_NE': {
        'kernel': ((-3, -3, -3), (-3, 0, 5), (-3, 5, 5)),
        'type': 'convolution'
    },
    'laplacian': {
        'kernel': ((0, 1, 0), (1, -4, 1), (0, 1, 0)),
        'type': 'convolution'
    },
    'inv_laplacian': {
        'kernel': ((0, -1,  0), (-1,  4, -1), (0, -1,  0)),
        'type': 'convolution'
    },
    'high_pass': {
        'kernel': ((-1, -1, -1), (-1,  8, -1), (-1, -1, -1)),
        'type': 'convolution'
    },
    'high_boost': {
        'kernel': ((-1, -1, -1), (-1, 9, -1), (-1, -1, -1)),
        'type': 'convolution'
    },
    'laplacian_5x5': {
        'kernel': ((0, -2, -4, -2, 0), (-2, -4, 8, -4, -2), (-4, 8, 16, 8, -4), (-2, -4, 8, -4, -2),
                   (0, -2, -4, -2, 0)),
        'type': 'convolution'
    },
    'farid_transform': {
        'kernel': ((-0.229879, 0.540242, 0.229879), (0.425827, 0, -0.425827), (0.229879, -0.540242, -0.229879)),
        'type': 'convolution'
    },
    'deriv_of_gaussian': {
        'kernel': ((-0.01724138, -0.03448276, 0, 0.03448276, 0.01724138),
                   (-0.06896552, -0.17241379, 0, 0.17241379, 0.06896552),
                   (-0.12068966, -0.29310345, 0, 0.29310345, 0.12068966),
                   (-0.06896552, -0.17241379, 0, 0.17241379, 0.06896552),
                   (-0.01724138, -0.03448276, 0, 0.03448276, 0.01724138)),
        'type': 'convolution'
    },
    'laplac_of_gaussian': {
        'kernel': ((0, 0, 0.0125, 0.0125, 0.0125, 0, 0),
                   (0, 0.0125, 0.0625, 0.075, 0.0625, 0.0125, 0),
                   (0.0125, 0.0625, 0, -0.1375, 0, 0.0625, 0.0125),
                   (0.0125, 0.075, -0.1375, -0.45, -0.1375, 0.075, 0.0125),
                   (0.0125, 0.0625, 0, -0.1375,  0, 0.0625, 0.0125),
                   (0, 0.0125, 0.0625, 0.075, 0.0625, 0.0125, 0),
                   (0, 0, 0.0125, 0.0125, 0.0125, 0, 0)),
        'type': 'convolution'
    },
    'emboss': {
        'kernel': ((-2, -1, 0), (-1,  1, 1), (0,  1, 2)),
        'type': 'convolution'
    },
    'sharpen': {
        'kernel': ((0, -1,  0), (-1,  5, -1), (0, -1,  0)),
        'type': 'convolution'
    },
    'bayer_2x2': {
        'kernel': ((-0.5, 0), (0.25, -0.25)),
        'type': 'ordered dither'
    },
    'bayer_4x4':{
        'kernel': ((-0.5, 0, -0.375, 0.125), (0.25, -0.25, 0.375, -0.125),
                   (-0.3125, 0.1875, -0.4375, 0.0625), (0.4375, -0.0625, 0.3125, -0.1875)),
        'type': 'ordered dither'
    },
    'checkerboard_2x2': {
        'kernel': ((1, 0), (0, 1)),
        'type': 'ordered dither'
    },
    'checkerboard_4x4': {
        'kernel': ((1, 0, 1, 0), (0, 1, 0, 1), (1, 0, 1, 0), (0, 1, 0, 1)),
        'type': 'ordered dither'
    },
    'tpdf_dither': {
        'kernel': ((0.25, 0.5, 0.75, 1), (0.5, 0.75, 1, 0.75), (0.75, 1, 0.75, 0.5),
                   (1, 0.75, 0.5, 0.25)),
        'type': 'ordered dither'
    },
    'dispersed_dot': {
        'kernel': ((-0.125, -0.0625, 0, 0.0625), (-0.1875, -0.5, -0.4375, 0.125),       # +0.5?
                   (-0.25, -0.3125, -0.375, 0.1875), (0.4375, 0.375, 0.3125, 0.25)),
        'type': 'ordered dither'
    },
    'clustered_dot': {
        'kernel': ((0.88, 0.56, 0.4, 0.68, 0.84), (0.72, 0.24, 0.08, 0.2, 0.52),
                   (0.44, 0.12, 0, 0.04, 0.36), (0.6, 0.28, 0.16, 0.32, 0.8), (0.92, 0.76, 0.48, 0.64, 0.96)),
        'type': 'ordered dither'
    },
    'floyd_steinberg': {
        'kernel': ((0, 0, 0), (0, 1, 0.4375), (0.1875, 0.3125, 0.0625)),
        'type': 'error diffusion'
    },
    'jarvis_judice_ninke': {
        'kernel': ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0,), (0, 0, 1, 0.145833, 0.104167),
                   (0.0625, 0.104167, 0.145833, 0.104167, 0.0625),
                   (0.02083333, 0.0625, 0.10416667, 0.0625, 0.02083333)),
        'type': 'error diffusion'
    },
    'stucki_dither': {
        'kernel': ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 1, 0.190476, 0.095238),
                   (0.047619, 0.095238, 0.190476, 0.095238, 0.047619),
                   (0.023809, 0.047619, 0.095238, 0.047619, 0.023809)),
        'type': 'error diffusion'
    },
    'atkinson_dither': {
        'kernel': ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 1, 0.125, 0.125),
                   (0, 0.125, 0.125, 0.125, 0), (0, 0, 0.125, 0, 0)),
        'type': 'error diffusion'
    },
    'burkes_dither': {
        'kernel': ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 1, 0.25, 0.125),
                   (0.0625, 0.125, 0.25, 0.125, 0.0625), (0, 0, 0, 0, 0)),
        'type': 'error diffusion'
    },
    'sierra_dither': {
        'kernel': ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 1, 0.15625, 0.09375),
                   (0.0625, 0.125, 0.15625, 0.125, 0.0625), (0, 0.0625, 0.09375, 0.0625, 0)),
        'type': 'error diffusion'
    }
}
