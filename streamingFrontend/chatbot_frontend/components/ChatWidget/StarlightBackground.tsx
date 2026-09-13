"use client";

import { useEffect, useRef } from "react";

type Star = {
  x: number;
  y: number;
  radius: number;
  opacity: number;
  twinkleSpeed: number;
  twinkleOffset: number;
  isDiamond: boolean;
};

type FallingStar = {
  x: number;
  y: number;
  length: number;
  speed: number;
  opacity: number;
  delay: number;
};

function createStars(width: number, height: number, count: number): Star[] {
  return Array.from({ length: count }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    radius: Math.random() * 1.4 + 0.4,
    opacity: Math.random() * 0.5 + 0.2,
    twinkleSpeed: Math.random() * 0.002 + 0.001,
    twinkleOffset: Math.random() * Math.PI * 2,
    isDiamond: Math.random() > 0.94,
  }));
}

function createFallingStars(width: number, height: number, count: number): FallingStar[] {
  return Array.from({ length: count }, (_, index) => ({
    x: Math.random() * width * 1.2 - width * 0.1,
    y: Math.random() * height * -0.5,
    length: Math.random() * 28 + 18,
    speed: Math.random() * 0.7 + 0.45,
    opacity: Math.random() * 0.35 + 0.25,
    delay: index * 900 + Math.random() * 2200,
  }));
}

function drawDiamond(
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  size: number,
  opacity: number,
) {
  context.save();
  context.translate(x, y);
  context.rotate(Math.PI / 4);
  context.fillStyle = `rgba(255, 248, 231, ${opacity})`;
  context.fillRect(-size / 2, -size / 2, size, size);
  context.strokeStyle = `rgba(212, 175, 55, ${opacity * 0.8})`;
  context.lineWidth = 0.5;
  context.strokeRect(-size / 2, -size / 2, size, size);
  context.restore();
}

function drawFallingStar(
  context: CanvasRenderingContext2D,
  star: FallingStar,
  width: number,
  height: number,
  progress: number,
) {
  const headX = star.x + progress * star.speed * 0.55;
  const headY = star.y + progress * star.speed;
  const tailX = headX - star.length * 0.35;
  const tailY = headY - star.length;

  if (headY > height + star.length || headX > width + star.length) {
    return false;
  }

  const gradient = context.createLinearGradient(tailX, tailY, headX, headY);
  gradient.addColorStop(0, "rgba(255, 248, 231, 0)");
  gradient.addColorStop(0.55, `rgba(212, 175, 55, ${star.opacity * 0.35})`);
  gradient.addColorStop(1, `rgba(255, 248, 231, ${star.opacity})`);

  context.beginPath();
  context.moveTo(tailX, tailY);
  context.lineTo(headX, headY);
  context.strokeStyle = gradient;
  context.lineWidth = 1.4;
  context.lineCap = "round";
  context.stroke();

  context.beginPath();
  context.arc(headX, headY, 1.6, 0, Math.PI * 2);
  context.fillStyle = `rgba(255, 248, 231, ${star.opacity})`;
  context.fill();

  return true;
}

type StarlightBackgroundProps = {
  className?: string;
  starCount?: number;
  fallingStarCount?: number;
  showFallingStars?: boolean;
};

export default function StarlightBackground({
  className = "",
  starCount = 90,
  fallingStarCount = 14,
  showFallingStars = true,
}: StarlightBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const context = canvas.getContext("2d");
    if (!context) {
      return;
    }

    const canvasEl = canvas;
    const ctx = context;

    let animationFrame = 0;
    let stars: Star[] = [];
    let fallingStars: FallingStar[] = [];
    let startTime = performance.now();
    let width = 0;
    let height = 0;

    function resetFallingStar(star: FallingStar) {
      star.x = Math.random() * width * 1.2 - width * 0.1;
      star.y = -Math.random() * height * 0.35 - star.length;
      star.length = Math.random() * 28 + 18;
      star.speed = Math.random() * 0.7 + 0.45;
      star.opacity = Math.random() * 0.35 + 0.25;
      star.delay = Math.random() * 1800;
    }

    function resize() {
      const parent = canvasEl.parentElement;
      if (!parent) {
        return;
      }

      const rect = parent.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      const dpr = window.devicePixelRatio || 1;

      canvasEl.width = width * dpr;
      canvasEl.height = height * dpr;
      canvasEl.style.width = `${width}px`;
      canvasEl.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      stars = createStars(width, height, starCount);
      fallingStars = createFallingStars(width, height, fallingStarCount);
    }

    function draw() {
      const parent = canvasEl.parentElement;
      if (!parent) {
        return;
      }

      const elapsed = performance.now() - startTime;

      ctx.clearRect(0, 0, width, height);

      for (const star of stars) {
        const twinkle =
          0.35 +
          0.65 *
            ((Math.sin(elapsed * star.twinkleSpeed + star.twinkleOffset) + 1) /
              2);
        const alpha = star.opacity * twinkle;

        if (star.isDiamond) {
          drawDiamond(ctx, star.x, star.y, star.radius * 3.5, alpha);
          continue;
        }

        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 248, 231, ${alpha})`;
        ctx.fill();

        if (star.radius > 1.2) {
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.radius * 2.5, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(212, 175, 55, ${alpha * 0.15})`;
          ctx.fill();
        }
      }

      if (showFallingStars) {
        for (const star of fallingStars) {
          const progress = Math.max(0, elapsed - star.delay);
          const visible = drawFallingStar(ctx, star, width, height, progress);

          if (!visible && progress > 0) {
            resetFallingStar(star);
            star.delay = elapsed + Math.random() * 1200;
          }
        }
      }

      animationFrame = window.requestAnimationFrame(draw);
    }

    resize();
    draw();

    const parent = canvasEl.parentElement;
    if (!parent) {
      return;
    }

    const observer = new ResizeObserver(resize);
    observer.observe(parent);

    return () => {
      window.cancelAnimationFrame(animationFrame);
      observer.disconnect();
    };
  }, [fallingStarCount, showFallingStars, starCount]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className={`pointer-events-none absolute inset-0 h-full w-full ${className}`}
    />
  );
}
