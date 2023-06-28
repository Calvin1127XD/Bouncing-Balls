import pygame
import numpy as np
import cv2

# Initialize pygame
pygame.init()

# Define the screen dimensions and other constants
WIDTH, HEIGHT = 800, 800
FPS = 60
RADIUS = 6
BOUNCE_THRESHOLD = 2 * RADIUS
GRAVITY = np.array([0, 0.1])
ENERGY_LOSS_FACTOR = 1

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def hsv_to_rgb(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

def reflect_velocity(circle_center, ball_position, velocity):
    normal = ball_position - circle_center
    normal /= np.linalg.norm(normal)
    dot_product = np.dot(velocity, normal)
    reflection = velocity - 2 * dot_product * normal
    return reflection

class Ball:
    def __init__(self, x, y, color):
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([np.random.uniform(-2, 2), np.random.uniform(-1, 1)], dtype=float)
        self.color = color

    def update(self, boundary_func, circle_center):
        self.vel += GRAVITY
        next_pos = self.pos + self.vel
        if not boundary_func(next_pos[0], next_pos[1]):
            self.vel = reflect_velocity(circle_center, next_pos, self.vel) * ENERGY_LOSS_FACTOR
        else:
            self.pos = next_pos

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, tuple(self.pos.astype(int)), RADIUS)

def create_balls_horizontal(num_balls, y_position, center_x, center_y, radius):
    balls = []
    x_spacing = WIDTH / (num_balls + 1)
    max_height = HEIGHT - BOUNCE_THRESHOLD
    for i in range(num_balls):
        x = (i + 1) * x_spacing
        if not circle_boundary(x, y_position, center_x, center_y, radius):
            continue
        y = y_position
        relative_height = HEIGHT - y
        h = (relative_height / max_height) * 300  # Adjust hue range to 0-300
        color = hsv_to_rgb(h, 1, 1)
        balls.append(Ball(x, y, color))
    return balls

def circle_boundary(x, y, center_x, center_y, radius):
    return (x - center_x) ** 2 + (y - center_y) ** 2 <= (radius - BOUNCE_THRESHOLD) ** 2

def draw_boundary(surface, center_x, center_y, radius):
    pygame.draw.circle(surface, WHITE, (center_x, center_y), radius, 1)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Balls")
    clock = pygame.time.Clock()

    circle_center = np.array([WIDTH // 2, HEIGHT // 2])
    circle_radius = min(WIDTH, HEIGHT) // 3
    boundary_func = lambda x, y: circle_boundary(x, y, circle_center[0], circle_center[1], circle_radius)
    balls = create_balls_horizontal(300, HEIGHT // 2, circle_center[0], circle_center[1], circle_radius)

    # Video recording setup
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter("simulation.mp4", fourcc, FPS, (WIDTH, HEIGHT))

    running = True
    recording = False
    frame_count = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        draw_boundary(screen, circle_center[0], circle_center[1], circle_radius)

        for ball in balls:
            ball.update(boundary_func, circle_center)
            ball.draw(screen)

        pygame.display.flip()

        # Record video
        if recording:
            frame = pygame.surfarray.array3d(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            video.write(frame)

            frame_count += 1
            if frame_count >= FPS * 600:
                recording = False
                video.release()

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
