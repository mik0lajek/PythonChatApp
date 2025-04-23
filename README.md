
# Chat Server with Tic-Tac-Toe Game

This project implements a basic multi-client chat server in Python with support for a turn-based Tic-Tac-Toe game between two users.

## Features

- TCP socket-based chat server.
- Handles multiple clients using threads.
- Supports simple text-based commands:
  - `/help`: Display available commands.
  - `/ttt {username}`: Challenge another user to a game of Tic-Tac-Toe.
  - `/ttt-move {position}`: Make a move in the current game.
  - `/disconnect`: Disconnect from the server.
- Game logic for Tic-Tac-Toe:
  - Turn-based play.
  - Win/draw detection.
  - Automatic game cleanup on disconnect.
- Stores chat history setup (database interaction initialized but unused).

## Server Requirements

- Python 3.x
- SQLite3 (for future extension)

## Running the Server

```
python server.py
```

This will start the server on `localhost:5678` and wait for incoming client connections.

## Running the Client

```
python client.py
```

Each client must enter a unique username when connecting. Messages typed in the console are sent to all other connected clients unless prefixed with a command.

## Game Instructions

To start a game of Tic-Tac-Toe:
1. Use `/ttt {username}` to challenge another connected user.
2. Players alternate moves using `/ttt-move {position}`, where position is 0-8 (board is 3x3).

Example board positions:

```
0 | 1 | 2
---------
3 | 4 | 5
---------
6 | 7 | 8
```

## Notes

- The game supports only one active game per user.
- Disconnected players will automatically forfeit any ongoing game.
- This project is meant for local testing and should be extended with security and robustness features for production use.
