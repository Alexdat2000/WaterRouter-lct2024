import json
import os
import shutil
import sys
import time
import traceback
from pathlib import Path

from prepare import prepare_data_for_solver, exit_calc
from run_solver import run_solver
from visuals import generate_images, generate_map_data


def background_calc(cid):
    try:
        path = os.path.join("_workingdir", cid)
        if os.path.isdir(os.path.join(path, "result")):
            shutil.rmtree(os.path.join(path, "result"))
        time.sleep(1)
        Path(os.path.join("_workingdir", cid, "result")).mkdir(parents=True, exist_ok=True)
        Path(os.path.join("_workingdir", cid, "result", "data")).mkdir(parents=True, exist_ok=True)

        if not generate_images(os.path.join(path), os.path.join(path, "result", "pics")):
            return

        x = prepare_data_for_solver(cid)
        if not x:
            return

        solver_res = run_solver(cid)
        if not solver_res:
            return

        rej = []
        for line in solver_res[1].strip().split("\n"):
            if len(line.split()) >= 4 and line.split()[3].isnumeric():
                rej.append(line.split()[3])
        json.dump(rej, open(os.path.join("_workingdir", cid, "result", "reject.txt"), "w", encoding="utf-8"), ensure_ascii=False)

        if not generate_map_data(cid, *solver_res):
            return
        exit_calc(cid, "OK")
    except Exception as ex:
        exit_calc(cid, "Не удалось выполнить расчёт")
        print(traceback.format_exc())


if __name__ == "__main__":
    background_calc(sys.argv[1])
