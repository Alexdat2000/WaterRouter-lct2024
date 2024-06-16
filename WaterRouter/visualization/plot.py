import numpy as np
import pylightxl as xl
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree
from time import time

colors = [(37, 66, 201), (97, 129, 201), (131, 196, 236), (250, 252, 253)]

Y_ZOOM = 4
X_RANGE = [20, 199]
Y_RANGE = [64, 81]
IMG_SIZE = (1000, 500)

def main():
    start = time()

    data = xl.readxl('IntegrVelocity.xlsx')
    lon = data.ws('lon')
    lat = data.ws('lat')

    points = []
    for i in range(269):
        for j in range(217):
            points.append([round(lon.index(i + 1, j + 1) * 10 ** 4), round(lat.index(i + 1, j + 1) * Y_ZOOM * 10 ** 4)])

    tree = cKDTree(np.array(points, dtype=np.int64))

    for q in range(len(data.ws_names) - 2):
        ice = data.ws(data.ws_names[q + 2])
        val = []

        for i in range(269):
            for j in range(217):
                x = round(ice.index(i + 1, j + 1))
                if x >= 20:
                    y = 0
                elif x >= 15:
                    y = 1
                elif x >= 10:
                    y = 2
                else:
                    y = 3
                val.append(y)

        img = Image.new('RGB', IMG_SIZE)
        pixels = img.load()
        for i in range(0, IMG_SIZE[0], 2):
            for j in range(0, IMG_SIZE[1], 2):
                x = i * (10 ** 4 // IMG_SIZE[0]) * (X_RANGE[1] - X_RANGE[0]) + X_RANGE[0] * 10 ** 4
                y = (j * (10 ** 4 // IMG_SIZE[1]) * (Y_RANGE[1] - Y_RANGE[0]) + Y_RANGE[0] * 10 ** 4) * Y_ZOOM
                closest = sorted([val[i] for i in tree.query([x, y], k=9)[1]])[9 // 2]
                pixels[i, j] = colors[closest]
                pixels[i + 1, j] = colors[closest]
                pixels[i, j + 1] = colors[closest]
                pixels[i + 1, j + 1] = colors[closest]
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        anchor = Image.open("../static/anchor.png")
        draw = ImageDraw.Draw(img)
        now = 0
        for line in open("../solver/data/points.txt").readlines()[1:]:
            b, a = map(float, line.split())
            a %= 360
            if not (X_RANGE[0] <= a <= X_RANGE[1] and Y_RANGE[0] <= b <= Y_RANGE[1]):
                continue
            x = round((a - X_RANGE[0]) / (X_RANGE[1] - X_RANGE[0]) * IMG_SIZE[0])
            y = IMG_SIZE[1] - round((b - Y_RANGE[0]) / (Y_RANGE[1] - Y_RANGE[0]) * IMG_SIZE[1])

            img.paste(anchor, (x - 5, y - 5), anchor)
            # draw.text((x - 25, y - 10), str(now), (255,0,0), font_size=18)
            now += 1

        legend = Image.open("../static/legend.png")
        size = (1593, 898)
        scale = 0.15
        legend = legend.resize((round(size[0] * scale), round(size[1] * scale)), Image.Resampling.LANCZOS)
        img.paste(legend, (420, 350), legend)

        img.save(f'images/{q * 7}.png')
        break
    print(time() - start)


if __name__ == "__main__":
    main()
