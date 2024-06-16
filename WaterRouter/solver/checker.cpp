#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
#include <filesystem>
#include <cassert>
#include "solver.h"

const double EPS = 1e-4, WAIT_TIME = 1e-1;
#define INCORECT_FROM_POSITION 1
#define INCORRECT_TIME_OF_MOVEMENT 2
#define EMPTY_MOVEMENT 4
#define SPEED_EXCEEDED 8
#define CONVOY_SIZE_EXCEEDED 16
#define INCORRECT_CONVOY 32
#define ABANDONED_SHIP 64
#define DESTINATION_UNREACHED 128

using namespace std;

int check(const vector<movement>& answer) {
    vector<int> pos(all_data.ships.size()), ice_pos(all_data.iceships.size());
    vector<double> time(all_data.ships.size()), ice_time(all_data.iceships.size());

    for (const auto& ev : data_copy.events) {
        if (ev.ship_id < 0) ice_pos[-ev.ship_id] = ev.from;
        if (ev.ship_id > 0) pos[ev.ship_id] = ev.from;
        if (ev.ship_id < 0) ice_time[-ev.ship_id] = ev.time;
        if (ev.ship_id > 0) time[ev.ship_id] = ev.time;
    }

    int error = 0;

    for (const auto& mv : answer) {
        if (mv.ships.size() == 0) {
            cerr << "Error: emtpy movement" << endl;
            error |= EMPTY_MOVEMENT;
        }
        if (mv.ships.size() > 4) {
            cerr << "Error: convoy size cannot exceed 4" << endl;
            error |= CONVOY_SIZE_EXCEEDED;
        }
        if (mv.ships.size() > 1 && mv.ships[0] > 0) {
            cerr << "Error: convoy must be led by an icebreaker" << endl;
            error |= INCORRECT_CONVOY;
        }
        
        bool convoyed = (mv.ships[0] < 0);
        for (auto ship : mv.ships) {
            if (ship > 0) {
                if (!(mv.from == pos[ship])) {
                    cerr << "Error: ship with id " << ship << " tried to move from point " << mv.from << " at time " << mv.start << " when it actually was at position " << pos[ship] << endl;
                    error |= INCORECT_FROM_POSITION;
                }
                if (!(mv.start >= time[ship] - EPS)) {
                    cerr << "Error: ship with id " << ship << " tried to move from point " << mv.from << " at time " << mv.start << " when its previous action ended at time " << time[ship] << endl;
                    error |= INCORRECT_TIME_OF_MOVEMENT;
                }

                int good_level = 1;
                if (data_copy.ships[ship].sp1conv <= 1e-2) good_level = 2;
                if (data_copy.ships[ship].sp2conv <= 1e-2) good_level = 3;

                if (mv.start - EPS > time[ship] && get_ice(pos[ship], pos[ship], time[ship]).first < good_level) {
                    cerr << "Error: ship is abandoned by an icebreaker in heavy ice" << endl;
                    error |= ABANDONED_SHIP;
                }

                pos[ship] = mv.to;
                time[ship] = mv.end;

                //if (mv.start)
            } else if (ship < 0) {
                if (!(mv.from == ice_pos[-ship])) {
                    cerr << "Error: iceship with id " << -ship << " tried to move from point " << mv.from << " at time " << mv.start << " when it actually was at position " << pos[-ship] << endl;
                    error |= INCORECT_FROM_POSITION;
                }

                if (!(mv.start >= ice_time[-ship] - EPS)) {
                    cerr << "Error: iceship with id " << -ship << " tried to move from point " << mv.from << " at time " << mv.start << " when its previous action ended at time " << ice_time[-ship] << endl;
                    error |= INCORRECT_TIME_OF_MOVEMENT;
                }

                ice_pos[-ship] = mv.to;
                ice_time[-ship] = mv.end;
            }

            if (convoyed) {
                if (edge_cost_convoyed_ship(mv.from, mv.to, ship, mv.start) > mv.end - mv.start + (1e-2)) {
                    cerr << "Error: ship " << ship << " is not fast enough to move from point " << mv.from << " to " << mv.to << " in " << mv.end - mv.start << " time" << endl;
                    error |= SPEED_EXCEEDED;
                }
            } else {
                if (edge_cost_not_convoyed_ship(mv.from, mv.to, ship, mv.start) > mv.end - mv.start + (1e-2)) {
                    cerr << "Error: ship " << ship << " is not fast enough to move from point " << mv.from << " to " << mv.to << " in " << mv.end - mv.start << " time" << endl;
                    error |= SPEED_EXCEEDED;
                }
            }
        }
    }

    for (auto ev : data_copy.events) {
        if (ev.ship_id > 0 && ev.to != pos[ev.ship_id]) {
            cerr << "Error: ship " << ev.ship_id << " did not reach its destination" << endl;
            error |= DESTINATION_UNREACHED;
        }
    }

    if (error == 0) {
        cerr << "Checker found no errors" << endl;
    }
    return error;
}