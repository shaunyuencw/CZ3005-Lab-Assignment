#library courtesy of Richard

# Imports
from operator import is_
import sys
import time
import pygame

from queue import PriorityQueue
from graph_lib import Graph

# pygame constants
WINDOW_SIZE = (WIDTH, HEIGHT) = 512, 512
COLORS = {
    "WHITE" : (255, 255, 255),
    "BLUE" : (0, 0, 255),
    "GREEN" : (0, 255, 0),
    "RED" : (255, 0, 0), 
    "BLACK" : (0, 0, 0)
}

# coordinate limits for NYC dataset
min_x = -74499998
max_x = -73500016
min_y = 40300009
max_y = 41299997

w_scale = WIDTH / ((-73500016) - (-74499998))
h_scale = HEIGHT / (41299997 - 40300009)

# scale dataset to fit Window
def scale_coordinate(coord: 'list[float, float]'):
    return [(coord[0] - min_x) * w_scale, (coord[1] - min_y) * h_scale]

# return path trace and reverse to display path from start to terminal node
def trace_path(parent, start, end):
    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.reverse()
    print_path(path)
    return path

# print out path
def print_path(path: 'list[str]'):
    print("S->", end="")
    for node in path[1:-1]:
        print(f"{node}->", end="")
    print("T")

class Window:
    # Window constructor
    def __init__(self, graph):
        self.graph = graph
        self.window = None

    # Draw node on window
    def draw_node(self, coord: 'list[float, float]', colour: 'tuple[int, int, int]' = COLORS["RED"], size: int = 1):
        scaled_coord = scale_coordinate(coord)
        pygame.draw.circle(self.window, colour, scaled_coord, size)

    # Draw edge between two nodes
    def draw_edge(self, node_from: str, node_to: str, colour: 'tuple[int, int, int]' = COLORS["RED"]):
        node_from_coord = self.graph.get_coordinates(node_from)
        scaled_node_from_coord = scale_coordinate(node_from_coord)
        node_to_coord = self.graph.get_coordinates(node_to)
        scaled_node_to_coord = scale_coordinate(node_to_coord)
        pygame.draw.line(self.window, colour, scaled_node_from_coord, scaled_node_to_coord)

    # Relaxed shortest distance with no energy constraint, using Uniform Cost Search
    def relaxed_shortest_distance(self, start_node, end_node):
        pygame.init()

        font = pygame.font.SysFont("monospace", 15)
        self.window = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Search Path Graph Visualization")

        is_searching = True
        is_setup = True # To run setup once

        # Setup initialization
        cost_tracker: dict[str, float] = {start_node: 0.}
        dist_tracker: dict[str, float] = {start_node: 0.}

        p_queue = PriorityQueue()

        # Enqueue starting node
        p_queue.put((0, start_node))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
            # Draw start and end vertices
            start_coord = self.graph.get_coordinates(start_node)
            self.draw_node(start_coord, COLORS["BLACK"], 3)
            start_label = font.render(start_node, False, COLORS["BLACK"], COLORS["WHITE"])
            scaled_coords = scale_coordinate(start_coord)
    
            self.window.blit(start_label, scaled_coords)

            end_coord = self.graph.get_coordinates(end_node)
            self.draw_node(end_coord, COLORS["BLACK"], 3)
            end_label = font.render(end_node, False, COLORS["BLACK"], COLORS["WHITE"])
            self.window.blit(end_label, scale_coordinate(end_coord))

            # Run once to render start
            if is_setup:
                self.window.fill(COLORS["WHITE"])
                # Draw every node
                for _, coordinate in self.graph.coords.items():
                    self.draw_node(coordinate)

                for node_from, adjacent_nodes in self.graph.adj_list.items():
                    for node_to in adjacent_nodes:
                        self.draw_edge(node_from, node_to)

                # End setup        
                is_setup = False
                start_time = time.time()

            # Run if still searching and there are still nodes to explore
            if is_searching and p_queue.empty() == False:
                distance, current_node = p_queue.get()
                coordinates = self.graph.get_coordinates(current_node)
                self.draw_node(coordinates, COLORS["BLUE"])

                # Stop searching if target node is found
                if current_node == end_node:
                    is_searching = False #* Stop searching 
                    self.graph.path = trace_path(self.graph.previous_path, start_node, end_node)
                    end_time = time.time()
                    print(f"Total distance: {dist_tracker[end_node]}")
                    print(f"Total cost: {cost_tracker[end_node]}")
                    print(f"No. of Edges: {len(self.graph.path) - 1}")
                    print(f"Explored {len(dist_tracker)} nodes")
                    print(f"Time elapsed: {round(end_time - start_time, 2)} seconds.")

                # Process adjacent nodes
                adjacent_nodes = self.graph.get_adj_nodes(current_node)
                for adj_node in adjacent_nodes:
                    # Get new distance and cost
                    new_distance = dist_tracker[current_node] + self.graph.get_distance(current_node, adj_node)
                    new_cost = cost_tracker[current_node] + self.graph.get_cost(current_node, adj_node)

                    # Check if first time visiting or distance is shorter than previous distance
                    if adj_node not in dist_tracker or new_distance < dist_tracker[adj_node]:
                        dist_tracker[adj_node] = new_distance
                        cost_tracker[adj_node] = new_cost

                        # Draw frontier
                        frontier = self.graph.get_coordinates(adj_node)
                        self.draw_node(frontier, COLORS["GREEN"])
                        p_queue.put((new_distance, adj_node))

                        # Add parent tracer
                        self.graph.previous_path[adj_node] = current_node
                
                #! If no possible paths
                if is_searching and p_queue.empty():
                    label_text = font.render("No Possible Path",
                        False, COLORS["BLACK"], COLORS["WHITE"]
                    )
                    label_frame = label_text.get_rect(center=(WIDTH / 2, HEIGHT /2))
                    # Display label
                    self.window.blit(label_text, label_frame)
                    print(f"No path found.")
                    time.sleep(5)
                    pygame.quit()
                    is_searching = False # Stop searching
                
                #* Draw valid path
                if self.graph.path:
                    node_from = self.graph.path[0]
                    for node_to in self.graph.path[1:]:
                        self.draw_node(self.graph.get_coordinates(node_to), COLORS["GREEN"])
                        self.draw_edge(node_from, node_to, COLORS["GREEN"])
                        node_from = node_to # Process next in path

                    label_text = font.render(
                        "Path found, more details in output.",
                        False, COLORS["BLACK"], COLORS["WHITE"]
                    )
                    label_frame = label_text.get_rect(center = (WIDTH / 2, HEIGHT / 2))
                    self.window.blit(label_text, label_frame)

                    pygame.display.flip() #Update display
                    time.sleep(5)
                    pygame.quit()

                    #! Reset
                    self.graph.path = []
                    self.graph.previous_path = {}
                    break

                pygame.display.flip() #Update display

    # Constraint shortest distance with energy budget, using Uniform Cost Search
    def constraint_shortest_distance(self, start_node, end_node, budget):
        pygame.init()

        font = pygame.font.SysFont("monospace", 15)
        self.window = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Search Path Graph Visualization")

        is_searching = True
        is_setup = True # To run setup once

        # Setup initialization
        cost_tracker: dict[str, float] = {start_node: 0.}
        dist_tracker: dict[str, float] = {start_node: 0.}

        p_queue = PriorityQueue()

        # Enqueue starting node
        p_queue.put((0, start_node))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
        # Draw start and end vertices
            start_coord = self.graph.get_coordinates(start_node)
            self.draw_node(start_coord, COLORS["BLACK"], 3)
            start_label = font.render(start_node, False, COLORS["BLACK"], COLORS["WHITE"])
            scaled_coords = scale_coordinate(start_coord)
    
            self.window.blit(start_label, scaled_coords)

            end_coord = self.graph.get_coordinates(end_node)
            self.draw_node(end_coord, COLORS["BLACK"], 3)
            end_label = font.render(end_node, False, COLORS["BLACK"], COLORS["WHITE"])
            self.window.blit(end_label, scale_coordinate(end_coord))

            # Run once to render start
            if is_setup:
                self.window.fill(COLORS["WHITE"])
                # Draw every node
                for _, coordinate in self.graph.coords.items():
                    self.draw_node(coordinate)

                for node_from, adjacent_nodes in self.graph.adj_list.items():
                    for node_to in adjacent_nodes:
                        self.draw_edge(node_from, node_to)

                # End setup        
                is_setup = False
                start_time = time.time()
            
            # Run if still searching and there are still nodes to explore
            if is_searching and p_queue.empty() == False:
                distance, current_node = p_queue.get()
                coordinates = self.graph.get_coordinates(current_node)
                self.draw_node(coordinates, COLORS["GREEN"])

                # Stop searching if target node is found
                if current_node == end_node:
                    is_searching = False #* Stop searching 
                    self.graph.path = trace_path(self.graph.previous_path, start_node, end_node)
                    end_time = time.time()
                    print(f"Total distance: {dist_tracker[end_node]}")
                    print(f"Total cost: {cost_tracker[end_node]}")
                    print(f"No. of Edges: {len(self.graph.path) - 1}")
                    print(f"Explored {len(dist_tracker)} nodes")
                    print(f"Time elapsed: {round(end_time - start_time, 2)} seconds.")

                # Process adjacent nodes
                adjacent_nodes = self.graph.get_adj_nodes(current_node)
                for adj_node in adjacent_nodes:
                    # Get new distance and cost
                    new_distance = dist_tracker[current_node] + self.graph.get_distance(current_node, adj_node)
                    new_cost = cost_tracker[current_node] + self.graph.get_cost(current_node, adj_node)

                    #! Skip this node if energy exceeds our budget
                    if new_cost > budget:
                        continue
            
                    # Check if first time visiting or distance is shorter than previous distance
                    if adj_node not in dist_tracker or new_distance < dist_tracker[adj_node]:
                        dist_tracker[adj_node] = new_distance
                        cost_tracker[adj_node] = new_cost

                        # Draw frontier
                        frontier = self.graph.get_coordinates(adj_node)
                        self.draw_node(frontier, COLORS["GREEN"])
                        p_queue.put((new_distance, adj_node))

                        # Add parent tracer
                        self.graph.previous_path[adj_node] = current_node  

                #! If no possible paths
                if is_searching and p_queue.empty():
                    label_text = font.render("No Possible Path",
                        False, COLORS["BLACK"], COLORS["WHITE"]
                    )
                    label_frame = label_text.get_rect(center=(WIDTH / 2, HEIGHT /2))
                    # Display label
                    self.window.blit(label_text, label_frame)
                    print(f"No path found.")
                    time.sleep(5)
                    pygame.quit()
                    is_searching = False # Stop searching
                
                #* Draw valid path
                if self.graph.path:
                    node_from = self.graph.path[0]
                    for node_to in self.graph.path[1:]:
                        self.draw_node(self.graph.get_coordinates(node_to), COLORS["GREEN"])
                        self.draw_edge(node_from, node_to, COLORS["GREEN"])
                        node_from = node_to # Process next in path

                    label_text = font.render(
                        "Path found, more details in output.",
                        False, COLORS["BLACK"], COLORS["WHITE"]
                    )
                    label_frame = label_text.get_rect(center = (WIDTH / 2, HEIGHT / 2))
                    self.window.blit(label_text, label_frame)

                    pygame.display.flip() #Update display
                    time.sleep(5)
                    pygame.quit()

                    #! Reset
                    self.graph.path = []
                    self.graph.previous_path = {}
                    break

                pygame.display.flip() #Update display

    # Constraint shortest distance with energy budget, using Uniform Cost Search
    def heuristic_constraint_shortest_distance(self, start_node, end_node, budget, heuristic_multiplier, dist_type):
        pygame.init()

        font = pygame.font.SysFont("monospace", 15)
        self.window = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Search Path Graph Visualization")

        is_searching = True
        is_setup = True # To run setup once

        # Setup initialization
        cost_tracker: dict[str, float] = {start_node: 0.}
        heuristic_tracker: dict[str, float] = {start_node: 0.}
        dist_tracker: dict[str, float] = {start_node: 0.}

        p_queue = PriorityQueue()

        # Enqueue starting node
        #! Note: Additional value in tuple
        p_queue.put((0, 0, start_node))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Draw start and end vertices
            start_coord = self.graph.get_coordinates(start_node)
            self.draw_node(start_coord, COLORS["BLACK"], 3)
            start_label = font.render(start_node, False, COLORS["BLACK"], COLORS["WHITE"])
            scaled_coords = scale_coordinate(start_coord)
    
            self.window.blit(start_label, scaled_coords)

            end_coord = self.graph.get_coordinates(end_node)
            self.draw_node(end_coord, COLORS["BLACK"], 3)
            end_label = font.render(end_node, False, COLORS["BLACK"], COLORS["WHITE"])
            self.window.blit(end_label, scale_coordinate(end_coord))

            # Run once to render start
            if is_setup:
                self.window.fill(COLORS["WHITE"])
                # Draw every node
                for _, coordinate in self.graph.coords.items():
                    self.draw_node(coordinate)

                for node_from, adjacent_nodes in self.graph.adj_list.items():
                    for node_to in adjacent_nodes:
                        self.draw_edge(node_from, node_to)

                # End setup        
                is_setup = False
                start_time = time.time()

            # Run if still searching and there are still nodes to explore
            if is_searching and p_queue.empty() == False:
                herustic_cost, nodes_tracker, current_node = p_queue.get()
                coordinates = self.graph.get_coordinates(current_node)
                self.draw_node(coordinates, COLORS["BLUE"])

                # Stop searching if target node is found
                if current_node == end_node:
                    is_searching = False #* Stop searching 
                    self.graph.path = trace_path(self.graph.previous_path, start_node, end_node)
                    end_time = time.time()
                    print(f"Total distance: {dist_tracker[end_node]}")
                    print(f"Total cost: {cost_tracker[end_node]}")
                    print(f"No. of Edges: {len(self.graph.path) - 1}")
                    print(f"Explored {len(dist_tracker)} nodes")
                    print(f"Time elapsed: {round(end_time - start_time, 2)} seconds.")
                    continue

            # Process adjacent nodes using cost function heuristic
            adjacent_nodes = self.graph.get_adj_nodes(current_node)
            for adj_node in adjacent_nodes:
                # Get new distance and cost
                new_distance = dist_tracker[current_node] + self.graph.get_distance(current_node, adj_node)
                new_cost = cost_tracker[current_node] + self.graph.get_cost(current_node, adj_node)

                #! Heuristic
                #* Euclidean distance (Bird's Eye / Pythagorean theorem)
                if dist_type == "euclidean":
                    herustic_cost = self.graph.get_euclidean_distance(adj_node, end_node)

                #* Manhattan distance (Grid Distance / x_coord distance + y_coord distance)
                elif dist_type == "manhattan":
                    herustic_cost = self.graph.get_manhattan_distance(adj_node, end_node)

                a_star_cost = new_distance + (herustic_cost * heuristic_multiplier)

                #! Skip this node if energy exceeds our budget
                if new_cost > budget:
                    continue
        
                # Check if first time visiting or adjusted distance is shorter than previous
                if adj_node not in heuristic_tracker or a_star_cost < heuristic_tracker[adj_node]:
                    dist_tracker[adj_node] = new_distance
                    cost_tracker[adj_node] = new_cost
                    heuristic_tracker[adj_node] = a_star_cost

                    # Draw frontier
                    frontier = self.graph.get_coordinates(adj_node)
                    self.draw_node(frontier, COLORS["GREEN"])
                    p_queue.put((a_star_cost, nodes_tracker, adj_node))

                    # Add parent tracer
                    self.graph.previous_path[adj_node] = current_node

            #! If no possible paths
            if is_searching and p_queue.empty():
                label_text = font.render("No Possible Path",
                    False, COLORS["BLACK"], COLORS["WHITE"]
                )
                label_frame = label_text.get_rect(center=(WIDTH / 2, HEIGHT /2))
                # Display label
                self.window.blit(label_text, label_frame)
                print(f"No path found.")

                time.sleep(5)
                pygame.quit()
                is_searching = False # Stop searching
            
            #* Draw valid path
            if self.graph.path:
                node_from = self.graph.path[0]
                for node_to in self.graph.path[1:]:
                    self.draw_node(self.graph.get_coordinates(node_to), COLORS["GREEN"])
                    self.draw_edge(node_from, node_to, COLORS["GREEN"])
                    node_from = node_to # Process next in path

                label_text = font.render(
                    "Path found, more details in output.",
                    False, COLORS["BLACK"], COLORS["WHITE"]
                )
                label_frame = label_text.get_rect(center = (WIDTH / 2, HEIGHT / 2))
                self.window.blit(label_text, label_frame)

                pygame.display.flip() #Update display
                time.sleep(5)
                pygame.quit()

                #! Reset
                self.graph.path = []
                self.graph.previous_path = {}
                break

            pygame.display.flip() #Update display