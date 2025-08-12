import pygame
import math

pygame.init()
pygame.display.set_caption("3d engine")

# Window
width = 400
aspect_ratio = 4 / 3
fps = 20

window = pygame.display.set_mode((width, width / aspect_ratio))
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
player_a = 0
player_l = 0
sensitivity = 4
player_speed = 1



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
        dy = player_speed * math.sin(rad(player_a))
        dx = player_speed * -math.cos(rad(player_a))
    if tasteri[pygame.K_a]:
        dy = player_speed * -math.sin(rad(player_a))
        dx = player_speed * math.cos(rad(player_a))
    # Z
    if tasteri[pygame.K_SPACE]:
        dz = player_speed
    if tasteri[pygame.K_LSHIFT]:
        dz = -player_speed

    # Camera
    # Horizontal angle
    if tasteri[pygame.K_RIGHT]:
        player_a -= sensitivity
        if player_a < 0:
            player_a = player_a + 360
    if tasteri[pygame.K_LEFT]:
        player_a += sensitivity
        if player_a > 360:
            player_a = player_a - 360
    # Look angle
    if tasteri[pygame.K_UP]:
        player_l -= sensitivity
        if player_l < 0:
            player_l = player_l + 360
    if tasteri[pygame.K_DOWN]:
        player_l += sensitivity
        if player_l > 360:
            player_l = player_l - 360

    return dx, dy, dz, player_a, player_l


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

    print(f"x: {player_x} y: {player_y} z: {player_z} a: {player_a} l: {player_l}")
    


    pygame.display.update()
    pygame.time.delay(1000 // fps)
