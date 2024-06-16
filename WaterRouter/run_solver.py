import os
import subprocess
from os.path import isfile

from prepare import exit_calc


def run_solver(cid):
    data = os.path.join("_workingdir", cid)
    args = ["./solver/solver",
            os.path.join("common_data", "points.txt"),
            os.path.join("common_data", "edges.txt"),
            os.path.join(data, "lat.txt"),
            os.path.join(data, "lon.txt"),
            os.path.join(data, "result", "data", "info.txt"),
            os.path.join(data, "ice"),
            os.path.join(data, "result", "data", "iceships.txt"),
            os.path.join(data, "result", "data", "ships.txt"),
            os.path.join(data, "result", "movements.txt")
            ]
    x = subprocess.run(args, capture_output=True)
    if (not x.stdout.decode() or not isfile(os.path.join("_workingdir", cid, "result", "movements.txt")) or
            not open(os.path.join("_workingdir", cid, "result", "movements.txt")).read().strip()):
        return exit_calc(cid, "Произошла ошибка во время расчёта")
    return x.stdout.decode(), x.stderr.decode()
