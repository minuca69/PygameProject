import pygame
import os

# Inicializa o Pygame
pygame.init()

# Configurações da tela
screen_width = 800
screen_height = int(screen_width * 0.8)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Alemones')

# Configura a taxa de quadros
clock = pygame.time.Clock()
FPS = 60

# Variáveis do jogo
GRAVITY = 0.75

# Variáveis de movimento do jogador
moving_left = False
moving_right = False
shoot = False 
granada = False
granada_thrown = False  # Inicializa como False

# Carregar imagens
bullet_img = pygame.image.load('Icons/bala.png').convert_alpha()
granada_img = pygame.image.load('Icons/granada.png').convert_alpha()

# Cores
BG = (144, 201, 120)
ROT = (255, 0, 0)

# Função para desenhar o fundo
def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, ROT, (0, 300), (screen_width, 300))

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = 10  # Velocidade da bala

    def update(self):
        self.rect.x += self.speed * self.direction
        
        # Remove a bala se sair da tela
        if self.rect.x < 0 or self.rect.x > screen_width:
            self.kill()

class Soldado(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, granadas):
        super().__init__()
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.granadas = granadas
        self.shoot_cooldown = 0
        self.health = 100
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # Carregar animações (Idle, Run, Jump, Death)
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            try:
                num_of_frames = len(os.listdir(f'{self.char_type}/{animation}'))
            except FileNotFoundError:
                print(f"Diretório não encontrado: {self.char_type}/{animation}")
                num_of_frames = 0
            for i in range(num_of_frames):
                img = pygame.image.load(f'{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # Limitar movimento do jogador à tela
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right

        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20  # Cooldown para o tiro
            bullet = Bala(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bala_group.add(bullet)
            self.ammo -= 1

    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        if len(self.animation_list[self.action]) > 0:
            self.image = self.animation_list[self.action][self.frame_index]

            if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1

            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:  # Death
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Granada(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = granada_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y
        
        # Atualiza a posição da granada
        self.rect.x += dx
        self.rect.y += dy
        
        # Remove granada se sair da tela
        if self.rect.y > screen_height:  # Verifica se saiu pela parte inferior
            self.kill()

# Grupos de sprites
bala_group = pygame.sprite.Group()
granada_group = pygame.sprite.Group()

# Criação dos objetos do jogador e inimigo
player = Soldado('player', 300, 300, 0.5, 5, 20, 5)
enemy = Soldado('enemy', 500, 300, 0.5, 5, 20, 0)

# Loop principal do jogo
run = True
while run:
    clock.tick(FPS)

    draw_bg()

    player.update()
    player.draw()
    
    enemy.update()
    enemy.draw()
    
    # Atualizar e desenhar grupos
    bala_group.update()
    granada_group.update()
    bala_group.draw(screen)
    granada_group.draw(screen)

    # Atualiza a ação do player
    if player.alive:
        # Tiro
        if shoot:
            player.shoot()
        # Jogar granada
        if granada and not granada_thrown and player.granadas > 0:
            nova_granada = Granada(player.rect.centerx, player.rect.centery, player.direction)
            granada_group.add(nova_granada)
            player.granadas -= 1
            granada_thrown = True

        if player.in_air:
            player.update_action(2)  # Jump
        elif moving_left or moving_right:
            player.update_action(1)  # Run
        else:
            player.update_action(0)  # Idle
        player.move(moving_left, moving_right)

    # Verifica se o jogo acabou
    if not player.alive or not enemy.alive:
        print("Game Over")
        run = False

    # Tratamento de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_f:
                shoot = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
            if event.key == pygame.K_g and player.alive:
                granada = True
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_f:
                shoot = False
            if event.key == pygame.K_g:
                granada = False 
                granada_thrown = False  # Permite lançar outra granada

    pygame.display.update()

pygame.quit()