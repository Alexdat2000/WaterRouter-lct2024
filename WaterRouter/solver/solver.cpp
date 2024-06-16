#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
#include <filesystem>
#include <cassert>
#include "solver.h"

const double FINITE_EDGE = 5.8, TIME_TOLL = 1.5;
const bool RUN_CHECK = true;

using namespace std;

dataset all_data, data_copy;

int best_adj(int ev_id, int flag = 1) {
    int v = all_data.events[ev_id].from;
    assert(all_data.events[ev_id].ship_id > 0);
    int fr = all_data.events[ev_id].to;
    pair<double, int> opt = {INFINITY, -1};

    int id = all_data.events[ev_id].ship_id;
    int good_level = 1;
    if (all_data.ships[id].sp1conv <= 1e-2) good_level = 2;
    if (all_data.ships[id].sp2conv <= 1e-2) good_level = 3;
    
    for (auto to: all_data.gr[v]) {
        double add = edge_cost_convoyed(v, to, ev_id, all_data.events[ev_id].time);
        if (!flag) add = edge_cost_not_convoyed(v, to, ev_id, all_data.events[ev_id].time);
        if (opt.second == -1 || (edge_dist(fr, to, good_level, all_data.events[ev_id].time) + add < opt.first)) {
            opt = {edge_dist(fr, to, good_level, all_data.events[ev_id].time) + add, to};
        }
    }

    return opt.second;
}

bool can_solo(int ev_id) {
    int best_adj0 = best_adj(ev_id, 0);
    int ship_from = all_data.events[ev_id].from, ship_to = all_data.events[ev_id].to;
    double cur_time = all_data.events[ev_id].time, dist_cut = edge_dist(best_adj0, ship_to, 1, cur_time), dist_whole = edge_dist(ship_from, ship_to, 1, cur_time), dist_edge = edge_cost_not_convoyed(ship_from, best_adj0, ev_id, cur_time);
    return (dist_edge <= FINITE_EDGE && dist_cut < dist_whole);
}

bool release(int ev_id) {
    int id = all_data.events[ev_id].ship_id, v = all_data.events[ev_id].from;
    double date =all_data.events[ev_id].time;
    int good_level = 1;
    if (all_data.ships[id].sp1conv <= 1e-2) good_level = 2;
    if (all_data.ships[id].sp2conv <= 1e-2) good_level = 3;
    return get_ice(v, v, date).first >= good_level;
}

int main(int argc, char *argv[]) {
    auto start_time = clock();
    input(all_data, argc, argv);
    if (RUN_CHECK) data_copy = all_data;
    vector<movement> answer;

    vector<int> prior(all_data.ships.size(), 0);
    double last = 0, first = INFINITY, total_no_ice = 0;
    while (all_data.events.size() + 1 != all_data.iceships.size()) {
        for (int i = 0; i < all_data.events.size(); ++i) {
            if (all_data.events[i].ship_id > 0 && can_solo(i)) prior[all_data.events[i].ship_id] = 0;
            if (all_data.events[i].ship_id > 0) prior[all_data.events[i].ship_id] = 0;
        }
        stable_sort(all_data.events.begin(), all_data.events.end(), [&](const event &a, const event &b) {
            return make_tuple(a.ship_id > 0 ? prior[a.ship_id] : 0, a.ship_id < 0, a.time) < make_tuple(b.ship_id > 0 ? prior[b.ship_id] : 0, b.ship_id < 0, b.time);
        });
        first = min(first, all_data.events[0].time);
        assert(all_data.events[0].ship_id > 0);

        movement cur_mov;
        int best_adj0 = best_adj(0, 0);
        int ship_from = all_data.events[0].from, ship_to = all_data.events[0].to;
        double cur_time = all_data.events[0].time, dist_cut = edge_dist(best_adj0, ship_to, 1, cur_time), dist_whole = edge_dist(ship_from, ship_to, 1, cur_time), dist_edge = edge_cost_not_convoyed(ship_from, best_adj0, 0, cur_time);
        if (can_solo(0)) { // Try to push ship without anything interfering case
            cur_mov = {cur_time, cur_time + dist_edge, ship_from, best_adj0, {all_data.events[0].ship_id}};
            prior[all_data.events[0].ship_id] = 0;
        } else {
            pair<double, int> best = {INFINITY, -1};
            for (int i = 1; i < all_data.events.size(); ++i) {
                if (all_data.events[i].ship_id > 0) continue;
                double tneed = (all_data.events[i].time + honest_edge_dist(all_data.events[i].from, all_data.events[0].from, all_data.events[0].time, i) - all_data.events[0].time);
                //if (locked[-all_data.events[i].ship_id] != all_data.events[0].ship_id && locked[-all_data.events[i].ship_id] != 0) continue;

                int count_tied = 1;
                for (auto ev : all_data.events) {
                    if (ev.from == all_data.events[i].from && abs(all_data.events[i].time - ev.time) <= 1e-2) count_tied++;
                }

                tneed = max(tneed, double(0));
                tneed += 10;
                if (count_tied > 0 && all_data.events[0].from != all_data.events[i].from) tneed *= count_tied;

                if (best.second == -1 || best.first > tneed) {
                    best = {tneed, i};
                }
            }

            assert(best.second != -1);
            prior[all_data.events[0].ship_id] = -1;
        
            int v = all_data.events[best.second].from, to;
            if (v != all_data.events[0].from) {
                pair<double, int> best_to = {INFINITY, -1};
                for (auto to: all_data.gr[v]) {
                    double len = edge_dist(v, to, 1, all_data.events[0].time) + edge_dist(to, all_data.events[0].from, 1, all_data.events[0].time);

                    if (best_to.second == -1 || best_to.first > len) {
                        best_to = {len, to};
                    }
                }

                assert(best_to.second != -1);
                to = best_to.second;
            } else {
                to = best_adj(0, 1);
            } 

            vector<pair<double, int>> srt;
            for (int i = 0; i < all_data.events.size(); ++i) {
                if (all_data.events[i].ship_id < 0 || all_data.events[i].from != v) continue;
                int good_level = 1, id = all_data.events[i].ship_id;
                if (all_data.ships[id].sp1conv <= 1e-2) good_level = 2;
                if (all_data.ships[id].sp2conv <= 1e-2) good_level = 3;
                if (best_adj(i) != to && get_ice(v, v, all_data.events[i].time).first >= good_level) continue;
                if (i != 0 && all_data.events[i].time > all_data.events[best.second].time + TIME_TOLL) continue;
                if (v == all_data.events[0].from && all_data.events[i].time > all_data.events[0].time + TIME_TOLL) continue;
                // Add some smarter check for okay edges and better metric

                srt.push_back({all_data.events[i].time, i});
            }

            sort(srt.begin(), srt.end());
            cur_mov = {0, 0, v, to, {all_data.events[best.second].ship_id}};
            cur_mov.start = all_data.events[best.second].time;
            for (int i = 0; i < min(3, int(srt.size())); ++i) {
                cur_mov.start = max(cur_mov.start, all_data.events[srt[i].second].time);
                cur_mov.ships.push_back(all_data.events[srt[i].second].ship_id);
            }
            cur_mov.end = edge_cost_convoyed(v, to, best.second, cur_mov.start);
            for (int i = 0; i < min(3, int(srt.size())); ++i) {
                cur_mov.end = max(cur_mov.end, edge_cost_convoyed(v, to, srt[i].second, cur_mov.start));
            }

            cur_mov.end += cur_mov.start;
        }

        // Applying cur_mov to events
        std::vector<event> events;
        for (const auto &ship: all_data.events) {
            bool flag = false;
            for (auto s: cur_mov.ships) {
                if (s == ship.ship_id) flag = true;
            }

            if (flag) {
                if (ship.ship_id > 0) {
                    total_no_ice += cur_mov.end - ship.time;
                }
                if (cur_mov.to != ship.to) {
                    events.push_back({cur_mov.to, ship.to, ship.ship_id, cur_mov.end});
                }
            } else {
                events.push_back(ship);
            }
        }
        all_data.events = events;
        answer.push_back(cur_mov);

        // Recalculating time metrics
        last = max(last, answer.back().end);
        assert(cur_mov.ships.size() <= 4);
        assert(cur_mov.ships.size() == 1 || (cur_mov.ships[0] < 0));
    }

    cout << last - first << " " << total_no_ice << " " << answer.size() << "\n";
    cout << "Elapsed time: " << double(clock() - start_time) / CLOCKS_PER_SEC << endl;
    
    output(answer, argc, argv);
    if (RUN_CHECK) check(answer);

    return 0;
}