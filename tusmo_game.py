import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

class TusmoGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TUSMO - Le jeu de lettres")
        self.setGeometry(100, 100, 400, 400)
        

        def load_dictionary(file_path):
            with open(file_path) as file:
                words = [line.strip().upper() for line in file]
            return words
        
        # Liste de mots (tu peux en ajouter plus)
        self.word_list = load_dictionary("answers.txt")
        
        # Initialisation du jeu
        self.max_attempts = 6
        self.current_attempt = 0
        self.current_word = ""
        self.word_length = 5
        self.used_keys = {}  # Pour colorer le clavier
        
        self.init_ui()
        self.new_game()
        
    def init_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(1)
        
        # Titre
        title = QLabel("Tusmo")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #e74c3c; margin: 20px;")
        main_layout.addWidget(title)
        
        # Grille de jeu
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(1)
        self.grid_cells = []
        
        for row in range(self.max_attempts):
            row_cells = []
            for col in range(self.word_length):
                cell = QLabel("")
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFont(QFont("Arial", 20, QFont.Weight.Bold))
                cell.setFixedSize(50, 50)
                cell.setStyleSheet("""
                    QLabel {
                        background-color: white;
                        border: 3px solid #34495e;
                        border-radius: 8px;
                        color: black;
                    }
                """)
                self.grid_layout.addWidget(cell, row, col)
                row_cells.append(cell)
            self.grid_cells.append(row_cells)
        
        main_layout.addLayout(self.grid_layout)
        
        # Zone de saisie (invisible, juste pour stocker)
        self.current_input = ""
        
        # Label pour afficher le mot en cours
        self.input_display = QLabel("")
        self.input_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_display.setFont(QFont("Arial", 20))
        self.input_display.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(self.input_display)
        
        # Clavier virtuel
        keyboard_layout = QVBoxLayout()
        keyboard_layout.setSpacing(1)
        
        keyboard_rows = [
            ['A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['Q', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M'],
            ['W', 'X', 'C', 'V', 'B', 'N', '⌫', '✓']
        ]
        
        self.key_buttons = {}
        
        for row in keyboard_rows:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(1)
            for key in row:
                btn = QPushButton(key)
                btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                btn.setFixedSize(50, 50)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #95a5a6;
                        color: white;
                        border: none;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #7f8c8d;
                    }
                    QPushButton:pressed {
                        background-color: #5d6d7e;
                    }
                """)
                
                if key == '⌫':
                    btn.clicked.connect(self.backspace)
                elif key == '✓':
                    btn.clicked.connect(self.submit_word)
                else:
                    btn.clicked.connect(lambda checked, k=key: self.add_letter(k))
                
                row_layout.addWidget(btn)
                if key not in ['⌫', '✓']:
                    self.key_buttons[key] = btn
            
            keyboard_layout.addLayout(row_layout)
        
        main_layout.addLayout(keyboard_layout)
        
        # Bouton nouvelle partie
        new_game_btn = QPushButton("🔄 Nouvelle Partie")
        new_game_btn.setFont(QFont("Arial", 14))
        new_game_btn.setFixedHeight(50)
        new_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        new_game_btn.clicked.connect(self.new_game)
        main_layout.addWidget(new_game_btn)
        
    def new_game(self):
        """Démarre une nouvelle partie"""
        self.target_word = random.choice(self.word_list)
        self.current_attempt = 0
        self.current_input = ""
        self.used_keys = {}
        self.input_display.setText("")
        
        # Réinitialiser la grille
        for row in self.grid_cells:
            for cell in row:
                cell.setText("")
                cell.setStyleSheet("""
                    QLabel {
                        background-color: white;
                        border: 3px solid #34495e;
                        border-radius: 8px;
                        color: black;
                    }
                """)
        
        # Afficher la première lettre
        self.grid_cells[0][0].setText(self.target_word[0])
        self.grid_cells[0][0].setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                border: 3px solid #c0392b;
                border-radius: 8px;
                color: white;
            }
        """)
        
        # Réinitialiser le clavier
        for key, btn in self.key_buttons.items():
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
    
    def add_letter(self, letter):
        """Ajoute une lettre au mot en cours"""
        if len(self.current_input) < self.word_length - 1:  # -1 car première lettre déjà donnée
            self.grid_cells[self.current_attempt][len(self.current_input)+1].setText(letter)
            self.current_input += letter
            self.update_display()
    
    def backspace(self):
        """Supprime la dernière lettre"""
        if self.current_input:
            self.current_input = self.current_input[:-1]
            self.grid_cells[self.current_attempt][len(self.current_input)].setText("")
            self.update_display()
    
    def update_display(self):
        """Met à jour l'affichage du mot en cours"""
        full_word = self.target_word[0] + self.current_input
        self.input_display.setText(f"Mot actuel: {full_word}")
    
    def submit_word(self):
        """Soumet le mot pour vérification"""
        if len(self.current_input) != self.word_length - 1:
            QMessageBox.warning(self, "Attention", 
                              f"Le mot doit contenir {self.word_length} lettres!")
            return
        
        # Construire le mot complet
        guessed_word = self.target_word[0] + self.current_input
        
        # Vérifier et colorer
        self.check_word(guessed_word)
        
        # Vérifier victoire
        if guessed_word == self.target_word:
            QMessageBox.information(self, "Bravo! 🎉", 
                                   f"Tu as trouvé le mot {self.target_word} en {self.current_attempt + 1} essai(s)!")
            return
        
        # Passer à la tentative suivante
        self.current_attempt += 1
        self.current_input = ""
        self.input_display.setText("")
        
        # Vérifier défaite
        if self.current_attempt >= self.max_attempts:
            QMessageBox.information(self, "Perdu! 😢", 
                                   f"Le mot était: {self.target_word}")
            return
        
        # Afficher la première lettre pour la prochaine ligne
        if self.current_attempt < self.max_attempts:
            self.grid_cells[self.current_attempt][0].setText(self.target_word[0])
            self.grid_cells[self.current_attempt][0].setStyleSheet("""
                QLabel {
                    background-color: #e74c3c;
                    border: 3px solid #c0392b;
                    border-radius: 8px;
                    color: white;
                }
            """)
    
    def check_word(self, guessed_word):
        """Vérifie le mot et applique les couleurs"""
        target_letters = list(self.target_word)
        guessed_letters = list(guessed_word)
        colors = ['gray'] * self.word_length
        
        # D'abord marquer les lettres exactes (rouge)
        for i in range(self.word_length):
            if guessed_letters[i] == target_letters[i]:
                colors[i] = 'red'
                target_letters[i] = None  # Marquer comme utilisé
        
        # Ensuite marquer les lettres présentes mais mal placées (jaune)
        for i in range(self.word_length):
            if colors[i] != 'red' and guessed_letters[i] in target_letters:
                colors[i] = 'yellow'
                target_letters[target_letters.index(guessed_letters[i])] = None
        
        # Appliquer les couleurs
        for i in range(self.word_length):
            cell = self.grid_cells[self.current_attempt][i]
            cell.setText(guessed_letters[i])
            
            if colors[i] == 'red':
                cell.setStyleSheet("""
                    QLabel {
                        background-color: #e74c3c;
                        border: 3px solid #c0392b;
                        border-radius: 8px;
                        color: white;
                    }
                """)
                # Mettre à jour le clavier
                if guessed_letters[i] in self.key_buttons:
                    self.used_keys[guessed_letters[i]] = 'red'
                    
            elif colors[i] == 'yellow':
                cell.setStyleSheet("""
                    QLabel {
                        background-color: #f39c12;
                        border: 3px solid #d68910;
                        border-radius: 8px;
                        color: white;
                    }
                """)
                # Mettre à jour le clavier (sauf si déjà rouge)
                if guessed_letters[i] in self.key_buttons:
                    if self.used_keys.get(guessed_letters[i]) != 'red':
                        self.used_keys[guessed_letters[i]] = 'yellow'
            else:
                cell.setStyleSheet("""
                    QLabel {
                        background-color: #7f8c8d;
                        border: 3px solid #5d6d7e;
                        border-radius: 8px;
                        color: white;
                    }
                """)
                # Mettre à jour le clavier
                if guessed_letters[i] in self.key_buttons:
                    if guessed_letters[i] not in self.used_keys:
                        self.used_keys[guessed_letters[i]] = 'gray'
        
        # Mettre à jour l'apparence du clavier
        self.update_keyboard_colors()
    
    def update_keyboard_colors(self):
        """Met à jour les couleurs du clavier selon les lettres utilisées"""
        for key, color in self.used_keys.items():
            if key in self.key_buttons:
                btn = self.key_buttons[key]
                if color == 'red':
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border: none;
                            border-radius: 5px;
                        }
                    """)
                elif color == 'yellow':
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #f39c12;
                            color: white;
                            border: none;
                            border-radius: 5px;
                        }
                    """)
                elif color == 'gray':
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #7f8c8d;
                            color: white;
                            border: none;
                            border-radius: 5px;
                        }
                    """)

def main():
    app = QApplication(sys.argv)
    game = TusmoGame()
    game.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
