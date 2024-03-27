import sys

def is_between(start_pos, end_pos, pellet_pos):
    if start_pos[0] == end_pos[0]:  
        return start_pos[0] == pellet_pos[0] and min(start_pos[1], end_pos[1]) <= pellet_pos[1] <= max(start_pos[1], end_pos[1])
    elif start_pos[1] == end_pos[1]: 
        return start_pos[1] == pellet_pos[1] and min(start_pos[0], end_pos[0]) <= pellet_pos[0] <= max(start_pos[0], end_pos[0])
    return False


def node_pellet_weight(node_pos, nodes, pellet_positions, depth=2):
    if depth == 0:
        return 0  
    
    pellet_count = 0
    neighbors = nodes.getNeighbors(node_pos)
    
    for neighbor_pos in neighbors:
        # Immediate neighbor pellet count
        pellet_count += sum(1 for pellet_pos in pellet_positions if is_between(node_pos, neighbor_pos, pellet_pos))
        
        # further pellet potential, check the neighbors
        for next_neighbor_pos in nodes.getNeighbors(neighbor_pos):
            if next_neighbor_pos != node_pos:  # Avoid going back
                pellet_count += node_pellet_weight(next_neighbor_pos, nodes, pellet_positions, depth-1)
    
    return pellet_count

def check_ghost_proximity(ghost_pos, node_pos, end_node_pos, neighbors):
    # add a penalty in case a ghost is nearby

    if is_between(node_pos, end_node_pos, ghost_pos): # direct path between node and end node
        return 100  # ghost on a direct path = penalty 100
    
    for neighbor in neighbors: #check paths from the node to the neighbors
        if is_between(node_pos, neighbor, ghost_pos):
            return 50  # ghost on a neighboring path = penalty 50
    return 0 #else penalty is 0

def get_path_weight(start_node_pos, end_node_pos, pellet_positions, nodes, ghosts):
    immediate_pellet_count = sum(1 for pellet_pos in pellet_positions if is_between(start_node_pos, end_node_pos, pellet_pos)) #direct path between node and end node = check how many pellets
    if immediate_pellet_count > 0:
        weight = 1 / immediate_pellet_count #weight will be lower if there are more pellets on the way
    else:
        extended_potential = node_pellet_weight(end_node_pos, nodes, pellet_positions) #extended lookup for neighbor pellet potential
        weight = 100 - extended_potential  # decrease weight for nodes with higher extended potential
        # 100 here is a penalty for taking a route that does not have any pellets on the way to the nearest node - tho that weight gets decreased the more pellets the neighbors of a target node can offer
    
    start_neighbors = nodes.getNeighbors(start_node_pos)

    for ghost in ghosts:
        ghost_pos = (ghost.target.x, ghost.target.y) 
        
        weight += check_ghost_proximity(ghost_pos, start_node_pos, end_node_pos, start_neighbors)
    return weight
   


def dijkstra(nodes, start_node, pellet_positions, ghosts):
    unvisited_nodes = list(nodes.costs) 
    # print(unvisited_nodes)
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
        neighbors = nodes.getNeighbors(current_min_node)
        
        for neighbor in neighbors:
            if neighbor in list(nodes.costs):
                path_weight = get_path_weight(current_min_node, neighbor, pellet_positions, nodes, ghosts)
                tentative_value = shortest_path[current_min_node] + path_weight
                if tentative_value < shortest_path[neighbor]:
                    shortest_path[neighbor] = tentative_value
                    previous_nodes[neighbor] = current_min_node
            
        unvisited_nodes.remove(current_min_node)

    
    # print(f"Shortest path: {shortest_path}")
    sorted_paths = sorted(shortest_path.items(), key=lambda item: item[1])
    print(sorted_paths)
    return previous_nodes, shortest_path