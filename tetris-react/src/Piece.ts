import { ROWS, COLS } from './config';

// Piece.ts
export type Piece = {
  x: number;
  y: number;
  shape: number[][];
  color: string;
};

const SHAPES: number[][][] = [
  [[1, 1, 1, 1]], // I
  [[1, 1], [1, 1]], // O
  [[0, 1, 0], [1, 1, 1]], // T
  [[1, 0, 0], [1, 1, 1]], // L
  [[0, 0, 1], [1, 1, 1]], // J
  [[1, 1, 0], [0, 1, 1]], // S
  [[0, 1, 1], [1, 1, 0]]  // Z
];

const COLORS: string[] = [
  'cyan', 'yellow', 'magenta', 'orange', 'blue', 'green', 'red'
];

export const getRandomPiece = (): Piece => {
  const index = Math.floor(Math.random() * SHAPES.length);
  return {
    x: Math.floor(COLS / 2) - 1,
    y: 0,
    shape: SHAPES[index],
    color: COLORS[index]
  };
};

export const rotatePiece = (piece: Piece): Piece => {
  const rotatedShape = piece.shape[0].map((_, index) => piece.shape.map(row => row[index])).reverse();
  return { ...piece, shape: rotatedShape };
};

export const checkCollision = (piece: Piece, grid: number[][]): boolean => {
  for (let y = 0; y < piece.shape.length; y++) {
    for (let x = 0; x < piece.shape[y].length; x++) {
      if (piece.shape[y][x] !== 0) {
        const newY = piece.y + y;
        const newX = piece.x + x;
        if (newY < 0 || newY >= ROWS || newX < 0 || newX >= COLS || grid[newY][newX] !== 0) {
          return true;
        }
      }
    }
  }
  return false;
};

export default Piece;
