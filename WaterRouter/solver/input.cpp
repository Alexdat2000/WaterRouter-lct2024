#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
#include <filesystem>
#include "solver.h"

using namespace std;

void input(dataset &d, int argc, char *argv[]) {
    cout.tie(0); cin.tie(0);
    ios_base::sync_with_stdio(0);
    if (argc == 1) {
        freopen("data/points.txt", "r", stdin);
    } else {
        freopen(argv[1], "r", stdin);
    }
    int n;
    cin >> n;
    d.n = n;
    d.points.resize(n);
    for (auto &c : d.points) cin >> c.first >> c.second;

    if (argc == 1) {
        freopen("data/edges.txt", "r", stdin);
    } else {
        freopen(argv[2], "r", stdin);
    }
    d.gr.resize(n);
    d.closest.resize(n, {-1, -1});
    int m;
    cin >> m;
    for (int i = 0; i < m; ++i) {
        int u, v;
        double len;
        cin >> u >> v >> len;
        d.edges.push_back({u, v, 0, 0});
        d.edges.push_back({v, u, 0, 0});
        d.gr[u].push_back(v);
        d.gr[v].push_back(u);
    }

    if (argc == 1) {
        freopen("data/lat.txt", "r", stdin);
    } else {
        freopen(argv[3], "r", stdin);
    }
    int h, w;
    cin >> h >> w;
    d.lat.resize(h, vector<double>(w));
    for (auto &row : d.lat) {
        for (auto &cell : row) cin >> cell;
    }

    if (argc == 1) {
        freopen("data/lon.txt", "r", stdin);
    } else {
        freopen(argv[4], "r", stdin);
    }
    int h2, w2;
    cin >> h2 >> w2;
    if (h2 != h || w2 != w) {
        throw std::invalid_argument("grid sizes should be equal");
    }
    d.lon.resize(h, vector<double>(w));
    for (auto &row : d.lon) {
        for (auto &cell : row) cin >> cell;
    }

    if (argc == 1) {
        freopen("data/info.txt", "r", stdin);
    } else {
        freopen(argv[5], "r", stdin);
    }
    int ice;
    cin >> ice;
    d.days.resize(ice);
    for (auto &c : d.days) cin >> c;

    string path;
    if (argc == 1) {
        path = "data/ice";
    } else {
        path = string(argv[6]);
    }
    d.ice.resize(ice, vector<vector<int>>(h, vector<int>(w)));

    for (const auto &entry : filesystem::directory_iterator(path)) {
        std::filesystem::path outfilename = entry.path();
        std::string s = outfilename.string();
        std::string cpy = s;
        const char* path = cpy.c_str();

        freopen(path, "r", stdin);
        cin >> h2 >> w2;
        if (h2 != h || w2 != w) {
            throw std::invalid_argument("grid sizes should be equal");
        }

        s = s.substr(s.rfind('/') + 1, s.rfind('.') - s.rfind('/'));
        int day = stoi(s);
        int ind = -1;
        for (int i = 0; i < d.days.size(); ++i) ind = (d.days[i] == day) ? i : ind;

        if (ind == -1) {
            throw std::invalid_argument("found unspesified day in folder");
        }
        for (auto &row : d.ice[ind]) {
            for (auto &cell : row) {
                cin >> cell;
            }
        }
    }

    if (argc == 1) {
        freopen("data/iceships.txt", "r", stdin);
    } else {
        freopen(argv[7], "r", stdin);
    }
    int icebreakers, date;
    cin >> icebreakers >> date;
    d.iceships.resize(icebreakers + 1);
    for (int i = 0; i < icebreakers; ++i) {
        int v; double sp1, sp2, sp3;
        cin >> v >> sp3 >> sp2 >> sp1;
        d.iceships[i + 1].sp1 = sp1;
        d.iceships[i + 1].sp2 = sp2;
        d.iceships[i + 1].sp3 = sp3;
        d.iceships[i + 1].sp1conv = sp1;
        d.iceships[i + 1].sp2conv = sp2;
        d.iceships[i + 1].sp3conv = sp3;
        d.events.push_back({v, -1, -(i + 1), (double)date});
    }

    if (argc == 1) {
        freopen("data/ships.txt", "r", stdin);
    } else {
        freopen(argv[8], "r", stdin);
    }
    int ships;
    cin >> ships;
    d.ships.resize(ships + 1);
    for (int i = 0; i < ships; ++i) {
        int from, to, day; double sp1, sp1conv, sp2, sp2conv, sp3, sp3conv;
        cin >> from >> to >> day >> sp3 >> sp3conv >> sp2 >> sp2conv >> sp1 >> sp1conv;
        d.ships[i + 1].sp1 = sp1;
        d.ships[i + 1].sp2 = sp2;
        d.ships[i + 1].sp3 = sp3;
        d.ships[i + 1].sp1conv = sp1conv;
        d.ships[i + 1].sp2conv = sp2conv;
        d.ships[i + 1].sp3conv = sp3conv;

        int good_level = 1;
        if (d.ships[i + 1].sp1conv <= 1e-2) good_level = 2;
        if (d.ships[i + 1].sp2conv <= 1e-2) good_level = 3;

        if (get_ice(from, from, day).first < good_level) {
            cerr << "Query rejected ship " << i + 1 << " has invalid start location" << endl; 
        } else{
            d.events.push_back({from, to, i + 1, (double)day});
        }
    }
}
