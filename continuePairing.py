import sys
import math
import serial
import time
import pygame
# ----- CONFIG -----
PORT = "COM11"   # Change if needed
BAUD = 9600      # Must match Arduino/ESP sketch
TIMEOUT = 1
# ----- SERIAL CONNECTION -----
def connect_bluetooth():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
        time.sleep(2)
        ser.reset_input_buffer()
        print(f"[+] Connected to {PORT} at {BAUD} baud")
        return ser
    except serial.SerialException as e:
        print(f"[!] Could not connect: {e}")
        sys.exit(1)
ser = connect_bluetooth()
# ----- PYGAME SETUP -----
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MPU6050 Cube Simulation")
clock = pygame.time.Clock()
# ----- CUBE DEFINITION -----
cube_vertices = [
    [-1, -1, -1], [-1, -1,  1], [-1,  1, -1], [-1,  1,  1],
    [ 1, -1, -1], [ 1, -1,  1], [ 1,  1, -1], [ 1,  1,  1]
]
cube_faces = [(0,1,3,2),(4,5,7,6),(0,1,5,4),(2,3,7,6),(0,2,6,4),(1,3,7,5)]
face_colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,165,0),(128,0,128)]
# ----- ROTATION FUNCTIONS -----
def rotate_x(point, angle):
    x, y, z = point
    c, s = math.cos(angle), math.sin(angle)
    y, z = y*c - z*s, y*s + z*c
    return x, y, z
def rotate_y(point, angle):
    x, y, z = point
    c, s = math.cos(angle), math.sin(angle)
    x, z = x*c + z*s, -x*s + z*c
    return x, y, z
def rotate_z(point, angle):
    x, y, z = point
    c, s = math.cos(angle), math.sin(angle)
    x, y = x*c - y*s, x*s + y*c
    return x, y, z
def project(point):
    scale = 200 / (point[2] + 5)
    x = int(point[0] * scale + WIDTH // 2)
    y = int(point[1] * scale + HEIGHT // 2)
    return x, y
# ----- PARSE SERIAL DATA -----
def parse_line(line):
    """Expecting 'roll,pitch,yaw' in degrees"""
    try:
        parts = line.strip().split(',')
        if len(parts) != 3:
            return None
        roll = float(parts[0]) * math.pi / 180
        pitch = float(parts[1]) * math.pi / 180
        yaw = float(parts[2]) * math.pi / 180
        return roll, pitch, yaw
    except:
        return None
# ----- MAIN LOOP -----
roll, pitch, yaw = 0, 0, 0
while True:
    screen.fill((10, 10, 30))
    # Quit handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ser.close()
            pygame.quit()
            sys.exit()
    # Read serial data
    if ser.in_waiting > 0:
        raw = ser.readline().decode(errors="ignore")
        angles = parse_line(raw)
        if angles:
            roll, pitch, yaw = angles
    # Transform cube
    transformed = []
    for v in cube_vertices:
        x, y, z = v
        x, y, z = rotate_x((x, y, z), pitch)
        x, y, z = rotate_y((x, y, z), yaw)
        x, y, z = rotate_z((x, y, z), roll)
        transformed.append((x, y, z))
    # Draw cube
    depths = []
    for i, face in enumerate(cube_faces):
        z_avg = sum(transformed[v][2] for v in face) / 4
        depths.append((z_avg, i))
    depths.sort(reverse=True)
    for _, i in depths:
        face = cube_faces[i]
        points = [project(transformed[v]) for v in face]
        pygame.draw.polygon(screen, face_colors[i], points)
        pygame.draw.polygon(screen, (0,0,0), points, 2)
    # HUD text
    font = pygame.font.SysFont("Arial", 24)
    txt = f"Roll: {math.degrees(roll):.1f}°  Pitch: {math.degrees(pitch):.1f}°  Yaw: {math.degrees(yaw):.1f}°"
    info = font.render(txt, True, (255,255,255))
    screen.blit(info, (20, 20))
    pygame.display.flip()
    clock.tick(60)










