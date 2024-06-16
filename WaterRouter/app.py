import json
import os
import shutil
import subprocess
import time
import uuid
from io import BytesIO
from os.path import isfile
from subprocess import Popen

from flask import Flask, render_template, send_from_directory, request, send_file
from flask_cors import CORS

import input_parsing
from gantt import calc_gantt_ships, calc_gantt_iceships
from input_parsing import normalize_name
from my_utils import parse

app = Flask("WaterRouter")
CORS(app)


# Handlers for images
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/getMap')
def get_map():
    cid = request.args.get('id')
    if 'id' not in request.args or not os.path.isdir(os.path.join("_workingdir", cid)):
        return "Неизвестный id", 404
    map_id = request.args.get('mapid')
    for _ in range(10):
        try:
            return send_file(os.path.join("_workingdir", cid, "result", "pics", map_id + ".png"), mimetype='image/png')
        except:
            time.sleep(1)


@app.route('/getIcon')
def get_icon():
    iid = request.args.get('id')
    if 'id' not in request.args:
        return "Неизвестный id", 404
    return send_file(os.path.join("static", iid), mimetype='image/png')


# Creating new calculation
@app.route('/new')
def create_new_calculation():
    new_id = str(uuid.uuid4())[:8]
    shutil.copytree("_workingdir_template_empty", os.path.join("_workingdir", new_id))
    return new_id


@app.route('/newFromTemplate')
def create_new_calculation_from_template():
    new_id = str(uuid.uuid4())[:8]
    shutil.copytree("_workingdir_template", os.path.join("_workingdir", new_id))
    return new_id


@app.route('/newFromExisting')
def create_new_calculation_from_existing():
    new_id = str(uuid.uuid4())[:8]
    old_id = request.args.get('old_id')
    if 'id' not in request.args or not os.path.isdir(os.path.join("_workingdir", old_id)):
        return "Неизвестный id", 404
    shutil.copytree(os.path.join("_workingdir", old_id), os.path.join("_workingdir", new_id))
    return new_id


# Form handlers
def form_info(cid):
    info = json.load(open(os.path.join("_workingdir", cid, "raw_data_info.json"), encoding="utf-8"))
    ships = json.load(open(os.path.join("_workingdir", cid, "ships.json"), encoding="utf-8"))
    info["current_ships"] = ships
    return json.dumps(info, ensure_ascii=False)


@app.route('/getFormInfo')
def get_form_info():
    cid = request.args.get('id')
    if 'id' not in request.args or not os.path.isdir(os.path.join("_workingdir", cid)):
        return "Неизвестный id", 404
    return form_info(cid)


# Submit form
@app.route('/submitApplicationsXlsx', methods=['POST'])
def submit_applications_xlsx():
    if 'file' not in request.files:
        return "Не найден файл", 400
    if 'id' not in request.form:
        return "Не найден id", 400

    cid = request.form.get('id')
    path = os.path.join("_workingdir", cid)
    if not os.path.isdir(path):
        return "Неизвестный id", 404
    file = request.files['file']
    file.save(os.path.join("_workingdir", cid, "ships.xlsx"))

    info = json.load(open(os.path.join("_workingdir", cid, "raw_data_info.json"), encoding="utf-8"))
    info["ships_filename"] = file.filename
    json.dump(info, open(os.path.join("_workingdir", cid, "raw_data_info.json"), "w", encoding="utf-8"),
              ensure_ascii=False)

    x = input_parsing.parse_ships(os.path.join("_workingdir", cid, "ships.xlsx"),
                                  os.path.join("_workingdir", cid, "ships.json"))

    if len(x) == 2 and x[1] >= 400:
        return x
    return form_info(cid)


@app.route('/submitApplicationsTable', methods=['POST'])
def submit_applications_table():
    if 'id' not in request.json:
        return "Не найден id", 400
    if 'current_ships' not in request.json:
        return "Не найден current_ships", 400
    cid = request.json["id"]
    current_ships = request.json["current_ships"]

    path = os.path.join("_workingdir", cid)
    if not os.path.isdir(path):
        return "Неизвестный id", 404

    if type(current_ships) != list:
        return "Неверный формат", 400

    points_info = json.load(open("common_data/points.json", encoding="utf-8"))
    points = set()
    for point in points_info:
        points.add(input_parsing.normalize_name(point["name"]))

    for ship in current_ships:
        if sorted(list(ship.keys())) != ['class', 'date', 'from', 'name', 'speed', 'to']:
            return "Неверный формат", 400

        if normalize_name(ship["from"]) not in points:
            return f"Неизвестная локация {ship["from"]}", 400
        if normalize_name(ship["to"]) not in points:
            return f"Неизвестная локация {ship["to"]}", 400
        try:
            clas = min(7, int(0 if len(str(ship["class"]).split()) == 1 else ship["class"][-1]))
            assert 0 <= clas <= 7
        except ValueError:
            return f"Некорректный класс {ship["class"]}", 400
        try:
            float(ship["speed"])
        except ValueError:
            return f"Некорректная скорость {ship["speed"]}", 400
        try:
            parse(ship["date"], dayfirst=True)
        except ValueError:
            return f"Дата {ship["date"]} не соответствует шаблону YYYY/MM/DD", 400

    json.dump(current_ships, open(os.path.join(path, "ships.json"), "w", encoding="utf-8"), ensure_ascii=False)
    return "", 200


@app.route('/submitIceships', methods=['POST'])
def submit_ice_ships():
    if 'id' not in request.json:
        return "Не найден id", 400
    if 'data' not in request.json or type(request.json["data"]) != list:
        return "Не найден data", 400
    cid = request.json["id"]
    current_iceships = request.json["data"]

    path = os.path.join("_workingdir", cid)
    if not os.path.isdir(path):
        return "Неизвестный id", 404

    points_info = json.load(open("common_data/points.json", encoding="utf-8"))
    points = set()
    for point in points_info:
        points.add(input_parsing.normalize_name(point["name"]))
    for ship in current_iceships:
        if type(ship) != dict or sorted(list(ship.keys())) != ['fine1', 'fine2', 'location', 'name', 'sp3']:
            return "Неверный формат", 400

        if normalize_name(ship["location"]) not in points:
            return f"Неизвестная локация {ship["location"]}", 400
        try:
            float(ship["fine1"])
        except ValueError:
            return f"Некорректный штраф {ship["fine1"]}", 400
        try:
            float(ship["fine2"])
        except ValueError:
            return f"Некорректный штраф {ship["fine2"]}", 400

    data = json.load(open(os.path.join(path, "raw_data_info.json"), encoding="utf-8"))
    data["iceships"] = current_iceships

    if "iceships_date" not in request.json:
        return "Нет даты", 400
    try:
        parse(request.json["iceships_date"], dayfirst=True)
    except ValueError:
        return f"Дата {request.json["iceships_date"]} не соответствует шаблону YYYY/MM/DD", 400
    data["iceships_date"] = request.json["iceships_date"]
    print(data)
    json.dump(data, open(os.path.join(path, "raw_data_info.json"), "w", encoding="utf-8"), ensure_ascii=False)
    return json.dumps({"status": "OK"}, ensure_ascii=False)


@app.route('/submitIceXlsx', methods=['POST'])
def submit_ice_xlsx():
    if 'file' not in request.files:
        return "Не найден файл", 400
    if 'id' not in request.form:
        return "Не найден id", 400

    cid = request.form.get('id')
    path = os.path.join("_workingdir", cid)
    if not os.path.isdir(path):
        return "Неизвестный id", 404

    file = request.files['file']
    file.save(os.path.join("_workingdir", cid, "ice.xlsx"))
    status = input_parsing.parse_ice(cid)
    if status[1] != 200:
        return status

    info = json.load(open(os.path.join("_workingdir", cid, "raw_data_info.json"), encoding="utf-8"))
    info["ice_filename"] = file.filename
    json.dump(info, open(os.path.join("_workingdir", cid, "raw_data_info.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    return file.filename


#  Calculation result
@app.route('/runCalc')
def run_calc():
    if 'id' not in request.args:
        return "Не найден id", 400

    cid = request.args.get('id')
    path = os.path.join("_workingdir", cid)
    if os.path.isdir(os.path.join(path, "result")) and not os.path.isfile(os.path.join(path, "result", "state.txt")):
        return "Процесс уже запущен", 400
    Popen([f"python3.12 background_calc.py {cid}"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    return ""


@app.route('/getResult')
def get_result():
    if 'id' not in request.args:
        return "Не найден id", 400
    cid = request.args.get('id')
    path = os.path.join("_workingdir", cid)
    if not os.path.isdir(path):
        return "Неизвестный id", 404

    time.sleep(0.5)
    while not os.path.isfile(os.path.join("_workingdir", cid, "result", "state.txt")):
        time.sleep(1)
    text = open(os.path.join("_workingdir", cid, "result", "state.txt"), encoding="utf-8").read().strip()
    if text == "OK":
        return open(os.path.join("_workingdir", cid, "result", "visual.json")).read()
    else:
        return text, 400


@app.route('/getPoints')
def get_points():
    return open(os.path.join("common_data", "points_data.json"), encoding="utf-8").read()


# Gantt diagrams
@app.route('/ganttShips')
def gantt():
    if 'id' not in request.args:
        return "Не найден id", 400
    cid = request.args.get("id")
    path = os.path.join("_workingdir", cid)
    if not os.path.isdir(path):
        return "Неизвестный id", 404
    if not isfile(os.path.join("_workingdir", cid, "result", "movements.txt")):
        return "Не посчитано", 400
    return render_template("gantt.html", gantt=calc_gantt_ships(cid), id=cid)


@app.route('/ganttIceShips')
def gantt_ice():
    if 'id' not in request.args:
        return "Не найден id", 400
    cid = request.args.get("id")
    path = os.path.join("_workingdir", cid)
    if not os.path.isdir(path):
        return "Неизвестный id", 404
    if not isfile(os.path.join("_workingdir", cid, "result", "movements.txt")):
        return "Не посчитано", 400
    return render_template("gantt.html", gantt=calc_gantt_iceships(cid), id=cid)


# Raw data output

@app.route('/getRawData')
def get_raw_data():
    if 'id' not in request.args:
        return "Не найден id", 400
    cid = request.args.get("id")
    path = os.path.join("_workingdir", cid)
    if not os.path.isdir(path):
        return "Неизвестный id", 404
    if not isfile(os.path.join("_workingdir", cid, "result", "movements.txt")):
        return "Не посчитано", 400

    points_info = json.load(open("common_data/points.json", encoding="utf-8"))
    name = dict()
    for i in points_info:
        name[i["id"]] = i["name"]
    iceship_data = json.load(open(os.path.join("_workingdir", cid, "raw_data_info.json"), encoding="utf-8"))

    ans = []
    for j in open(os.path.join("_workingdir", cid, "result", "movements.txt")):
        x = j.split()
        fr, to = map(int, x[2:4])
        ships = list(map(int, x[4:]))

        ans.append({
            "from": name[fr],
            "to": name[to],
            "icebreaker": "" if ships[0] > 0 else iceship_data["iceships"][-ships[0] - 1]["name"],
            "ships": ships[1:] if ships[0] < 0 else ships
        })

    buffer = BytesIO()
    data = json.dumps(ans, indent=4, ensure_ascii=False).replace("'", '"')
    buffer.write(data.encode())
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'{cid}.json',
        mimetype='application/json'
    )


#  Misc
@app.route('/cleanAll')
def clean_workingdir():
    for root, dirs, files in os.walk('_workingdir'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    return ""


if __name__ == '__main__':
    app.run(host="0.0.0.0")
