import os
import shutil

import pylightxl as xl
from my_utils import parse

start = None
iid = dict()


def normalize_place_name(s):
    return ' '.join(s.lower().split("(")[0].replace('-', ' ').split()).strip()


def prepare_folder():
    shutil.rmtree("data")
    os.mkdir("data")
    os.mkdir("data/ice")


def parse_ice_data():
    global start
    data = xl.readxl('./raw_data/IntegrVelocity.xlsx')

    dates = []
    for ws_name in data.ws_names:
        if ws_name in ['lon', 'lat']:
            continue
        dates.append(ws_name)
    dates.sort(key=lambda x: parse(x, dayfirst=True))

    date_files = []
    start = parse(dates[0], dayfirst=True).date()
    for ws_name in dates:
        sh = data.ws(ws_name)
        date = parse(ws_name, dayfirst=True).date()
        diff = (date - start).days
        date_files.append(str(diff))
        f = open(f"data/ice/{diff}.txt", "w")
        print(sh.maxrow, sh.maxcol, file=f)
        for i in range(sh.maxrow):
            for j in range(sh.maxcol):
                assert sh.index(i + 1, j + 1) != ""
                val = round(sh.index(i + 1, j + 1))
                print(val, end=" ", file=f)
            print(file=f)
        f.close()

    for ws_name in ['lon', 'lat']:
        sh = data.ws(ws_name)

        f = open(f"data/{ws_name}.txt", "w")
        print(sh.maxrow, sh.maxcol, file=f)
        for i in range(sh.maxrow):
            for j in range(sh.maxcol):
                print(sh.index(i + 1, j + 1), end=" ", file=f)
                assert sh.index(i + 1, j + 1) != ""
            print(file=f)
        f.close()

    f = open("data/info.txt", "w")
    print(len(dates), file=f)
    print(' '.join(date_files), file=f)
    f.close()


def parse_graph():
    global iid
    data = xl.readxl('./raw_data/ГрафДанные.xlsx')

    points = data.ws("points")
    f = open("data/points.txt", "w")
    print(points.maxrow - 1, file=f)
    for i in range(1, points.maxrow):
        print(points.index(i + 1, 2), points.index(i + 1, 3), file=f)
        iid[normalize_place_name(points.index(i + 1, 4))] = points.index(i + 1, 1)
    f.close()

    points = data.ws("edges")
    f = open("data/edges.txt", "w")
    print(points.maxrow - 1, file=f)
    for i in range(1, points.maxrow):
        print(points.index(i + 1, 2), points.index(i + 1, 3), points.index(i + 1, 4), file=f)
    f.close()


def parse_ships():
    data = xl.readxl('./raw_data/Расписание движения судов.xlsx').ws(
        xl.readxl('./raw_data/Расписание движения судов.xlsx').ws_names[0])
    f = open("data/ships.txt", "w")
    lines = 2
    while data.index(lines, 1) != "":
        lines += 1
    print(lines - 2, file=f)

    for i in range(2, lines):
        cla, speed, fr, to, da = (data.index(i, 2), data.index(i, 3),
                                  data.index(i, 4), data.index(i, 5), data.index(i, 6))
        date = parse(da, dayfirst=True).date()
        sp3 = int(speed)
        sp3conv = sp3
        type = min(7, int(0 if len(cla.split()) == 1 else cla[-1]))
        sp2_info = [0, 0, 0, 0,
                    0, 0, 0,
                    round(sp3 * 0.8, 1)]
        sp2conv_info = [sp3, sp3, sp3, sp3,
                        round(sp3 * 0.8, 1), round(sp3 * 0.8, 1), round(sp3 * 0.8, 1),
                        round(sp3 * 0.6, 1)]
        sp1_info = [0, 0, 0, 0,
                    0, 0, 0,
                    round(sp3 * 0.15, 1)]
        sp1conv_info = [0, 0, 0, 0,
                        round(sp3 * 0.7, 1), round(sp3 * 0.7, 1), round(sp3 * 0.7, 1),
                        round(sp3 * 0.8, 1)]

        print(iid[normalize_place_name(fr)], iid[normalize_place_name(to)], (date - start).days,
              sp3, sp3conv, sp2_info[type], sp2conv_info[type], sp1_info[type], sp1conv_info[type],
              file=f)
    f.close()


def parse_ice_ships():
    f = open("data/iceships.txt", "w")
    print("""4 -6
27 22 22 22
41 21 21 21
16 18.5 16.7 13.9
6 18.5 16.7 13.9
""", file=f)
    f.close()


def main():
    prepare_folder()
    parse_ice_data()
    parse_graph()
    parse_ships()
    parse_ice_ships()


if __name__ == "__main__":
    main()
