import pygame
import random
import numpy as np
import sys
import time
import copy

# Initialize the game
pygame.init()
pygame.display.set_caption('Find the gap!')
clock = pygame.time.Clock()
delay = 300                         # Rendering speed in ms
level = 1
game_over = False
begin = False
first_pass_given = False
first_pass_arrived = False
second_pass_given = False
second_pass_arrived = False
R2_selected = False
pull_selected = False
forward_pass = False
no_decision = False
wrong_decision = False
mistake = False
ball_at_D = True
success = False

# Initialize the field
WIDTH = 1000
HEIGHT = 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Define the RGB color codes
GREEN = (50, 205, 50)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
font = pygame.font.Font('freesansbold.ttf', 32)

# Initialize the positions and speeds of the players
pos_D1 = [100, 75]
pos_D2 = [330, 75]
pos_9 = [100, 200]
pos_R1 = [330, 300]
speed_R1 = [0, 0]

init_pos_R2 = [600, 500]
init_pos_pull = [420, 600]
init_speed_R2 = [-0.2, -0.5]
init_speed_pull = [0.6, -0.6]
pos_R2 = copy.deepcopy(init_pos_R2)
pos_pull = copy.deepcopy(init_pos_pull)
speed_R2 = copy.deepcopy(init_speed_R2)
speed_pull = copy.deepcopy(init_speed_pull)

pos_D3 = [random.randint(400, 900), 75]

# Initialize the position of the ball
init_pos_ball = [100, 170]
pos_ball = copy.deepcopy(init_pos_ball)


# Pass the ball from its current position to another player
def passBall(pos_ball, pos_player2, speed_player2):
    # Compute the Euclidean distance between the ball and the receiving player
    distance = np.sqrt((pos_ball[0]-pos_player2[0]) ** 2 + (pos_ball[1]-pos_player2[1]) ** 2)

    # Time in which the pass needs to be completed in ms
    pass_time = distance / 1.5

    # Location of the receiving player when the pass is completed
    pos_receiver = [pos_player2[0] + speed_player2[0]*pass_time, pos_player2[1] + speed_player2[1]*pass_time]

    # Ensure that the ball is passed in front of the player
    pos_destination = [pos_receiver[0] - 15, pos_receiver[1] - 40]

    # Compute the required direction of the ball
    speed_ball = [(pos_destination[0] - pos_ball[0]) / pass_time, (pos_destination[1] - pos_ball[1]) / pass_time]

    return pos_destination, speed_ball


# Check whether the ball has arrived at the receiving player
def passArrived(pos_ball, speed_ball, pos_destination):
    if speed_ball[0] > 0 and speed_ball[1] > 0:
        if pos_ball[0] >= pos_destination[0] and pos_ball[1] >= pos_destination[1]:
            return True
    elif speed_ball[0] > 0 and speed_ball[1] < 0:
        if pos_ball[0] >= pos_destination[0] and pos_ball[1] <= pos_destination[1]:
            return True
    elif speed_ball[0] < 0 and speed_ball[1] > 0:
        if pos_ball[0] <= pos_destination[0] and pos_ball[1] >= pos_destination[1]:
            return True
    elif speed_ball[0] < 0 and speed_ball[1] < 0:
        if pos_ball[0] <= pos_destination[0] and pos_ball[1] <= pos_destination[1]:
            return True
    else:
        return False


def checkDecision(pos_receiver, speed_receiver, pos_D3):
    # Compute the x-coordinate of R2/pull when at the defensive line
    num_iter = (75 - pos_receiver[1]) / speed_receiver[1]
    x_at_D = pos_receiver[0] + num_iter*speed_receiver[0]

    # Check whether this x-coordinate is not too close to the defender
    margin = 200
    if x_at_D >= pos_D3[0] - margin and x_at_D <= pos_D3[0] + margin:
        wrong_decision = True
    else:
        wrong_decision = False

    return wrong_decision


def ballAtD(pos_ball, pos_D3):
    # Check if the ball has passed the defensive line
    if pos_ball[1] <= pos_D3[1]:
        ball_at_D = True
    else:
        ball_at_D = False

    return ball_at_D


# Run the game
while not game_over:
    # Reset all variables when one level is finished
    if success:
        level += 1
        pos_D3 = [random.randint(400, 900), 75]
        pos_R2 = copy.deepcopy(init_pos_R2)
        pos_pull = copy.deepcopy(init_pos_pull)
        speed_R2 = copy.deepcopy(init_speed_R2)
        speed_pull = copy.deepcopy(init_speed_pull)
        pos_ball = copy.deepcopy(init_pos_ball)
        R2_selected = False
        pull_selected = False
        begin = False
        first_pass_given = False
        first_pass_arrived = False
        second_pass_given = False
        second_pass_arrived = False
        success = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        # The game begins if the space bar is hit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                begin = True
            # If the game has begun, the player can make one choice: pass to the R2, or to the pull
            if event.key == pygame.K_RIGHT and begin and not pull_selected:
                R2_selected = True
            if event.key == pygame.K_DOWN and begin and not R2_selected:
                pull_selected = True

    if not mistake:
        # Draw the field
        screen.fill(GREEN)

        # Draw the defenders
        pygame.draw.circle(screen, RED, pos_D1, 20)
        pygame.draw.circle(screen, RED, pos_D2, 20)
        pygame.draw.circle(screen, RED, pos_D3, 20)

        # Draw the attackers
        pygame.draw.circle(screen, WHITE, pos_9, 20)
        pygame.draw.circle(screen, WHITE, pos_R1, 20)
        pygame.draw.circle(screen, WHITE, pos_R2, 20)
        pygame.draw.circle(screen, WHITE, pos_pull, 20)

        # Draw the ball
        pygame.draw.ellipse(screen, YELLOW, (pos_ball[0], pos_ball[1], 30, 30))

        # Denote the level
        level_string = 'Level: ' + str(level)
        text = font.render(level_string, True, BLACK, GREEN)
        textRect = text.get_rect()
        textRect.center = (WIDTH - 100, HEIGHT - 50)
        screen.blit(text, textRect)

        # Pass the ball from 9 to R1, and move the R2 and pull players
        if begin:
            # Compute the pass direction only once
            if not first_pass_given:
                begin_time = time.time()
                pos_destination_1, speed_ball_1 = passBall(pos_ball, pos_R1, speed_R1)
                first_pass_given = True

            # Execute the pass as long as it has not arrived yet
            if not first_pass_arrived:
                if not passArrived(pos_ball, speed_ball_1, pos_destination_1):
                    pos_ball[0] += speed_ball_1[0]
                    pos_ball[1] += speed_ball_1[1]
                else:
                    first_pass_arrived = True

            # Move the R2 and pull players after a slight delay
            if time.time() >= begin_time + 0.3:
                pos_R2[0] += speed_R2[0]
                pos_R2[1] += speed_R2[1]
                pos_pull[0] += speed_pull[0]
                pos_pull[1] += speed_pull[1]

            # If the player makes no decision, the game is over
            if not R2_selected and not pull_selected and time.time() >= begin_time + 4:
                no_decision = True
                mistake_time = time.time()
                if time.time() >= mistake_time:
                    mistake = True

        # Executes the decision of the player
        if first_pass_arrived:
            if R2_selected:
                # Compute the pass direction only once
                if not second_pass_given:
                    pos_destination_2, speed_ball_2 = passBall(pos_ball, pos_R2, speed_R2)
                    second_pass_given = True
                    wrong_decision = checkDecision(pos_R2, speed_R2, pos_D3)
                    if wrong_decision:
                        mistake_time = time.time()

                    if speed_ball_2[1] < 0:
                        mistake_time = time.time()
                        forward_pass = True

                # Execute the pass as long as it has not arrived yet
                if not second_pass_arrived:
                    if not passArrived(pos_ball, speed_ball_2, pos_destination_2):
                        pos_ball[0] += speed_ball_2[0]
                        pos_ball[1] += speed_ball_2[1]
                    # When the pass has arrived, move the ball with the receiving player
                    else:
                        second_pass_arrived = True

                if second_pass_arrived:
                    pos_ball[0] += speed_R2[0]
                    pos_ball[1] += speed_R2[1]

            elif pull_selected:
                # Compute the pass direction only once
                if not second_pass_given:
                    pos_destination_2, speed_ball_2 = passBall(pos_ball, pos_pull, speed_pull)
                    second_pass_given = True
                    wrong_decision = checkDecision(pos_pull, speed_pull, pos_D3)
                    if wrong_decision:
                        mistake_time = time.time()

                    if speed_ball_2[1] < 0:
                        mistake_time = time.time()
                        forward_pass = True

                # Execute the pass as long as it has not arrived yet
                if not second_pass_arrived:
                    if not passArrived(pos_ball, speed_ball_2, pos_destination_2):
                        pos_ball[0] += speed_ball_2[0]
                        pos_ball[1] += speed_ball_2[1]
                    # When the pass has arrived, move the ball with the receiving player
                    else:
                        second_pass_arrived = True

                if second_pass_arrived:
                    pos_ball[0] += speed_pull[0]
                    pos_ball[1] += speed_pull[1]

            # Check whether the pass was executed correctly
            if second_pass_arrived:
                if forward_pass:
                    if time.time() >= mistake_time + 1.3:
                        mistake = True
                elif wrong_decision:
                    if time.time() >= mistake_time + 2:
                        mistake = True
                elif ballAtD(pos_ball, pos_D3):
                    success = True

    # If a mistake has been made
    else:
        if forward_pass:
            # First notify the player what went wrong
            screen.fill(WHITE)
            text = font.render('Forward pass...', True, BLACK, WHITE)
            textRect = text.get_rect()
            textRect.center = (WIDTH/2, HEIGHT/2)
            screen.blit(text, textRect)

            # Then close the game
            if time.time() >= mistake_time + 4:
                game_over = True

        elif no_decision:
            # First notify the player what went wrong
            screen.fill(WHITE)
            text = font.render('Making no decision is the worst decision!', True, BLACK, WHITE)
            textRect = text.get_rect()
            textRect.center = (WIDTH / 2, HEIGHT / 2)
            screen.blit(text, textRect)

            # Then close the game
            if time.time() >= mistake_time + 4:
                game_over = True

        elif wrong_decision:
            if R2_selected:
                # First notify the player what went wrong
                screen.fill(WHITE)
                text = font.render('Pull was the better option.', True, BLACK, WHITE)
                textRect = text.get_rect()
                textRect.center = (WIDTH / 2, HEIGHT / 2)
                screen.blit(text, textRect)

                # Then close the game
                if time.time() >= mistake_time + 5:
                    game_over = True
            elif pull_selected:
                # First notify the player what went wrong
                screen.fill(WHITE)
                text = font.render('R2 was the better option.', True, BLACK, WHITE)
                textRect = text.get_rect()
                textRect.center = (WIDTH / 2, HEIGHT / 2)
                screen.blit(text, textRect)

                # Then close the game
                if time.time() >= mistake_time + 5:
                    game_over = True


    # Add some delay to the updating
    clock.tick(delay)
    pygame.display.update()
