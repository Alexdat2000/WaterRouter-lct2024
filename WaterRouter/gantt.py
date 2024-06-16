import collections
import datetime
import json
import math
import os

from my_utils import parse


def calc_gantt_ships(cid):
    gantt = ""
    info = json.load(open(os.path.join("_workingdir", cid, "raw_data_info.json"), encoding="utf-8"))
    start_date = parse(info["iceships_date"], dayfirst=True)

    points_info = json.load(open("common_data/points.json", encoding="utf-8"))
    name = dict()
    for i in points_info:
        name[i["id"]] = i["name"]

    now_parity = collections.defaultdict(lambda: 0)

    for j in open(os.path.join("_workingdir", cid, "result", "movements.txt")):
        x = j.split()
        t_start, t_end = map(float, x[:2])
        fr, to = map(int, x[2:4])
        ships = list(map(int, x[4:]))
        for i in ships:
            if i < 0:
                continue
            start = datetime.datetime.combine(start_date, datetime.datetime.min.time()) + datetime.timedelta(
                minutes=math.ceil(t_start * 24 * 60))
            end = datetime.datetime.combine(start_date, datetime.datetime.min.time()) + datetime.timedelta(
                minutes=math.floor(t_end * 24 * 60))
            target = f"Корабль {i}"
            if len(ships) > 1:
                target += f', конвой от ледокола {info["iceships"][-ships[0] - 1]['name']}'
            target += f": {name[fr]} — {name[to]}"

            if len(ships) == 1:
                brightness = now_parity[i] * 0.3
            else:
                brightness = 1 - now_parity[i] * 0.3
            now_parity[i] ^= 1

            gantt += "{" + ', '.join([
                f'name: "{i}"',
                f'target: "{target}"',
                f'fromDate: "{start.strftime("%d-%m-%Y-%H-%M")}"',
                f'toDate: "{end.strftime("%d-%m-%Y-%H-%M")}"',
                f'color: colorSet.getIndex({i % 4}).brighten({brightness})'
            ]) + "}, "
    return gantt


def calc_gantt_iceships(cid):
    info = json.load(open(os.path.join("_workingdir", cid, "raw_data_info.json"), encoding="utf-8"))
    start_date = parse(info["iceships_date"], dayfirst=True)
    datapath = os.path.join("_workingdir", cid, "result")
    gantt = ""
    cnt = 0

    points_info = json.load(open("common_data/points.json", encoding="utf-8"))
    name = dict()
    for i in points_info:
        name[i["id"]] = i["name"]

    iceship_data = json.load(open(os.path.join("_workingdir", cid, "raw_data_info.json"), encoding="utf-8"))
    now_parity = [i % 2 for i in range(len(iceship_data["iceships"]))]
    for j in open(os.path.join(datapath, "movements.txt")):
        x = j.split()
        t_start, t_end = map(float, x[:2])
        fr, to = map(int, x[2:4])
        ships = list(map(int, x[4:]))

        if ships[0] < 0:
            cnt += 1
            start = datetime.datetime.combine(start_date, datetime.datetime.min.time()) + datetime.timedelta(
                minutes=math.ceil(t_start * 24 * 60))
            end = datetime.datetime.combine(start_date, datetime.datetime.min.time()) + datetime.timedelta(
                minutes=math.floor(t_end * 24 * 60))

            if len(ships) == 1:
                target = "Переход"
            elif len(ships) == 2:
                target = "Конвой корабля: " + ", ".join(map(str, sorted(ships[1:])))
            else:
                target = "Конвой кораблей: " + ", ".join(map(str, sorted(ships[1:])))

            target += f": {name[fr]} — {name[to]}"

            if len(ships) == 1:
                brightness = now_parity[-ships[0] - 1] * 0.3
            else:
                brightness = 1 - now_parity[-ships[0] - 1] * 0.3
            now_parity[-ships[0] - 1] ^= 1

            gantt += "{" + ', '.join([
                f'name: "{iceship_data["iceships"][-ships[0] - 1]["name"]}"',
                f'target: "{target}"',
                f'fromDate: "{start.strftime("%d-%m-%Y-%H-%M")}"',
                f'toDate: "{end.strftime("%d-%m-%Y-%H-%M")}"',
                f'color: colorSet.getIndex({-ships[0] - 1}).brighten({brightness})'
            ]) + "}, "
    return gantt
