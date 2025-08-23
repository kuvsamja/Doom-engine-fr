import pygame
import math
import cProfile
# import numpy

import map
from textures.texture_lists import T_00, T_01, T_02, T_03, T_04, T_05, T_06, T_07



pygame.init()
pygame.display.set_caption("3d engine")

# Window

aspect_ratio = 4 / 3
width = 200
height = width // aspect_ratio
scale = 4
fps = 30
game_speed = 1
window = pygame.display.set_mode((width * scale, height * scale))
scaled_surface = pygame.Surface((width, height))


# Camera
focal_lenght = 100
focal_lenght_old = focal_lenght
zoom = 3000

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
player_x = 2850
player_y = 180
player_z = -600
player_a = 0    # Horizontal angle
player_l = 180    # Vertical angle
player_height = 200
sensitivity_x = 160 / fps
sensitivity_y = 40 / fps
player_speed = 1600 / fps
colliding = False
last_z_pos = 2

#----------------------------------------------------------------------------------------------------------

class Walls():
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    color = (0, 0, 0)
    wall_texture = 0
    u = 0
    v = 0
    shade = 0

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
    ceiling_texture = 0
    floor_texture = 0
    surface_scale = 1

class TextureMaps():
    width = 0
    height = 0
    name = "placeholder"


textures = [TextureMaps() for i in range(64)]

textures[0].name = T_00.T_00
textures[0].height = T_00.HEIGHT
textures[0].width = T_00.WIDTH

textures[1].name = T_01.T_01
textures[1].height = T_01.HEIGHT
textures[1].width = T_01.WIDTH

textures[2].name = T_02.T_02
textures[2].height = T_02.HEIGHT
textures[2].width = T_02.WIDTH

textures[3].name = T_03.T_03
textures[3].height = T_03.HEIGHT
textures[3].width = T_03.WIDTH

textures[4].name = T_04.T_04
textures[4].height = T_04.HEIGHT
textures[4].width = T_04.WIDTH

textures[5].name = T_05.T_05
textures[5].height = T_05.HEIGHT
textures[5].width = T_05.WIDTH

textures[6].name = T_06.T_06
textures[6].height = T_06.HEIGHT
textures[6].width = T_06.WIDTH

textures[7].name = T_07.T_07
textures[7].height = T_07.HEIGHT
textures[7].width = T_07.WIDTH


def loadMap():
    global textures, W, S
    W = [Walls() for i in range(256)]
    S = [Sectors() for i in range(128)]
    v1 = 0
    v2 = 0
    for s in range(map.SECTOR_NUM):
        S[s].wall_start = map.loadSectors()[v1 + 0]
        S[s].wall_end = map.loadSectors()[v1 + 1]
        S[s].z1 = map.loadSectors()[v1 + 2]
        S[s].z2 = map.loadSectors()[v1 + 3] - map.loadSectors()[v1 + 2]
        S[s].floor_texture = map.loadSectors()[v1 + 4]
        S[s].ceiling_texture = map.loadSectors()[v1 + 5]
        v1 = v1 + 6
        for w in range(S[s].wall_start, S[s].wall_end):
            W[w].x1 = map.loadWalls()[v2+0]
            W[w].y1 = map.loadWalls()[v2+1]
            W[w].x2 = map.loadWalls()[v2+2]
            W[w].y2 = map.loadWalls()[v2+3]
            W[w].wall_texture = map.loadWalls()[v2+4]
            W[w].u = map.loadWalls()[v2+5]
            W[w].v = map.loadWalls()[v2+6]
            v2 = v2 + 7
loadMap()

def floors():
    mult = focal_lenght / 64
    look_up_down = (player_l -180) *  mult
    move_up_down = -player_z / 512
    xo = int(width/2)
    yo = int(height/2)
    pixel_array = pygame.PixelArray(scaled_surface)
    ys = int(look_up_down)
    ye = yo
    if move_up_down < 0:
        ye = int(look_up_down)
        ys = int(-yo)
    
    for y in range(ys, ye):
        for x in range(-xo, xo):
            z = y - look_up_down
            if z == 0:
                z = 0.0001
            fx = x / z * move_up_down
            fy = focal_lenght / z * move_up_down
            rx = fx*math.sin(math.radians(player_a)) - fy*math.cos(math.radians(player_a)) - player_y/512
            ry = fx*math.cos(math.radians(player_a)) + fy*math.sin(math.radians(player_a)) + player_x/512

            if rx < 0:
                rx = -rx + 1
            if ry < 0:
                ry = -ry + 1
            if rx <= 0 or ry <= 0 or rx >=5 or ry >= 5:
                continue
            
            if int(rx) % 2 == int(ry) % 2:
                pixel_array[x + xo, y + yo] = (255, 0, 0)
            else:
                pixel_array[x + xo, y + yo] = (0, 255, 0)

    del pixel_array

                


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

def drawWall(x1, x2, b1, b2, t1, t2, color, s, w, frontBack):
    wt = W[w].wall_texture
    SN = math.sin(math.radians(player_a))
    CS = math.cos(math.radians(player_a))

    framebuffer = pygame.surfarray.pixels3d(scaled_surface)
    dyb = b2 - b1
    dyt = t2 - t1
    dx = x2 - x1
    if dx == 0:
        dx = 1
    xs = x1

    ht = 0
    ht_step = textures[wt].width * W[w].u / dx
    
    # Clip x
    if x1 < 0:
        ht -= ht_step * x1
        x1 = 0
    if x2 < 0:
        x1 = 0
    if x1 > width:
        x1 = width
    if x2 > width:
        x2 = width

    for x in range(x1, x2):
        y1 = dyb * (x - xs) / dx + b1
        y2 = dyt * (x - xs) / dx + t1

        vt = 0
        if y1 == y2:
            vt_step = textures[wt].height * W[w].v
        else:
            vt_step = textures[wt].height * W[w].v / (y2 - y1)
        # Clip y
        if y1 < 0:
            vt -= vt_step * y1
            y1 = 0
        if y2 < 0:
            y2 = 0
        if y1 > height:
            y1 = height
        if y2 > height:
            y2 = height
        # Front walls
        if frontBack == 0:
            if S[s].surface == 1:
                S[s].surf[x] = y1
            if S[s].surface == 2:
                S[s].surf[x] = y2
            # pixel_array[x, int(y1):int(y2)] = color
            for y in range(int(y1), int(y2)):
                pixel = int(vt)%textures[wt].height * 3 * textures[wt].width + int(ht)%textures[wt].width * 3
                # print(pixel)
                c = (textures[wt].name[pixel + 0], textures[wt].name[pixel + 1], textures[wt].name[pixel + 2])
                vt += vt_step
                framebuffer[x, y] = c
            ht += ht_step


        # Back walls
        if frontBack == 1:
            
            mult = focal_lenght / 64
            xo = int(width/2)
            yo = int(height/2)
            x2 = x - xo
            tile = S[s].surface_scale * 10

            if S[s].surface == 1:
                y2 = S[s].surf[x]
                wo = S[s].z1
                surface_texture = S[s].floor_texture

                # c = S[s].color1
            if S[s].surface == 2:
                y1 = S[s].surf[x]
                wo = S[s].z1 + S[s].z2
                surface_texture = S[s].ceiling_texture
                # c = S[s].color2
            # pixel_array[x, int(y1):int(y2)] = c

            look_up_down = (player_l -180) *  mult
            move_up_down = (-player_z + wo) / 512
            ys = int(y1 - yo)
            ye = int(y2 - yo)

            for y in range(ys, ye):
                z = y - look_up_down
                if z == 0:
                    z = 0.0001
                fx = x2 / z * move_up_down * tile
                fy = focal_lenght / z * move_up_down * tile
                rx = fx*SN - fy*CS - player_y/500*tile
                ry = fx*CS + fy*SN + player_x/500*tile

                if rx < 0:
                    rx = -rx + 1
                if ry < 0:
                    ry = -ry + 1
                
                st = surface_texture
                pixel = (textures[st].height - int(ry) % textures[st].height - 1) * 3 * textures[st].width + (int(rx) % textures[st].width)*3
                r = textures[st].name[pixel + 0]
                g = textures[st].name[pixel + 1]
                b = textures[st].name[pixel + 2]
                framebuffer[x2 + xo, y + yo] = (r, g, b)
                # if int(rx) % 2 == int(ry) % 2:
                #     pixel_array[x2 + xo, y + yo] = (255, 0, 0)
                # else:
                #     pixel_array[x2 + xo, y + yo] = (0, 255, 0)



    del framebuffer
    

def draw3D():
    scaled_surface.fill(BLACK)
    world_x = [0, 0, 0, 0]
    world_y = [0, 0, 0, 0]
    world_z = [0, 0, 0, 0]
    CS = math.cos(math.radians(player_a))
    SN = math.sin(math.radians(player_a))
    
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
            cycles = 2
            for i in range(width):
                S[s].surf[i] = height
        elif player_z > S[s].z2 + S[s].z1:
            S[s].surface = 2
            cycles = 2
            for i in range(width):
                S[s].surf[i] = 0
        else:
            S[s].surface = 0
            cycles = 1

        for frontBack in range(cycles):
            S[s].d = 0
            for w in range (S[s].wall_start, S[s].wall_end):
                # Point world location (no tilting)
                x1 = W[w].x1 - player_x; y1 = W[w].y1 - player_y
                x2 = W[w].x2 - player_x; y2 = W[w].y2 - player_y
                if frontBack == 1:
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
                world_z[0] = S[s].z1 - player_z
                world_z[1] = S[s].z1 - player_z
                world_z[2] = S[s].z2 + S[s].z1 - player_z
                world_z[3] = S[s].z2 + S[s].z1 - player_z
                # Adjust Y for vertical camera
                world_z[0] = world_z[0] + ((player_l - 180) * world_y[0] / 64)
                world_z[1] = world_z[1] + ((player_l - 180) * world_y[1] / 64)
                world_z[2] = world_z[2] + ((player_l - 180) * world_y[2] / 64)
                world_z[3] = world_z[3] + ((player_l - 180) * world_y[3] / 64)
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
                drawWall(world_x[0], world_x[1], world_y[0], world_y[1], world_y[2], world_y[3], W[w].color, s, w, frontBack)
            S[s].d = S[s].d / (S[s].wall_end - S[s].wall_start)

#------------------------------------------------------------------------------------------------------------------------

def collision3D(player_x, player_y, player_z):
    player_x = player_x + dx
    player_y = player_y + dy
    player_z = player_z + dz
    colliding = False
    for s in range(map.SECTOR_NUM):
        collision_counter = 0
        for w in range(S[s].wall_start, S[s].wall_end):
            if W[w].x1 == W[w].x2:
                continue
            k = (W[w].y1 - W[w].y2) / (W[w].x1 - W[w].x2)
            n = W[w].y1 - k * W[w].x1
            y_intercept = k * player_x + n
            if player_y < y_intercept:
                if W[w].x1 <= player_x <= W[w].x2 or W[w].x2 <= player_x <= W[w].x1:
                    collision_counter += 1
                    # print(collision_counter, w)
        if collision_counter % 2 == 1 and S[s].z1 <= player_z <= S[s].z2 + S[s].z1:
            colliding = True
            collisionPush(w, s, colliding)
            break
        
    return colliding

def collisionPush(w, s, colliding):
    global dx, dy, dz, last_z_pos
    if player_z < S[s].z1:
        last_z_pos = 1
    if player_z > S[s].z2 + S[s].z1:
        last_z_pos = -1
    if last_z_pos != 0:
        dz = 0
    else:
        dx = 0
        dy = 0
    last_z_pos = 0


def testTextures():
    t = 1
    for y in range(textures[t].height):
        for x in range(textures[t].width):
            pixel = y * 3 * textures[t].width + x * 3
            r = textures[t].name[pixel + 0]
            g = textures[t].name[pixel + 1]
            b = textures[t].name[pixel + 2]

            scaled_surface.set_at((x, y), (r, g, b))

#-----------------------------------------------------------------------------------------------


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
        dx = dx + player_speed * math.sin(math.radians(player_a))
        dy = dy + player_speed * math.cos(math.radians(player_a))
    if buttons[pygame.K_s]:
        dx = dx + player_speed * -math.sin(math.radians(player_a))
        dy = dy + player_speed * -math.cos(math.radians(player_a))
    # Y
    if buttons[pygame.K_d]:
        dx = dx + player_speed * math.cos(math.radians(player_a))
        dy = dy + player_speed * -math.sin(math.radians(player_a))
    if buttons[pygame.K_a]:
        dx = dx + player_speed * -math.cos(math.radians(player_a))
        dy = dy + player_speed * math.sin(math.radians(player_a))
    # Z
    if buttons[pygame.K_SPACE]:
        dz = dz + -player_speed
    if buttons[pygame.K_LSHIFT]:
        dz = dz + player_speed

    # Camera
    # Horizontal angle
    if buttons[pygame.K_LEFT]:
        player_a -= sensitivity_x
        if player_a < 0:
            player_a = player_a + 360
    if buttons[pygame.K_RIGHT]:
        player_a += sensitivity_x
        if player_a > 360:
            player_a = player_a - 360
    # Look angle
    if buttons[pygame.K_DOWN]:
        player_l -= sensitivity_y
    if buttons[pygame.K_UP]:
        player_l += sensitivity_y

    return dx, dy, dz, player_a, player_l


def misc_inputs():
    # Zoom
    global focal_lenght, focal_lenght_old, zoom
    focal_lenght = focal_lenght_old
    if buttons[pygame.K_c]:
        focal_lenght = zoom

    # ms delay
    global delta_time, last_tick
    delta_time = pygame.time.get_ticks() - last_tick
    last_tick = pygame.time.get_ticks()
    if buttons[pygame.K_m]:
        print(delta_time)

    # Load map
    if buttons[pygame.K_KP_ENTER]:
        loadMap()

def inputs():
    global dx, dy, dz, player_a, player_l
    dx, dy, dz, player_a, player_l = playerMovement(player_speed, player_a, player_l)
    misc_inputs()
def delay():
    global last_tick
    delta_time = pygame.time.get_ticks() - last_tick
    if 1000 // fps > delta_time:
        pygame.time.delay(1000 // fps - delta_time)
    delta_time = pygame.time.get_ticks() - last_tick
    print(delta_time)
    last_tick = pygame.time.get_ticks()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    buttons = pygame.key.get_pressed()

    inputs()
    collision3D(player_x, player_y, player_z)
    player_x = player_x + dx; player_y = player_y + dy; player_z = player_z + dz
    draw3D()

    window.blit(pygame.transform.scale(scaled_surface, (width * scale, height * scale)), (0, 0))
    pygame.display.update()

    delay()