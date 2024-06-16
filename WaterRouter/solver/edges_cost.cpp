#include <cmath>
#include <cassert>
#include "solver.h"
#include <iostream>

using namespace std;

const double R = 3443.9185;

double toRadians(double degree) {
    return degree * M_PI / 180.0;
}

double haversineDistance(double lat1, double lon1, double lat2, double lon2) {
    lat1 = toRadians(lat1);
    lon1 = toRadians(lon1);
    lat2 = toRadians(lat2);
    lon2 = toRadians(lon2);

    double dlat = lat2 - lat1;
    double dlon = lon2 - lon1;
    double a = sin(dlat / 2) * sin(dlat / 2) + cos(lat1) * cos(lat2) * sin(dlon / 2) * sin(dlon / 2);
    double c = 2 * atan2(sqrt(a), sqrt(1 - a));
    double distance = R * c;

    return distance;
}

double haver(int from, int to) {
    // Calculates haversine distance between vertexes
    double x = all_data.points[from].first, y = all_data.points[from].second;
    double x2 = all_data.points[to].first, y2 = all_data.points[to].second;
    return haversineDistance(x, y, x2, y2);
}

template <typename T>
bool chkmin(T& value, const T& new_value) {
    if (value > new_value) {
        value = new_value;
        return true;
    }
    return false;
}

pair<int, int> get_position(int v) {
    // gets closest position to vertex on a grid
    if (all_data.closest[v].first != -1) return all_data.closest[v];
    pair<int, int> pos{0, 0};
    double min_dist = INFINITY;
    for (int i = 0; i < (int) all_data.lat.size(); i++) {
        for (int j = 0; j < (int) all_data.lat[i].size(); j++) {
            if (chkmin(min_dist, haversineDistance(all_data.lat[i][j], all_data.lon[i][j], all_data.points[v].first,
                                  all_data.points[v].second))) {
                pos = {i, j};
            }
        }
    }
    return all_data.closest[v] = pos;
}

struct line { 
    // Stores line in a format a * x + b * y + c = 0
    double a, b, c;

    explicit line(int x, int y, int x2, int y2) {
        a = y - y2;
        b = x2 - x;
        c = -a * x - b * y;
    }

    double get(int x, int y) {
        return abs(a * x + b * y + c) / sqrt(a * a + b * b);
    }
};

int ice_classification(int hardness) {
    if (hardness < 10) return 3;
    if (10 <= hardness && hardness <= 14) return 1;
    if (15 <= hardness && hardness <= 19) return 2;
    return 3;
}

pair<int, double> get_ice(int v, int u, double date) {
    // Gets hardness level of ice between vertices at a given time
    auto [xv, yv] = get_position(v);
    auto [xu, yu] = get_position(u);
    int day = 0;
    while (day + 1 < (int) all_data.days.size() && all_data.days[day + 1] <= date) {
        day++;
    }
    auto& table = all_data.ice[day];
    int result_ice = std::min(ice_classification(table[xv][yv]), ice_classification(table[xu][yu]));
    if (xv == xu && yv == yu) {
        return {result_ice, table[xv][yv]};
    }
    if (xu < xv) {
        swap(xv, xu);
        swap(yv, yu);
    }
    line path_line(xv, yv, xu, yu);
    // Uses two pointers to find an interval [l, r] of grid cells intersecting our line
    double sum = table[xv][yv] + table[xu][yu], cnt = 2;
    for (int i = xv, l = 0, r = (int) table[0].size() - 1; i <= xu; i++) {
        while (l > 0 && path_line.get(i, l - 1) < 1e-2) {
            l--;
        }
        while (r + 1 < (int) table[0].size() && path_line.get(i, r + 1) < 1e-2) {
            r++;
        }
        while (l < r && path_line.get(i, l) > 1e-2) {
            l++;
        }
        while (l < r && path_line.get(i, r) > 1e-2) {
            r--;
        }
        for (int j = l; j <= r; j++) {
            chkmin(result_ice, ice_classification(table[i][j]));
            ++cnt;
            sum += max(0, table[i][j]);
        }
    }
    return {result_ice, sum / cnt};
}

double edge_cost_convoyed_ship(int from, int to, int ship_id, double date) {
    double len = haver(from, to);
    pair<int, double> ice_q = get_ice(from, to, date);
    int ice = ice_q.first;
    double actual_speed = 0;
    ship_info ship;
    if (ship_id < 0) ship = all_data.iceships[-ship_id];
    else ship = all_data.ships[ship_id];

    if (ice == 1) actual_speed = ship.sp1conv;
    if (ice == 2) actual_speed = ship.sp2conv;
    if (ice == 3) actual_speed = ship.sp3conv;

    if (ship_id < 0 && ice < 3) return len / (ice_q.second * (ship.sp1conv / actual_speed)) / 24;

    return len / actual_speed / 24;
}

double edge_cost_convoyed(int from, int to, int ev_id, double date) {
    return edge_cost_convoyed_ship(from, to, all_data.events[ev_id].ship_id, date);
}

double edge_cost_not_convoyed_ship(int from, int to, int ship_id, double date) {
    double len = haver(from, to);
    int ice = get_ice(from, to, date).first;
    assert(ship_id > 0);
    double actual_speed = 0;
    ship_info ship;
    if (ship_id < 0) assert(false);
    else ship = all_data.ships[ship_id];

    if (ice == 1) actual_speed = ship.sp1;
    if (ice == 2) actual_speed = ship.sp2;
    if (ice == 3) actual_speed = ship.sp3;
    
    return len / actual_speed / 24;
}

double edge_cost_not_convoyed(int from, int to, int ev_id, double date) {
    return edge_cost_not_convoyed_ship(from, to, all_data.events[ev_id].ship_id, date);
}

double edge_dist(int from, int to, int ice, double date) {
    // Finds distance between two vertices at a given time under assumption that we are allowed to only use values of hardness >= ice
    int day = 0;
    while (day + 1 < (int) all_data.days.size() && all_data.days[day + 1] <= date) {
        day++;
    }

    int n = all_data.gr.size();
    assert(from < n && to < n);
    assert(ice != 0);

    if (all_data.dists[ice].size() > day) {
        return all_data.dists[ice - 1][day][from][to];
    } else {
        while (true) {
            int cur_day = all_data.dists[0].size();
            all_data.dists[0].resize(cur_day + 1);
            all_data.dists[1].resize(cur_day + 1);
            all_data.dists[2].resize(cur_day + 1);
            assert(cur_day <= day);
            for (int ice = 1; ice <= 3; ++ice) {
                vector<vector<double>> dists(n, vector<double>(n, INFINITY));
                for (int i = 0; i < n; ++i) {
                    dists[i][i] = 0;
                    for (auto to : all_data.gr[i]) {
                        if (get_ice(i, to, all_data.days[cur_day] + 1e-2).first >= ice) dists[i][to] = (dists[to][i] = min(dists[to][i], haver(to, i)));
                    }
                }

                for (int k = 0; k < n; ++k) {
                    for (int j = 0; j < n; ++j) {
                        for (int i = 0; i < n; ++i) dists[i][j] = min(dists[i][j], dists[i][k] + dists[k][j]);
                    }
                }

                all_data.dists[ice - 1][cur_day] = dists;
            }

            if (cur_day == day) break;
        }
    }
    
    return all_data.dists[ice - 1][day][from][to];
}

double honest_edge_dist(int from, int to, double date, int ev_id) {
    // Finds distance between two vertices at a given time. Works slower than edge_dist
    int n = all_data.gr.size();
    assert(from < n && to < n);

    vector<double> dists(n, INFINITY);
    vector<int> used(n);
    dists[from] = 0;
    
    while (true) {
        int cur_best = -1;
        for (int i = 0; i < n; ++i) {
            if (!used[i] && (cur_best == -1 || dists[cur_best] > dists[i])) cur_best = i;
        }

        used[cur_best] = 1;
        if (cur_best == to) return dists[to];

        for (auto to : all_data.gr[cur_best]) {
            dists[to] = min(dists[to], dists[cur_best] + edge_cost_convoyed(cur_best, to, ev_id, date));
        }
    }

    assert(false);
}
