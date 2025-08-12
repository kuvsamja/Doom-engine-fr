import pygame
import math

pygame.init()
pygame.display.set_caption("3d engine")

# Window
aspect_ratio = 4 / 3
width = 800
height = width / aspect_ratio
fps = 20

window = pygame.display.set_mode((width, height))
# Boje
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
PURPLE = (100,10,100)
YELLOW = (255, 255, 0)

# Player
player_x = 70
player_y = -110
player_z = 20
player_a = 0    # Horizontal angle
player_l = 180    # Vertical angle
sensitivity = 8
player_speed = 8

# Camera
focal_lenght = 200


def player_movement(player_speed, player_a, player_l):
    tasteri = pygame.key.get_pressed()
    dx = 0
    dy = 0
    dz = 0
    # Movement
    # X
    if tasteri[pygame.K_w]:
        dx = player_speed * math.sin(rad(player_a))
        dy = player_speed * math.cos(rad(player_a))
    if tasteri[pygame.K_s]:
        dx = player_speed * -math.sin(rad(player_a))
        dy = player_speed * -math.cos(rad(player_a))
    # Y
    if tasteri[pygame.K_d]:
        dx = player_speed * math.cos(rad(player_a))
        dy = player_speed * -math.sin(rad(player_a))
    if tasteri[pygame.K_a]:
        dx = player_speed * -math.cos(rad(player_a))
        dy = player_speed * math.sin(rad(player_a))
    # Z
    if tasteri[pygame.K_SPACE]:
        dz = -player_speed
    if tasteri[pygame.K_LSHIFT]:
        dz = player_speed

    # Camera
    # Horizontal angle
    if tasteri[pygame.K_LEFT]:
        player_a -= sensitivity
        if player_a < 0:
            player_a = player_a + 360
    if tasteri[pygame.K_RIGHT]:
        player_a += sensitivity
        if player_a > 360:
            player_a = player_a - 360
    # Look angle
    if tasteri[pygame.K_DOWN]:
        player_l -= sensitivity
        if player_l < 0:
            player_l = player_l + 360
    if tasteri[pygame.K_UP]:
        player_l += sensitivity
        if player_l > 360:
            player_l = player_l - 360
    return dx, dy, dz, player_a, player_l


def drawWall(x1, x2, b1, b2):
    dyb = b2 - b1
    dx = x2 - x1
    if dx == 0:
        dx = 1
    xs = x1
    for x in range(x1, x2):
        y1 = dyb * (x - xs) / dx + b1
        window.set_at((x, int(y1)), YELLOW)
    

def draw3D():
    world_x = [0, 0, 0, 0]
    world_y = [0, 0, 0, 0]
    world_z = [0, 0, 0, 0]
    CS = math.cos(rad(player_a))
    SN = math.sin(rad(player_a))

    # Point world location (no tilting)
    x1 = 70 - player_x; y1 = 10 - player_y
    x2 = 70 - player_x; y2 = 290 - player_y
    # World X position
    world_x[0] = x1 * CS - y1 * SN
    world_x[1] = x2 * CS - y2 * SN
    # World Y position
    world_y[0] = y1 * CS + x1 * SN
    world_y[1] = y2 * CS + x2 * SN
    # World Z position
    world_z[0] = 0 - player_z + ((player_l - 180) * world_y[0] / 64)
    world_z[1] = 0 - player_z + ((player_l - 180) * world_y[1] / 64)
    # Screen x, y, z
    world_x[0] = int(world_x[0] * focal_lenght / world_y[0] + width / 2); world_y[0] = int(world_z[0] * focal_lenght / world_y[0] + height / 2)
    world_x[1] = int(world_x[1] * focal_lenght / world_y[1] + width / 2); world_y[1] = int(world_z[1] * focal_lenght / world_y[1] + height / 2)
    #print(f"worldx: {world_x}, world_y: {world_y}")
    # Draw points
    if(world_x[0] > 0 and world_x[0] < width and world_y[0] > 0 and world_y[0] < height):
        window.set_at((int(world_x[0]), int(world_y[0])), YELLOW)
    if(world_x[1] > 0 and world_x[1] < width and world_y[1] > 0 and world_y[1] < height):
        window.set_at((int(world_x[1]), int(world_y[1])), YELLOW)
    drawWall(world_x[0], world_x[1], world_y[0], world_y[1])
        
def rad(deg):
    return deg / 180 * math.pi

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    window.fill(BLACK)
    dx, dy, dz, player_a, player_l = player_movement(player_speed, player_a, player_l)
    player_x = player_x + dx; player_y = player_y + dy; player_z = player_z + dz

    #print(f"x: {player_x} y: {player_y} z: {player_z} a: {player_a} l: {player_l}")
    draw3D()

    pygame.display.update()
    pygame.time.delay(1000 // fps)