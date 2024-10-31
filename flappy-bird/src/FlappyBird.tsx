import React, { useState, useEffect, useRef } from 'react';
import './FlappyBird.css';

interface BirdProps {
  x: number;
  y: number;
  alive: boolean;
  score: number;
  player: string;
}

const GRAVITY = 0.8;
const FLAP_POWER = -12;
const PIPE_GAP = 200;
const PIPE_WIDTH = 80;
const PIPE_SPEED = 5;
const BIRD_SIZE = 50;
const WIDTH = 800;
const HEIGHT = 600;

const FlappyBird: React.FC = () => {
  const [birds, setBirds] = useState<BirdProps[]>([
    { x: 150, y: HEIGHT / 2, alive: true, score: 0, player: 'Player 1' },
    { x: 250, y: HEIGHT / 2, alive: true, score: 0, player: 'Player 2' },
  ]);
  const [pipes, setPipes] = useState<{ x: number; height: number }[]>([
    { x: WIDTH, height: Math.random() * (HEIGHT - PIPE_GAP - 100) + 50 },
  ]);
  const [gameOver, setGameOver] = useState(false);

  const gameInterval = useRef<NodeJS.Timer | null>(null);

  useEffect(() => {
    if (!gameOver) {
      gameInterval.current = setInterval(() => {
        updateGame();
      }, 20);
    } else {
      if (gameInterval.current) clearInterval(gameInterval.current);
    }
    return () => {
      if (gameInterval.current) clearInterval(gameInterval.current);
    };
  }, [gameOver]);

  const updateGame = () => {
    setBirds((prevBirds) =>
      prevBirds.map((bird) => {
        if (!bird.alive) return bird;
        let newY = bird.y + GRAVITY;
        if (newY > HEIGHT - BIRD_SIZE) {
          return { ...bird, y: HEIGHT - BIRD_SIZE, alive: false };
        }
        return { ...bird, y: newY };
      })
    );

    setPipes((prevPipes) =>
      prevPipes.map((pipe) => ({ ...pipe, x: pipe.x - PIPE_SPEED })).filter((pipe) => pipe.x > -PIPE_WIDTH)
    );

    setPipes((prevPipes) => {
      if (prevPipes.length === 0 || prevPipes[prevPipes.length - 1].x < WIDTH - 300) {
        return [
          ...prevPipes,
          { x: WIDTH, height: Math.random() * (HEIGHT - PIPE_GAP - 100) + 50 },
        ];
      }
      return prevPipes;
    });

    setBirds((prevBirds) =>
      prevBirds.map((bird) => {
        if (!bird.alive) return bird;
        for (let pipe of pipes) {
          if (
            bird.x + BIRD_SIZE > pipe.x &&
            bird.x < pipe.x + PIPE_WIDTH &&
            (bird.y < pipe.height || bird.y + BIRD_SIZE > pipe.height + PIPE_GAP)
          ) {
            return { ...bird, alive: false };
          }
        }
        return bird;
      })
    );

    if (birds.every((bird) => !bird.alive)) {
      setGameOver(true);
    }
  };

  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.code === 'Space') {
      setBirds((prevBirds) =>
        prevBirds.map((bird, index) => (index === 0 && bird.alive ? { ...bird, y: bird.y + FLAP_POWER } : bird))
      );
    }
    if (e.code === 'ShiftLeft') {
      setBirds((prevBirds) =>
        prevBirds.map((bird, index) => (index === 1 && bird.alive ? { ...bird, y: bird.y + FLAP_POWER } : bird))
      );
    }
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, []);

  return (
    <div className="flappy-bird" style={{ width: WIDTH, height: HEIGHT }}>
      {birds.map((bird, index) => (
        <div
          key={index}
          className={`bird ${bird.alive ? '' : 'bird-dead'}`}
          style={{
            left: bird.x,
            top: bird.y,
            width: BIRD_SIZE,
            height: BIRD_SIZE,
          }}
        ></div>
      ))}
      {pipes.map((pipe, index) => (
        <div key={index} className="pipe" style={{ left: pipe.x, height: pipe.height, top: 0 }}></div>
      ))}
      {pipes.map((pipe, index) => (
        <div
          key={index + '-bottom'}
          className="pipe pipe-bottom"
          style={{ left: pipe.x, height: HEIGHT - pipe.height - PIPE_GAP, top: pipe.height + PIPE_GAP }}
        ></div>
      ))}
      <div className="scoreboard">
        {birds.map((bird, index) => (
          <div key={index} className="score">
            {bird.player}: {bird.score}
          </div>
        ))}
      </div>
      {gameOver && <div className="game-over">Game Over</div>}
    </div>
  );
};

export default FlappyBird;
