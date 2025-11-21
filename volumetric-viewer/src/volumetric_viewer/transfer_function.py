import numpy as np
from OpenGL.GL import (
    GL_CLAMP_TO_EDGE,
    GL_FLOAT,
    GL_LINEAR,
    GL_RGBA,
    GL_RGBA32F,
    GL_TEXTURE0,
    GL_TEXTURE_1D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    glActiveTexture,
    glBindTexture,
    glDeleteTextures,
    glGenTextures,
    glTexImage1D,
    glTexParameteri,
)


class TransferFunction:
    def __init__(self, size=256):
        self.size = size
        self.color_knots = []
        self.alpha_knots = []
        self.texture_id = None

    def add_color_knot(self, r, g, b, intensity):
        self.color_knots.append((intensity, r, g, b)) 
        self.color_knots.sort(key=lambda x: x[0])  

    def add_alpha_knot(self, alpha, intensity):
        self.alpha_knots.append((intensity, alpha))  
        self.alpha_knots.sort(key=lambda x: x[0])  

    def _interp_knots(self, knots, x, is_color=True):
        if not knots:
            return (0.0, 0.0, 0.0) if is_color else 0.0

        first = knots[0]
        last = knots[-1]

        x_first = first[0] 
        x_last = last[0]    

        if x <= x_first:
            return first[1:] if is_color else first[1]
        if x >= x_last:
            return last[1:] if is_color else last[1]

        for i in range(len(knots) - 1):
            x0 = knots[i][0]  
            x1 = knots[i+1][0]  
            if x0 <= x <= x1:
                t = (x - x0) / (x1 - x0)
                if is_color:
                    r0, g0, b0 = knots[i][1:]
                    r1, g1, b1 = knots[i+1][1:]
                    return (
                        r0 * (1 - t) + r1 * t,
                        g0 * (1 - t) + g1 * t,
                        b0 * (1 - t) + b1 * t
                    )
                else:
                    a0 = knots[i][1]
                    a1 = knots[i+1][1]
                    return a0 * (1 - t) + a1 * t

        return (0.0, 0.0, 0.0) if is_color else 0.0

    def generate_texture_data(self):
        tf_data = np.zeros((self.size, 4), dtype=np.float32)

        for i in range(self.size):
            r, g, b = self._interp_knots(self.color_knots, i, is_color=True)
            a = self._interp_knots(self.alpha_knots, i, is_color=False)
            tf_data[i] = [r, g, b, a]

        return tf_data
    
    def update(self, color_knots=None, alpha_knots=None):
        if color_knots is not None:
            self.color_knots = color_knots
            self.color_knots.sort(key=lambda x: x[0])
        if alpha_knots is not None:
            self.alpha_knots = alpha_knots
            self.alpha_knots.sort(key=lambda x: x[0])
        if self.texture_id is not None:
            glDeleteTextures([self.texture_id])
            self.texture_id = None
        self.upload_to_gpu()

    def upload_to_gpu(self):
        tf_data = self.generate_texture_data()
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_1D, self.texture_id)
        glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA32F, self.size, 0, GL_RGBA, GL_FLOAT, tf_data)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_1D, 0)

    def bind(self, texture_unit):
        if len(self.color_knots) == 0 or len(self.alpha_knots)==0:
            return
        glActiveTexture(GL_TEXTURE0 + texture_unit)
        glBindTexture(GL_TEXTURE_1D, self.texture_id)

    def delete(self):
        if self.texture_id:
            glDeleteTextures([self.texture_id])
            self.texture_id = None

    def get_alpha_knots(self):
        return self.alpha_knots
    
    def get_color_knots(self):
        return self.color_knots
