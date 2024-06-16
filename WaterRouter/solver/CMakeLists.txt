cmake_minimum_required(VERSION 3.28)
project(solver)

set(CMAKE_CXX_STANDARD 17)

add_executable(solver solver.cpp input.cpp edges_cost.cpp output.cpp)
