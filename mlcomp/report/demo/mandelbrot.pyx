# -*- coding: utf-8 -*-
import cython
from cpython.array cimport array, clone

__all__ = ['Mandelbrot']


@cython.wraparound(False)
@cython.cdivision(True)
@cython.nonecheck(False)
@cython.boundscheck(False)
cdef make_image(int width, int height, int max_iteration, int super_sampling):
    cdef float sw = 1. / width
    cdef float sh = 1. / height
    cdef float dx = 3.75 * sw
    cdef float dy = 2.5 * sh
    cdef float dx1 = dx / 3
    cdef float dy1 = dy / 3
    cdef int pos = 0

    cdef int h, w
    cdef float t
    cdef float x, y, x1, y1
    cdef complex z, c
    cdef float k, z_abs
    cdef int r, g, b
    cdef array[unsigned char] buffer_template, buffer

    # initialize the loop
    buffer_template = array('B', [])
    buffer = clone(buffer_template, width * height * 3, zero=False)
    y = -1.25       # y = (h * sh - 0.5) * 2.5

    if super_sampling:
        # compute each pixel with 3x super-sampling
        for h in range(height):
            x = -2.7    # x = w * sw * 3.75 - 2.7

            for w in range(width):
                t = 0.
                for x1 in (x - dx1, x, x + dx1):
                    for y1 in (y - dy1, y, y + dy1):
                        z = 0
                        c = x1 + y1 * 1j
                        k = max_iteration
                        z_abs = abs(z)
                        while z_abs < 6 and k > 0:
                            z = z * z + c
                            z_abs = abs(z)
                            k -= 1
                        if z_abs >= 6.:
                            k = (2 + k - 4 * z_abs ** -0.4) / max_iteration
                        else:
                            k = (2 + k) / max_iteration
                        t += k ** 2
                t = t / 9.

                if t < 1.0 - 1e-8:
                    r = <int>(t * max_iteration ** (1 - t ** 45 * 2))
                    g = <int>(t * 70 - 880 * t ** 18 + 701 * t ** 9)
                    b = <int>(t * 80 + t ** 9 * max_iteration - 950 * t ** 99)
                    buffer[pos] = 255 if r > 255 else (0 if r < 0 else r)
                    buffer[pos + 1] = 255 if g > 255 else (0 if g < 0 else g)
                    buffer[pos + 2] = 255 if b > 255 else (0 if b < 0 else b)
                else:
                    buffer[pos] = buffer[pos + 1] = buffer[pos + 2] = 0

                # move to next pixel
                x += dx
                pos += 3

            # move to next row
            y += dy
    else:
        # compute each pixel without 3x super-sampling
        for h in range(height):
            x = -2.7    # x = w * sw * 3.75 - 2.7

            for w in range(width):
                z = 0
                c = x + y * 1j
                k = max_iteration
                z_abs = abs(z)
                while z_abs < 6 and k > 0:
                    z = z * z + c
                    z_abs = abs(z)
                    k -= 1
                if z_abs >= 6.:
                    k = (2 + k - 4 * z_abs ** -0.4) / max_iteration
                else:
                    k = (2 + k) / max_iteration
                t = k ** 2

                if t < 1.0 - 1e-8:
                    r = <int>(t * max_iteration ** (1 - t ** 45 * 2))
                    g = <int>(t * 70 - 880 * t ** 18 + 701 * t ** 9)
                    b = <int>(t * 80 + t ** 9 * max_iteration - 950 * t ** 99)
                    buffer[pos] = 255 if r > 255 else (0 if r < 0 else r)
                    buffer[pos + 1] = 255 if g > 255 else (0 if g < 0 else g)
                    buffer[pos + 2] = 255 if b > 255 else (0 if b < 0 else b)
                else:
                    buffer[pos] = buffer[pos + 1] = buffer[pos + 2] = 0

                # move to next pixel
                x += dx
                pos += 3

            # move to next row
            y += dy
    return buffer


class Mandelbrot(object):

    def __init__(self, width, height, max_iteration=255, super_sampling=True):
        self.width = width
        self.height = height
        self.max_iteration = max_iteration
        self.super_sampling = super_sampling

    def make_image(self):
        data = make_image(self.width, self.height, self.max_iteration,
                          int(self.super_sampling))
        return bytes(data)
