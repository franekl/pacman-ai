import sys

def is_between(start_pos, end_pos, pellet_pos):
    if start_pos[0] == end_pos[0]:  
        return start_pos[0] == pellet_pos[0] and min(start_pos[1], end_pos[1]) <= pellet_pos[1] <= max(start_pos[1], end_pos[1])
    elif start_pos[1] == end_pos[1]: 
        return start_pos[1] == pellet_pos[1] and min(start_pos[0], end_pos[0]) <= pellet_pos[0] <= max(start_pos[0], end_pos[0])
    return False

def get_path_weight(start_node_pos, end_node_pos, pellet_positions):
    for pellet_pos_x, pellet_pos_y in pellet_positions:
        if is_between(start_node_pos, end_node_pos, (pellet_pos_x, pellet_pos_y)):
            return 1  
    return 100  

def dijkstra(nodes, start_node, pellet_positions):
    unvisited_nodes = list(nodes.costs) 
    shortest_path = {}
    previous_nodes = {}

    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    shortest_path[start_node] = 0

    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node == None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node
        # print(current_min_node)
        neighbors = nodes.getNeighbors(current_min_node)
        # print(neighbors)
        for neighbor in neighbors:
            if neighbor in list(nodes.costs):
                path_weight = get_path_weight(current_min_node, neighbor, pellet_positions)
                print(path_weight)
                tentative_value = shortest_path[current_min_node] + path_weight #nodes.value(current_min_node, neighbor)
                if tentative_value < shortest_path[neighbor]:
                    shortest_path[neighbor] = tentative_value
                    # We also update the best path to the current node
                    previous_nodes[neighbor] = current_min_node
 
        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)
    
    return previous_nodes, shortest_path




# Previous nodes: {(240, 512): (240, 464), (288, 464): (240, 464), (288, 416): (288, 464), (192, 512): (240, 512), (416, 512): (240, 512), (240, 416): (288, 416), (336, 416): (288, 416), (192, 464): (192, 512), (16, 512): (192, 512), (416, 464): (416, 512), (240, 368): (240, 416), (336, 368): (336, 416), (336, 464): (336, 416), (144, 464): (192, 464), (384, 464): (416, 464), (16, 464): (16, 512), (288, 368): (240, 368), (336, 272): (336, 368), (416, 368): (336, 368), (48, 464): (16, 464), (144, 416): (144, 464), (384, 416): (384, 464), (336, 176): (336, 272), (96, 416): (144, 416), (192, 416): (144, 416), (48, 416): (48, 464), (96, 464): (48, 464), (336, 128): (336, 176), (416, 176): (336, 176), (96, 368): (96, 416), (192, 368): (192, 416), (336, 64): (336, 128), (288, 128): (336, 128), (416, 128): (336, 128), (96, 272): (96, 368), (16, 368): (96, 368), (144, 368): (96, 368), (240, 64): (336, 64), (416, 64): (336, 64), (288, 176): (288, 128), (240, 128): (288, 128), (96, 176): (96, 272), (192, 128): (240, 128), (96, 128): (96, 176), (16, 176): (96, 176), (240, 176): (288, 176), (96, 64): (96, 128), (16, 128): (96, 128), (144, 128): (96, 128), (192, 64): (192, 128), (16, 64): (96, 64), (144, 176): (144, 128), (192, 176): (144, 176)}
#Shortest path:  {(16, 64): 12, (96, 64): 11, (192, 64): 11, (240, 64): 9, (336, 64): 8, (416, 64): 9, (16, 128): 11, (96, 128): 10, (144, 128): 11, (192, 128): 10, (240, 128): 9, (288, 128): 8, (336, 128): 7, (416, 128): 8, (16, 176): 10, (96, 176): 9, (144, 176): 12, (192, 176): 13, (240, 176): 10, (288, 176): 9, (336, 176): 6, (416, 176): 7, (96, 272): 8, (336, 272): 5, (16, 368): 8, (96, 368): 7, (144, 368): 8, (192, 368): 7, (240, 368): 4, (288, 368): 5, (336, 368): 4, (416, 368): 5, (48, 416): 6, (96, 416): 6, (144, 416): 5, (192, 416): 6, (240, 416): 3, (288, 416): 2, (336, 416): 3, (384, 416): 5, (16, 464): 4, (48, 464): 5, (96, 464): 6, (144, 464): 4, (192, 464): 3, (240, 464): 0, (288, 464): 1, (336, 464): 4, (384, 464): 4, (416, 464): 3, (16, 512): 3, (192, 512): 2, (240, 512): 1, (416, 512): 2}

# def print_result(previous_nodes, shortest_path, start_node, target_node):
#     path = []
#     node = target_node
    
#     while node != start_node:
#         path.append(node)
#         node = previous_nodes[node]
 
#     # Add the start node manually
#     path.append(start_node)
    
#     print("We found the following best path with a value of {}.".format(shortest_path[target_node]))
#     print(path)


# #########
# # A*
# def heuristic(node1, node2):
#     # manhattan distance
#     return abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])


# def dijkstra_or_a_star(nodes, start_node, a_star=False):
#     unvisited_nodes = list(nodes.costs)
#     shortest_path = {}
#     previous_nodes = {}

#     max_value = sys.maxsize
#     for node in unvisited_nodes:
#         shortest_path[node] = max_value
#     shortest_path[start_node] = 0

#     while unvisited_nodes:
#         current_min_node = None
#         for node in unvisited_nodes:
#             if current_min_node == None:
#                 current_min_node = node
#             elif shortest_path[node] < shortest_path[current_min_node]:
#                 current_min_node = node

#         neighbors = nodes.getNeighbors(current_min_node)
#         for neighbor in neighbors:
#             if a_star:
#                 tentative_value = shortest_path[current_min_node] + heuristic(current_min_node,neighbor) 
#             else:
#                 tentative_value = shortest_path[current_min_node] + 1
#             if tentative_value < shortest_path[neighbor]:
#                 shortest_path[neighbor] = tentative_value
#                 # We also update the best path to the current node
#                 previous_nodes[neighbor] = current_min_node
 
#         # After visiting its neighbors, we mark the node as "visited"
#         unvisited_nodes.remove(current_min_node)
#     return previous_nodes, shortest_path