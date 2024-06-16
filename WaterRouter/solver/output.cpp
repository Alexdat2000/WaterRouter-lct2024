#include <iostream>
#include <vector>
#include "solver.h"

using namespace std;

void output(const vector<movement>& ans, int argc, char *argv[]) {
    if (argc == 1) {
        freopen("movements.txt", "w", stdout);
    } else {
        freopen(argv[9], "w", stdout);
    }
    for (const auto& c : ans) {
        cout << c.start << " " << c.end << " " << c.from << " " << c.to << " ";
        for (int i = 0; i < c.ships.size(); ++i) {
            cout << c.ships[i] << " \n"[i + 1 == c.ships.size()];
        }
    }
}
