from PIL import Image
from plot import X_RANGE, Y_RANGE, IMG_SIZE
import cv2
import numpy as np


for ship in range(-4, 43):
    if ship == 0:
        continue

    coords = []
    for line in open("../solver/data/points.txt").readlines()[1:]:
        b, a = map(float, line.split())
        x = round((a - X_RANGE[0]) / (X_RANGE[1] - X_RANGE[0]) * IMG_SIZE[0])
        y = IMG_SIZE[1] - round((b - Y_RANGE[0]) / (Y_RANGE[1] - Y_RANGE[0]) * IMG_SIZE[1])
        coords.append((x, y))

    img = Image.open("images/0.png")
    na = np.array(img)

    for i in open("../solver/movements.txt"):
        x = i.split()
        t_start, t_end = map(float, x[:2])
        fr, to = map(int, x[2:4])
        ships = list(map(int, x[4:]))
        if ship in ships:
            if ships[0] < 0:
                na = cv2.arrowedLine(na, coords[fr], coords[to], (255, 0, 0), 2, tipLength=0.1)
            else:
                na = cv2.arrowedLine(na, coords[fr], coords[to], (0, 255, 0), 2, tipLength=0.1)

    Image.fromarray(na).save(f'paths/ship_{ship}_path.png')
