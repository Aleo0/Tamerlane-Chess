import pygame
import sys
import os
from board import CustomChessBoard, WIDTH, HEIGHT, WHITE, BLACK, GOLD

class Menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Timur Satrancı - Ana Menü")
        
        # Font tanımlamaları
        self.title_font = pygame.font.Font(None, 64)
        self.button_font = pygame.font.Font(None, 36)
        
        # Buton boyutları ve pozisyonları
        self.button_width = 300
        self.button_height = 50
        self.button_spacing = 20
        
        # Butonları oluştur
        button_y = HEIGHT // 2
        self.pvp_button = pygame.Rect((WIDTH - self.button_width) // 2, 
            button_y, 
            self.button_width, 
            self.button_height)
        
        self.ai_white_button = pygame.Rect((WIDTH - self.button_width) // 2, 
            button_y + self.button_height + self.button_spacing, 
            self.button_width, 
            self.button_height)
        
        self.ai_black_button = pygame.Rect((WIDTH - self.button_width) // 2, 
            button_y + 2 * (self.button_height + self.button_spacing), 
            self.button_width, 
            self.button_height)
        
        self.exit_button = pygame.Rect((WIDTH - self.button_width) // 2, 
            button_y + 3 * (self.button_height + self.button_spacing), 
            self.button_width, 
            self.button_height)
        
        try:
            # Uygulama yolunu belirle
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            # Doğrudan timur.png'yi yüklemeyi dene
            bg_path = os.path.join(application_path, "images", "timur.png")
            
            if os.path.exists(bg_path):
                try:
                    # Arka plan resmini yükle
                    self.background = pygame.image.load(bg_path).convert_alpha()
                    
                    # Ekran boyutuna ölçekle, oranı koru
                    bg_ratio = self.background.get_width() / self.background.get_height()
                    screen_ratio = WIDTH / HEIGHT
                    
                    if bg_ratio > screen_ratio:  # Resim ekrandan daha geniş
                        new_height = HEIGHT
                        new_width = int(HEIGHT * bg_ratio)
                    else:  # Resim ekrandan daha uzun
                        new_width = WIDTH
                        new_height = int(WIDTH / bg_ratio)
                    
                    self.background = pygame.transform.scale(self.background, (new_width, new_height))
                    
                    # Resmi ortalamak için offset hesapla
                    self.bg_x = (WIDTH - new_width) // 2
                    self.bg_y = (HEIGHT - new_height) // 2
                    
                    print(f"Arka plan başarıyla yüklendi: {bg_path}")
                except Exception as e:
                    print(f"Resim yükleme hatası: {e}")
                    self._create_default_background()
            else:
                print(f"Arka plan resmi bulunamadı: {bg_path}")
                self._create_default_background()
                
        except Exception as e:
            print(f"Arka plan oluşturma hatası: {e}")
            self._create_default_background()

    def _create_default_background(self):
        """Varsayılan arka planı oluştur"""
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill((238, 203, 162))  # LIGHT_BROWN
        self.bg_x = 0
        self.bg_y = 0

    def draw(self):
        # Önce arka planı temizle
        self.screen.fill((238, 203, 162))  # LIGHT_BROWN
        
        # Arka plan resmini ortala
        self.screen.blit(self.background, (self.bg_x, self.bg_y))
        
        # Yarı saydam siyah overlay ekle
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)  # 128/255 opaklık
        self.screen.blit(overlay, (0, 0))
    
        # Başlık (gölgeli)
        title_shadow = self.title_font.render("Timur Satrancı", True, (0, 0, 0))  # Gölge için siyah
        title_text = self.title_font.render("Timur Satrancı", True, GOLD)  # Ana yazı altın rengi
        
        # Gölgeyi biraz kaydırarak çiz
        shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 2, HEIGHT // 4 + 2))
        self.screen.blit(title_shadow, shadow_rect)
        
        # Ana yazıyı çiz
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.screen.blit(title_text, title_rect)
    
        # Butonlar
        buttons = [
            (self.pvp_button, "İki Oyunculu"),
            (self.ai_white_button, "Beyaz AI'a Karşı"),
            (self.ai_black_button, "Siyah AI'a Karşı"),
            (self.exit_button, "Çıkış")
        ]
    
        for button, text in buttons:
            pygame.draw.rect(self.screen, GOLD, button)
            pygame.draw.rect(self.screen, BLACK, button, 2)
        
            text_surface = self.button_font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=button.center)
            self.screen.blit(text_surface, text_rect)
    
        pygame.display.flip()

    def run(self):
        running = True
        selected_option = None

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                
                    if self.pvp_button.collidepoint(mouse_pos):
                        return "PVP"
                    elif self.ai_white_button.collidepoint(mouse_pos):
                        return "AI_WHITE"
                    elif self.ai_black_button.collidepoint(mouse_pos):
                        return "AI_BLACK"
                    elif self.exit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
        
            self.draw()