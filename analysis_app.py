# Imports
import time
import csv
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
    mult, max_mult, step = 0, 5, 0.01
    while(mult <= max_mult):
        multiplier_list.append(round(mult,2))
        mult += step

    with open("data/euclidean.csv", 'w', newline='') as file:
        writer =csv.writer(file)

        graph = Graph()
        print(multiplier_list)
        print(f"Testing run_time data from node 1 to 50 with different multipliers")
        for multiplier in multiplier_list:
            data = graph.a_star_search('1', '50', multiplier, 'euclidean', False)
            print(f"Multipler {multiplier} : {data[0]} seconds, {data[1]} nodes explored, distance of path {data[2]}")
            writer.writerow([multiplier, data[0], data[1], data[2]])

    with open("data/manhattan.csv", 'w', newline='') as file:
        writer =csv.writer(file)
        for multiplier in multiplier_list:
            data = graph.a_star_search('1', '50', multiplier, 'manhattan', False)
            print(f"Multipler {multiplier} : {data[0]} seconds, {data[1]} nodes explored, distance of path {data[2]}")
            writer.writerow([multiplier, data[0], data[1], data[2]])

if __name__ == "__main__":
    main()