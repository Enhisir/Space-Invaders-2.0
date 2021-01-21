import os
import pygame
from globals import load_image
from units import Player


pygame.init()


class Button:
    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, image_filename: str):
        # инициализация интерфейса для общения с кнопкой
        self.image = load_image(image_filename, screen)
        self.x, self.y = x, y
        self.rect = pygame.rect.Rect(x, y, self.image.get_width(), self.image.get_height())


class Game:
    FPS = 60
    SIZE = WIDTH, HEIGHT = 1000, 1000
    SW_FONT_MAIN = pygame.font.Font(os.path.join("res", "sw_font.ttf"), 80) # кастомный шрифт

    def __init__(self):
        self.screen = pygame.display.set_mode(Game.SIZE)
        self.bg_image = load_image("background.png", self.screen)
        self.screen.blit(self.bg_image, (0, 0))
        self.clock = pygame.time.Clock()

    def start_activity(self) -> bool:
        running = True
        start_game = False

        # создание кнопок start и exit
        start_button = Button(400, 300, self.screen, "space_invaders_start.png")
        exit_button = Button(400, 425, self.screen, "space_invaders_exit.png")

        text = Game.SW_FONT_MAIN.render("SPACE INVADERS 2.0", True, "#FFD700")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # проверяем, нажал ли ползователь одну из кнопок
                    if start_button.rect.collidepoint(*event.pos):
                        start_game = True
                        running = False
                    elif exit_button.rect.collidepoint(*event.pos):
                        running = False

            # инициализация главного меню
            self.screen.blit(self.bg_image, (0, 0))
            self.screen.blit(text, (42, 100))
            self.screen.blit(start_button.image, (start_button.x, start_button.y))
            self.screen.blit(exit_button.image, (exit_button.x, exit_button.y))

            self.clock.tick(Game.FPS)
            pygame.display.flip()

        return start_game # возвращаем результат: True если нажата start, в ином случае False

    def main_activity(self) -> None:
        running = True

        all_sprites = pygame.sprite.Group()
        player_group = pygame.sprite.Group()

        player = Player(425, 800, self.screen, all_sprites, player_group)
        while running:
            time = self.clock.tick(Game.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            player_group.update(time)

            self.screen.blit(self.bg_image, (0, 0))
            player_group.draw(self.screen)

            pygame.display.flip()


def main() -> None:
    window = Game()
    if window.start_activity() == True:
        window.main_activity()


if __name__ == '__main__':
    main()
pygame.quit()