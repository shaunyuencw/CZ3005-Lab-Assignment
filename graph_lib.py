# Imports
import json

from queue import PriorityQueue
from math import radians, cos, sin, asin, sqrt
import time

# Opens file and return data as a dictionary
def load_json(file_name : str) -> dict:
    with open(file_name, 'r') as file:
        data_dict = json.load(file)
    return data_dict

# return traced and reversed path
def trace_path(parent, start, end, toPrint):
    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.reverse()
    if toPrint:
        print_path(path)
    return path

# Print out path
def print_path(path: list[str]):
    print("S->", end="")
    for node in path[1:-1]:
        print(f"{node}->", end="")
    print("T")

# Graph structure with helper functions
class Graph:
    def __init__(self, input_graph = None, input_coords = None, input_dists = None, input_cost = None):
        # Load and initialize graph

        if input_graph == None or input_coords == None or input_dists == None or input_cost == None:
            print(f"Initializing graph from data file")
            print(f"Loading graph from G.json")
            self.adj_list = load_json("data/G.json")

            print(f"Loading coordinates from Coord.json")
            self.coords = load_json("data/Coord.json")

            print(f"Loading distances from Dist.json")
            self.dists = load_json("data/Dist.json")

            print(f"Loading costs from Cost.json")
            self.costs = load_json("data/Cost.json")

            self.previous_path = {}
            self.path = []
            print(f"Graph initialized")
        else:
            print(f"Initializing test graph from inputs")
            self.adj_list = input_graph
            self.coords = input_coords
            self.dists = input_dists
            self.costs = input_cost
            self.previous_path = {}
            self.path = []
            print(f"Graph initialized")    

    # Get and return adjacent nodes as a list
    def get_adj_nodes(self, node: str) -> 'list[str]':
        return self.adj_list[node]

    # Get and return coordinates of a node
    def get_coordinates(self, node: str) -> 'list[float, float]':
        return self.coords[node]

    # Get and return distance between two nodes
    def get_distance(self, node_from: str, node_to: str) -> float:
        return self.dists[f"{node_from},{node_to}"]

    # Get and return cost between two nodes
    def get_cost(self, node_from: str, node_to: str) -> float:
        return self.costs[f"{node_from},{node_to}"]

    # Test functions 
    def test_func(self):
        test_val = self.costs["2,12"]
        print(test_val)

    # Print path
    def print_path(self):
        print("S->", end="")
        for node in self.path[1:-1]:
            print(f"{node}->", end="")
        print("T")

    # Return total distance of path
    def calculate_distance(self) -> float:
        total_distance = 0
        previous_node = self.path[0]
        for node in self.path[1:]:
            # Increment by previous node and next node
            total_distance += self.get_distance(previous_node, node)
            previous_node = node
        
        # Round off to 2 decimal points
        total_distance = round(total_distance, 2)
        print(f"Distance of path: {total_distance}")
        return total_distance

    # Return total cost of path
    def calculate_cost(self) -> float:
        total_cost = 0
        previous_node = self.path[0]
        for node in self.path[1:]:
            # Increment by previous node and next node
            total_cost += self.get_cost(previous_node, node)
            previous_node = node
        
        # Round off to 2 decimal points
        total_cost = round(total_cost, 2)
        print(f"Cost of path: {total_cost}")
        return total_cost

    # Gets and return Euclidean distance (Bird's eye) between two nodes
    def get_euclidean_distance(self, node_from: str, node_to: str) -> float:
        x_from, y_from = self.get_coordinates(node_from)
        x_to, y_to = self.get_coordinates(node_to)

        # Pythagorean theorem
        return ((x_from - x_to) ** 2 + (y_from - y_to) ** 2) ** 0.5

    # Gets and return Manhattan distance (Grid distance) between two nodes
    def get_manhattan_distance(self, node_from: str, node_to) -> float:
        x_from, y_from = self.get_coordinates(node_from)
        x_to, y_to = self.get_coordinates(node_to)
        
        # Move by x_axis then by y_axis
        return abs(x_from - x_to) + abs(y_from - y_to)

    # A* Algorithm
    def a_star_search(self, start_node: str, end_node: str, heuristic_multiplier, dist_type, print_path):
        start_time = time.time()
        dist_tracker: dict[str, float] = {start_node: 0.}
        heuristic_tracker: dict[str, float] = {start_node: 0.}
        cost_tracker: dict[str, float] = {start_node: 0.}
        p_queue = PriorityQueue()

        # Enqueue starting node
        p_queue.put((0, start_node))
        self.previous_path = {}

        while not p_queue.empty():
            a_star_cost, current_node = p_queue.get()

            # Stop searching if target node is found
            if current_node == end_node:
                self.path = trace_path(self.previous_path, start_node, end_node, print_path)

                #return(self.path, dist_tracker[end_node], cost_tracker[end_node])
                return (time.time() - start_time, len(dist_tracker), dist_tracker[end_node])

            # Process adjacent nodes using cost function heuristic
            adjacent_nodes = self.get_adj_nodes(current_node)
            for adj_node in adjacent_nodes:
                # Get new distance and cost
                new_distance = dist_tracker[current_node] + self.get_distance(current_node, adj_node)
                new_cost = cost_tracker[current_node] + self.get_cost(current_node, adj_node)

                #! Heuristic
                #* Euclidean distance (Bird's Eye / Pythagorean theorem)
                if dist_type == "euclidean":
                    herustic_cost = self.get_euclidean_distance(adj_node, end_node)

                #* Manhattan distance (Grid Distance / x_coord distance + y_coord distance)
                elif dist_type == "manhattan":
                    herustic_cost = self.get_manhattan_distance(adj_node, end_node)

                a_star_cost = new_distance + (herustic_cost * heuristic_multiplier)

                # Check if first time visiting or adjusted distance is shorter than previous
                if adj_node not in heuristic_tracker or a_star_cost < heuristic_tracker[adj_node]:
                    dist_tracker[adj_node] = new_distance
                    cost_tracker[adj_node] = new_cost
                    heuristic_tracker[adj_node] = a_star_cost

                    p_queue.put((a_star_cost, adj_node))

                    # Add parent tracer
                    self.previous_path[adj_node] = current_node

        #! No path found            
        return (time.time() - start_time, len(dist_tracker), dist_tracker[end_node])

    # Uniform Cost Search Algorithm
    def ucs_search(self, start_node: str, end_node: str):
        dist_tracker: dict[str, float] = {start_node: 0.}
        cost_tracker: dict[str, float] = {start_node: 0.}
        p_queue = PriorityQueue()

        # Enqueue starting node
        p_queue.put((0, start_node))
        self.previous_path = {}

        while not p_queue.empty():
            distance, current_node = p_queue.get()

            # Stop searching if target node is found
            if current_node == end_node:
                self.path = trace_path(self.previous_path, start_node, end_node)

                return(self.path, dist_tracker[end_node], cost_tracker[end_node])

            # Process adjacent nodes using cost function heuristic
            adjacent_nodes = self.get_adj_nodes(current_node)
            for adj_node in adjacent_nodes:
                # Get new distance and cost
                new_distance = dist_tracker[current_node] + self.get_distance(current_node, adj_node)
                new_cost = cost_tracker[current_node] + self.get_cost(current_node, adj_node)

                # Check if first time visiting or adjusted distance is shorter than previous
                if adj_node not in dist_tracker or new_distance < dist_tracker[adj_node]:
                    dist_tracker[adj_node] = new_distance
                    cost_tracker[adj_node] = new_cost

                    p_queue.put((new_distance, adj_node))

                    # Add parent tracer
                    self.previous_path[adj_node] = current_node

        #! No path found            
        return None