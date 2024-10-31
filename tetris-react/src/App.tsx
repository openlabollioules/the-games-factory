// App.tsx
import React from 'react';
import GameBoard from './GameBoard';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="App">
      <h1>Tetris Game</h1>
      <GameBoard />
    </div>
  );
};

export default App;
