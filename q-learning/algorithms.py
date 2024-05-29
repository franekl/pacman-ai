import sys

def is_between(start_pos, end_pos, entity):
    entity_x = entity.position.x if hasattr(entity, 'position') else entity[0]
    entity_y = entity.position.y if hasattr(entity, 'position') else entity[1]

    # check whether there are any pellets between the start and end positions
    if start_pos[0] == end_pos[0]:  # check if they are on the same row
        # return true if pellet's y-coordinate is between start and end
        return start_pos[0] == entity_y and min(start_pos[1], end_pos[1]) <= entity_x <= max(start_pos[1], end_pos[1])
    elif start_pos[1] == end_pos[1]:  # same column
        # return true if pellet's x-coordinate is between start and end
        return start_pos[1] == entity_x and min(start_pos[0], end_pos[0]) <= entity_y <= max(start_pos[0], end_pos[0])
    return False  # if not aligned either horizontally or vertically

def node_pellet_weight(node_pos, nodes, pellet_positions, depth=2):
    if depth == 0:  # stop recursion and return 0
        return 0  
    
    pellet_count = 0
    neighbors = nodes.getNeighbors(node_pos)  # neighbors of the current node
    
    for neighbor_pos in neighbors:
        # count pellets on the path between the current node and each neighbor
        pellet_count += sum(1 for pellet in pellet_positions if is_between(node_pos, neighbor_pos, pellet))
        
        # For each neighbor, check their neighbors for additional pellets on their edges
        for next_neighbor_pos in nodes.getNeighbors(neighbor_pos):
            if next_neighbor_pos != node_pos:  # Avoid going back
                # calculate the pellet weight for neighbors, decreasing depth with each call
                pellet_count += node_pellet_weight(next_neighbor_pos, nodes, pellet_positions, depth-1)
    
    return pellet_count  # total count of pellets found directly on the path and through further short exploration

def check_ghost_proximity(ghost_pos, node_pos, end_node_pos, neighbors):
    # add a penalty in case a ghost is nearby

    if is_between(node_pos, end_node_pos, ghost_pos):  # is ghost on a direct path between the current node and target one?
        return 100  # ghost on a direct path = penalty 100
    
    for neighbor in neighbors:  # check the neighbors, whether there's a ghost on one of their edges
        if is_between(node_pos, neighbor, ghost_pos):
            return 50  # ghost on a neighboring path = penalty 50
    return 0  # else no additional "ghost" penalty

def get_path_weight(start_node_pos, end_node_pos, pellet_positions, nodes, ghosts):
    # get path weight based on the presence of pellets and ghosts

    immediate_pellet_count = sum(1 for pellet in pellet_positions if is_between(start_node_pos, end_node_pos, pellet))  # check how many pellets on a direct path to the target
    if immediate_pellet_count > 0:
        weight = 1 / immediate_pellet_count  # the more pellets on the path, the lower the weight -> attractive path
    else:
        # if no pellets directly on the path, we'll apply a penalty of 100 but reduce that by number of "close-by" pellets, will examine neighbors for that
        extended_potential = node_pellet_weight(end_node_pos, nodes, pellet_positions)  # extended lookup for neighbor pellet potential
        weight = 100 - extended_potential  # decrease weight for nodes with higher extended potential
        # 100 here is a penalty for taking a route that does not have any pellets on the way to the nearest node...
        # tho that weight gets decreased the more pellets the neighbors of a target node can offer
    
    # adjust the path weight based on the proximity of the ghosts
    start_neighbors = nodes.getNeighbors(start_node_pos)
    for ghost in ghosts:
        ghost_pos = (ghost.target.x, ghost.target.y)  # target position for each ghost
        # add penalty based on ghost proximity to the path, also considering the neighboring paths
        weight += check_ghost_proximity(ghost_pos, start_node_pos, end_node_pos, start_neighbors)
    return weight  # final calculated path weight
   

def dijkstra(nodes, start_node, pellet_positions, ghosts):
    unvisited_nodes = list(nodes.costs)  # init the list of nodes

    shortest_path = {}  # store shortest path length to each node
    previous_nodes = {}  # track the previous node for each node, helps to reconstruct the path

    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value  # all nodes initialied with initial distance (high number)
    shortest_path[start_node] = 0  # start node's distance to itself is 0

    while unvisited_nodes:  # carry on until all nodes are visited
        current_min_node = None  # track the node with the current minimum distance
        for node in unvisited_nodes:  # find the node with the smallest known distance
            if current_min_node is None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        # go through all the neighbors of the current node
        neighbors = nodes.getNeighbors(current_min_node)
        
        for neighbor in neighbors: 
            if neighbor in list(nodes.costs): 
                # get path weight considering pellets and ghosts 
                path_weight = get_path_weight(current_min_node, neighbor, pellet_positions, nodes, ghosts)
                tentative_value = shortest_path[current_min_node] + path_weight  # distance with weight/penalty added
                if tentative_value < shortest_path[neighbor]:  # if a new distance is shorter, update the shortest path and prev node
                    shortest_path[neighbor] = tentative_value 
                    previous_nodes[neighbor] = current_min_node
             
        unvisited_nodes.remove(current_min_node)  # mark the current node as visited

    sorted_paths = sorted(shortest_path.items(), key=lambda item: item[1])
    print(sorted_paths)
    return previous_nodes, shortest_path
