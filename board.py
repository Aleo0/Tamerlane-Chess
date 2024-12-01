import pygame
import sys

# Pygame başlat
pygame.init()

# Kare boyutu ve ekran boyutları
SQUARE_SIZE = 60
WIDTH = 13 * SQUARE_SIZE  # Oyun tahtası için
HEIGHT = 10 * SQUARE_SIZE
SIDEBAR_WIDTH = 250  # Yan panel genişliği

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (238, 203, 162)
DARK_BROWN = (166, 125, 92)
GOLD = (255, 215, 0)
GREEN = (0, 255, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Ekranı oluştur
screen = pygame.display.set_mode((WIDTH + SIDEBAR_WIDTH, HEIGHT))
pygame.display.set_caption("Timur Satrancı")

# Font ayarları
FONT_NORMAL = pygame.font.Font(None, 24)
FONT_SMALL = pygame.font.Font(None, 18)


class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_GRAY, hover_color=DARK_GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border
        text_surface = FONT_NORMAL.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)


class Piece:
    def __init__(self, name, color, row, col):
        self.name = name
        self.color = color
        self.row = row
        self.col = col

    def get_savaş_motoru_moves(self, board):
        moves = []
        possible_moves = [
            (self.row + 2, self.col), (self.row - 2, self.col),
            (self.row, self.col + 2), (self.row, self.col - 2)
        ]
        for r, c in possible_moves:
            if 0 <= r <= 9 and 0 <= c <= 10:
                if board[r][c] is None or board[r][c].color != self.color:
                    moves.append((r, c))
        return moves

    def get_valid_moves(self, board):
        # Taşın None olup olmadığını kontrol et
        if self is None or self.name is None:
            return []

        valid_moves = []
        if self.name and self.name.endswith("Piyonu"):
            move_func = self.get_piyon_moves
        else:
            move_func = getattr(self, f"get_{self.name.lower().replace(' ', '_')}_moves", None)

        if move_func:
            return move_func(board)
        return []

    def _get_moves_in_direction(self, board, directions, max_distance=None):
        moves = []
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            distance = 1
            while 0 <= r <= 9 and 0 <= c <= 10:
                if max_distance and distance > max_distance:
                    break
                piece = board[r][c]
                if piece is None:
                    moves.append((r, c))
                elif piece.color != self.color:
                    moves.append((r, c))  # Rakip taş olsa bile hareketi ekle
                
                r += dr
                c += dc
                distance += 1
        return moves

    def get_şah_moves(self, board):
        directions = [(dr, dc) for dr in range(-1, 2) for dc in range(-1, 2) if (dr, dc) != (0, 0)]
        return self._get_moves_in_direction(board, directions, max_distance=1)

    def get_vezir_moves(self, board):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        return self._get_moves_in_direction(board, directions, max_distance=1)

    def get_general_moves(self, board):
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        return self._get_moves_in_direction(board, directions, max_distance=1)

    def get_zürafa_moves(self, board):
        moves = []
        çapraz_yönler = [(1, 1), (-1, -1), (1, -1), (-1, 1)]

        for çapraz_dr, çapraz_dc in çapraz_yönler:
            r, c = self.row + çapraz_dr, self.col + çapraz_dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] is None:

                # İzin verilen ortogonal yönleri belirle
                ortogonal_yönler = []
                if çapraz_dr == 1 and çapraz_dc == 1:  # Sağ üst çapraz
                    ortogonal_yönler = [(0, 1), (1, 0)]  # Yukarı ve sağa
                elif çapraz_dr == -1 and çapraz_dc == -1:  # Sol alt çapraz
                    ortogonal_yönler = [(0, -1), (-1, 0)]  # Aşağı ve sola
                elif çapraz_dr == 1 and çapraz_dc == -1:  # Sağ alt çapraz
                    ortogonal_yönler = [(1, 0), (0, -1)]  # Sağa ve aşağı
                elif çapraz_dr == -1 and çapraz_dc == 1:  # Sol üst çapraz
                    ortogonal_yönler = [(-1, 0), (0, 1)]  # Sola ve yukarı

                for orto_dr, orto_dc in ortogonal_yönler:
                    for distance in range(1, 11):
                        end_r, end_c = r + orto_dr * distance, c + orto_dc * distance
                        if 0 <= end_r < len(board) and 0 <= end_c < len(board[0]):
                            if distance >= 3:  # Zürafa hareketi 3 kare uzaklıktan başlar
                                # Hareketin geçerli olması için aradaki tüm karelerin boş olması gerekir
                                if all(board[r + orto_dr * i][c + orto_dc * i] is None for i in range(1, distance)):
                                    if board[end_r][end_c] is None:
                                        moves.append((end_r, end_c))
                                    elif board[end_r][end_c].color != self.color:
                                        moves.append((end_r, end_c))
                                        break  # Rakip taş varsa dur
                                    else:
                                        break  # Kendi taşımız varsa dur
                                else:
                                    break  # Arada bir taş varsa dur
                        else:
                            break  # Tahta dışına çıkarsa dur
        return moves

    def get_gözcü_moves(self, board):
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        moves = []
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            while 0 <= r <= 9 and 0 <= c <= 10:
                if board[r][c] is None:
                    if abs(r - self.row) >= 2 and abs(c - self.col) >= 2:
                        moves.append((r, c))
                elif board[r][c].color != self.color: # Rakip taş ise yeme hareketini ekle
                    if abs(r - self.row) >= 2 and abs(c - self.col) >= 2:
                        moves.append((r, c))
                    break # Rakip taşı yedikten sonra dur
                else:
                    break # Kendi taşına rastlarsa dur
                r += dr
                c += dc
        return moves

    def get_at_moves(self, board):
        possible_moves = [
            (self.row - 2, self.col - 1), (self.row - 2, self.col + 1),
            (self.row - 1, self.col - 2), (self.row - 1, self.col + 2),
            (self.row + 1, self.col - 2), (self.row + 1, self.col + 2),
            (self.row + 2, self.col - 1), (self.row + 2, self.col + 1)
        ]
        return [(r, c) for r, c in possible_moves if
                0 <= r <= 9 and 0 <= c <= 10 and (board[r][c] is None or board[r][c].color != self.color)]

    def get_kale_moves(self, board):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Yatay ve dikey yönler

        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            while 0 <= r <= 9 and 0 <= c <= 10:
                if board[r][c] is None:
                    moves.append((r, c))
                else:
                    # Eğer bir taşa rastlanırsa, o yönde hareket sona eriyor
                    if board[r][c].color != self.color:  # Rakip taş ise, alınabilir
                        moves.append((r, c))
                    break  # Kendi taşımız veya rakip taş olsun, döngüyü kır
                r += dr
                c += dc

        return moves

    def get_fil_moves(self, board):
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        moves = []

        for dr, dc in directions:
            r, c = self.row + dr * 2, self.col + dc * 2
            if 0 <= r <= 9 and 0 <= c <= 10:
                # Hedef kare boş veya rakip taş içeriyorsa geçerli bir harekettir
                if board[r][c] is None or board[r][c].color != self.color:
                    moves.append((r, c))
                # Aradaki taşın durumu önemli değil, üstünden atlayabilir

        return moves

    def get_deve_moves(self, board):
        moves = []
        # Deve'nin gidebileceği tüm olası kareler
        possible_moves = [
            (self.row + 1, self.col + 3), (self.row + 1, self.col - 3),
            (self.row - 1, self.col + 3), (self.row - 1, self.col - 3),
            (self.row + 3, self.col + 1), (self.row + 3, self.col - 1),
            (self.row - 3, self.col + 1), (self.row - 3, self.col - 1)
        ]

        for end_r, end_c in possible_moves:
            if 0 <= end_r <= 9 and 0 <= end_c <= 10:
                if board[end_r][end_c] is None or board[end_r][end_c].color != self.color:
                    moves.append((end_r, end_c))

        return moves

    def get_piyon_moves(self, board):
        moves = []
        direction = 1 if self.color == "BLACK" else -1
        r, c = self.row + direction, self.col

        # Tek hamle ileri
        if 0 <= r <= 9 and board[r][c] is None:
            moves.append((r, c))

        # Çapraz yeme
        for dc in [-1, 1]:
            r, c = self.row + direction, self.col + dc
            if 0 <= r <= 9 and 0 <= c <= 10 and board[r][c] is not None and board[r][c].color != self.color:
                moves.append((r, c))

        return moves

    def promote(self):
        promotion_map = {
        "Piyon\n Piyonu": "Piyon",  # Piyon Piyonu'nun terfi etmesi gerekiyorsa, Piyon'a terfi eder.
        "Savaş Motoru\n Piyonu": "Savaş Motoru",
        "Deve\n Piyonu": "Deve",
        "Fil\n Piyonu": "Fil",
        "General\n Piyonu": "General",
        "Vezir\n Piyonu": "Vezir",
        "Zürafa\n Piyonu": "Zürafa",
        "Gözcü\n Piyonu": "Gözcü",
        "Şah\n Piyonu": "Prens", 
        "At\n Piyonu": "At",
        "Kale\n Piyonu": "Kale",
        }
        return promotion_map.get(self.name)
    
    def get_prens_moves(self, board):
        return self.get_şah_moves(board) # Prens, Şah ile aynı hareketleri yapar.



class CustomChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(11)] for _ in range(10)]
        self.selected_piece = None
        self.create_pieces()
        self.turn = "WHITE"
        self.check = {"WHITE": False, "BLACK": False}  # Şah durumunu takip etmek için
        self.captured_pieces = {"WHITE": [], "BLACK": []}  # Ele geçirilen taşları saklamak için

        # Hamle geçmişi
        self.move_history = []
        self.current_move_index = -1


    def create_pieces(self):
        # Siyah taşlar
        self.board[0][0] = Piece("Fil", "BLACK", 0, 0)
        self.board[0][2] = Piece("Deve", "BLACK", 0, 2)
        self.board[0][8] = Piece("Deve", "BLACK", 0, 8)
        self.board[0][10] = Piece("Fil", "BLACK", 0, 10)
        self.board[1][0] = Piece("Kale", "BLACK", 1, 0)
        self.board[1][1] = Piece("At", "BLACK", 1, 1)
        self.board[1][2] = Piece("Gözcü", "BLACK", 1, 2)
        self.board[1][3] = Piece("Zürafa", "BLACK", 1, 3)
        self.board[1][4] = Piece("Vezir", "BLACK", 1, 4)
        self.board[1][5] = Piece("Şah", "BLACK", 1, 5)
        self.board[1][6] = Piece("General", "BLACK", 1, 6)
        self.board[1][7] = Piece("Zürafa", "BLACK", 1, 7)
        self.board[1][8] = Piece("Gözcü", "BLACK", 1, 8)
        self.board[1][9] = Piece("At", "BLACK", 1, 9)
        self.board[1][10] = Piece("Kale", "BLACK", 1, 10)

        # Siyah piyonlar
        self.board[2][0] = Piece("Piyon\n Piyonu", "BLACK", 2, 0)
        self.board[2][1] = Piece("Savaş Motoru\n Piyonu", "BLACK", 2, 1)
        self.board[2][2] = Piece("deve\n Piyonu", "BLACK", 2, 2)
        self.board[2][3] = Piece("Fil\n Piyonu", "BLACK", 2, 3)
        self.board[2][4] = Piece("General\n Piyonu", "BLACK", 2, 4)
        self.board[2][5] = Piece("Şah\n Piyonu", "BLACK", 2, 5)
        self.board[2][6] = Piece("Vezir\n Piyonu", "BLACK", 2, 6)
        self.board[2][7] = Piece("Zürafa\n Piyonu", "BLACK", 2, 7)
        self.board[2][8] = Piece("Gözcü\n Piyonu", "BLACK", 2, 8)
        self.board[2][9] = Piece("At\n Piyonu", "BLACK", 2, 9)
        self.board[2][10] = Piece("Kale\n Piyonu", "BLACK", 2, 10)

        # Beyaz taşlar
        self.board[9][0] = Piece("Fil", "WHITE", 9, 0)
        self.board[9][2] = Piece("Deve", "WHITE", 9, 2)
        self.board[9][8] = Piece("Deve", "WHITE", 9, 8)
        self.board[9][10] = Piece("Fil", "WHITE", 9, 10)
        self.board[8][0] = Piece("Kale", "WHITE", 8, 0)
        self.board[8][1] = Piece("At", "WHITE", 8, 1)
        self.board[8][2] = Piece("Gözcü", "WHITE", 8, 2)
        self.board[8][3] = Piece("Zürafa", "WHITE", 8, 3)
        self.board[8][4] = Piece("General", "WHITE", 8, 4)
        self.board[8][5] = Piece("Şah", "WHITE", 8, 5)
        self.board[8][6] = Piece("Vezir", "WHITE", 8, 6)
        self.board[8][7] = Piece("Zürafa", "WHITE", 8, 7)
        self.board[8][8] = Piece("Gözcü", "WHITE", 8, 8)
        self.board[8][9] = Piece("At", "WHITE", 8, 9)
        self.board[8][10] = Piece("Kale", "WHITE", 8, 10)

        # Beyaz piyonlar
        self.board[7][0] = Piece("Piyon\n Piyonu", "WHITE", 7, 0)
        self.board[7][1] = Piece("Savaş Motoru\n Piyonu", "WHITE", 7, 1)
        self.board[7][2] = Piece("Deve\n Piyonu", "WHITE", 7, 2)
        self.board[7][3] = Piece("Fil\n Piyonu", "WHITE", 7, 3)
        self.board[7][4] = Piece("General\n Piyonu", "WHITE", 7, 4)
        self.board[7][5] = Piece("Şah\n Piyonu", "WHITE", 7, 5)
        self.board[7][6] = Piece("Vezir\n Piyonu", "WHITE", 7, 6)
        self.board[7][7] = Piece("Zürafa\n Piyonu", "WHITE", 7, 7)
        self.board[7][8] = Piece("Gözcü\n Piyonu", "WHITE", 7, 8)
        self.board[7][9] = Piece("At\n Piyonu", "WHITE", 7, 9)
        self.board[7][10] = Piece("Kale\n Piyonu", "WHITE", 7, 10)

        # Savaş Motorları
        self.board[0][4] = Piece("Savaş Motoru", "BLACK", 0, 4)  # E1
        self.board[0][6] = Piece("Savaş Motoru", "BLACK", 0, 6)  # G1
        self.board[9][4] = Piece("Savaş Motoru", "WHITE", 9, 4)  # E10
        self.board[9][6] = Piece("Savaş Motoru", "WHITE", 9, 6)  # G10


    def draw(self, screen):
        for row in range(10):
            for col in range(11):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(screen, color, ((col + 1) * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

                # Koordinatları yazdır
                font = pygame.font.Font(None, 20)
                text = font.render(chr(ord('A') + col) + str(10 - row), True, BLACK)
                text_rect = text.get_rect(bottomright=((col + 2) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE))
                screen.blit(text, text_rect)

                piece = self.board[row][col]
                if piece:
                    piece_color = BLACK if piece.color == "BLACK" else WHITE
                    piece_font = pygame.font.Font(None, 12)
                    lines = piece.name.splitlines()
                    for i, line in enumerate(lines):
                        piece_text = piece_font.render(line, True, piece_color)
                        piece_text_rect = piece_text.get_rect(
                            center=((col + 1.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE + i * 12))
                        screen.blit(piece_text, piece_text_rect)

                    # Şah durumunu kontrol et ve efekti çiz
                    if piece.name == "Şah" and self.check[piece.color]:
                        pygame.draw.rect(screen, (255, 0, 0),
                                         ((col + 1) * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

                # Seçili taşın geçerli hareketlerini göster
                if self.selected_piece and (row, col) in self.selected_piece.get_valid_moves(self.board):
                    pygame.draw.circle(screen, GREEN, ((col + 1.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE), 10)

        self.draw_palace(screen, 0, SQUARE_SIZE, DARK_BROWN)  # Sol saray
        self.draw_palace(screen, 12 * SQUARE_SIZE, 8 * SQUARE_SIZE, LIGHT_BROWN)  # Sağ saray

    def draw_palace(self, screen, x, y, base_color):
        pygame.draw.rect(screen, base_color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
        pygame.draw.rect(screen, GOLD, (x - 2, y - 2, SQUARE_SIZE + 4, SQUARE_SIZE + 4), 2)
        pygame.draw.rect(screen, GOLD, (x - 4, y - 4, SQUARE_SIZE + 8, SQUARE_SIZE + 8), 2)

    def handle_click(self, pos):
        col = pos[0] // SQUARE_SIZE - 1
        row = pos[1] // SQUARE_SIZE

        if 0 <= row <= 9 and 0 <= col <= 10:  # Tahta sınırları kontrolü
            clicked_piece = self.board[row][col]

            if self.selected_piece:  # Bir taş zaten seçiliyse
                if (row, col) in self.selected_piece.get_valid_moves(
                        self.board) and self.selected_piece.color == self.turn:
                    original_piece = self.board[row][col]
                    original_row, original_col = self.selected_piece.row, self.selected_piece.col
                    self.move_piece(original_row, original_col, row, col)

                    if self.is_check(self.turn):  # Şah çekme kontrolü
                        self.move_piece(row, col, original_row, original_col)  # Eğer şah çekiliyorsa hareketi geri al
                        return



                    self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"
                    self.selected_piece = None  # Seçimi kaldır


                elif clicked_piece and clicked_piece.color == self.turn:  # Başka bir kendi taşına tıklandıysa
                    self.selected_piece = clicked_piece  # Yeni taşı seç
                else:  # Geçersiz bir kareye tıklandıysa
                    self.selected_piece = None  # Seçimi kaldır
            elif clicked_piece and clicked_piece.color == self.turn:  # Henüz bir taş seçili değilse ve kendi taşına tıklandıysa
                self.selected_piece = clicked_piece  # Taşı seç

    def update_check_status(self):
        self.check["WHITE"] = self.is_check("WHITE")
        self.check["BLACK"] = self.is_check("BLACK")

    def change_turn(self):
        self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"

    def move_piece(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        if piece:
            captured_piece = self.board[end_row][end_col]

            # Hamle geçmişine kaydet
            move_info = {
                'start_row': start_row,
                'start_col': start_col,
                'end_row': end_row,
                'end_col': end_col,
                'piece': piece,
                'captured_piece': captured_piece
            }


            # Mevcut konumdan sonraki hamleleri sil
            if self.current_move_index < len(self.move_history) - 1:
                self.move_history = self.move_history[:self.current_move_index + 1]
            
            self.move_history.append(move_info)
            self.current_move_index += 1


        if captured_piece:
            self.captured_pieces[captured_piece.color].append(captured_piece)
        self.board[end_row][end_col] = piece
        piece.row = end_row
        piece.col = end_col
        self.board[start_row][start_col] = None

        # Piyon terfisi kontrolü
        if "Piyonu" in piece.name and (end_row == 0 or end_row == 9):  # Piyon karşı tarafa ulaştıysa
            promoted_piece_name = piece.promote()
            if promoted_piece_name:
                self.board[end_row][end_col] = Piece(promoted_piece_name, piece.color, end_row, end_col)




    def undo_move(self):
        if self.current_move_index >= 0:
            move = self.move_history[self.current_move_index]
            
            # Taşı geri getir
            piece = move['piece']
            self.board[move['start_row']][move['start_col']] = piece
            piece.row = move['start_row']
            piece.col = move['start_col']
            
            # Yakalanan taşı geri getir
            if move['captured_piece']:
                self.board[move['end_row']][move['end_col']] = move['captured_piece']
                self.captured_pieces[move['captured_piece'].color].remove(move['captured_piece'])
            else:
                self.board[move['end_row']][move['end_col']] = None
            
            # Sırayı değiştir
            self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"
            
            # Geçmiş indeksini güncelle
            self.current_move_index -= 1
            self.selected_piece = None

    def redo_move(self):
        if self.current_move_index < len(self.move_history) - 1:
            self.current_move_index += 1
            move = self.move_history[self.current_move_index]
            
            # Taşı ileri götür
            piece = move['piece']
            self.board[move['end_row']][move['end_col']] = piece
            piece.row = move['end_row']
            piece.col = move['end_col']
            self.board[move['start_row']][move['start_col']] = None
            
            # Yakalanan taşı ekle
            if move['captured_piece']:
                self.captured_pieces[move['captured_piece'].color].append(move['captured_piece'])
            
            # Sırayı değiştir
            self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"
            self.selected_piece = None

    def draw_sidebar(self, screen):
        # Yan paneli çiz
        sidebar_rect = pygame.Rect(WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
        pygame.draw.rect(screen, LIGHT_GRAY, sidebar_rect)
        pygame.draw.line(screen, BLACK, (WIDTH, 0), (WIDTH, HEIGHT), 2)

        # Sıradaki oyuncu (Türkçe)
        turn_color = "Beyaz" if self.turn == "WHITE" else "Siyah"
        turn_text = FONT_NORMAL.render(f"Sıra: {turn_color}", True, BLACK)
        screen.blit(turn_text, (WIDTH + 10, 20))

        # Yenilen taşlar
        captured_text = FONT_NORMAL.render("Yenilen Taşlar:", True, BLACK)
        screen.blit(captured_text, (WIDTH + 10, 60)) # Konumu yukarı taşıdık

        # Beyaz yenilen taşlar
        white_captured = [f"{piece.name} (Siyah)" for piece in self.captured_pieces["BLACK"]]
        for i, piece_name in enumerate(white_captured):
            piece_text = FONT_SMALL.render(piece_name, True, BLACK)
            screen.blit(piece_text, (WIDTH + 10, 90 + i * 20)) # Konumu yukarı taşıdık

        # Siyah yenilen taşlar
        black_captured = [f"{piece.name} (Beyaz)" for piece in self.captured_pieces["WHITE"]]
        for i, piece_name in enumerate(black_captured):
            piece_text = FONT_SMALL.render(piece_name, True, BLACK)
            screen.blit(piece_text, (WIDTH + 130, 90 + i * 20)) # Konumu yukarı taşıdık



                
    def is_check(self, color):
        """Belirtilen renkteki şahın tehdit altında olup olmadığını kontrol eder."""
        king_pos = None
    
        # Şah konumunu bul
        for row in range(10):
            for col in range(11):
                piece = self.board[row][col]
                if piece and piece.name == "Şah" and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        opponent_color = "BLACK" if color == "WHITE" else "WHITE"
        for row in range(10):
            for col in range(11):
                piece = self.board[row][col]
                # Rakip taşların hareketlerini kontrol et
                if piece and piece.color == opponent_color:
                    valid_moves = piece.get_valid_moves(self.board)
                    if king_pos in valid_moves:
                        return True

        return False
    

    def is_checkmate(self, color):
        """Belirtilen renkteki şahın mat olup olmadığını kontrol eder."""
        if not self.is_check(color):
            return False  # Şah çekilmiyorsa mat olamaz

        king_pos = None
        for r in range(10):
            for c in range(11):
                piece = self.board[r][c]
                if piece and piece.name == "Şah" and piece.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        if not king_pos: # Şah yoksa oyun biter
            return True

        # Şahın herhangi bir hamleyle tehditten kurtulabilmesi durumunda mat değil
        for move in self.get_valid_moves(king_pos[0], king_pos[1]):
            original_piece = self.board[move[0]][move[1]]
            self.move_piece(king_pos[0], king_pos[1], move[0], move[1])
            if not self.is_check(color):
                self.move_piece(move[0], move[1], king_pos[0], king_pos[1]) # Hareketi geri al
                if original_piece:
                    self.board[move[0]][move[1]] = original_piece
                return False # Mat değil
            self.move_piece(move[0], move[1], king_pos[0], king_pos[1]) # Hareketi geri al
            if original_piece:
                self.board[move[0]][move[1]] = original_piece

        return True # Mat
    

    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if piece:
            return piece.get_valid_moves(self.board)
        return []


def main():
    chess_board = CustomChessBoard()
    
    # Butonları oluştur
    undo_button = Button(WIDTH + 10, HEIGHT - 120, SIDEBAR_WIDTH - 20, 40, "Geri Al")
    redo_button = Button(WIDTH + 10, HEIGHT - 70, SIDEBAR_WIDTH - 20, 40, "İleri Al")

    game_over = False
    running = True
    clock = pygame.time.Clock() # FPS kontrolü için
    while running:
        for event in pygame.event.get():         
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Sol tıklama
                    if undo_button.rect.collidepoint(event.pos):  # Geri al butonuna tıklandıysa
                        chess_board.undo_move()
                        game_over = False # Oyun geri alındığında game_over'ı False yap
                    elif redo_button.rect.collidepoint(event.pos): # İleri al butonuna tıklandıysa
                        chess_board.redo_move()
                        game_over = False # Oyun ileri alındığında game_over'ı False yap

                    elif not game_over: # Oyun bitmediyse hamle işle
                        chess_board.handle_click(event.pos)


            if event.type == pygame.MOUSEMOTION:
                undo_button.handle_event(event) # Her zaman buton hover'ını kontrol et
                redo_button.handle_event(event)

        if chess_board.is_checkmate("WHITE"):
            print("Siyah Kazandı!")
            game_over = True
        elif chess_board.is_checkmate("BLACK"):
            print("Beyaz Kazandı!")
            game_over = True

        screen.fill(WHITE)
        chess_board.draw(screen)
        chess_board.draw_sidebar(screen)

        # Butonları her zaman çiz
        undo_button.draw(screen)
        redo_button.draw(screen)


        pygame.display.flip()
        clock.tick(60) # FPS'yi 60 olarak sınırla

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    
