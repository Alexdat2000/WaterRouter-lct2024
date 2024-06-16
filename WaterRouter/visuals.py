import datetime
import json
import math
import os
import shutil
import time
from collections import defaultdict
from os.path import isfile, isdir

import numpy as np
from PIL import Image
from filehash import FileHash
from scipy.spatial import cKDTree

from input_parsing import normalize_name
from my_utils import parse

X_RANGE = [20, 199]
Y_RANGE = [64, 81]
IMG_SIZE = (1000, 500)

colors = [(37, 66, 201), (97, 129, 201), (131, 196, 236), (250, 252, 253)]
Y_ZOOM = 4


def scale(x, y):
    return (round((x - X_RANGE[0]) / (X_RANGE[1] - X_RANGE[0]) * IMG_SIZE[0]),
            IMG_SIZE[1] - round((y - Y_RANGE[0]) / (Y_RANGE[1] - Y_RANGE[0]) * IMG_SIZE[1]))


def generate_visual_map(cid, start, finish):
    visual_map = []
    datapath = os.path.join("_workingdir", cid, "result")

    iceship_data = json.load(open(os.path.join("_workingdir", cid, "raw_data_info.json"), encoding="utf-8"))
    ships_data = json.load(open(os.path.join("_workingdir", cid, "ships.json"), encoding="utf-8"))
    days = list(map(int, open(os.path.join(datapath, "data", "info.txt")).readlines()[1].split()))
    days.sort()

    points_info = json.load(open("common_data/points.json", encoding="utf-8"))
    loc = dict()
    name = dict()
    point_id = dict()

    for i in points_info:
        loc[i["id"]] = (i["lon"], i["lat"])
        name[i["id"]] = i["name"]
        point_id[normalize_name(i["name"])] = i["id"]

    appear = defaultdict(lambda: float('-inf'))
    disappear = defaultdict(lambda: float('inf'))
    for j in open(os.path.join(datapath, "movements.txt")):
        x = j.split()
        t_start, t_end = map(float, x[:2])
        ships = list(map(int, x[4:]))
        for i in ships:
            if i < 0:
                continue
            if i not in appear:
                appear[i] = math.floor(t_start)
            disappear[i] = math.ceil(t_start)
    for i in json.load(open(os.path.join(datapath, "reject.txt"))):
        appear[int(i)] = float('inf')

    start_date = datetime.datetime.combine(
        parse(open(os.path.join("_workingdir", cid, f"start.txt"), encoding="utf-8").read(), dayfirst=True).date(),
        datetime.datetime.min.time())
    for i in range(start * 8, (finish + 1) * 8):
        now = {"date": (start_date + datetime.timedelta(days=i // 8, hours=(i % 8) * 3)).strftime("%d/%m/%Y %H:%M")}
        i /= 8
        if i <= days[0]:
            now["map_id"] = "0"
        elif i >= days[-1]:
            now["map_id"] = str(days[-1])
        else:
            for j in range(len(days) - 1):
                if days[j] <= i <= days[j + 1]:
                    now["map_id"] = str(days[j])
                    break

        now["infos"] = []
        ship_loc = dict()
        for idx, iceship in enumerate(iceship_data["iceships"]):
            ship_loc[-idx - 1] = point_id[normalize_name(iceship["location"])]
        for idx, iceship in enumerate(ships_data):
            ship_loc[idx + 1] = point_id[normalize_name(iceship["from"])]
        moving = set()

        # currently moving
        for j in open(os.path.join(datapath, "movements.txt")):
            x = j.split()
            t_start, t_end = map(float, x[:2])
            fr, to = map(int, x[2:4])
            ships = list(map(int, x[4:]))

            if t_start <= i:
                for ship in ships:
                    ship_loc[ship] = to

            if not t_start <= i <= t_end:
                continue

            for ship in ships:
                moving.add(ship)

            fr_x = loc[fr][0]
            fr_y = loc[fr][1]
            to_x = loc[to][0]
            to_y = loc[to][1]
            x = fr_x + (to_x - fr_x) / (t_end - t_start) * (i - t_start)
            y = fr_y + (to_y - fr_y) / (t_end - t_start) * (i - t_start)
            fr_x, fr_y = scale(fr_x, fr_y)
            to_x, to_y = scale(to_x, to_y)
            x, y = scale(x, y)

            if len(ships) == 1:
                if ships[0] < 0:
                    icon = "icebreaker.png"
                else:
                    icon = "ship.png"
            else:
                icon = "convoy.png"
            if to_x > fr_x:
                icon = icon[:icon.rfind('.')] + "-r.png"

            if len(ships) == 1:
                if ships[0] < 0:
                    tooltip = f'Ледокол "{iceship_data["iceships"][-ships[0] - 1]["name"]}"<br>{name[fr]} — {name[to]}'
                else:
                    tooltip = f'Корабль "{ships_data[ships[0] - 1]["name"]}" (заявка {ships[0]}, класс {ships_data[ships[0] - 1]["class"]})<br>{name[fr]} — {name[to]}'
            else:
                tooltip = f'Конвой: {name[fr]} — {name[to]}<br>Ледокол "{iceship_data["iceships"][-ships[0] - 1]["name"]}"<br>Заявки: ' + ', '.join(
                    map(str, sorted(ships[1:])))

            now["infos"].append({
                "x": x,
                "y": y,
                "cnt": len(ships),
                "from_x": fr_x,
                "from_y": fr_y,
                "to_x": to_x,
                "to_y": to_y,
                "tooltip": tooltip,
                "icon": icon,
            })

        stationary = defaultdict(lambda: [])
        for ship in ship_loc:
            if i < appear[ship] or i > disappear[ship] or ship in moving:
                continue
            stationary[ship_loc[ship]].append(ship)

        for lo in stationary:
            tooltip = f'Точка "{name[lo]}"'
            if min(stationary[lo]) < 0:
                iceship_names = []
                for j in stationary[lo]:
                    if j < 0:
                        iceship_names.append(f'"{iceship_data["iceships"][-j - 1]["name"]}"')
                tooltip += f'<br>Ледоколы: ' + ', '.join(iceship_names)
            if max(stationary[lo]) > 0:
                ship_names = []
                for j in stationary[lo]:
                    if j > 0:
                        ship_names.append(str(j))
                tooltip += f'<br>Корабли из заявок: ' + ', '.join(ship_names)

            if min(stationary[lo]) < 0 < max(stationary[lo]):
                icon = "convoy_stop.png"
            elif stationary[lo][0] < 0:
                icon = "icebreaker_stop.png"
            else:
                icon = "ship_stop.png"
            x, y = scale(loc[lo][0], loc[lo][1])
            now["infos"].append({
                "x": x,
                "y": y,
                "from_x": 0,
                "from_y": 0,
                "to_x": 0,
                "to_y": 0,
                "tooltip": tooltip,
                "icon": icon,
            })
        visual_map.append(now)

    return visual_map


def generate_map_data(cid, stdout, stderr):
    datapath = os.path.join("_workingdir", cid, "result")
    start = float('inf')
    finish = float('-inf')

    for i in open(os.path.join(datapath, "movements.txt")):
        x = i.split()
        t_start, t_end = map(float, x[:2])
        start = min(t_start, start)
        finish = max(finish, t_end)
    start = math.floor(start)
    finish = math.ceil(finish)

    visual_map = generate_visual_map(cid, start, finish)

    metric1, metric2, metric3 = map(float, stdout.split()[:3])
    info = (f"Дней на обработку всех запросов: {round(metric1, 2)}<br>"
            f"Сумма времени по всем запросам (в днях): {round(metric2, 2)}")

    rej = json.load(open(os.path.join(datapath, "reject.txt")))
    if len(rej) == 1:
        info += (f"<br><br>Заявка {rej[0]} была отклонена из-за слишком плотного льда, "
                 f"рекомендуется перенести точку отправления/прибытия в более благоприятный порт или применить дизельный ледокол")
    elif len(rej) > 1:
        info += (f"<br><br>Заявки {', '.join(rej)} были отклонены из-за слишком плотного льда, "
                 f"рекомендуется перенести точки отправления/прибытия в более благоприятные порты или применить дизельные ледоколы")
    info += "<br>" + open(os.path.join("_workingdir", cid, "result", "reroutes.txt")).read()
    json.dump({
        "info": info,
        "visual_map": visual_map,
    }, open(os.path.join(datapath, "visual.json"), "w"), ensure_ascii=False)
    return True


def generate_images(path, output):
    md5hasher = FileHash('md5')
    if md5hasher.hash_file(os.path.join(path, "ice.xlsx")) == md5hasher.hash_file(
            os.path.join("common_data", "ice.xlsx")):
        shutil.copytree(os.path.join("common_data", "pics_precalc"), output)

        for i in range(10):
            time.sleep(1)
            if isdir(output) and os.listdir(os.path.join("common_data", "pics_precalc")) == os.listdir(output):
                continue
        return True

    os.mkdir(output)
    lon = [list(map(float, line.split())) for line in open(os.path.join(path, "lon.txt")).readlines()[1:]]
    lat = [list(map(float, line.split())) for line in open(os.path.join(path, "lat.txt")).readlines()[1:]]

    points = []
    for i in range(269):
        for j in range(217):
            points.append([round(lon[i][j] * 10 ** 4), round(lat[i][j] * Y_ZOOM * 10 ** 4)])

    tree = cKDTree(np.array(points, dtype=np.int64), leafsize=24)

    for q in os.listdir(os.path.join(path, "ice")):
        ice = [list(map(float, line.split())) for line in open(os.path.join(path, "ice", q)).readlines()[1:]]
        val = []

        for i in range(269):
            for j in range(217):
                x = round(ice[i][j])
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
        step = 1
        for i in range(0, IMG_SIZE[0] // step):
            for j in range(0, IMG_SIZE[1] // step):
                x = i * (10 ** 4 // IMG_SIZE[0]) * (X_RANGE[1] - X_RANGE[0]) + X_RANGE[0] * 10 ** 4
                y = (j * (10 ** 4 // IMG_SIZE[1]) * (Y_RANGE[1] - Y_RANGE[0]) + Y_RANGE[0] * 10 ** 4) * Y_ZOOM
                closest = sorted([val[i] for i in tree.query([x, y], k=5)[1]])[5 // 2]
                pixels[i, j] = colors[closest]
                if step == 2:
                    pixels[i + 1, j] = colors[closest]
                    pixels[i, j + 1] = colors[closest]
                    pixels[i + 1, j + 1] = colors[closest]
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        anchor = Image.open("static/anchor.png")
        now = 0
        for line in open("common_data/points.txt").readlines()[1:]:
            b, a = map(float, line.split())
            a %= 360
            if not (X_RANGE[0] <= a <= X_RANGE[1] and Y_RANGE[0] <= b <= Y_RANGE[1]):
                continue
            x = round((a - X_RANGE[0]) / (X_RANGE[1] - X_RANGE[0]) * IMG_SIZE[0])
            y = IMG_SIZE[1] - round((b - Y_RANGE[0]) / (Y_RANGE[1] - Y_RANGE[0]) * IMG_SIZE[1])

            img.paste(anchor, (x - 5, y - 5), anchor)
            now += 1

        legend = Image.open("static/legend.png")
        size = (1593, 898)
        scale = 0.15
        legend = legend.resize((round(size[0] * scale), round(size[1] * scale)), Image.Resampling.LANCZOS)
        img.paste(legend, (420, 350), legend)
        img.save(os.path.join(output, f"{q[:q.rfind(".")]}.png"))
    return True
