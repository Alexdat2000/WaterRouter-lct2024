import datetime
import json
import os
import shutil
import time
from pathlib import Path

import pandas as pd
import pylightxl as xl
from my_utils import parse


def normalize_name(s):
    return ' '.join(s.lower().split("(")[0].replace('-', ' ').split()).strip()


def parse_points(filepath, output):
    data = xl.readxl(filepath)
    points = data.ws("points")

    points_data = []
    for i in range(2, points.maxrow + 1):
        points_data.append({
            "id": points.index(i, 1),
            "name": points.index(i, 4),
            "lat": points.index(i, 2),
            "lon": points.index(i, 3),
        })
    json.dump(points_data, open(output, "w", encoding="UTF-8"), ensure_ascii=False)


def parse_ships(filepath, output):
    try:
        data = xl.readxl(filepath)
    except Exception:
        return "Некорректный файл", 400

    points_info = json.load(open("common_data/points.json", encoding="utf-8"))
    points = set()
    for point in points_info:
        points.add(normalize_name(point["name"]))

    if len(data.ws_names) != 1:
        return "Таблица с заявками должна содержать 1 лист", 404
    data = data.ws(data.ws_names[0])

    lines = 2
    while data.index(lines, 1) != "" \
            and data.index(lines, 2) != "" \
            and data.index(lines, 3) != "" \
            and data.index(lines, 4) != "" \
            and data.index(lines, 5) != "" \
            and data.index(lines, 6) != "":
        lines += 1
    if lines == 2:
        return "Не найдены запросы", 400
    info = []

    for i in range(2, lines):
        name, cla, speed, fr, to, da = map(str, [data.index(i, 1), data.index(i, 2), data.index(i, 3),
                                                 data.index(i, 4), data.index(i, 5), data.index(i, 6)])

        if normalize_name(fr) not in points:
            return f"Неизвестная точка {fr}", 400
        if normalize_name(to) not in points:
            return f"Неизвестная точка {to}", 400
        try:
            clas = min(7, int(0 if len(cla.split()) == 1 else cla[-1]))
            assert 0 <= clas <= 7
        except ValueError:
            return f"Некорректный класс {cla}", 400
        try:
            sp = float(speed)
        except ValueError:
            return f"Некорректная скорость {speed}", 400
        try:
            parse(da, dayfirst=True)
        except ValueError:
            return f"Дата {da} не соответствует шаблону YYYY/MM/DD", 400
        if not name:
            return f"Имя не может быть пустым", 400

        info.append(
            {"name": name,
             "class": clas,
             "speed": sp,
             "from": fr,
             "to": to,
             "date": da,
             }
        )

    json.dump(info, open(output, "w", encoding="utf-8"), ensure_ascii=False)
    return "", 200


def parse_ice(cid):
    if os.path.isdir(os.path.join("_workingdir", cid, "ice")):
        shutil.rmtree(os.path.join("_workingdir", cid, "ice"))
        time.sleep(0.1)
    Path(os.path.join("_workingdir", cid, "ice")).mkdir(parents=True, exist_ok=True)
    try:
        xl_file = pd.ExcelFile(os.path.join("_workingdir", cid, "ice.xlsx"))
    except:
        return "Некорректный файл со льдом", 400

    if xl_file.sheet_names.count("lon") != 1 or xl_file.sheet_names.count("lat") != 1:
        return 'В документе должно быть по 1 листу с названиями "lon" и "lat"', 400
    if len(xl_file.sheet_names) < 3:
        return "Не найдено файлов с информацией о льдах", 400

    dates = []
    for ws_name in xl_file.sheet_names:
        if ws_name in ['lon', 'lat']:
            continue
        try:
            parse(ws_name, dayfirst=True)
        except:
            return f"Дата {ws_name} не соответствует шаблону dd-Mon-yyyy", 400
        dates.append(ws_name)
    dates.sort(key=lambda x: parse(x, dayfirst=True))

    date_files = []
    start = parse(dates[0], dayfirst=True).date()
    sizes = set()
    for ws_name in dates:
        sh = xl_file.parse(ws_name, header=None)
        sizes.add(sh.shape)
        if len(sizes) != 1:
            return "Все листы в документе со льдом должны быть одинакового размера", 400

        date = parse(ws_name, dayfirst=True).date()
        diff = (date - start).days
        date_files.append(str(diff))
        out = f"{sh.shape[0]} {sh.shape[1]}\n"
        for i in range(sh.shape[0]):
            for j in range(sh.shape[1]):
                try:
                    val = round(sh[j][i])
                    assert -30 <= val <= 30
                    out += str(val) + " "
                except Exception:
                    return f"Некорректное значение в ячейке {ws_name}: {i};{j}", 400
            out += "\n"
        print(out, file=open(os.path.join("_workingdir", cid, "ice", f"{diff}.txt"), "w",
                             encoding="utf-8"))

    for ws_name in ['lon', 'lat']:
        sh = xl_file.parse(ws_name, header=None)
        sizes.add(sh.shape)
        if len(sizes) != 1:
            return "Все листы в документе со льдом должны быть одинакового размера", 400

        out = f"{sh.shape[0]} {sh.shape[1]}\n"
        for i in range(sh.shape[0]):
            for j in range(sh.shape[1]):
                try:
                    float(sh[j][i])
                except Exception:
                    return f"Некорректное значение в ячейке {ws_name}: {i};{j}", 400
                out += str(sh[j][i]) + " "
            out += "\n"
        print(out,
              file=open(os.path.join("_workingdir", cid, f"{ws_name}.txt"), "w", encoding="utf-8"))

    print(start.strftime("%d-%m-%Y"), file=open(os.path.join("_workingdir", cid, f"start.txt"), "w", encoding="utf-8"))
    return "", 200
