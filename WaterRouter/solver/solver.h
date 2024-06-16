#include <vector>

struct event {
    int from, to, ship_id;
    double time;
};

struct ship_info {
    double sp1, sp1conv, sp2, sp2conv, sp3, sp3conv;
    int type;
};

struct dataset {
    int n;
    std::vector<std::pair<double, double>> points;
    std::vector<std::vector<int>> gr;

    struct edge {
        int from, to;
        double pot, hist;
    };
    std::vector<edge> edges;

    std::vector<std::vector<double>> lat, lon;
    std::vector<event> events;

    std::vector<ship_info> ships, iceships;
    std::vector<int> days;
    std::vector<std::vector<std::vector<double>>> dists[3];

    std::vector<std::vector<std::vector<int>>> ice;
    std::vector<std::pair<int, int>> closest;
};

struct movement {
    double start, end;
    int from, to;
    std::vector<int> ships;
};

void input(dataset &d, int argc, char *argv[]);

void output(const std::vector<movement> &ans, int argc, char *argv[]);

std::pair<int, double> get_ice(int v, int u, double date);
double edge_cost_convoyed(int from, int to, int ev_id, double date);
double edge_cost_convoyed_ship(int from, int to, int ship_id, double date);
double edge_cost_not_convoyed(int from, int to, int ev_id, double date);
double edge_cost_not_convoyed_ship(int from, int to, int ship_id, double date);

double edge_dist(int from, int to, int ice, double date);
double honest_edge_dist(int from, int to, double date, int ev_id);

int check(const std::vector<movement>& answer);

extern dataset all_data;
extern dataset data_copy;