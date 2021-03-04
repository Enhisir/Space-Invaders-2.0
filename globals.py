import sys
import os
import pygame
from typing import Tuple


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


def load_image(name: str, screen: pygame.surface.Surface,
               colorkey: int or Tuple[int, int, int] or str = None) -> pygame.surface.Surface:
    pygame.font.init()
    fullname = resource_path(os.path.join("res", name))
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha(screen)
    return image