import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_SIZE = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SPEED = [5, 5]
PADDLE_SPEED = 7

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong')

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Paddle and Ball Initialization
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
left_paddle = pygame.Rect(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 20 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Move paddles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN]:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_w]:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s]:
        right_paddle.y += PADDLE_SPEED

    # Bounce the ball off the top and bottom walls
    if ball.y <= 0 or ball.y >= HEIGHT - BALL_SIZE:
        ball.y = -ball.y
        BALL_SPEED[1] = -BALL_SPEED[1]

    # Move the ball
    ball.x += BALL_SPEED[0]
    ball.y += BALL_SPEED[1]

    # Bounce the ball off the paddles
    if (ball.colliderect(left_paddle) or ball.colliderect(right_paddle)) and ball.x <= WIDTH - BALL_SIZE:
        BALL_SPEED[0] = -BALL_SPEED[0]

    # Check for ball out of bounds (game over)
    if ball.x <= 0:
        ball.x, ball.y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2
        ball.y = HEIGHT // 2 - BALL_SIZE // 2
        BALL_SPEED[0] = 5

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)
