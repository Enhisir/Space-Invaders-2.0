import pygame
from globals import load_image


class Character(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, *group):
        super().__init__(*group)
        self.screen = screen
        self.image = self.get_image(screen)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return pygame.surface.Surface()


class Player(Character):
    velocity = 500
    power = 1

    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, *group):
        super().__init__(x, y, screen, *group)
        self.hp = 3

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return load_image("player.png", screen)

    def get_health(self) -> int:
        return self.hp

    def hurt(self, other):
        self.hp -= other.power
        if self.hp < 0:
            self.hp = 0

    def update(self, time: int) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect = self.rect.move(0, -Player.velocity * time / 1000)
        elif keys[pygame.K_s]:
            self.rect = self.rect.move(0, Player.velocity * time / 1000)

        if self.rect.y < 50:
            self.rect.y = 50
        elif self.rect.y + self.rect.h > self.screen.get_height() - 10:
            self.rect.y = self.screen.get_height() - 10 - self.rect.h

        if keys[pygame.K_a]:
            self.rect = self.rect.move(-Player.velocity * time / 1000, 0)
        elif keys[pygame.K_d]:
            self.rect = self.rect.move(Player.velocity * time / 1000, 0)

        if self.rect.x < 10:
            self.rect.x = 10
        elif self.rect.x + self.rect.w >= self.screen.get_width() - 10:
            self.rect.x = self.screen.get_width() - 10 - self.rect.w


class BaseEnemy(Character):
    power = 1