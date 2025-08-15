import pygame
import math
import map

pygame.init()
pygame.display.set_caption("3d engine")

# Window
aspect_ratio = 4 / 3
width = 800
height = width // aspect_ratio
scale = 1
fps = 30
window = pygame.display.set_mode((width * scale, height * scale))
scaled_surface = pygame.Surface((width, height))


# Camera
focal_lenght = 300

# Time
last_tick = 0

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
sensitivity = 160 / fps
player_speed = 1600 / fps

def rad(deg):
    return deg / 180 * math.pi
#_____________________________________________________________________________________


def distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)) 
    return distance
def playerMovement(player_speed, player_a, player_l):
    dx = 0
    dy = 0
    dz = 0
    # Movement
    # X
    if buttons[pygame.K_w]:
        dx = dx + player_speed * math.sin(rad(player_a))
        dy = dy + player_speed * math.cos(rad(player_a))
    if buttons[pygame.K_s]:
        dx = dx + player_speed * -math.sin(rad(player_a))
        dy = dy + player_speed * -math.cos(rad(player_a))
    # Y
    if buttons[pygame.K_d]:
        dx = dx + player_speed * math.cos(rad(player_a))
        dy = dy + player_speed * -math.sin(rad(player_a))
    if buttons[pygame.K_a]:
        dx = dx + player_speed * -math.cos(rad(player_a))
        dy = dy + player_speed * math.sin(rad(player_a))
    # Z
    if buttons[pygame.K_SPACE]:
        dz = dz + -player_speed
    if buttons[pygame.K_LSHIFT]:
        dz = dz + player_speed

    # Camera
    # Horizontal angle
    if buttons[pygame.K_LEFT]:
        player_a -= sensitivity
        if player_a < 0:
            player_a = player_a + 360
    if buttons[pygame.K_RIGHT]:
        player_a += sensitivity
        if player_a > 360:
            player_a = player_a - 360
    # Look angle
    if buttons[pygame.K_DOWN]:
        player_l -= sensitivity
        if player_l < 0:
            player_l = player_l + 360
    if buttons[pygame.K_UP]:
        player_l += sensitivity
        if player_l > 360:
            player_l = player_l - 360
    return dx, dy, dz, player_a, player_l

#_______________________________________________________________________________________

class Walls():
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    color = (0, 0, 0)

class Sectors():
    wall_start = 0
    wall_end = 0
    d = 0
    color1 = (0, 0, 0)
    color2 = (0, 0, 0)
    surf = [0 for i in range(width)]
    surface = 0
    z1 = 0
    z2 = 0

W = [Walls() for i in range(100)]
S = [Sectors() for i in range(100)]
v1 = 0
v2 = 0
for s in range(map.SECTOR_NUM):
    S[s].wall_start = map.loadSectors()[v1 + 0]
    S[s].wall_end = map.loadSectors()[v1 + 1]
    S[s].z1 = map.loadSectors()[v1 + 2]
    S[s].z2 = map.loadSectors()[v1 + 3] - map.loadSectors()[v1 + 2]
    S[s].color1 = map.loadSectors()[v1 + 4]
    S[s].color2 = map.loadSectors()[v1 + 5]
    v1 = v1 + 6
    for w in range(S[s].wall_start, S[s].wall_end):
        W[w].x1 = map.loadWalls()[v2+0]
        W[w].y1 = map.loadWalls()[v2+1]
        W[w].x2 = map.loadWalls()[v2+2]
        W[w].y2 = map.loadWalls()[v2+3]
        W[w].color = map.loadWalls()[v2+4]
        v2 = v2 + 5

def clipBehindPlayer(x1, y1, z1, x2, y2, z2):
    da = y1
    db = y2
    d = da - db
    if d == 0:  d = 1
    s = da / d
    x1 = x1 + s * (x2 - x1)
    y1 = y1 + s * (y2 - y1)
    if y1 <= 0.1:
        y1 = 1
    z1 = z1 + s * (z2 - z1)
    return x1, y1, z1

def drawWall(x1, x2, b1, b2, t1, t2, color, s):
    pixel_array = pygame.PixelArray(scaled_surface)
    dyb = b2 - b1
    dyt = t2 - t1
    dx = x2 - x1
    if dx == 0:
        dx = 1
    xs = x1
    # Clip x
    if x1 < 1:  x1 = 1
    if x2 < 1:  x1 = 1
    if x1 > width - 1:  x1 = width - 1
    if x2 > width - 1:  x2 = width - 1
    for x in range(x1, x2):
        y1 = dyb * (x - xs) / dx + b1
        y2 = dyt * (x - xs) / dx + t1
        # Clip y
        if y1 < 1:  y1 = 1
        if y2 < 1:  y2 = 1
        if y1 > height - 1:  y1 = height - 1
        if y2 > height - 1:  y2 = height - 1
        if S[s].surface == 1:
            S[s].surf[x] = y1
            continue
        if S[s].surface == 2:
            S[s].surf[x] = y2
            continue
        if S[s].surface == -1:
            pixel_array[x, int(S[s].surf[x]):int(y1)] = S[s].color1
            # for y in range(int(S[s].surf[x]), int(y1)):
            #     pixel_array[x, y] = S[s].color1
        if S[s].surface == -2:
            pixel_array[x, int(y2):int(S[s].surf[x])] = S[s].color2
            # for y in range(int(y2), int(S[s].surf[x])):
            #     pixel_array[x, y] = S[s].color2




        pixel_array[x, int(y1):int(y2)] = color
    del pixel_array
    

def draw3D():
    world_x = [0, 0, 0, 0]
    world_y = [0, 0, 0, 0]
    world_z = [0, 0, 0, 0]
    CS = math.cos(rad(player_a))
    SN = math.sin(rad(player_a))
    
    # Sort sectors by distance
    for s in range(map.SECTOR_NUM):
        for w in range(map.SECTOR_NUM-s-1):
            if S[w].d < S[w + 1].d:
                st = S[w]
                S[w] = S[w + 1]
                S[w + 1] = st
    for s in range(map.SECTOR_NUM):
        if player_z < S[s].z1:
            S[s].surface = 1
        elif player_z > S[s].z2 + S[s].z1:
            S[s].surface = 2
        else:
            S[s].surface = 0

        for loop in range(2):
            S[s].d = 0
            for w in range (S[s].wall_start, S[s].wall_end):
                # Point world location (no tilting)
                x1 = W[w].x1 - player_x; y1 = W[w].y1 - player_y
                x2 = W[w].x2 - player_x; y2 = W[w].y2 - player_y
                if loop == 0:
                    swp = x2
                    x2 = x1
                    x1 = swp
                    swp = y2
                    y2 = y1
                    y1 = swp
                # World X position
                world_x[0] = int(x1 * CS - y1 * SN)
                world_x[1] = int(x2 * CS - y2 * SN)
                world_x[2] = int(world_x[0])
                world_x[3] = int(world_x[1])
                # World Y position
                world_y[0] = int(y1 * CS + x1 * SN)
                world_y[1] = int(y2 * CS + x2 * SN)
                world_y[2] = int(world_y[0])
                world_y[3] = int(world_y[1])
                S[s].d = S[s].d + distance(0, 0, (world_x[0] + world_x[1])/2, (world_y[0] + world_y[1])/2)
                # World Z position
                world_z[0] = int(S[s].z1 - player_z + ((player_l - 180) * world_y[0] / 64))
                world_z[1] = int(S[s].z1 - player_z + ((player_l - 180) * world_y[1] / 64))
                world_z[2] = int(world_z[0] + S[s].z2)
                world_z[3] = int(world_z[1] + S[s].z2)
                # Skip drawing behind the player
                if world_y[0] < 1 and world_y[1] < 1: continue
                # Point 1 behind the player
                if world_y[0] < 1:
                    world_x[0], world_y[0], world_z[0] = clipBehindPlayer(world_x[0], world_y[0], world_z[0], world_x[1], world_y[1], world_z[1])
                    world_x[2], world_y[2], world_z[2] = clipBehindPlayer(world_x[2], world_y[2], world_z[2], world_x[3], world_y[3], world_z[3])
                if world_y[1] < 1:
                    world_x[1], world_y[1], world_z[1] = clipBehindPlayer(world_x[1], world_y[1], world_z[1], world_x[0], world_y[0], world_z[0])
                    world_x[3], world_y[3], world_z[3] = clipBehindPlayer(world_x[3], world_y[3], world_z[3], world_x[2], world_y[2], world_z[2])
                
                
                # Screen x, y, z
                world_x[0] = int(world_x[0] * focal_lenght / world_y[0] + width / 2); world_y[0] = int(world_z[0] * focal_lenght / world_y[0] + height / 2)
                world_x[1] = int(world_x[1] * focal_lenght / world_y[1] + width / 2); world_y[1] = int(world_z[1] * focal_lenght / world_y[1] + height / 2)
                world_x[2] = int(world_x[2] * focal_lenght / world_y[2] + width / 2); world_y[2] = int(world_z[2] * focal_lenght / world_y[2] + height / 2)
                world_x[3] = int(world_x[3] * focal_lenght / world_y[3] + width / 2); world_y[3] = int(world_z[3] * focal_lenght / world_y[3] + height / 2)
                
                # Draw points
                drawWall(world_x[0], world_x[1], world_y[0], world_y[1], world_y[2], world_y[3], W[w].color, s)
            S[s].d = S[s].d / (S[s].wall_end - S[s].wall_start)
            S[s].surface = S[s].surface * -1


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    buttons = pygame.key.get_pressed()
    dx, dy, dz, player_a, player_l = playerMovement(player_speed, player_a, player_l)
    player_x = player_x + dx; player_y = player_y + dy; player_z = player_z + dz
    scaled_surface.fill(BLACK)

    draw3D()
    window.blit(pygame.transform.scale(scaled_surface, (width * scale, height * scale)), (0, 0))
    pygame.display.update()

    delta_time = pygame.time.get_ticks() - last_tick
    last_tick = pygame.time.get_ticks()
    
    if buttons[pygame.K_m or True]:
        print(delta_time)

    pygame.time.delay(1000 // fps)