import json
import os
from pathlib import Path

from input_parsing import normalize_name
from my_utils import parse


def exit_calc(cid, message):
    Path(os.path.join("_workingdir", cid, "result")).mkdir(parents=True, exist_ok=True)
    print(message, file=open(os.path.join("_workingdir", cid, "result", "state.txt"), "w", encoding="utf-8"))
    return False


def prepare_data_for_solver(cid):
    path = os.path.join("_workingdir", cid)
    if not os.path.isfile(os.path.join(path, "ice.xlsx")):
        return exit_calc(cid, "Не найдена информация о льдах")

    try:
        data = json.load(open(os.path.join(path, "raw_data_info.json"), encoding="utf-8"))
        assert "iceships" in data
    except:
        return exit_calc(cid, "Не найдена информация о ледоколах")

    try:
        ships = json.load(open(os.path.join(path, "ships.json"), encoding="utf-8"))
    except:
        return exit_calc(cid, "Не найдена информация о заявках")

    start = parse(open(os.path.join("_workingdir", cid, f"start.txt"), encoding="utf-8").read(), dayfirst=True).date()

    try:
        iceship_date = parse(data["iceships_date"], dayfirst=True).date()
    except:
        return exit_calc(cid, "Некорректная дата")

    points_info = json.load(open("common_data/points.json", encoding="utf-8"))
    points = dict()
    for point in points_info:
        points[normalize_name(point["name"])] = point["id"]

    iceship_info = f"{len(data["iceships"])} {(iceship_date - start).days}\n"
    for ship in data["iceships"]:
        if normalize_name(ship["location"]) not in points:
            return exit_calc(cid, f"Неизвестная локация {ship["location"]}")

        sp3 = float(ship["sp3"])
        sp2 = sp3 * (100 - float(ship["fine2"])) / 100
        sp1 = sp3 * (100 - float(ship["fine1"])) / 100
        iceship_info += f"{points[normalize_name(ship["location"])]} {sp3} {sp2} {sp1}\n"
    print(iceship_info, file=open(os.path.join(path, "result", "data", "iceships.txt"), "w", encoding="UTF-8"))

    info = f"{len(os.listdir(os.path.join(path, "ice")))}\n"
    for i in os.listdir(os.path.join(path, "ice")):
        info += f"{i.replace(".txt", "")} "
    print(info, file=open(os.path.join(path, "result", "data", "info.txt"), "w", encoding="UTF-8"))

    reroutes = open(os.path.join(path, "result", "reroutes.txt"), "w", encoding="UTF-8")
    x = []
    for i in open(os.path.join(path, "ice", "0.txt")):
        x.append(list(map(int, i.split())))

    ship_info = f"{len(ships)}\n"
    for idx, ship in enumerate(ships):
        if normalize_name(ship["from"]) not in points:
            return exit_calc(cid, f"Неизвестная локация {ship["from"]}")
        if normalize_name(ship["to"]) not in points:
            return exit_calc(cid, 'Неизвестная локация {ship["to"]}')

        try:
            date = parse(ship["date"], dayfirst=True).date()
        except:
            return exit_calc(cid, 'Некорректная дата')
        sp3 = int(ship["speed"])
        sp3conv = sp3
        type = int(ship["class"])
        sp2_info = [0, 0, 0, 0,
                    0, 0, 0,
                    sp3]
        sp2conv_info = [sp3, sp3, sp3, sp3,
                        round(sp3 * 0.8, 1), round(sp3 * 0.8, 1), round(sp3 * 0.8, 1),
                        round(sp3 * 0.6, 1)]
        sp1_info = [0, 0, 0, 0,
                    0, 0, 0,
                    round(sp3 * 0.15, 1)]
        sp1conv_info = [0, 0, 0, 0,
                        round(sp3 * 0.7, 1), round(sp3 * 0.7, 1), round(sp3 * 0.7, 1),
                        round(sp3 * 0.8, 1)]
        date = max(date, iceship_date)

        if points[normalize_name(ship["to"])] == 29 and x[11][40] < 10:
            print(
                f'Заявка {idx} была перенаправлена: "{ship["to"]}" => "Индига". Далее необходимо использовать дизельный ледокол<br>',
                file=reroutes)
            ship["to"] = "Индига"

        ship_info += ' '.join([str(points[normalize_name(ship["from"])]),
                               str(points[normalize_name(ship["to"])]),
                               str((date - start).days),
                               str(sp3), str(sp3conv),
                               str(sp2_info[type]), str(sp2conv_info[type]),
                               str(sp1_info[type]), str(sp1conv_info[type]),
                               ]) + "\n"
    print(ship_info, file=open(os.path.join(path, "result", "data", "ships.txt"), "w", encoding="UTF-8"))
    return True
