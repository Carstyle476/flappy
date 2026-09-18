
import pygame
from random import random, randint

WINDOW_SIZE: tuple[int, int] = (640, 480)
WINDOW_NAME: str = "Flappy!"
TRANSPARENCY: int = 128
BIG_FONT_SIZE: int = 48
SMALL_FONT_SIZE: int = 24
BIRD_COLOR: tuple[int, int, int] = (255, 255, 255)
OBSTACLE_COLOR: tuple[int, int, int] = (192, 192, 192)

FLAP_FORCE: int = 500
GRAVITY: int = 1500
FLY_SPEED: int = 200

BIRD_SIZE: tuple[int, int] = (20, 15)
MIN_OBSTACLE_SIZE: tuple[int, int] = (50, 50)
MAX_OBSTACLE_SIZE: tuple[int, int] = (150, 150)
UNPAUSE_DELAY: int = 3
OBSTACLE_DELAY: float = 1


class Entity(pygame.sprite.Sprite):

    def __init__(self, size: tuple[int, int], color: tuple[int, int, int], x: float, y: float) -> None:
        super().__init__()
        self.image: pygame.Surface = pygame.Surface(size)
        self.image.fill(color)
        self.rect: pygame.Rect = self.image.get_rect(topleft=(int(x), int(y)))
        self.x: float = x
        self.y: float = y

    def update(self, dt: float) -> None:
        self.x -= FLY_SPEED * dt
        self.rect.x = int(self.x)


class Bird(Entity):

    def __init__(self, size: tuple[int, int], color: tuple[int, int, int], x: float, y: float, vel_y: float = 0) -> None:
        super().__init__(size, color, x, y)
        self.vel_y: float = vel_y

    def update(self, dt: float) -> None:
        self.vel_y += GRAVITY * dt / 2
        self.y += self.vel_y * dt
        self.vel_y += GRAVITY * dt / 2
        self.rect.y = int(self.y)


# return a tuple containing rendered text and its centering info
def text_rect_center(font: pygame.font.Font, text: str, color: tuple[int, int, int], pos: tuple[int, int]) -> tuple[pygame.Surface, pygame.Rect]:
    result: pygame.Surface = font.render(text, True, color)
    return (result, result.get_rect(center=pos))


def main() -> None:
    pygame.init()

    pygame.mixer.init()
    crash: pygame.mixer.Sound = pygame.mixer.Sound("sounds/crash.ogg")
    flap_sfx: pygame.mixer.Sound = pygame.mixer.Sound("sounds/flap_sfx.ogg")
    menu_move: pygame.mixer.Sound = pygame.mixer.Sound("sounds/menu_move.ogg")

    SMALL_FONT: pygame.font.Font = pygame.font.SysFont("Verdana", SMALL_FONT_SIZE)
    BIG_FONT: pygame.font.Font = pygame.font.SysFont("Verdana", BIG_FONT_SIZE)

    MENU_TEXT: tuple[pygame.Surface, pygame.Rect] = text_rect_center(
        BIG_FONT,
        "Flappy!",
        (255, 255, 255),
        (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 3)
    )

    MENU_INSTRUCTIONS: tuple[pygame.Surface, pygame.Rect] = text_rect_center(
        SMALL_FONT,
        "Space to play, Escape to pause/exit",
        (255, 255, 255),
        (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
    )

    CONTROL_INSTRUCTIONS: tuple[pygame.Surface, pygame.Rect] = text_rect_center(
        SMALL_FONT,
        "Press any other key to flap",
        (255, 255, 255),
        (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] * 2 // 3)
    )

    PAUSE_TEXT: tuple[pygame.Surface, pygame.Rect] = text_rect_center(
        BIG_FONT,
        "Paused",
        (255, 255, 255),
        (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 3)
    )

    PAUSE_INSTRUCTIONS: tuple[pygame.Surface, pygame.Rect] = text_rect_center(
        SMALL_FONT,
        "Space to continue, Escape to exit",
        (255, 255, 255),
        (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] * 2 // 3)
    )

    GAME_OVER_TEXT: tuple[pygame.Surface, pygame.Rect] = text_rect_center(
        BIG_FONT,
        "Game over!",
        (255, 255, 255),
        (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 3)
    )

    GAME_OVER_INSTRUCTIONS: tuple[pygame.Surface, pygame.Rect] = text_rect_center(
        SMALL_FONT,
        "Space to restart, Escape to return to menu",
        (255, 255, 255),
        (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] * 2 // 3)
    )

    final_score_display: tuple[pygame.Surface, pygame.Rect] = (pygame.Surface((0, 0)), pygame.Rect(0, 0, 0, 0))

    screen: pygame.Surface = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED, vsync=1)
    transparent: pygame.Surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    pygame.display.set_caption(WINDOW_NAME)
    clock: pygame.time.Clock = pygame.time.Clock()

    running: bool = True
    paused: bool = False
    unpause_timer: float = 0
    unpause_timer_render: pygame.Surface = pygame.Surface((0, 0))
    player_score: int = 0
    player_score_render: pygame.Surface = pygame.Surface((0, 0))
    spawn_obstacle_timer: float = 0
    flap: bool = False

    all_sprites: pygame.sprite.Group = pygame.sprite.Group()
    player: Bird = Bird((0, 0), (0, 0, 0), 0, 0)

    def setup_game() -> None:
        nonlocal paused, unpause_timer, player_score, player_score_render, spawn_obstacle_timer, flap, all_sprites, player

        paused = False
        unpause_timer = UNPAUSE_DELAY
        player_score = 0
        player_score_render = SMALL_FONT.render(str(player_score), True, (255, 255, 255))
        spawn_obstacle_timer = OBSTACLE_DELAY
        flap = False

        all_sprites = pygame.sprite.Group()
        player = Bird(BIRD_SIZE, BIRD_COLOR, BIRD_SIZE[0], WINDOW_SIZE[1] // 2 - BIRD_SIZE[1] // 2)
        all_sprites.add(player)

    # 0 = menu
    # 1 = game
    # 2 = dead
    state: int = 0


    # game loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if state == 0 or state == 2:
                    if event.key == pygame.K_SPACE:
                        state = 1
                        setup_game()
                        menu_move.play()
                    elif event.key == pygame.K_ESCAPE:
                        if state == 0: running = False
                        else:
                            state = 0
                            menu_move.play()
                elif state == 1:
                    if paused:
                        if event.key == pygame.K_ESCAPE:
                            state = 0
                            menu_move.play()
                        elif event.key == pygame.K_SPACE:
                            paused = False
                            unpause_timer = UNPAUSE_DELAY
                            menu_move.play()
                    elif event.key == pygame.K_ESCAPE:
                        paused = True
                        flap = False
                        menu_move.play()
                    elif unpause_timer <= 0 and player.y >= 0: flap = True

        dt: float = clock.tick() / 1000
        transparent.fill((0, 0, 0, TRANSPARENCY)) # drawing background with transparency makes a cool fake motion blur effect
        screen.blit(transparent, (0, 0))

        if state == 0: # menu (nothing interesting)
            screen.blit(MENU_TEXT[0], MENU_TEXT[1])
            screen.blit(MENU_INSTRUCTIONS[0], MENU_INSTRUCTIONS[1])
            screen.blit(CONTROL_INSTRUCTIONS[0], CONTROL_INSTRUCTIONS[1])
        elif state == 1: # game
            if not(paused):
                if unpause_timer > 0: # unpause delay
                    unpause_timer -= dt
                    unpause_timer_render = BIG_FONT.render(str(int(unpause_timer) + 1), True, (255, 255, 255))
                    screen.blit(unpause_timer_render, unpause_timer_render.get_rect(center=(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2)))
                else:                    
                    if spawn_obstacle_timer > 0: spawn_obstacle_timer -= dt
                    else:
                        obstacle_height: int = randint(MIN_OBSTACLE_SIZE[1], MAX_OBSTACLE_SIZE[1])
                        all_sprites.add(Entity((randint(MIN_OBSTACLE_SIZE[0], MAX_OBSTACLE_SIZE[0]), obstacle_height), OBSTACLE_COLOR, WINDOW_SIZE[0], randint(0, WINDOW_SIZE[1] - obstacle_height)))
                        spawn_obstacle_timer = OBSTACLE_DELAY

                    all_sprites.update(dt)
                    if player.y + player.rect.height > WINDOW_SIZE[1] or len(pygame.sprite.spritecollide(player, all_sprites, False)) > 1: # pyright: ignore[reportArgumentType]
                        #                                                                      the player always collides with itself  ^^^
                        state = 2
                        final_score_display = text_rect_center(SMALL_FONT, f"Final score: {player_score}", (255, 255, 255), (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
                        crash.play()

                    # sprite deletion
                    to_delete: list[Entity] = []
                    for sprite in all_sprites:
                        if sprite.x + sprite.rect.width < 0: to_delete.append(sprite)
                    for sprite in to_delete:
                        all_sprites.remove(sprite)
                        player_score += 1
                        player_score_render = SMALL_FONT.render(str(player_score), True, (255, 255, 255))

                    # flapping
                    if flap:
                        player.vel_y = -FLAP_FORCE
                        flap = False
                        flap_sfx.play()

            screen.blit(player_score_render, player_score_render.get_rect(center=(WINDOW_SIZE[0] // 2, SMALL_FONT_SIZE)))
            all_sprites.draw(screen)
            if paused:
                screen.blit(transparent, (0, 0))
                screen.blit(PAUSE_TEXT[0], PAUSE_TEXT[1])
                screen.blit(PAUSE_INSTRUCTIONS[0], PAUSE_INSTRUCTIONS[1])
        elif state == 2: # dead
            screen.blit(final_score_display[0], final_score_display[1])
            screen.blit(GAME_OVER_TEXT[0], GAME_OVER_TEXT[1])
            screen.blit(GAME_OVER_INSTRUCTIONS[0], GAME_OVER_INSTRUCTIONS[1])

        pygame.display.flip()


    pygame.quit()

if __name__ == "__main__": main()
