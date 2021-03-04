import os
import sys
import pygame
from random import randrange, choice
from globals import load_image, resource_path
from units import Player, WeakEnemy, AltWeakEnemy, StrongEnemy, Bullet, AnimatedExplosion, MedKit

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
    font = pygame.font.Font(resource_path(os.path.join("res", "sw_font.ttf")), 45)

    def __init__(self, screen: pygame.surface.Surface):
        self.screen = screen
        self.x = self.y = 25
        self.count = 0

    def add(self, number: int) -> None:
        self.count += number

    def draw(self) -> None:
        text = Score.font.render(f"SCORE: {self.count}", True, pygame.Color("#FFD700"))
        self.screen.blit(text, (self.x, self.y))


class ScoreWindow:
    def __init__(self):
        self.size = self.width, self.height = 1000, 1000
        self.screen = pygame.display.set_mode(self.size)
        self.screen.blit(load_image("background.png", self.screen), (0, 0))
        main_font = pygame.font.Font(resource_path(os.path.join("res", "sw_font.ttf")), 45)
        text = main_font.render("SCORE", True, pygame.Color("#FFD700"))
        self.x, self.y = self.width // 4 + self.width // 6, self.height // 4 + self.height // 20
        self.screen.blit(text, (self.x, self.y))
        self.file = "score.txt"

        pygame.draw.rect(self.screen, pygame.Color("#FFD700"),
                         ((self.width // 4, self.height // 4), (self.width // 2, self.height // 2)), 5)

    def get_score(self, score, weakenemy, strongenemy):
        font = pygame.font.Font(resource_path(os.path.join("res", "sw_font.ttf")), 25)
        with open(self.file, 'a', encoding='utf-8') as file:
            file.write(str(score) + "\n")
        data = open(self.file, 'r', encoding='utf-8').readlines()
        max_score = max(list(map(int, data)))
        text1 = font.render(f"LAST SCORE: {score}", True, pygame.Color("#FFD700"))
        text2 = font.render(f"BEST SCORE: {max_score}", True, pygame.Color("#FFD700"))
        text3 = font.render(f"KILLED WEAK ENEMIES: {weakenemy}", True, pygame.Color("#FFD700"))
        text4 = font.render(f"KILLED STRONG ENEMIES: {strongenemy}", True, pygame.Color("#FFD700"))
        self.screen.blit(text1, (self.x - self.width // 9, self.y + self.height // 12))
        self.screen.blit(text2, (self.x - self.width // 9, self.y + self.height // 12 * 2))
        self.screen.blit(text3, (self.x - self.width // 9, self.y + self.height // 12 * 3))
        self.screen.blit(text4, (self.x - self.width // 9, self.y + self.height // 12 * 4))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
            pygame.display.flip()


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
    VELOCITY = 400
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


class CollisionHandler:
    def __init__(self, player: Player,
                 all_sprites: pygame.sprite.Group,
                 enemy_group: pygame.sprite.Group,
                 bullet_group: pygame.sprite.Group,
                 exploration_group: pygame.sprite.Group,
                 medkit_group: pygame.sprite.Group,
                 score: Score,
                 screen: pygame.surface.Surface):
        self.player = player
        self.agroup = all_sprites
        self.engroup = enemy_group
        self.bgroup = bullet_group
        self.exgroup = exploration_group
        self.mgroup = medkit_group
        self.screen = screen
        self.score = score
        self.count_weakenemy = 0
        self.count_strongenemy = 0

    def update(self) -> bool:
        running = True

        for b in self.bgroup.sprites():
            if b.rect.y >= self.screen.get_height():
                b.kill()
            elif b.get_owner() is self.player:
                for e in self.engroup.sprites():
                    if pygame.sprite.collide_mask(e, b):
                        e.hurt(b)
                        b.kill()
                        break
            else:
                if pygame.sprite.collide_mask(self.player, b):
                    self.player.hurt(b)
                    b.kill()

        for e in self.engroup.sprites():
            if pygame.sprite.collide_mask(self.player, e):
                running = False
                AnimatedExplosion(e.rect.x, e.rect.y, self.screen, self.agroup, self.exgroup)
                e.kill()
                break
            elif e.get_health() <= 0:
                if isinstance(e, WeakEnemy) or isinstance(e, AltWeakEnemy):
                    self.score.add(50)
                    self.count_weakenemy += 1
                elif isinstance(e, StrongEnemy):
                    self.score.add(100)
                    self.count_strongenemy += 1
                AnimatedExplosion(e.rect.x, e.rect.y, self.screen, self.agroup, self.exgroup)
                e.kill()
            elif e.rect.y >= self.screen.get_height():
                AnimatedExplosion(e.rect.x, e.rect.y, self.screen, self.agroup, self.exgroup)
                e.kill()

        for boom in self.exgroup.sprites():
            if boom.rect.y >= self.screen.get_height():
                boom.kill()

        for kit in self.mgroup.sprites():
            if pygame.sprite.collide_mask(self.player, kit):
                self.player.heal(1)
                kit.kill()
            elif kit.rect.y >= self.screen.get_height():
                kit.kill()

        if self.player.get_health() <= 0:
            running = False
        return running


class Game:
    FPS = 120
    SIZE = WIDTH, HEIGHT = 1000, 1000
    SW_FONT_MAIN = pygame.font.Font(resource_path(os.path.join("res", "sw_font.ttf")), 80)  # кастомный шрифт
    SCORE_EVENT = pygame.USEREVENT + 1
    ENEMY_APPEAR_EVENT = pygame.USEREVENT + 2
    ENEMY_SHOOT_EVENT = pygame.USEREVENT + 3
    MEDKIT_APPEAR_EVENT = pygame.USEREVENT + 4

    def __init__(self):
        self.screen = pygame.display.set_mode(Game.SIZE)
        pygame.display.set_caption('Space Invaders 2.0')
        pygame.display.set_icon(load_image("icon.ico", self.screen))
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
            last = pygame.time.get_ticks()
            while pygame.time.get_ticks() - last <= 1500:
                time = self.clock.tick(Game.FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
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
                all_sprites.update(time)
                c_handler.update()

                self.background.draw(time)
                all_sprites.draw(self.screen)

                score.draw()
                pygame.display.flip()
            pygame.time.set_timer(Game.SCORE_EVENT, 0)
            pygame.time.set_timer(Game.ENEMY_APPEAR_EVENT, 0)
            pygame.time.set_timer(Game.ENEMY_SHOOT_EVENT, 0)
            pygame.time.set_timer(Game.MEDKIT_APPEAR_EVENT, 0)
            for item in all_sprites.sprites():
                item.kill()
            self.background.set_static(True)

        running = True
        pygame.time.set_timer(Game.SCORE_EVENT, 90)
        pygame.time.set_timer(Game.ENEMY_APPEAR_EVENT, 1250)
        pygame.time.set_timer(Game.ENEMY_SHOOT_EVENT, 1250)
        pygame.time.set_timer(Game.MEDKIT_APPEAR_EVENT, 10000)

        all_sprites = pygame.sprite.Group()
        player_group = pygame.sprite.Group()
        enemy_group = pygame.sprite.Group()
        bullet_group = pygame.sprite.Group()
        exploration_group = pygame.sprite.Group()
        medkit_group = pygame.sprite.Group()

        player = Player(425, 800, self.screen, all_sprites, player_group)

        self.background.set_static(False)
        score = Score(self.screen)
        hp_bar = HealthBar(player, self.screen)

        c_handler = CollisionHandler(player, all_sprites, enemy_group, bullet_group,
                                     exploration_group, medkit_group, score, self.screen)

        while running:
            time = self.clock.tick(Game.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
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
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    Bullet(player.rect.x + player.rect.w / 2, player.rect.y, player, player_group,
                           self.screen, all_sprites, bullet_group)
                elif event.type == Game.ENEMY_SHOOT_EVENT:
                    for e in enemy_group.sprites():
                        Bullet(e.rect.x + e.rect.w / 2, e.rect.y + e.rect.h,
                               e, enemy_group, self.screen, all_sprites, bullet_group)
                elif event.type == Game.SCORE_EVENT:
                    score.add(1)
                elif event.type == Game.MEDKIT_APPEAR_EVENT and player.get_health() < 3:
                    MedKit(randrange(0, Game.WIDTH - 150), -150,
                           self.screen, all_sprites, medkit_group)

            all_sprites.update(time)

            if not c_handler.update():
                AnimatedExplosion(player.rect.x, player.rect.y, self.screen, all_sprites, exploration_group)
                player.kill()
                destroy()
                win = ScoreWindow()
                win.get_score(c_handler.score.count, c_handler.count_weakenemy, c_handler.count_strongenemy)
                win.run()
                return

            self.background.draw(time)
            all_sprites.draw(self.screen)

            score.draw()
            hp_bar.draw()

            pygame.display.flip()


def main() -> None:
    window = Game()
    while window.start_activity():
        window.main_activity()


if __name__ == '__main__':
    main()
pygame.quit()