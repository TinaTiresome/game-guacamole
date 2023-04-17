import pygame
import sys
import random

## Class definitions
class Node:
    def __init__(self, x, y, resource_type):
        """
        Initialize a new node object.

        Args:
        - x (int): the x-coordinate of the node
        - y (int): the y-coordinate of the node
        - resource_type (str): the type of resource produced by the node
        """
        self.x = x
        self.y = y
        self.status = "inactive"
        self.resource = resource_type
        self.cost_resource = random.choice([r for r in COLORS.keys() if r != resource_type])
        self.base_output = 1  # You can set the base output as needed.
        self.output_multiplier = 1
        self.size = 20
        self.connection_points = [(x-10, y), (x+10, y), (x, y-10), (x, y+10)]
        
    def get_closest_connection_point(self, target_x, target_y):
        """
        Get the closest connection point on the node to the given target point.

        Args:
        - target_x (int): the x-coordinate of the target point
        - target_y (int): the y-coordinate of the target point

        Returns:
        - (tuple): a tuple representing the closest connection point on the node, in the form (x, y)
        """
        closest_point = self.connection_points[0]
        closest_distance = ((closest_point[0] - target_x)**2 + (closest_point[1] - target_y)**2)**0.5

        for point in self.connection_points[1:]:
            distance = ((point[0] - target_x)**2 + (point[1] - target_y)**2)**0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_point = point

        return closest_point


class Bridge:
    def __init__(self, nodeA, nodeB):
        """
        Initialize a new bridge object between two nodes.

        Args:
        - nodeA (Node): the first node in the bridge
        - nodeB (Node): the second node in the bridge
        """
        self.nodeA = nodeA
        self.nodeB = nodeB
        self.pointA = nodeA.get_closest_connection_point(nodeB.x, nodeB.y)
        self.pointB = nodeB.get_closest_connection_point(nodeA.x, nodeA.y)
        self.cost = int(((self.pointA[0] - self.pointB[0])**2 + (self.pointA[1] - self.pointB[1])**2)**0.5)  # Calculate cost based on distance

## Global variable and setup
# Initialize Pygame
pygame.init()

# Define some colors for the resources
COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
}

# Initialize an empty list to store bridges
bridges = []

# Set the initial selected node to None
selected_node = None

## Helper function definitions
# generate nodes
def generate_nodes(num_nodes, screen_width, screen_height):
    """
    Generate a list of randomly positioned nodes.

    Args:
    - num_nodes (int): the number of nodes to generate
    - screen_width (int): the width of the game screen, in pixels
    - screen_height (int): the height of the game screen, in pixels

    Returns:
    - (list): a list of Node objects
    """
    nodes = []
    for i in range(num_nodes):
        while True:
            x = random.randint(50, screen_width - 50)
            y = random.randint(50, screen_height - 50)
            overlapping = False
            for node in nodes:
                distance = ((node.x - x) ** 2 + (node.y - y) ** 2) ** 0.5
                if distance < 2 * node.size:
                    overlapping = True
                    break
            if not overlapping:
                break
        resource_type = random.choice(list(COLORS.keys()))
        node = Node(x, y, resource_type)
        node.cost_resource = random.choice([r for r in COLORS.keys() if r != resource_type])
        if i == 0:
            node.status = "active"
        nodes.append(node)
    return nodes

# Helper function to draw nodes
def draw_nodes(nodes, screen):
    """
    Draw the nodes on the game screen.

    Args:
    - nodes (list): a list of Node objects
    - screen (pygame.Surface): the game screen to draw on
    """
    for node in nodes:
        color = COLORS[node.resource] if node.status == "active" else (200, 200, 200)
        pygame.draw.circle(screen, color, (node.x, node.y), node.size)
        outline_color = COLORS[node.resource] if node.status == "inactive" else (0, 0, 0)
        pygame.draw.circle(screen, outline_color, (node.x, node.y), node.size, 2)  # Draw node border

# Helper function to draw bridges
def draw_bridges(bridges, screen):
    """
    Draw the bridges on the game screen.

    Args:
    - bridges (list): a list of Bridge objects
    - screen (pygame.Surface): the game screen to draw on
    """
    for bridge in bridges:
        pygame.draw.line(screen, (0, 0, 0), bridge.pointA, bridge.pointB, 2)

# Function to check if bridge is intersecting with node
def is_line_intersecting(p1, q1, p2, q2):
    """
    Check if two line segments intersect.

    Args:
    - p1 (tuple): the start point of the first line segment, in the form (x, y)
    - q1 (tuple): the end point of the first line segment, in the form (x, y)
    - p2 (tuple): the start point of the second line segment, in the form (x, y)
    - q2 (tuple): the end point of the second line segment, in the form (x, y)

    Returns:
    - (bool): True if the line segments intersect, False otherwise
    """
    # Helper function to calculate the orientation of three points
    def orientation(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0:
            return 0
        return 1 if val > 0 else 2
    
    # Helper function to check if a point lies on a line segment
    def on_segment(p, q, r):
        if (
            q[0] <= max(p[0], r[0])
            and q[0] >= min(p[0], r[0])
            and q[1] <= max(p[1], r[1])
            and q[1] >= min(p[1], r[1])
        ):
            return True
        return False

    # Calculate the orientations of all relevant points
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # Check if the line segments intersect
    if o1 != o2 and o3 != o4:
        return True
    
    # Check if any points lie on the other line segment
    if o1 == 0 and on_segment(p1, p2, q1):
        return True

    if o2 == 0 and on_segment(p1, q2, q1):
        return True

    if o3 == 0 and on_segment(p2, p1, q2):
        return True

    if o4 == 0 and on_segment(p2, q1, q2):
        return True
    # If none of the above conditions are met, the line segments do not intersect
    return False

# Check if two bridges are intersecting
def is_bridge_intersecting(bridge1, bridge2):
    p1, q1 = bridge1.pointA, bridge1.pointB
    p2, q2 = bridge2.pointA, bridge2.pointB
    return is_line_intersecting(p1, q1, p2, q2)

# Function for hover text
def draw_hover_text(node, screen):
    """
    Draw the hover text for the given node, showing the cost of a potential bridge.

    Args:
    - node (Node): the node to show the hover text for
    - screen (pygame.Surface): the game screen to draw on
    """
    if selected_node:
        bridge = Bridge(selected_node, node)
        font = pygame.font.Font(None, 20)
        text = f"Cost: {bridge.cost} {node.cost_resource}"
        text_surface = font.render(text, True, (0, 0, 0), COLORS[node.cost_resource])
        screen.blit(text_surface, (node.x - 30, node.y - node.size - 30))

## Main game loop
def main():
    global selected_node  # use the global variable
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Game Title')

    nodes = generate_nodes(10, 800, 600) # Generate some nodes
    resources = {"red": 0, "green": 0, "blue": 0} # Initialize the resource counters

    clock = pygame.time.Clock()

    selected_node = None

    while True:
        screen.fill((255, 255, 255)) # Clear the screen

        for event in pygame.event.get(): # Handle events
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN: # Handle mouse clicks
                x, y = pygame.mouse.get_pos()
                clicked_node = None
                for node in nodes:
                    distance = ((node.x - x)**2 + (node.y - y)**2)**0.5
                    if distance < node.size:
                        clicked_node = node
                        break

                if clicked_node:
                    if selected_node is None:
                        if clicked_node.status == "active":
                            selected_node = clicked_node
                    else:
                        if clicked_node.status == "inactive":
                            bridge = Bridge(selected_node, clicked_node)
                            if resources[clicked_node.cost_resource] >= bridge.cost:
                                intersecting = False

                                # Check for intersection with existing bridges
                                for existing_bridge in bridges:
                                    if is_bridge_intersecting(bridge, existing_bridge):
                                        intersecting = True
                                        break

                                if not intersecting:
                                    resources[clicked_node.cost_resource] -= bridge.cost
                                    clicked_node.status = "active"
                                    bridges.append(bridge)  # Add the new bridge to the bridges list

                        selected_node = None

        # Draw a visual indicator for the selected node
        if selected_node:
            pygame.draw.circle(screen, (255, 255, 0), (selected_node.x, selected_node.y), selected_node.size + 5, 2)


        # Update the resources
        for node in nodes:
            if node.status == "active":
                resources[node.resource] += node.base_output * node.output_multiplier

        # Draw the nodes and bridges
        draw_nodes(nodes, screen)
        draw_bridges(bridges, screen)

        # Update and draw the resource counter
        resource_text = " | ".join(f"{key}: {value:.1f}" for key, value in resources.items())
        font = pygame.font.Font(None, 24)
        resource_surface = font.render(resource_text, True, (0, 0, 0))
        screen.blit(resource_surface, (10, 10))

        # Check for mouse hover on unactivated nodes
        x, y = pygame.mouse.get_pos()
        for node in nodes:
            if node.status == "inactive":
                distance = ((node.x - x)**2 + (node.y - y)**2)**0.5
                if distance < node.size:
                    draw_hover_text(node, screen)

        # Cap the frame rate at 60 FPS
        clock.tick(60)

        pygame.display.flip()

if __name__ == '__main__':
    main()
