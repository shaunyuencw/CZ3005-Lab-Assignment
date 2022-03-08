# Imports
import time
from queue import PriorityQueue

from graph_lib import Graph
from pygame_lib import Window

def backtrace(parent, start, end):
    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.reverse()
    # print_path(path)
    return path


def print_path(path: list[str]):
    print("S->", end="")
    for node in path[1:-1]:
        print(f"{node}->", end="")
    print("T")

def main():
    multiplier_list = []
    mult, max_mult, step = 0.5, 2, 0.05
    while(mult <= max_mult):
        multiplier_list.append(round(mult,2))
        mult += step

    graph = Graph()
    print(multiplier_list)
    print(f"Testing run_time data from node 1 to 50 with different multipliers")
    for multiplier in multiplier_list:
        data = graph.a_star_search('1', '50', multiplier, 'euclidean', False)
        print(f"Multipler {multiplier} : {round(data[0],3)} seconds, {data[1]} nodes explored, distance of path {round(data[2], 3)}")

if __name__ == "__main__":
    main()