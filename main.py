import sys
import pygame
from constants    import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from game_manager import GameManager


def main() -> None:

    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption(TITLE)


    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.DOUBLEBUF,
    )

    

    icon = pygame.image.load("assets/image.png").convert_alpha()
    pygame.display.set_icon(icon)

    
    manager = GameManager(screen)
    manager.run()


    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()