import socket
import threading
import sqlite3
from datetime import datetime

# Inicjalizacja bazy danych (pozostawiona, jeśli będzie potrzebna historia czatu lub użytkowników)
db_connection = sqlite3.connect('chat_history.db', check_same_thread=False)
db_cursor = db_connection.cursor()

# Tworzenie gniazda serwera
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 5678)
server_socket.bind(server_address)
server_socket.listen(5)

print("Serwer uruchomiony. Oczekiwanie na połączenia...")

clients = {}
usernames = {}
ttt_games = {}  # Słownik zarządzający grami kółko i krzyżyk

class TicTacToeGame:
    def __init__(self, player1, player2):
        self.board = [" " for _ in range(9)]  # Pusta plansza
        self.current_player = player1
        self.player1 = player1
        self.player2 = player2
        self.winner = None

    def make_move(self, position, player):
        if self.winner:
            return "Gra zakończona."
        if player != self.current_player:
            return "Nie Twoja kolej."
        if position < 0 or position >= 9 or self.board[position] != " ":
            return "Nieprawidłowy ruch."

        self.board[position] = "X" if player == self.player1 else "O"
        if self.check_winner():
            self.winner = player
            return f"{player} wygrywa!"
        elif " " not in self.board:
            self.winner = "remis"
            return "Remis!"
        else:
            self.current_player = self.player1 if self.current_player == self.player2 else self.player2
            return self.display_board()

    def check_winner(self):
        winning_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in winning_combinations:
            if self.board[a] == self.board[b] == self.board[c] != " ":
                return True
        return False

    def display_board(self):
        return f"\n" \
               f"{self.board[0]} | {self.board[1]} | {self.board[2]}\n" \
               f"---------\n" \
               f"{self.board[3]} | {self.board[4]} | {self.board[5]}\n" \
               f"---------\n" \
               f"{self.board[6]} | {self.board[7]} | {self.board[8]}\n"

# Obsługa klienta
def handle_client(client_socket, client_address):
    default_username = client_socket.recv(1024).decode('utf-8')
    username = default_username
    usernames[client_socket] = username
    clients[client_socket] = client_address

    print(f"{username} dołączył z adresu {client_address}.")
    client_socket.send(f"Witaj {username}! Jesteś podłączony do czatu. Wpisz /help aby dowiedzieć się więcej.\n".encode('utf-8'))

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message or message.lower() == "/disconnect":
                print(f"{username} zakończył połączenie.")
                break

            if message.startswith('/'):
                if message.lower() == "/help":
                    client_socket.send("Komendy:\n/ttt {gracz} - Rozpocznij grę w kółko i krzyżyk z graczem.\n/ttt-move {pozycja} - Wykonaj ruch.\n".encode('utf-8'))
                elif message.startswith("/ttt "):
                    opponent_name = message.split()[1]
                    opponent_socket = next((sock for sock, name in usernames.items() if name == opponent_name), None)

                    if not opponent_socket or opponent_socket == client_socket:
                        client_socket.send("Nieprawidłowy przeciwnik.\n".encode('utf-8'))
                    elif opponent_socket in ttt_games:
                        client_socket.send("Przeciwnik jest już w trakcie gry.\n".encode('utf-8'))
                    else:
                        ttt_games[client_socket] = TicTacToeGame(client_socket, opponent_socket)
                        ttt_games[opponent_socket] = ttt_games[client_socket]
                        client_socket.send("Rozpoczynasz grę w kółko i krzyżyk!\n".encode('utf-8'))
                        opponent_socket.send("Zostałeś wyzwany do gry w kółko i krzyżyk!\n".encode('utf-8'))
                elif message.startswith("/ttt-move "):
                    if client_socket not in ttt_games:
                        client_socket.send("Nie jesteś w trakcie gry.\n".encode('utf-8'))
                    else:
                        try:
                            position = int(message.split()[1])
                            game = ttt_games[client_socket]
                            result = game.make_move(position, client_socket)

                            player1, player2 = game.player1, game.player2
                            player1.send(result.encode('utf-8'))
                            if player2:
                                player2.send(result.encode('utf-8'))

                            if game.winner:
                                del ttt_games[player1]
                                del ttt_games[player2]
                        except (IndexError, ValueError):
                            client_socket.send("Nieprawidłowy ruch. Wybierz pozycję od 0 do 8.\n".encode('utf-8'))
            else:
                # Obsługa zwykłych wiadomości tekstowych
                broadcast_message(f"{username}: {message}", client_socket)

        except ConnectionResetError:
            break

    del clients[client_socket]
    del usernames[client_socket]
    if client_socket in ttt_games:
        opponent_socket = ttt_games[client_socket].player1 if ttt_games[client_socket].player2 == client_socket else ttt_games[client_socket].player2
        opponent_socket.send("Twój przeciwnik rozłączył się. Gra zakończona.\n".encode('utf-8'))
        del ttt_games[opponent_socket]
        del ttt_games[client_socket]
    client_socket.close()

# Wysyłanie wiadomości do wszystkich klientów
def broadcast_message(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                del clients[client]

# Akceptowanie klientów
def accept_clients():
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Połączono z {client_address}.")
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

# Uruchomienie serwera
try:
    accept_clients()
except KeyboardInterrupt:
    print("Zamykanie serwera...")
    server_socket.close()
