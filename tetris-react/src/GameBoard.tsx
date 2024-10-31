import React, { useState, useEffect } from 'react';
import './GameBoard.css';
import { Piece, getRandomPiece, rotatePiece, checkCollision } from './Piece';
import { ROWS, COLS } from './config';

const GameBoard: React.FC = () => {
  const [grid, setGrid] = useState<number[][]>(createEmptyGrid());
  const [currentPiece, setCurrentPiece] = useState<Piece | null>(getRandomPiece());
  const [score, setScore] = useState<number>(0);
  const [lines, setLines] = useState<number>(0);
  const [gameOver, setGameOver] = useState<boolean>(false);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (!currentPiece || gameOver) return;
      let movedPiece = { ...currentPiece };

      switch (e.key) {
        case 'ArrowLeft':
          movedPiece.x -= 1;
          if (!checkCollision(movedPiece, grid)) {
            setCurrentPiece(movedPiece);
          }
          break;
        case 'ArrowRight':
          movedPiece.x += 1;
          if (!checkCollision(movedPiece, grid)) {
            setCurrentPiece(movedPiece);
          }
          break;
        case 'ArrowDown':
          movePieceDown();
          break;
        case 'ArrowUp':
          const rotatedPiece = rotatePiece(movedPiece);
          if (!checkCollision(rotatedPiece, grid)) {
            setCurrentPiece(rotatedPiece);
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [currentPiece, gameOver]);

  useEffect(() => {
    if (gameOver) return;

    const interval = setInterval(() => {
      movePieceDown();
    }, 800);

    return () => clearInterval(interval);
  }, [currentPiece, gameOver]);

  const movePieceDown = () => {
    if (!currentPiece) return;
    let movedPiece = { ...currentPiece, y: currentPiece.y + 1 };

    if (!checkCollision(movedPiece, grid)) {
      setCurrentPiece(movedPiece);
    } else {
      placePiece();
    }
  };

  const placePiece = () => {
    if (!currentPiece) return;
    const newGrid = [...grid];
    currentPiece.shape.forEach((row: number[], i: number) => {
      row.forEach((value: number, j: number) => {
        if (value !== 0) {
          const newY = currentPiece.y + i;
          const newX = currentPiece.x + j;
          if (newY >= 0 && newY < ROWS && newX >= 0 && newX < COLS) {
            newGrid[newY][newX] = value;
          }
        }
      });
    });
    setGrid(newGrid);
    checkForLines();
    if (currentPiece.y < 1) {
      setGameOver(true);
    } else {
      setCurrentPiece(getRandomPiece());
    }
  };

  const checkForLines = () => {
    let newGrid = [...grid];
    let clearedLines = 0;
    for (let i = ROWS - 1; i >= 0; i--) {
      if (newGrid[i].every((cell) => cell !== 0)) {
        newGrid.splice(i, 1);
        newGrid.unshift(new Array(COLS).fill(0));
        clearedLines++;
      }
    }
    if (clearedLines > 0) {
      setScore(score + clearedLines * 10);
      setLines(lines + clearedLines);
      setGrid(newGrid);
    }
  };

  return (
    <div className="game-board">
      <div className="grid">
        {grid.map((row, rowIndex) => (
          <div key={rowIndex} className="row">
            {row.map((cell, cellIndex) => (
              <div key={cellIndex} className={`cell ${cell !== 0 ? 'filled' : ''}`}></div>
            ))}
          </div>
        ))}
      </div>
      <div className="info">
        <p>Score: {score}</p>
        <p>Lines: {lines}</p>
        {gameOver && <p>Game Over</p>}
      </div>
    </div>
  );
};

const createEmptyGrid = (): number[][] => {
  return Array.from({ length: ROWS }, () => Array(COLS).fill(0));
};

export default GameBoard;