import pygame
import sys
from engine.game import Game
from engine.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pirate's Sea")
    clock = pygame.time.Clock()

    game = Game(screen)

    while True:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        game.handle_events()
        game.update(dt)
        game.draw()

        pygame.display.flip()


if __name__ == "__main__":
    main()
