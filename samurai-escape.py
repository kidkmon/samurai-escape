import pgzrun
from pygame import Rect

TITLE = "Samurai Escape"
WIDTH = 800
HEIGHT = 600

game_state = "menu"
sound_on = True

platforms = [
    Rect(0, 500, 10, 8),
    Rect(100, 400, 10, 8),
    Rect(200, 340, 10, 8),
    Rect(300, 240, 10, 8),
    Rect(400, 140, 10, 8),
    Rect(450, 140, 10, 8),
]

grounds = [
    Rect(0, HEIGHT - 10, WIDTH, 10),
]


class UIManager:
    def __init__(self):
        self.menu_buttons = {
            "start": Rect(WIDTH // 2 - 100, 280, 200, 40),
            "music": Rect(WIDTH // 2 - 100, 330, 200, 40),
            "quit": Rect(WIDTH // 2 - 100, 380, 200, 40)
        }
        
    def draw_menu(self):
        screen.clear()
        screen.draw.text(TITLE, center=(WIDTH // 2, 150), fontsize=60, color="darkorange")
        self._draw_button("start", "Start Game", "darkgreen")
        self._draw_button("music", "Toggle Music", "darkblue")
        self._draw_button("quit", "Quit", "darkred")

    def draw_gameover(self):
        screen.clear()
        screen.draw.text("Game Over", center=(WIDTH // 2, 200), fontsize=60, color="red")
        self._draw_button("start", "Retry", "darkgreen")
        self._draw_button("quit", "Quit", "darkred")

    def draw_victory(self):
        screen.clear()
        screen.draw.text("You Win!", center=(WIDTH // 2, 200), fontsize=60, color="green")
        self._draw_button("start", "Play Again", "darkgreen")
        self._draw_button("quit", "Quit", "darkred")

    def _draw_button(self, key, text, color):
        screen.draw.filled_rect(self.menu_buttons[key], color)
        screen.draw.text(text, center=self.menu_buttons[key].center, fontsize=32)


class BaseActor:
    def __init__(self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image

    def rect(self):
        return Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        screen.blit(self.image, (self.x, self.y))


class Player(BaseActor):
    def __init__(self):
        super().__init__(50, HEIGHT - 100, 50, 80, "")
        self.velocity_y = 0
        self.frame = 0
        self.timer = 0
        self.facing = 'right'
        self.last_state = 'idle'
        self.on_ground = False
        self.can_double_jump = True

        self.animations = {
            'walk_right': [f"samurai-walk/samurai_walk_{str(i).zfill(2)}_right" for i in range(12)],
            'walk_left':  [f"samurai-walk/samurai_walk_{str(i).zfill(2)}_left" for i in range(12)],
            'idle_right': [f"samurai-idle/samurai_idle_{str(i).zfill(2)}_right" for i in range(10)],
            'idle_left':  [f"samurai-idle/samurai_idle_{str(i).zfill(2)}_left" for i in range(10)]
        }
        self.image = self.animations['idle_right'][0]

    def update(self):
        self.apply_gravity()
        self.check_collisions()
        self.handle_movement()
        self.update_animation()
        self.check_victory()

    def apply_gravity(self):
        self.velocity_y += 0.5
        self.y += self.velocity_y
        self.on_ground = False

    def check_collisions(self):
        for platform in platforms + grounds:
            if Rect(self.x, self.y + self.height, self.width, 10).colliderect(platform):
                self.y = platform.top - self.height
                self.velocity_y = 0
                self.on_ground = True
                self.can_double_jump = True

    def handle_movement(self):
        dx = 0
        if keyboard.left:
            dx = -3
            self.facing = 'left'
        elif keyboard.right:
            dx = 3
            self.facing = 'right'

        # Movement bounds
        self.x = max(-40, min(WIDTH - self.width, self.x + dx))

        self.timer += 1
        self.set_animation(dx != 0)

    def set_animation(self, moving):
        state = 'walk' if moving else 'idle'
        if self.last_state != state:
            self.frame = 0
            self.last_state = state

        delay = 5 if state == 'walk' else 10
        if self.timer > delay:
            self.frame = (self.frame + 1) % len(self.animations[f"{state}_{self.facing}"])
            self.timer = 0

    def update_animation(self):
        anim_key = f"{self.last_state}_{self.facing}"
        frames = self.animations.get(anim_key, [])
        if frames:
            self.image = frames[self.frame % len(frames)]

    def check_victory(self):
        if self.rect().colliderect(star.rect()):
            global game_state
            game_state = "victory"
            if sound_on:
                sounds.win.play()

    def jump(self):
        if self.on_ground:
            self.velocity_y = -10
            self.can_double_jump = True
            if sound_on:
                sounds.jump.play()
        elif self.can_double_jump:
            self.velocity_y = -10
            self.can_double_jump = False
            if sound_on:
                sounds.jump.play()

class Barrel(BaseActor):
    def __init__(self, x, y, direction):
        super().__init__(x, y, 30, 30, "barrel")
        self.dir = direction

    def update(self):
        self.x += self.dir * 2
        if self.x < 0 or self.x > WIDTH - self.width:
            self.dir *= -1

        if self.rect().colliderect(player.rect()):
            global game_state
            game_state = "gameover"
            if sound_on:
                sounds.hit.play()


def start_game():
    global player, barrels, game_state
    player = Player()
    barrels = [
        Barrel(100, 470, 1),
        Barrel(600, 370, -1),
        Barrel(100, 270, 1),
        Barrel(600, 170, -1),
    ]
    game_state = "playing"
    if sound_on:
        music.play("background")
        music.set_volume(0.3)


def draw():
    screen.clear()
    if game_state == "menu":
        ui.draw_menu()
    elif game_state == "victory":
        ui.draw_victory()
    elif game_state == "gameover":
        ui.draw_gameover()
    elif game_state == "playing":
        screen.fill((20, 20, 40))
        star.draw()
        player.draw()
        for p in platforms:
            screen.blit("platform", (p.left, p.top))
        for g in grounds:
            screen.blit("ground", (g.left, g.top))
        for b in barrels:
            b.draw()

def update():
    if game_state == "playing":
        player.update()
        for b in barrels:
            b.update()

def on_key_down(key):
    global game_state, sound_on
    if game_state in ["menu", "victory", "gameover"]:
        if key == keys.RETURN:
            start_game()
        elif key == keys.ESCAPE:
            exit()
        elif key == keys.M and game_state == "menu":
            toggle_music()
    elif game_state == "playing":
        if key == keys.SPACE:
            player.jump()

def on_mouse_down(pos):
    if game_state in ["menu", "victory", "gameover"]:
        if ui.menu_buttons["start"].collidepoint(pos):
            if sound_on:
                sounds.click.play()
            start_game()
        elif ui.menu_buttons["music"].collidepoint(pos):
            toggle_music()
        elif ui.menu_buttons["quit"].collidepoint(pos):
            exit()

def toggle_music():
    global sound_on
    sound_on = not sound_on
    if sound_on:
        music.play("background")
        music.set_volume(0.3)
    else:
        music.stop()


ui = UIManager()

player = Player()
barrels = []
star = BaseActor(700, 160, 40, 60, "star")

music.play("background")
music.set_volume(0.3)

pgzrun.go()