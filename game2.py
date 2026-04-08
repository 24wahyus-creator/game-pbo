import pygame
import sys
import random
import math

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🎈 BALLOON POPPER - Klik Balonnya! 🎯")
clock = pygame.time.Clock()

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
GREEN = (50, 200, 50)
YELLOW = (255, 255, 50)
PURPLE = (200, 50, 255)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
SKY_BLUE = (135, 206, 235)
GOLD = (255, 215, 0)

class FloatingScore:
    """Animasi score yang melayang"""
    def __init__(self, x, y, value, color=GOLD):
        self.x = x
        self.y = y
        self.value = value
        self.color = color
        self.lifetime = 60  # 1 detik (60 frame)
        self.vy = -2  # kecepatan naik
        self.font = pygame.font.Font(None, 28)
    
    def update(self):
        self.y += self.vy
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = min(255, self.lifetime * 4)
        text = self.font.render(f"+{self.value}", True, self.color)
        screen.blit(text, (self.x - text.get_width()//2, self.y))
    
    def is_alive(self):
        return self.lifetime > 0


class Particle:
    """Efek pecahan saat balon meletus"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.color = color
        self.lifetime = 30
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # gravitasi
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = min(255, self.lifetime * 8)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


class GameObject:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


class Balloon(GameObject):
    """Balon - turunan GameObject"""
    colors = [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE]
    
    def __init__(self, x, y, size, speed):
        super().__init__(x, y, size, size)
        self.size = size
        self.color = random.choice(self.colors)
        self.speed = speed
        self.popped = False
        self.wobble = 0  # efek goyang
    
    def update(self):
        self.move(0, -self.speed)
        self.wobble += 0.1
    
    def draw(self, screen):
        if not self.popped:
            # Efek goyang (wobble)
            wobble_x = math.sin(self.wobble) * 2
            
            # Balon
            balloon_rect = self.rect.move(wobble_x, 0)
            pygame.draw.ellipse(screen, self.color, balloon_rect)
            # Tali
            pygame.draw.line(screen, BLACK, (balloon_rect.centerx, balloon_rect.bottom), 
                           (balloon_rect.centerx, balloon_rect.bottom + 15), 2)
            # Pantulan cahaya
            pygame.draw.ellipse(screen, WHITE, (balloon_rect.x + 5, balloon_rect.y + 5, 8, 8))
    
    def pop(self):
        self.popped = True
        return 10


class BombBalloon(Balloon):
    """Balon bom - kalau diklik, game over!"""
    def __init__(self, x, y, size, speed):
        super().__init__(x, y, size, speed)
        self.color = BLACK
    
    def draw(self, screen):
        if not self.popped:
            wobble_x = math.sin(self.wobble) * 2
            balloon_rect = self.rect.move(wobble_x, 0)
            pygame.draw.ellipse(screen, self.color, balloon_rect)
            pygame.draw.line(screen, BLACK, (balloon_rect.centerx, balloon_rect.bottom), 
                           (balloon_rect.centerx, balloon_rect.bottom + 15), 2)
            # Gambar bom di tengah
            pygame.draw.circle(screen, GRAY, (int(balloon_rect.centerx), int(balloon_rect.centery)), self.size//3)
            pygame.draw.line(screen, RED, (balloon_rect.centerx - 5, balloon_rect.centery), 
                           (balloon_rect.centerx + 5, balloon_rect.centery), 2)
            pygame.draw.line(screen, RED, (balloon_rect.centerx, balloon_rect.centery - 5), 
                           (balloon_rect.centerx, balloon_rect.centery + 5), 2)
    
    def pop(self):
        return "BOOM"


class SpeedBalloon(Balloon):
    """Balon super cepat"""
    def __init__(self, x, y, size, speed):
        super().__init__(x, y, size, speed * 1.5)
        self.color = YELLOW
    
    def draw(self, screen):
        super().draw(screen)
        wobble_x = math.sin(self.wobble) * 2
        balloon_rect = self.rect.move(wobble_x, 0)
        # Garis kecepatan
        for i in range(3):
            pygame.draw.line(screen, WHITE, (balloon_rect.x + 5, balloon_rect.y + 10 + i*10),
                           (balloon_rect.x - 10, balloon_rect.y + 10 + i*10), 2)
    
    def pop(self):
        return 20

def draw_score_display(score, combo, level, target_score, progress):
    """Tampilan score yang keren"""
    font_big = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 24)
    
    # Card background untuk score
    score_card = pygame.Surface((250, 100))
    score_card.set_alpha(200)
    score_card.fill(BLACK)
    screen.blit(score_card, (SCREEN_WIDTH - 260, 10))
    
    # Border emas
    pygame.draw.rect(screen, GOLD, (SCREEN_WIDTH - 260, 10, 250, 100), 2)
    
    # Score utama dengan animasi efek
    score_text = font_big.render(f"🎈 {score}", True, GOLD)
    screen.blit(score_text, (SCREEN_WIDTH - 240, 15))
    
    # Combo display (kalau combo > 1)
    if combo > 1:
        combo_text = font_small.render(f"🔥 COMBO x{combo}!", True, ORANGE)
        screen.blit(combo_text, (SCREEN_WIDTH - 240, 55))
    
    # Level display
    level_text = font_small.render(f"Level {level}", True, YELLOW)
    screen.blit(level_text, (SCREEN_WIDTH - 240, 75))
    
    # Progress bar menuju level berikutnya
    bar_width = 200
    bar_height = 8
    bar_x = SCREEN_WIDTH - 240
    bar_y = 95
    
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * progress), bar_height))
    
    # Target text
    target_text = font_small.render(f"Next: {target_score}", True, WHITE)
    screen.blit(target_text, (bar_x + bar_width - 50, bar_y - 18))


def draw_game_over(score, final_combo, level):
    """Tampilan game over yang keren"""
    screen.fill(SKY_BLUE)
    
    # Efek gradien
    for i in range(SCREEN_HEIGHT):
        color_value = 135 + (i * 20 // SCREEN_HEIGHT)
        grad_color = (135, 206 - (i//10), 235 - (i//15))
        pygame.draw.line(screen, grad_color, (0, i), (SCREEN_WIDTH, i))
    
    font_title = pygame.font.Font(None, 72)
    font_big = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)
    
    # Judul GAME OVER dengan efek
    game_over = font_title.render("GAME OVER", True, RED)
    screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 150))
    
    # Score panel
    score_panel = pygame.Surface((400, 200))
    score_panel.set_alpha(220)
    score_panel.fill(BLACK)
    screen.blit(score_panel, (SCREEN_WIDTH//2 - 200, 250))
    pygame.draw.rect(screen, GOLD, (SCREEN_WIDTH//2 - 200, 250, 400, 200), 3)
    
    score_text = font_big.render(f"Final Score: {score}", True, GOLD)
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 270))
    
    combo_text = font_small.render(f"Highest Combo: x{final_combo}", True, ORANGE)
    screen.blit(combo_text, (SCREEN_WIDTH//2 - combo_text.get_width()//2, 330))
    
    level_text = font_small.render(f"Reached Level: {level}", True, YELLOW)
    screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 370))
    
    restart = font_small.render("Press R to Restart | Q to Quit", True, WHITE)
    screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 500))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    return False
    return False


def main():
    balloons = []
    floating_scores = []
    particles = []
    
    score = 0
    missed = 0
    combo = 1
    highest_combo = 1
    level = 1
    target_score = 100  # score target untuk naik level
    
    font = pygame.font.Font(None, 36)
    running = True
    spawn_timer = 0
    SPAWN_DELAY = 40
    
    # Timer untuk combo (kalau lama tidak klik, combo reset)
    combo_timer = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for balloon in balloons[:]:
                    # Hitung wobble offset untuk deteksi klik yang akurat
                    wobble_x = math.sin(balloon.wobble) * 2
                    balloon_rect = balloon.rect.move(wobble_x, 0)
                    
                    if balloon_rect.collidepoint(pos) and not balloon.popped:
                        result = balloon.pop()
                        
                        # Tambah efek particle
                        for _ in range(12):
                            particles.append(Particle(balloon_rect.centerx, balloon_rect.centery, balloon.color))
                        
                        if result == "BOOM":
                            if draw_game_over(score, highest_combo, level):
                                return main()
                            else:
                                return
                        else:
                            # Hitung bonus combo
                            bonus = result * combo
                            score += bonus
                            
                            # Tambah floating score
                            floating_scores.append(FloatingScore(balloon_rect.centerx, balloon_rect.centery, bonus, GOLD if combo > 1 else YELLOW))
                            
                            # Reset combo timer dan naikkan combo
                            combo_timer = 0
                            combo += 1
                            if combo > highest_combo:
                                highest_combo = combo
                            
                            balloons.remove(balloon)
                            
                            # Cek level up
                            if score >= target_score:
                                level += 1
                                target_score += 100  # target naik 100 setiap level
                                # Efek level up: semua balon direset
                                balloons.clear()
                                # Tambah efek particle meriah
                                for _ in range(50):
                                    particles.append(Particle(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), GOLD))
                                floating_scores.append(FloatingScore(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "LEVEL UP!", GOLD))
                                
                                # Kurangi spawn delay (game makin seru)
                                SPAWN_DELAY = max(25, SPAWN_DELAY - 2)
        
        # Update combo timer (reset combo kalau lama tidak klik)
        combo_timer += 1
        if combo_timer > 60:  # 1 detik tanpa klik
            combo = 1
            combo_timer = 0
        
        # Spawn balon
        spawn_timer += 1
        if spawn_timer > SPAWN_DELAY:
            spawn_timer = 0
            rand_num = random.random()
            # Semakin tinggi level, semakin banyak balon cepat dan bom
            bomb_chance = min(0.15, 0.05 + (level * 0.005))
            speed_chance = min(0.15, 0.10 + (level * 0.005))
            
            if rand_num < (0.85 - bomb_chance - speed_chance/2):
                balloons.append(Balloon(random.randint(0, SCREEN_WIDTH-40), SCREEN_HEIGHT-50, 40, random.uniform(1.5, 3.5 + level*0.1)))
            elif rand_num < (0.85 - bomb_chance):
                balloons.append(SpeedBalloon(random.randint(0, SCREEN_WIDTH-40), SCREEN_HEIGHT-50, 40, random.uniform(2, 4 + level*0.1)))
            else:
                balloons.append(BombBalloon(random.randint(0, SCREEN_WIDTH-40), SCREEN_HEIGHT-50, 40, random.uniform(1.5, 2.5 + level*0.05)))
        
        # Update dan cek balon yang lolos
        for balloon in balloons[:]:
            balloon.update()
            if balloon.rect.bottom < 0:
                balloons.remove(balloon)
                missed += 1
                if missed >= 8:
                    if draw_game_over(score, highest_combo, level):
                        return main()
                    else:
                        return
        
        # Update floating scores
        for fs in floating_scores[:]:
            if not fs.update():
                floating_scores.remove(fs)
        
        # Update particles
        for p in particles[:]:
            if not p.update():
                particles.remove(p)
        
        # Background gradien langit
        for i in range(SCREEN_HEIGHT):
            grad_color = (135, 206 - (i//10), 235 - (i//15))
            pygame.draw.line(screen, grad_color, (0, i), (SCREEN_WIDTH, i))
        
        # Awan-awan
        for i in range(8):
            cloud_x = (i * 150 + pygame.time.get_ticks() * 0.03) % (SCREEN_WIDTH + 200) - 100
            cloud_y = 50 + (i * 70) % 300
            pygame.draw.circle(screen, WHITE, (int(cloud_x), cloud_y), 30)
            pygame.draw.circle(screen, WHITE, (int(cloud_x - 20), cloud_y - 10), 25)
            pygame.draw.circle(screen, WHITE, (int(cloud_x + 20), cloud_y - 5), 25)
        
        # Balon
        for balloon in balloons:
            balloon.draw(screen)
        
        # Particles
        for p in particles:
            p.draw(screen)
        
        # Floating scores
        for fs in floating_scores:
            fs.draw(screen)
        
        # Tampilan score keren
        progress = (score % target_score) / target_score if target_score > 0 else 1
        draw_score_display(score, combo, level, target_score, progress)
        
        # Missed counter dengan icon
        missed_bg = pygame.Surface((150, 40))
        missed_bg.set_alpha(180)
        missed_bg.fill(BLACK)
        screen.blit(missed_bg, (10, 10))
        missed_text = font.render(f"💔 Missed: {missed}/8", True, RED if missed > 5 else WHITE)
        screen.blit(missed_text, (15, 15))
        
        # Combo indicator besar kalau combo tinggi
        if combo > 3:
            combo_indicator = pygame.font.Font(None, 60).render(f"x{combo} COMBO!", True, ORANGE)
            combo_shadow = pygame.font.Font(None, 60).render(f"x{combo} COMBO!", True, RED)
            screen.blit(combo_shadow, (SCREEN_WIDTH//2 - combo_indicator.get_width()//2 + 2, 52))
            screen.blit(combo_indicator, (SCREEN_WIDTH//2 - combo_indicator.get_width()//2, 50))
        
        # Instruksi
        instruksi = pygame.font.Font(None, 24).render("🖱️ CLICK BALLOONS! 🎈", True, BLACK)
        instruksi_bg = pygame.Surface((instruksi.get_width() + 20, 30))
        instruksi_bg.set_alpha(180)
        instruksi_bg.fill(WHITE)
        screen.blit(instruksi_bg, (SCREEN_WIDTH//2 - instruksi.get_width()//2 - 10, SCREEN_HEIGHT - 35))
        screen.blit(instruksi, (SCREEN_WIDTH//2 - instruksi.get_width()//2, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()