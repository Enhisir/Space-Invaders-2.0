import os
import pygame
from random import randrange, choice
from globals import load_image
from units import Player, WeakEnemy, AltWeakEnemy, StrongEnemy

pygame.init()


class HealthBar:
    def __init__(self, player: Player, screen: pygame.surface.Surface):
        self.image = load_image("hp.png", screen)
        self.screen = screen
        self.player = player
        self.rect = pygame.rect.Rect(845, 25, self.image.get_width(),
                                     self.image.get_height())
        self.space = 5

    def draw(self) -> None:
        hp = self.player.get_health()
        if hp:
            for i in range(hp):
                self.screen.blit(
                    self.image,
                    (self.rect.x + self.rect.w * i + self.space * i, self.rect.y)
                )


class Score:
    font = pygame.font.Font(os.path.join("res", "sw_font.ttf"), 45)

    def __init__(self, screen: pygame.surface.Surface):
        self.screen = screen
        self.x = self.y = 25
        self.count = 0

    def add(self, number: int) -> None:
        self.count += number

    def draw(self) -> None:
        text = Score.font.render(f"SCORE: {self.count}", True, pygame.Color("#FFD700"))
        self.screen.blit(text, (self.x, self.y))


class Button:
    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, image_filename: str):
        # инициализация интерфейса для общения с кнопкой
        self.image = load_image(image_filename, screen)
        self.screen = screen
        self.x, self.y = x, y
        self.rect = pygame.rect.Rect(x, y, self.image.get_width(), self.image.get_height())

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))


class Background:
    VELOCITY = 500
    SIZE = WIDTH, HEIGHT = 1000, 1000

    def __init__(self, screen: pygame.surface.Surface, static: bool = True):
        self.screen = screen
        self.image = load_image("background.png", self.screen)
        self.static = static
        self.y = 0

    def set_static(self, state: bool) -> None:
        self.static = state

    def draw(self, time: int = None) -> None:
        if self.static:
            self.screen.blit(self.image, (0, 0))
        else:
            dy = round(Background.VELOCITY * time / 1000)
            self.y = (self.y + dy) % (Background.HEIGHT + 1)
            self.screen.blit(self.image, (0, -(Background.HEIGHT - self.y)))
            self.screen.blit(self.image, (0, self.y))


class Game:
    FPS = 120
    SIZE = WIDTH, HEIGHT = 1000, 1000
    SW_FONT_MAIN = pygame.font.Font(os.path.join("res", "sw_font.ttf"), 80)  # кастомный шрифт
    SCORE_EVENT = pygame.USEREVENT + 1
    ENEMY_APPEAR_EVENT = pygame.USEREVENT + 2

    def __init__(self):
        self.screen = pygame.display.set_mode(Game.SIZE)
        self.background = Background(self.screen)
        self.clock = pygame.time.Clock()

    def start_activity(self) -> bool:
        running = True
        start_game = False

        # создание кнопок start и exit
        start_button = Button(400, 300, self.screen, "space_invaders_start.png")
        exit_button = Button(400, 425, self.screen, "space_invaders_exit.png")
        text = Game.SW_FONT_MAIN.render("SPACE INVADERS 2.0", True, pygame.Color("#FFD700"))

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
            self.background.draw()
            self.screen.blit(text, (42, 100))
            start_button.draw()
            exit_button.draw()

            self.clock.tick(Game.FPS)
            pygame.display.flip()

        return start_game  # возвращаем результат: True если нажата start, в ином случае False

    def main_activity(self) -> None:
        def destroy():
            self.background.set_static(True)
            pygame.time.set_timer(Game.SCORE_EVENT, 0)
            pygame.time.set_timer(Game.ENEMY_APPEAR_EVENT, 0)
            for item in all_sprites.sprites():
                item.kill()

        running = True
        pygame.time.set_timer(Game.SCORE_EVENT, 90)
        pygame.time.set_timer(Game.ENEMY_APPEAR_EVENT, 750)

        all_sprites = pygame.sprite.Group()
        player_group = pygame.sprite.Group()
        enemy_group = pygame.sprite.Group()

        player = Player(425, 800, self.screen, all_sprites, player_group)

        self.background.set_static(False)
        score = Score(self.screen)
        hp_bar = HealthBar(player, self.screen)

        while running:
            time = self.clock.tick(Game.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    player.hp -= 1
                    print(player.get_health())
                elif event.type == Game.ENEMY_APPEAR_EVENT:
                    mode = choice([1, 1, 1, 1, 2, 2, 2, 2, 3, 3])
                    if mode == 1:
                        WeakEnemy(randrange(0, Game.WIDTH - 150), -150,
                                  self.screen, all_sprites, enemy_group)
                    elif mode == 2:
                        AltWeakEnemy(randrange(0, Game.WIDTH - 150), -150,
                                     self.screen, all_sprites, enemy_group)
                    elif mode == 3:
                        StrongEnemy(randrange(0, Game.WIDTH - 150), -150,
                                    self.screen, all_sprites, enemy_group)
                elif event.type == Game.SCORE_EVENT:
                    score.add(1)

            all_sprites.update(time)

            self.background.draw(time)
            all_sprites.draw(self.screen)

            score.draw()
            hp_bar.draw()

            if any(map(lambda x: pygame.sprite.collide_mask(player, x),
                       enemy_group.sprites())) or player.get_health() == 0:
                destroy()
                return

            pygame.display.flip()


def main() -> None:
    window = Game()
    while window.start_activity():
        window.main_activity()


if __name__ == '__main__':
    main()
pygame.quit()
