# Red-Blue Nim Game AI (Minimax + Alpha-Beta)

## Overview
This project implements an AI agent to play the Red-Blue Nim game using adversarial search techniques. The system supports both standard and misère versions of the game and uses Minimax with Alpha-Beta pruning to determine optimal moves.

## Features
- Supports two game versions:
  - Standard Nim
  - Misère Nim
- Implements Minimax search with Alpha-Beta pruning
- Depth-limited search with heuristic evaluation
- Human vs Computer gameplay
- Dynamic game state tracking
- Efficient move ordering for pruning optimization

## Technologies Used
- Python
- Minimax Algorithm
- Alpha-Beta Pruning
- Heuristic Evaluation

## How to Run
```bash
python red_blue_nim.py <num-red> <num-blue> [standard|misere] [computer|human] [depth]
