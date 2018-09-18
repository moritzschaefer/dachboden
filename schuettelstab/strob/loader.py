"""Load bw and rgb files to display them on the led stripe"""


import os

def load(filename):
    ext = os.path.splitext(filename)[1]
    if ext == '.bw':
        return load_bw(filename)
    elif ext == '.rgb':
        return load_rgb(filename)
    else:
        raise NotImplementedError('Extension {} not handleable'.format(ext))

def load_bw(filename):
    lines = []
    with open(filename) as f:
        for file_line in f.readlines():
            for i, char in enumerate(file_line):
                if char == '0':
                    value = (0,0,0)
                elif char == '1':
                    value = (255,255,255)
                elif char == '\n':
                    pass
                else:
                    raise ValueError('Found illegal character "{}" in file'.format(char))

                try:
                    lines[i].append(value)
                except IndexError:
                    lines.append([value])
    return lines

def load_rgb(filename):
    lines = []
    with open(filename) as f:
        for file_line in f.readlines():
            for i, color in enumerate(file_line.split('#')[1:]):
                value = (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
                try:
                    lines[i].append(value)
                except IndexError:
                    lines.append([value])
    return lines
