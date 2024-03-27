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
        
        # Look-ahead for further pellet potential
        for next_neighbor_pos in nodes.getNeighbors(neighbor_pos):
            if next_neighbor_pos != node_pos:  # Avoid going back to the starting node
                pellet_count += node_pellet_weight(next_neighbor_pos, nodes, pellet_positions, depth-1)
    
    return pellet_count

def get_path_weight(start_node_pos, end_node_pos, pellet_positions, nodes):
    immediate_pellet_count = sum(1 for pellet_pos in pellet_positions if is_between(start_node_pos, end_node_pos, pellet_pos))
    if immediate_pellet_count > 0:
        return 1 / immediate_pellet_count
    else:
        # Use extended look-ahead for neighbor pellet potential
        extended_potential = node_pellet_weight(end_node_pos, nodes, pellet_positions)
        return 500 - extended_potential  # Decrease weight for nodes with higher extended potential
    
def dijkstra(nodes, start_node, pellet_positions):
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
                path_weight = get_path_weight(current_min_node, neighbor, pellet_positions, nodes)
                tentative_value = shortest_path[current_min_node] + path_weight
                if tentative_value < shortest_path[neighbor]:
                    shortest_path[neighbor] = tentative_value
                    previous_nodes[neighbor] = current_min_node
            
        unvisited_nodes.remove(current_min_node)

    
    print(f"Shortest path: {shortest_path}")
    return previous_nodes, shortest_path