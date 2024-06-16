all:
	g++ solver.cpp edges_cost.cpp input.cpp output.cpp checker.cpp -o solver -Ofast -std=gnu++17 -Wno-unused-result && \
	./solver

san:
	g++ solver.cpp edges_cost.cpp input.cpp output.cpp checker.cpp -o solver -std=gnu++17 -Wno-unused-result -g -Wall -Wextra -D_GLIBCXX_DEBUG -Woverflow -fsanitize=bounds,address,undefined && \
	./solver
