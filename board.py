import pygame
import sys


pygame.init()

# Kare boyutu
SQUARE_SIZE = 75

# Ekran boyutları
WIDTH = 13 * SQUARE_SIZE  # 11 normal kare + 1 ek kare (SOLDA) + 1 ek kare (SAĞDA)
HEIGHT = 10 * SQUARE_SIZE
    
# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (238, 203, 162)
DARK_BROWN = (166, 125, 92)
GOLD = (255, 215, 0)
GREEN = (0, 255, 0)  
RED = (255, 0, 0)

# Ekranı oluştur
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Timur Satrancı")


class Piece:
    def __init__(self, name, color, row, col):
        self.name = name
        self.color = color
        self.row = row
        self.col = col
        self.is_sleeping = False  # Piyon Piyonu uyku modunda mı?
        self.pawn_pawn_journey_count = 0  # Piyon Piyonu'nun son sıraya kaç kez ulaştığı
        

    def get_savaş_motoru_moves(self, board):
        moves = []
        possible_moves = [
            (self.row + 2, self.col), (self.row - 2, self.col),
            (self.row, self.col + 2), (self.row, self.col - 2)
        ]
        for r, c in possible_moves:
            if 0 <= r <= 9 and 1 <= c <= 12:
                if board[r][c] is None or (board[r][c].color != self.color and not (board[r][c].name == "Piyon\n Piyonu" and (r == 0 or r == 9))):
                    moves.append((r, c))
        return moves

    def get_valid_moves(self, board):
        if self is None or self.name is None:
            return []

        valid_moves = []
        if self.name and self.name.endswith("Piyonu"):
            move_func = self.get_piyon_moves
        else:
            move_func = getattr(self, f"get_{self.name.lower().replace(' ', '_')}_moves", None)

        if move_func:
            all_moves = move_func(board)

            # Şahlar için özel kontrol (Maceracı Şah hariç)
            if self.name == "Şah" or self.name == "Prens":
                valid_moves = [
                    (r, c) for r, c in all_moves
                    if (c, r) not in [(12, 0), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 9),
                                    (0, 0), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 9)]
                    or (c, r) in [(0, 1)] and self.color == "WHITE"  # A9 beyaz şah için açık
                    or (c, r) in [(12, 8)] and self.color == "BLACK"  # M2 siyah şah için açık
                ]
            # Maceracı Şah için özel kontrol
            elif self.name == "Maceracı Şah":
                valid_moves = [
                    (r, c) for r, c in all_moves
                    if (c, r) not in [(12, 0), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 9),
                                    (0, 0), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 9)]
                ]
            else:
                valid_moves = [
                    (r, c) for r, c in all_moves
                    if (c, r) not in [
                        (12, 0), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 9),
                        (0, 0), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 9)
                    ]
                ]
        return valid_moves

    
    
    def _get_moves_in_direction(self, board, directions, max_distance=None):
        moves = []
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            distance = 1
            while 0 <= r < 10 and 0 <= c < 13:
                if max_distance and distance > max_distance:
                    break
                piece = board[r][c]
                if piece is None:
                    if (c, r) not in [(12, 0), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 9),  # M sütunu engelleri
                                        (0, 0), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 9)]:         # A sütunu engelleri
                        moves.append((r, c))
                    else:
                        break  # Engellenmiş kareye rastlandı, dur
                elif piece.color != self.color:
                    moves.append((r, c))  # Rakip taş olsa bile hareketi ekle
                    break  # Engelle karşılaşıldığında dur
                # Aynı renkteki taşlar hala engelliyor
                r += dr
                c += dc
                distance += 1
        return moves
    
    def get_kale_moves(self, board):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Yatay ve dikey yönler

        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            while 0 <= r < 10 and 1 <= c < 13:
                if (c, r) in [(12, 0), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 9),  # M sütunu engelleri
                              (0, 0), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0,8), (0, 9)]:         # A sütunu engelleri
                    break  # Engellenmiş kareye ulaşıldığında dur
                if board[r][c] is None:
                    moves.append((r, c))
                else:
                    # Eğer bir taşa rastlanırsa, o yönde hareket sona eriyor
                    if board[r][c].color != self.color:
                        moves.append((r, c))  # Rakip taş ise, alınabilir
                    break  # Hareketi durdur
                r += dr
                c += dc

        return moves




    def get_şah_moves(self, board):
        directions = [(dr, dc) for dr in range(-1, 2) for dc in range(-1, 2) if (dr, dc) != (0, 0)]
        moves = []
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < 10 and 0 <= c < 13:
                if board[r][c] is None or (board[r][c].color != self.color):
                    # A9 kontrolü: Sadece beyaz şahlar girebilir
                    if (r, c) == (1, 0) and self.color != "WHITE":
                        continue
                    
                    # M2 kontrolü: Sadece siyah şahlar girebilir
                    if (r, c) == (8, 12) and self.color != "BLACK":
                        continue
                    
                    moves.append((r, c))
        return moves
    

    def get_maceracı_şah_moves(self, board):
            
        directions = [(dr, dc) for dr in range(-1, 2) for dc in range(-1, 2) if (dr, dc) != (0, 0)]
        moves = []
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < 10 and 0 <= c < 13:
                if board[r][c] is None or (board[r][c].color != self.color):
                    # Maceracı Şah için A9 ve M2 kontrolü yok
                    moves.append((r, c))
        return moves
    

    def get_prens_moves(self, board):
        return self.get_şah_moves(board)




    def get_vezir_moves(self, board):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        moves = []

        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            # Tahta sınırları içinde kalmalı
            if 0 <= r <= 9 and 1 <= c <= 12:
                target_piece = board[r][c]
                # Hedef kare boş olmalı veya rakip bir taş içermeli (son sıradaki Piyon Piyonu hariç)
                if target_piece is None or (target_piece.color != self.color and not (target_piece.name == "Piyon\n Piyonu" and (r == 0 or r == 9))):
                    moves.append((r, c))  # Sadece bir kare uzağı ekle
        return moves

    def get_general_moves(self, board):
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        moves = []
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r <= 9 and 1 <= c <= 12:
                if board[r][c] is None or (board[r][c].color != self.color and not (board[r][c].name == "Piyon\n Piyonu" and (r == 0 or r == 9))):
                    moves.append((r, c))
        return moves

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
                            # 0. sütuna gitmesini engelle
                            if end_c == 0:
                                break
                            
                            if distance >= 3:  # Zürafa hareketi 3 kare uzaklıktan başlar
                                # Hareketin geçerli olması için aradaki tüm karelerin boş olması gerekir
                                if all(board[r + orto_dr * i][c + orto_dc * i] is None for i in range(1, distance)):
                                    if board[end_r][end_c] is None or (board[end_r][end_c].color != self.color and not (board[end_r][end_c].name == "Piyon\n Piyonu" and (end_r == 0 or end_r == 9))):
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
            while 0 <= r <= 9 and 1 <= c <= 12:
                current_piece = board[r][c]
                if current_piece is None:
                    if abs(r - self.row) >= 2 and abs(c - self.col) >= 2:
                        moves.append((r, c))
                else:
                    if current_piece.color != self.color:
                        if abs(r - self.row) >= 2 and abs(c - self.col) >= 2:
                            # "Piyon Piyonu" taşını son sırada yemeyi engelle
                            if not (current_piece.name == "Piyon\n Piyonu" and (r == 0 or r == 9)):
                                moves.append((r, c))
                    break
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
                0 <= r <= 9 and 1 <= c <= 12 and (board[r][c] is None or (board[r][c].color != self.color and not (board[r][c].name == "Piyon\n Piyonu" and (r == 0 or r == 9))))]

        return moves

    def get_fil_moves(self, board):
        moves = []
        possible_moves = [
            (self.row + 2, self.col + 2), (self.row + 2, self.col - 2),
            (self.row - 2, self.col + 2), (self.row - 2, self.col - 2)
        ]

        for r, c in possible_moves:
            if 0 <= r <= 9 and 1 <= c <= 12:
                # Hedef kare boşsa veya rakip taşsa (ve Piyon Piyonu son sırada değilse) hareketi ekle
                if board[r][c] is None or (board[r][c].color != self.color and not (board[r][c].name == "Piyon\n Piyonu" and (r == 0 or r == 9))):
                     moves.append((r,c))
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
            if 0 <= end_r <= 9 and 1 <= end_c <= 12:
                if board[end_r][end_c] is None or (board[end_r][end_c].color != self.color and not (board[end_r][end_c].name == "Piyon\n Piyonu" and (end_r == 0 or end_r == 9))):
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
            if 0 <= r <= 9 and 1 <= c <= 12 and board[r][c] is not None and board[r][c].color != self.color:
                moves.append((r, c))

        return moves
    
    



    def promote(self):
        promotion_map = {
        "Savaş Motoru\n Piyonu": "Savaş Motoru",
        "Deve\n Piyonu": "Deve",
        "Fil\n Piyonu": "Fil",
        "General\n Piyonu": "General",
        "Vezir\n Piyonu": "Vezir",
        "Zürafa\n Piyonu": "Zürafa",
        "Gözcü\n Piyonu": "Gözcü",
        "At\n Piyonu": "At",
        "Kale\n Piyonu": "Kale",
        "Şah\n Piyonu": "Prens",
        }
        return promotion_map.get(self.name)




class CustomChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(13)] for _ in range(10)]
        self.selected_piece = None
        self.create_pieces()
        self.turn = "WHITE"
        self.check = {"WHITE": False, "BLACK": False}  # Şah durumunu takip etmek için
        self.captured_pieces = {"WHITE": [], "BLACK": []}  # Ele geçirilen taşları saklamak için
        self.pawn_pawn_placeable = {"WHITE": [], "BLACK": []}
        self.pawn_pawn_move_count = {"WHITE": 0, "BLACK": 0}  # Piyon Piyonu hareket sayacı
        self.initial_pawn_pawn_positions = { #Başlangıç pozisyonlarını kaydet
            "WHITE": (7, 6),
            "BLACK": (2, 6),
        }

    def create_pieces(self):
        # Siyah taşlar
        self.board[0][1] = Piece("Fil", "BLACK", 0, 1)
        self.board[0][3] = Piece("Deve", "BLACK", 0, 3)
        self.board[0][9] = Piece("Deve", "BLACK", 0, 9)
        self.board[0][11] = Piece("Fil", "BLACK", 0, 11)
        self.board[1][1] = Piece("Kale", "BLACK", 1, 1)
        self.board[1][2] = Piece("At", "BLACK", 1, 2)
        self.board[1][3] = Piece("Gözcü", "BLACK", 1, 3)
        self.board[1][4] = Piece("Zürafa", "BLACK", 1, 4)
        self.board[1][5] = Piece("Vezir", "BLACK", 1, 5)
        self.board[1][6] = Piece("Şah", "BLACK", 1, 6)
        self.board[1][7] = Piece("General", "BLACK", 1, 7)
        self.board[1][8] = Piece("Zürafa", "BLACK", 1, 8)
        self.board[1][9] = Piece("Gözcü", "BLACK", 1, 9)
        self.board[1][10] = Piece("At", "BLACK", 1, 10)
        self.board[1][11] = Piece("Kale", "BLACK", 1, 11)

        # Siyah piyonlar
        self.board[2][1] = Piece("Piyon\n Piyonu", "BLACK", 2, 1)
        self.board[2][2] = Piece("Savaş Motoru\n Piyonu", "BLACK", 2, 2)
        self.board[2][3] = Piece("Deve\n Piyonu", "BLACK", 2, 3)
        self.board[2][4] = Piece("Fil\n Piyonu", "BLACK", 2, 4)
        self.board[2][5] = Piece("General\n Piyonu", "BLACK", 2, 5)
        self.board[2][6] = Piece("Şah\n Piyonu", "BLACK", 2, 6)
        self.board[2][7] = Piece("Vezir\n Piyonu", "BLACK", 2, 7)
        self.board[2][8] = Piece("Zürafa\n Piyonu", "BLACK", 2, 8)
        self.board[2][9] = Piece("Gözcü\n Piyonu", "BLACK", 2, 9)
        self.board[2][10] = Piece("At\n Piyonu", "BLACK", 2, 10)
        self.board[2][11] = Piece("Kale\n Piyonu", "BLACK", 2, 11)

        # Beyaz taşlar
        self.board[9][1] = Piece("Fil", "WHITE", 9, 1)
        self.board[9][3] = Piece("Deve", "WHITE", 9, 3)
        self.board[9][9] = Piece("Deve", "WHITE", 9, 9)
        self.board[9][11] = Piece("Fil", "WHITE", 9, 11)
        self.board[8][1] = Piece("Kale", "WHITE", 8, 1)
        self.board[8][2] = Piece("At", "WHITE", 8, 2)
        self.board[8][3] = Piece("Gözcü", "WHITE", 8, 3)
        self.board[8][4] = Piece("Zürafa", "WHITE", 8, 4)
        self.board[8][5] = Piece("General", "WHITE", 8, 5)
        self.board[8][6] = Piece("Şah", "WHITE", 8, 6)
        self.board[8][7] = Piece("Vezir", "WHITE", 8, 7)
        self.board[8][8] = Piece("Zürafa", "WHITE", 8, 8)
        self.board[8][9] = Piece("Gözcü", "WHITE", 8, 9)
        self.board[8][10] = Piece("At", "WHITE", 8, 10)
        self.board[8][11] = Piece("Kale", "WHITE", 8, 11)

        # Beyaz piyonlar
        self.board[7][1] = Piece("Piyon\n Piyonu", "WHITE", 7, 1)
        self.board[7][2] = Piece("Savaş Motoru\n Piyonu", "WHITE", 7, 2)
        self.board[7][3] = Piece("Deve\n Piyonu", "WHITE", 7, 3)
        self.board[7][4] = Piece("Fil\n Piyonu", "WHITE", 7, 4)
        self.board[7][5] = Piece("General\n Piyonu", "WHITE", 7, 5)
        self.board[7][6] = Piece("Şah\n Piyonu", "WHITE", 7, 6)
        self.board[7][7] = Piece("Vezir\n Piyonu", "WHITE", 7, 7)
        self.board[7][8] = Piece("Zürafa\n Piyonu", "WHITE", 7, 8)
        self.board[7][9] = Piece("Gözcü\n Piyonu", "WHITE", 7, 9)
        self.board[7][10] = Piece("At\n Piyonu", "WHITE", 7, 10)
        self.board[7][11] = Piece("Kale\n Piyonu", "WHITE", 7, 11)

        # Savaş Motorları
        self.board[0][5] = Piece("Savaş Motoru", "BLACK", 0, 5)  # E1
        self.board[0][7] = Piece("Savaş Motoru", "BLACK", 0, 7)  # G1
        self.board[9][5] = Piece("Savaş Motoru", "WHITE", 9, 5)  # E10
        self.board[9][7] = Piece("Savaş Motoru", "WHITE", 9, 7)  # G10


    def draw(self, screen):
        # Engellenmiş kareler
        blocked_squares = [
            (12, 0), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 9),(12, 1),  # M sütunu engelleri
            (0, 0), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 9),(0, 8)          # A sütunu engelleri
        ]
        
        for row in range(10):
            for col in range(13):
                # Kare rengi belirle
                if (col, row) in blocked_squares:
                    color = BLACK  # Engellenmiş kareleri siyaha boya
                else:
                    color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN  # Diğer kareleri normal renklendir

                # Kareyi çiz
                pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

                # Kare üzerine koordinat yazdır
                font = pygame.font.Font(None, 20)
                if col > 0:
                    text = font.render(chr(ord('A') + col - 1) + str(10 - row), True, BLACK)
                    text_rect = text.get_rect(bottomright=(col * SQUARE_SIZE, (row + 1) * SQUARE_SIZE))
                    screen.blit(text, text_rect)
                if col == 12:
                    text = font.render("M" + str(10 - row), True, BLACK)
                    text_rect = text.get_rect(bottomright=((col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE))
                    screen.blit(text, text_rect)
                
                # Özel efekt çerçevesi ekle (M2 ve A9)
                if (col, row) == (12, 8) or (col, row) == (0, 1):
                    pygame.draw.rect(screen, GOLD, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

                # Taşı çiz
                piece = self.board[row][col]
                if piece:
                    piece_color = BLACK if piece.color == "BLACK" else WHITE
                    piece_font = pygame.font.Font(None, 12)
                    lines = piece.name.splitlines()
                    for i, line in enumerate(lines):
                        piece_text = piece_font.render(line, True, piece_color)
                        piece_text_rect = piece_text.get_rect(
                            center=((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE + i * 12))
                        screen.blit(piece_text, piece_text_rect)

                    # Şah durumunu kontrol et ve efekti çiz
                    if piece and (piece.name == "Şah" or piece.name == "Prens" or piece.name == "Maceracı Şah"):
                        if self.check[piece.color]:
                            pygame.draw.rect(screen, (255, 0, 0),
                                        (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

                if self.selected_piece:
                    if self.selected_piece.name == "Piyon\n Piyonu" and self.selected_piece.is_sleeping:
                        if (row, col) in self.valid_pawn_pawn_placements:
                            pygame.draw.circle(screen, GREEN, ((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE), 10)
                    elif (row, col) in self.selected_piece.get_valid_moves(self.board):
                            pygame.draw.circle(screen, GREEN, ((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE), 10)

    def handle_click(self, pos):
        col = pos[0] // SQUARE_SIZE
        row = pos[1] // SQUARE_SIZE

        if 0 <= row < 10 and 0 <= col < 13:
            clicked_piece = self.board[row][col]

            if self.selected_piece:
                # Uyuyan Piyon Piyonu yerleştirme
                if self.selected_piece.name == "Piyon\n Piyonu" and self.selected_piece.is_sleeping:
                    if (row, col) in self.valid_pawn_pawn_placements:
                        if self.place_sleeping_pawn_pawn(self.selected_piece.row, self.selected_piece.col, row, col):
                            self.selected_piece = None
                            self.change_turn()
                            self.update_check_status()
                    else:  # Geçersiz bir yere tıklandıysa seçimi kaldır
                        self.selected_piece = None
                        self.valid_pawn_pawn_placements = []
                # Normal taş hareketi
                elif (row, col) in self.selected_piece.get_valid_moves(self.board) and self.selected_piece.color == self.turn:
                    # A9 ve M2 için özel kontrol
                    if (row, col) in [(1, 0), (8, 12)]:
                        king_hierarchy = {
                            "Şah": 3,
                            "Prens": 2,
                            "Maceracı Şah": 1
                        }

                        # A9 kontrolü (BEYAZ için)
                    if (row, col) == (1, 0):
                        if self.selected_piece.color == "WHITE": #Beyaz taş A9'a girmek istiyor
                            # Aynı renkte tüm şahları kontrol et
                            max_rank_king = max(
                                (piece for row in range(10) for piece in self.board[row]
                                 if piece and piece.color == "WHITE" and piece.name in king_hierarchy),
                                key=lambda x: king_hierarchy.get(x.name, 0)
                            )
                            if self.selected_piece != max_rank_king:
                                self.selected_piece = None
                                return
                        elif self.selected_piece.color == "BLACK" and self.selected_piece.name != "Maceracı Şah": #Siyah taşlardan sadece Maceracı Şah A9'a girebilir
                            self.selected_piece = None
                            return

                    # M2 kontrolü (SİYAH için)
                    if (row, col) == (8, 12):
                        if self.selected_piece.color == "BLACK": #Siyah taş M2'ye girmek istiyor
                            # Aynı renkte tüm şahları kontrol et
                            max_rank_king = max(
                                (piece for row in range(10) for piece in self.board[row]
                                 if piece and piece.color == "BLACK" and piece.name in king_hierarchy),
                                key=lambda x: king_hierarchy.get(x.name, 0)
                            )
                            if self.selected_piece != max_rank_king:
                                self.selected_piece = None
                                return
                        elif self.selected_piece.color == "WHITE" and self.selected_piece.name != "Maceracı Şah": #Beyaz taşlardan sadece Maceracı Şah M2'ye girebilir.
                            self.selected_piece = None
                            return

                   
                    original_piece = self.board[row][col]
                    original_row, original_col = self.selected_piece.row, self.selected_piece.col

                    if (row, col) == (1, 0) or (row, col) == (8, 12):  # A9 ve M2 kontrolü
                        if self.selected_piece.name in ["Şah", "Prens", "Maceracı Şah"]:
                            self.move_piece(original_row, original_col, row, col)
                        
                            # Şah çekme kontrolü
                            if self.is_check(self.turn):
                                self.move_piece(row, col, original_row, original_col)  # Hareketi geri al
                                if original_piece:  # Alınan taşı geri koy
                                    self.board[row][col] = original_piece
                                    original_piece.row = row
                                    original_piece.col = col
                                return
                            self.change_turn()  # Sırayı değiştir
                            self.update_check_status()  # Şah durumunu güncelle
                            self.selected_piece = None  # Seçimi kaldır
                        else:  # Şah sınıfı değilse bu karelere hareket edemez
                            self.selected_piece = None
                            return
                    else:  # A9 veya M2 değilse
                        self.move_piece(original_row, original_col, row, col)

                        # Şah çekme kontrolü
                        if self.is_check(self.turn):
                            self.move_piece(row, col, original_row, original_col)  # Hareketi geri al
                            if original_piece:  # Alınan taşı geri koy
                                self.board[row][col] = original_piece
                                original_piece.row = row
                                original_piece.col = col
                            return
                        self.change_turn()  # Sırayı değiştir
                        self.update_check_status()  # Şah durumunu güncelle
                        self.selected_piece = None  # Seçimi kaldır

                # Başka bir taş seçme
                elif clicked_piece and clicked_piece.color == self.turn and clicked_piece != self.selected_piece:
                    self.selected_piece = clicked_piece
                    self.valid_pawn_pawn_placements = []

            # Yeni bir taş seçme (Piyon Piyonu veya normal taş)
            elif clicked_piece and clicked_piece.color == self.turn:
                if clicked_piece.name == "Piyon\n Piyonu" and clicked_piece.is_sleeping:
                    self.selected_piece = clicked_piece
                    self.highlight_pawn_pawn_placement_options(clicked_piece)
                else:
                    self.selected_piece = clicked_piece
                    self.valid_pawn_pawn_placements = []

    def update_check_status(self):
        self.check["WHITE"] = self.is_check("WHITE")
        self.check["BLACK"] = self.is_check("BLACK")

    def change_turn(self):
        self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"

    def move_piece(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        if piece:
            captured_piece = self.board[end_row][end_col]
            if captured_piece:
                self.captured_pieces[captured_piece.color].append(captured_piece)

            self.board[end_row][end_col] = piece
            piece.row = end_row
            piece.col = end_col
            self.board[start_row][start_col] = None

            # Tüm piyonlar için promosyon kontrolü
            if piece.name.endswith(" Piyonu") and (end_row == 0 or end_row == 9):
                promoted_name = piece.promote()
                if promoted_name:
                    self.board[end_row][end_col] = Piece(promoted_name, piece.color, end_row, end_col)

            # Piyon Piyonu hareket sayacı ve özel kural
            if piece.name == "Piyon\n Piyonu":
                if end_row == 0 or end_row == 9:
                    self.pawn_pawn_move_count[piece.color] += 1  # Hareket sayacını artır
                    piece.pawn_pawn_journey_count += 1 #Yolculuk sayacını arttır
                    if self.pawn_pawn_move_count[piece.color] == 1:
                        piece.is_sleeping = True  # İlk ulaşmada uyku moduna al

                    elif self.pawn_pawn_move_count[piece.color] == 2:
                        initial_row, initial_col = self.initial_pawn_pawn_positions[piece.color]

                        # Hedef karedeki taşı ele geçir (Şah hariç)
                        target_piece = self.board[initial_row][initial_col]
                        if target_piece and target_piece.name not in ("Şah", "Prens"):
                            self.captured_pieces[target_piece.color].append(target_piece)
                            self.board[initial_row][initial_col] = None

                        # Piyon Piyonu'nu başlangıç konumuna taşı
                        self.board[end_row][end_col] = None  # Eski konumdan kaldır
                        self.board[initial_row][initial_col] = piece  # Başlangıç noktasına koy                    
                        piece.row = initial_row
                        piece.col = initial_col
                        piece.is_sleeping = False # Uyku modundan çıkar. Normal hareketine devam etsin.

                    elif self.pawn_pawn_move_count[piece.color] == 3: # 3. kez son sıraya ulaştığında
                        self.board[end_row][end_col] = None
                        self.board[end_row][end_col] = Piece("Maceracı Şah", piece.color, end_row, end_col)
                        
            # Eğer taş Piyon Piyonu ise ve uyku modunda değilse (yani hareket ettiriliyorsa), listeden eski konumunu kaldır
            if piece.name == "Piyon\n Piyonu" and not piece.is_sleeping and (start_row, start_col) in self.pawn_pawn_placeable[piece.color]:
                self.pawn_pawn_placeable[piece.color].remove((start_row, start_col))

    def is_check(self, color):
        """Belirtilen renkteki şahın tehdit altında olup olmadığını kontrol eder."""
        kings_positions = []  # Şah ve Prens pozisyonlarını takip edeceğiz
        for row in range(10):
           for col in range(13):
               piece = self.board[row][col]
               if piece and piece.color == color and (piece.name == "Şah" or piece.name == "Prens" or piece.name == "Maceracı Şah"):
                   kings_positions.append((row, col))

        if not kings_positions:
            return False

        # Eğer sadece bir Şah veya Prens varsa şah çekilebilir
        if len(kings_positions) == 1:
            king_pos = kings_positions[0]
            opponent_color = "BLACK" if color == "WHITE" else "WHITE"
            for row in range(10):
                for col in range(11):
                    piece = self.board[row][col]
                    if piece and piece.color == opponent_color:
                        valid_moves = piece.get_valid_moves(self.board)
                        if king_pos in valid_moves:
                            return True
        return False
    

    def is_position_forking_or_trapping(self, row, col, color):
        """
        Konumun taşları çatallayıp çatallamadığını veya tuzaklayıp tuzaklamadığını kontrol eder.
        Yerleşim birden fazla taşı tehdit ediyorsa, bir taşı tuzağa düşürüyorsa True döndürür.
        """
        opponent_color = "BLACK" if color == "WHITE" else "WHITE"
    
        # Piyon Piyonunu yerleştirmeyi simüle et
        original_board = [row[:] for row in self.board]
        self.board[row][col] = Piece("Piyon\n Piyonu", color, row, col)
    
        
        threatened_pieces = []
        trapped_pieces = []
    
        # Her rakip taş için tehdit konrolü
        for r in range(10):
            for c in range(11):
                piece = self.board[r][c]
                if piece and piece.color == opponent_color:
                    valid_moves = self.board[row][col].get_valid_moves(self.board)
                    if (r, c) in valid_moves:
                        threatened_pieces.append(piece)
                    
                        
                        all_moves_blocked = True
                        for move_r in range(10):
                            for move_c in range(11):
                                if piece.get_valid_moves(self.board):
                                    all_moves_blocked = False
                                    break
                            if not all_moves_blocked:
                                break
                    
                        if all_moves_blocked:
                            trapped_pieces.append(piece)
    
        
        self.board = original_board
    
        # Yerleştirme şu durumlarda geçerlidir:
        # 1. İki taşı çatallayabileceği bir durumda veya
        # 2. bir taş tamamen sıkışmış, kaçamaz durumdaysa
        return len(threatened_pieces) > 1 or len(trapped_pieces) > 0
    

    def handle_pawn_pawn_placement(self, pos):
        """
        Son sıraya ulaştığında Piyon Piyon'un özel yerleşimini
        """
        col = pos[0] // SQUARE_SIZE - 1
        row = pos[1] // SQUARE_SIZE

        if 0 <= row <= 9 and 0 <= col <= 10:
            if row in [0, 9]:  # Son satırlar
                color = "WHITE" if row == 0 else "BLACK"
                
                # Bu renk için yerleştirilebilecek bir Piyon olup olmadığını kontrol
                available_pawn_pawns = [p for p in self.pawn_pawn_placeable[color] if p[0] == row]
                
                if available_pawn_pawns:
                    # Pozisyonun yerleştirme için geçerli olup olmadığını kontrol
                    if self.is_position_forking_or_trapping(row, col, color):
                        # Piyonu yerleştirilebilir listeden kaldır
                        pawn_to_remove = available_pawn_pawns[0]
                        self.pawn_pawn_placeable[color].remove(pawn_to_remove)
                        
                        # Piyon Piyonunu yerleştir
                        self.board[row][col] = Piece("Piyon\n Piyonu", color, row, col)
                        
                        # Tur değiştir
                        self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"
                        return True
        return False


    def place_sleeping_pawn_pawn(self, start_row, start_col, end_row, end_col):
        """Uyuyan Piyon Piyonu'nu yerleştirir, Şah hariç diğer taşları ele geçirme özelliği eklendi."""
        piece = self.board[start_row][start_col]

        if not piece or piece.name != "Piyon\n Piyonu" or not piece.is_sleeping:
            return False

        if (end_row, end_col) in self.valid_pawn_pawn_placements:
            # Hedef karede Şah yoksa, herhangi bir taşı ele geçirebilir
            target_piece = self.board[end_row][end_col]
            if target_piece and target_piece.name in ("Şah", "Prens"): # Şah ve Prens korumalı
                return False
            else: #Diğer taşlar alınabilir.
                 if target_piece:  # Eğer hedef karede bir taş varsa
                    self.captured_pieces[target_piece.color].append(target_piece) # Taşı ele geçir

                 self.move_piece(start_row, start_col, end_row, end_col) #hareketi yap
                 piece.is_sleeping = False
                 if (piece.row, piece.col) in self.pawn_pawn_placeable[piece.color]:
                    self.pawn_pawn_placeable[piece.color].remove((piece.row, piece.col))
                 self.valid_pawn_pawn_placements = []
                 return True

        return False
    

    def is_safe(self, row, col, color):
        """Belirtilen karenin belirtilen renk için güvenli olup olmadığını kontrol eder."""

        # Simülasyon için geçici bir taş oluştur
        temp_piece = Piece("Temp", color, row, col)  
        original_piece = self.board[row][col]
        self.board[row][col] = temp_piece

        opponent_color = "BLACK" if color == "WHITE" else "WHITE"
        is_safe = True  # Başlangıçta güvenli kabul et

        for r in range(10):
            for c in range(11):
                enemy_piece = self.board[r][c]
                if enemy_piece and enemy_piece.color == opponent_color:
                    # Potansiyel olarak tehlikeli hamleleri kontrol et
                    if (row, col) in enemy_piece.get_valid_moves(self.board):
                        is_safe = False
                        break  # Tehlike bulundu, döngüden 
            if not is_safe:
                break  # Tehlike bulundu, döngüden çık

        # Simülasyonu geri al
        self.board[row][col] = original_piece

        return is_safe
    

    def can_place_pawn_pawn(self, row, col, color):
        """Piyon Piyonu belirtilen konuma yerleştirilebilir mi kontrol eder."""
       #Güvenlik kontrolüne gerek yok çünkü artık tehlikeli karelere yerleştirilebilir.

        temp_piece = Piece("Piyon\n Piyonu", color, row, col)
        original_piece = self.board[row][col]  # Eski taşı sakla
        self.board[row][col] = temp_piece # Geçici taşı yerleştir
        temp_piece.row = row
        temp_piece.col = col

        # Yerleştirme geçerli mi kontrol et
        is_valid = self.check_unavoidable_attack(row, col, color) or self.check_double_fork(row, col, color)

        # Geçici taşı kaldır ve eski taşı geri koy
        self.board[row][col] = original_piece

        return is_valid
    


    def check_unavoidable_attack(self, row, col, color):
        """Kaçınılmaz saldırı var mı kontrol eder."""
        opponent_color = "BLACK" if color == "WHITE" else "WHITE"
        attacking_piece = self.board[row][col] # Saldıran taşı önce al

        # Saldıran taş yoksa, kaçınılmaz saldırı da yok.
        if attacking_piece is None:
            return False

        for r in range(10):
            for c in range(11):
                target_piece = self.board[r][c]
                if target_piece and target_piece.color == opponent_color:
                    
                    if (r,c) in attacking_piece.get_valid_moves(self.board):
                        can_escape = False
                        original_row, original_col = target_piece.row, target_piece.col

                        for next_r in range(10):
                            for next_c in range(11):
                                #Hedef taşın geçerli hamleleri varsa
                                if (next_r, next_c) in target_piece.get_valid_moves(self.board):
                                     #Simülasyon için gerekli değişkenler
                                    original_piece = self.board[next_r][next_c]
                                    can_escape = False

                                    # Hareketi simüle et
                                    self.move_piece(original_row, original_col, next_r, next_c)

                                    # Saldırı hala kaçınılmaz mı?
                                    if (next_r, next_c) not in attacking_piece.get_valid_moves(self.board):
                                        can_escape = True
                                        
                                    # Taşı ve varsa alınan taşı eski yerine koy
                                    self.board[original_row][original_col] = target_piece
                                    target_piece.row = original_row
                                    target_piece.col = original_col
                                    self.board[next_r][next_c] = original_piece
                                    if original_piece is not None:
                                        original_piece.row = next_r
                                        original_piece.col = next_c



                                    if can_escape:
                                        break # Kaçış yolu bulundu
                            if can_escape:
                                break # Kaçış yolu bulundu
                        if not can_escape: # Hiçbir kaçış yolu bulunamadı
                            return True # Saldırı kaçınılmaz
        return False
    


    def check_double_fork(self, row, col, color):
        """Çatallama var mı kontrol eder."""

        attacking_piece = self.board[row][col]

        # Eğer attacking_piece None ise, çatal olamaz
        if attacking_piece is None:  
            return False

        opponent_color = "BLACK" if color == "WHITE" else "WHITE"
        forked_pieces = []

        
        valid_moves = attacking_piece.get_valid_moves(self.board)

        for r in range(10):
            for c in range(11):
                target_piece = self.board[r][c] #Hedeflenen taşı al
                #Hedef taşın geçerli hamleler arasında olup olmadığını ve Şah olmadığını kontrol et
                if (r, c) in valid_moves and target_piece is not None and target_piece.color == opponent_color and target_piece.name != "Şah":
                    # Aynı taşın birden fazla kez eklenmesini engelle
                    if target_piece not in forked_pieces:
                        forked_pieces.append(target_piece)

        return len(forked_pieces) >= 2 # En az iki farklı taşın tehdit altında olması gerekiyor
    


    def highlight_pawn_pawn_placement_options(self, piece):
        if piece.name == "Piyon\n Piyonu" and piece.is_sleeping:
            self.valid_pawn_pawn_placements = []
            for row in range(1, 9):  
                for col in range(13):
                    target_piece = self.board[row][col] #Hedef karedeki taşı al

                    # Şah veya Prens değilse ve güvenliyse ekle.
                    if not (target_piece and target_piece.name in ("Şah", "Prens")) and self.is_safe(row, col, piece.color):  
                        if self.can_place_pawn_pawn(row, col, piece.color):
                           self.valid_pawn_pawn_placements.append((row, col))



def main():
    # Satranç tahtasını oluştur
    chess_board = CustomChessBoard()

    # Ana oyun döngüsü
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                chess_board.handle_click(event.pos)
                chess_board.update_check_status()  # Her tıklamadan sonra şah durumunu güncelle

        screen.fill(WHITE)
        pygame.draw.rect(screen, LIGHT_BROWN, (0, 0, WIDTH, HEIGHT))
        chess_board.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()