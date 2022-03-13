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


def astar_start(graph, start: str, end: str, heuristic):
    dist_so_far: dict[str, float] = {start: 0.}
    astar_cost_so_far: dict[str, float] = {start: 0.}
    energy_cost_so_far: dict[str, float] = {start: 0.}
    queue = PriorityQueue()
    queue.put((0, start))
    came_from = {}

    while not queue.empty():
        astar_cost, curr_node = queue.get()

        # stop if the current node is the end node
        if curr_node == end:
            path = backtrace(came_from, start, end)
            # print("distance:", dist_so_far[end])
            # print("energy:", energy_cost_so_far[end])
            # print("length of path:", len(graph.path))
            # print("nodes explored: ", len(dist_so_far))
            return (path, dist_so_far[end], energy_cost_so_far[end])

        # add adjacent nodes by cost function
        adjacent_nodes = graph.get_adj_nodes(curr_node)
        for adjacent_node in adjacent_nodes:
            new_dist = dist_so_far[curr_node] + graph.get_distance(curr_node, adjacent_node)
            new_energy_cost = energy_cost_so_far[curr_node] + graph.get_cost(curr_node, adjacent_node)

            # heuristic_cost = graph.euclidean_dist(adjacent_node, end)
            heuristic_cost = graph.get_manhattan_distance(adjacent_node, end)
            new_astar_cost = new_dist + heuristic_cost * heuristic

            # if new node or overall cost is lower than previously calculated cost,
            # add adjacent nodes
            if adjacent_node not in astar_cost_so_far or new_astar_cost < astar_cost_so_far[adjacent_node]:
                dist_so_far[adjacent_node] = new_dist
                energy_cost_so_far[adjacent_node] = new_energy_cost
                astar_cost_so_far[adjacent_node] = new_astar_cost
                queue.put((new_astar_cost, adjacent_node))
                # add parent pointers
                came_from[adjacent_node] = curr_node
    return None


def ucs_dist_start(graph, start, end):
    # initialisation
    energy_cost_so_far: dict[str, float] = {start: 0.}
    dist_so_far: dict[str, float] = {start: 0.}
    queue = PriorityQueue()
    queue.put((0, start))
    came_from = {}

    while queue.queue:
        distance, curr_node = queue.get()

        # stop if the current node is the end node
        if curr_node == end:
            path = backtrace(came_from, start, end)
            # print("distance:", dist_so_far[end])
            # print("energy:", energy_cost_so_far[end])
            # print("length of path:", len(path) - 1)
            # print("nodes explored: ", len(dist_so_far))
            return (path, dist_so_far[end], energy_cost_so_far[end])

        # add adjacent nodes by distance
        adjacent_nodes = graph.get_adj_nodes(curr_node)
        for adjacent_node in adjacent_nodes:
            new_dist = dist_so_far[curr_node] + graph.get_distance(curr_node, adjacent_node)
            new_energy_cost = energy_cost_so_far[curr_node] + graph.get_cost(curr_node, adjacent_node)

            # if new node or overall dist is lower than previously calculated dist,
            # add adjacent nodes
            if adjacent_node not in dist_so_far or new_dist < dist_so_far[adjacent_node]:
                dist_so_far[adjacent_node] = new_dist
                energy_cost_so_far[adjacent_node] = new_energy_cost
                queue.put((new_dist, adjacent_node))
                # add parent pointers
                came_from[adjacent_node] = curr_node
    return None


def yen_algo_mod(graph, start, end, budget, astar=True):
    
    # ucs/astar returns path, distance, and energy_cost
    if astar:
        shortest_path = astar_start(graph, start, end, 0.91)
    else:
        shortest_path = ucs_dist_start(graph, start, end)
    
    # A stores k-shortest paths
    A = [shortest_path]
    # B stores list of potential k-shortest paths
    B = []
    k = 1
    while True:
        print("finding ", k, " shortest path")
        # kmos => k-1 shortest path
        kmos_path = A[-1][0]
        for i in range(len(kmos_path) - 1):
            spur_node = kmos_path[i]
            root_path = kmos_path[:i+1]

            # prevent generation of the same path by removing edge of root path that coincides with previous paths
            original_adjacent_nodes = graph.adj_list[spur_node]
            new_adjacent_nodes = list(original_adjacent_nodes)
            for path in A:
                path = path[0]
                if len(path) > i and root_path == path[:i+1]:
                    to_be_deleted_node = path[i + 1]
                    if to_be_deleted_node in new_adjacent_nodes:
                        new_adjacent_nodes.remove(to_be_deleted_node)
            graph.adj_list[spur_node] = new_adjacent_nodes

            # remove nodes from the root path except for the spur node
            removed_nodes = []
            for node in root_path[0][:-1]:
                removed_node = graph.adj_list.pop(node)
                removed_nodes.append(removed_node)

            # find the shortest path from spur node to terminal node
            if astar:
                returned_values = astar_start(graph, spur_node, end, 0.91)
            else:
                returned_values = ucs_dist_start(graph, spur_node, end)

            if returned_values:
                spur_path, spur_dist, spur_energy_cost = returned_values

                # calculate the values of the generated path by combining the root and spur paths
                total_path = root_path[:-1] + spur_path
                total_dist, total_cost = calc_costs(total_path, graph)
                potential_k = (total_path, total_dist, total_cost)

                # add the newly generated path to the array
                if potential_k not in B:
                    B.append(potential_k)

            # Add the edges and nodes back
            graph.adj_list[spur_node] = original_adjacent_nodes
            for node, removed_node in zip(root_path[:-1], removed_nodes):
                graph.adj_list[node] = removed_node

        # handles the exception when there are no potential paths
        if not B:
            continue
        # sort the potential k-shortest paths by distance
        B.sort(key=lambda b: b[1])
        # let the lowest cost path become the k-shortest path
        next_shortest_path = B.pop(0)
        if next_shortest_path[2] <= budget:
            print_path(next_shortest_path[0])
            print("dist: ", next_shortest_path[1])
            print("cost: ", next_shortest_path[2])
            return next_shortest_path

        A.append(next_shortest_path)
        k += 1

        return A


def calc_costs(x:str, g: Graph):
    total_cost = 0.
    total_dist = 0.
    for i in range(1, len(x)):
        prev = x[i - 1]
        curr = x[i]
        cost = g.get_cost(prev, curr)
        dist = g.get_distance(prev, curr)
        total_dist += dist
        total_cost += cost
    return (total_dist, total_cost)


def main():
    graph = Graph()
    window = Window(graph)
    while(True):
            print()
            print(f"1) Relaxed shortest path (No energy constraint)")
            print(f"2) Energy Constrained shortest path")
            print(f"3) Energy Constrained shortest path with Heuristic")
            print(f" ~~ BONUS ~~")
            print(f"4) Yen's algorithm to find kth shortest path w/o heuristic")
            print(f"5) Yen's algorithm to find kth shortest path w heuristic")
            choice = input("What would you like to do (X to exit): ")

            if choice.upper() == 'X':
                break

            try:
                choice = int(choice)
            except:
                print("Invalid choice")
                continue
            
            try:
                start_node = input("Enter starting node: ")
                end_node = input("Enter ending node: ")

                if (choice >= 2 and choice <= 5):
                    budget = int(input("Enter energy budget: "))

                if (choice >= 3 and choice <= 5):
                    print("E: Euclidean (Pythagorean theorem aka Bird's Eye Distance)")
                    print("M: Manhattan (x_coord distance + y_coord distance aka Grid Distance)")
                    dist_choice = input("Select type of distance heuristic: ")
                    dist_choice = dist_choice.upper()

                    if dist_choice == 'E':
                        dist_type = "euclidean"
                    elif dist_choice == 'M': 
                        dist_type = "manhattan"
                    else: 
                        print("Invalid distance type")
                        continue

                    try:
                        heuristic_multiplier = float(input("Enter heuristic multiplier: "))
                    except:
                        print("Invalid value" + dist_choice)
                        continue
            except:
                print("Only integer values allowed")
                continue
            
            # Task 1
            if choice == 1:
                window.relaxed_shortest_distance(start_node, end_node)      

            elif choice == 2:
                window.constraint_shortest_distance(start_node, end_node, budget)

            elif choice == 3:
                window.heuristic_constraint_shortest_distance(start_node, end_node, budget, heuristic_multiplier, dist_type)

            elif choice == 4:
                start_time = time.time()
                yen_algo_mod(graph, start_node, end_node, budget, astar=False)
                end_time = time.time()
                print("total time taken: ", end_time - start_time)
            elif choice == 5:
                start_time = time.time()
                yen_algo_mod(graph, start_node, end_node, budget, astar=True)
                end_time = time.time()
                print("total time taken: ", end_time - start_time)
            else:
                print("Invalid choice")

if __name__ == "__main__":
    main()