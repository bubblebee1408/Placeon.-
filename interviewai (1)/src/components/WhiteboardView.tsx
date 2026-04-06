import React from 'react';
import { 
  Edit3, 
  Eraser, 
  Square, 
  Type, 
  Undo2, 
  Redo2,
  PenTool
} from 'lucide-react';

interface WhiteboardViewProps {
  question: string;
  status: 'connecting' | 'ready' | 'thinking' | 'error';
}

type WhiteboardTool = 'pen' | 'eraser' | 'rect' | 'text';

export const WhiteboardView = ({ question, status }: WhiteboardViewProps) => {
  const canvasRef = React.useRef<HTMLCanvasElement | null>(null);
  const containerRef = React.useRef<HTMLDivElement | null>(null);
  const startPointRef = React.useRef<{ x: number; y: number } | null>(null);
  const rectSnapshotRef = React.useRef<ImageData | null>(null);

  const [tool, setTool] = React.useState<WhiteboardTool>('pen');
  const [isDrawing, setIsDrawing] = React.useState(false);
  const [history, setHistory] = React.useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = React.useState(-1);

  const historyRef = React.useRef<string[]>([]);
  const historyIndexRef = React.useRef(-1);

  React.useEffect(() => {
    historyRef.current = history;
  }, [history]);

  React.useEffect(() => {
    historyIndexRef.current = historyIndex;
  }, [historyIndex]);

  const getCtx = React.useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return null;
    }
    return canvas.getContext('2d');
  }, []);

  const drawSnapshotUrl = React.useCallback((snapshot: string | null) => {
    const canvas = canvasRef.current;
    const ctx = getCtx();
    if (!canvas || !ctx) {
      return;
    }

    const width = canvas.width / (window.devicePixelRatio || 1);
    const height = canvas.height / (window.devicePixelRatio || 1);
    ctx.clearRect(0, 0, width, height);

    if (!snapshot) {
      return;
    }

    const image = new Image();
    image.onload = () => {
      ctx.drawImage(image, 0, 0, width, height);
    };
    image.src = snapshot;
  }, [getCtx]);

  const pushSnapshot = React.useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const snapshot = canvas.toDataURL('image/png');
    setHistory(prev => {
      const next = prev.slice(0, historyIndexRef.current + 1);
      next.push(snapshot);
      return next;
    });
    setHistoryIndex(prev => prev + 1);
  }, []);

  const initializeCanvas = React.useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) {
      return;
    }

    const previous = canvas.width > 0 && canvas.height > 0 ? canvas.toDataURL('image/png') : null;
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    const width = container.clientWidth;
    const height = container.clientHeight;

    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return;
    }

    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    if (previous) {
      drawSnapshotUrl(previous);
    } else {
      pushSnapshot();
    }
  }, [drawSnapshotUrl, pushSnapshot]);

  React.useEffect(() => {
    initializeCanvas();
    window.addEventListener('resize', initializeCanvas);
    return () => {
      window.removeEventListener('resize', initializeCanvas);
    };
  }, [initializeCanvas]);

  const pointFromEvent = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return { x: 0, y: 0 };
    }
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  };

  const onPointerDown = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    const ctx = getCtx();
    if (!canvas || !ctx) {
      return;
    }

    const point = pointFromEvent(event);

    if (tool === 'text') {
      const text = window.prompt('Enter note text');
      if (!text || !text.trim()) {
        return;
      }
      ctx.globalCompositeOperation = 'source-over';
      ctx.fillStyle = '#1e293b';
      ctx.font = '16px Inter, sans-serif';
      ctx.fillText(text.trim(), point.x, point.y);
      pushSnapshot();
      return;
    }

    event.currentTarget.setPointerCapture(event.pointerId);
    setIsDrawing(true);

    if (tool === 'rect') {
      startPointRef.current = point;
      rectSnapshotRef.current = ctx.getImageData(0, 0, canvas.width, canvas.height);
      return;
    }

    ctx.beginPath();
    ctx.moveTo(point.x, point.y);
    ctx.lineWidth = tool === 'eraser' ? 20 : 3;
    ctx.strokeStyle = '#2563eb';
    ctx.globalCompositeOperation = tool === 'eraser' ? 'destination-out' : 'source-over';
  };

  const onPointerMove = (event: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawing) {
      return;
    }

    const canvas = canvasRef.current;
    const ctx = getCtx();
    if (!canvas || !ctx) {
      return;
    }

    const point = pointFromEvent(event);

    if (tool === 'rect') {
      const start = startPointRef.current;
      const snapshot = rectSnapshotRef.current;
      if (!start || !snapshot) {
        return;
      }
      ctx.putImageData(snapshot, 0, 0);
      ctx.globalCompositeOperation = 'source-over';
      ctx.strokeStyle = '#2563eb';
      ctx.lineWidth = 2;
      ctx.strokeRect(start.x, start.y, point.x - start.x, point.y - start.y);
      return;
    }

    ctx.lineTo(point.x, point.y);
    ctx.stroke();
  };

  const onPointerUp = (event: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawing) {
      return;
    }

    const ctx = getCtx();
    if (!ctx) {
      return;
    }

    setIsDrawing(false);
    event.currentTarget.releasePointerCapture(event.pointerId);
    ctx.closePath();
    ctx.globalCompositeOperation = 'source-over';
    pushSnapshot();
  };

  const undo = () => {
    if (historyIndexRef.current <= 0) {
      return;
    }
    const nextIndex = historyIndexRef.current - 1;
    setHistoryIndex(nextIndex);
    drawSnapshotUrl(historyRef.current[nextIndex] ?? null);
  };

  const redo = () => {
    if (historyIndexRef.current >= historyRef.current.length - 1) {
      return;
    }
    const nextIndex = historyIndexRef.current + 1;
    setHistoryIndex(nextIndex);
    drawSnapshotUrl(historyRef.current[nextIndex] ?? null);
  };

  const clearBoard = () => {
    const canvas = canvasRef.current;
    const ctx = getCtx();
    if (!canvas || !ctx) {
      return;
    }
    const width = canvas.width / (window.devicePixelRatio || 1);
    const height = canvas.height / (window.devicePixelRatio || 1);
    ctx.clearRect(0, 0, width, height);
    pushSnapshot();
  };

  const toolClass = (name: WhiteboardTool) => {
    return name === tool
      ? 'w-10 h-10 flex items-center justify-center rounded-xl bg-blue-500 text-white transition-all active:scale-90'
      : 'w-10 h-10 flex items-center justify-center rounded-xl text-slate-400 hover:bg-slate-50 transition-colors';
  };

  return (
  <div className="flex-1 flex flex-col gap-6 relative overflow-hidden h-full">
    {/* Problem Statement (Pinned) */}
    <div className="rounded-2xl p-5 border border-blue-300 bg-[#eef3f8] shrink-0">
      <div className="flex items-center flex-col gap-3">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-slate-800 mb-1">Design a Distributed Rate Limiter</h1>
          <p className="text-slate-500 text-sm leading-relaxed max-w-3xl">
            Create a high-level architecture for a system that limits requests per user across multiple server clusters. Consider latency, consistency, and storage efficiency. Use the whiteboard to sketch the flow.
          </p>
          <p className="mt-2 text-[11px] text-slate-500 bg-white/60 rounded-lg border border-slate-100 px-3 py-2">
            Interview Prompt: {question || 'Waiting for backend question...'}
          </p>
        </div>
        <span className="text-[10px] font-extrabold uppercase tracking-widest px-4 py-1 rounded-full text-blue-600 bg-blue-50 border border-blue-200">
          SYSTEM DESIGN
        </span>
        <span className="text-[10px] font-bold text-slate-500">
          {status === 'thinking' ? 'Saving your explanation...' : 'Whiteboard is live'}
        </span>
      </div>
    </div>

    {/* Drawing Canvas Panel */}
    <div className="flex-1 rounded-2xl border border-slate-200/80 bg-[#eaf1f7] whiteboard-grid relative flex flex-col overflow-hidden group">
      {/* Floating Toolbar */}
      <div className="absolute left-5 top-1/2 -translate-y-1/2 flex flex-col gap-2 bg-white shadow-lg p-2 rounded-2xl z-30 border border-slate-200">
        <button onClick={() => setTool('pen')} className={toolClass('pen')} title="Pen">
          <Edit3 size={20} />
        </button>
        <button onClick={() => setTool('eraser')} className={toolClass('eraser')} title="Eraser">
          <Eraser size={20} />
        </button>
        <button onClick={() => setTool('rect')} className={toolClass('rect')} title="Rectangle">
          <Square size={20} />
        </button>
        <button onClick={() => setTool('text')} className={toolClass('text')} title="Text">
          <Type size={20} />
        </button>
        <div className="w-8 h-[1px] bg-slate-100 mx-auto my-1" />
        <button
          onClick={undo}
          disabled={historyIndex <= 0}
          className="w-10 h-10 flex items-center justify-center rounded-xl text-slate-400 hover:bg-slate-50 transition-colors disabled:text-slate-300 disabled:hover:bg-transparent"
          title="Undo"
        >
          <Undo2 size={20} />
        </button>
        <button
          onClick={redo}
          disabled={historyIndex >= history.length - 1}
          className="w-10 h-10 flex items-center justify-center rounded-xl text-slate-400 hover:bg-slate-50 transition-colors disabled:text-slate-300 disabled:hover:bg-transparent"
          title="Redo"
        >
          <Redo2 size={20} />
        </button>
      </div>

      <div className="absolute right-5 top-5 z-30">
        <button
          onClick={clearBoard}
          className="px-3 py-1.5 rounded-lg text-[11px] font-semibold text-slate-600 bg-white border border-slate-200 shadow-sm hover:bg-slate-50"
        >
          Clear Board
        </button>
      </div>

      <div ref={containerRef} className="absolute inset-0">
        <canvas
          ref={canvasRef}
          className="absolute inset-0 touch-none"
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerLeave={onPointerUp}
        />
      </div>

      {historyIndex <= 0 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-30">
          <div className="text-slate-400 flex flex-col items-center gap-4">
            <PenTool size={64} strokeWidth={1.5} />
            <p className="font-bold text-lg tracking-tight">Sketch your architecture here</p>
          </div>
        </div>
      )}
    </div>

    <style dangerouslySetInnerHTML={{ __html: `
      .whiteboard-grid {
        background-image: radial-gradient(circle, #cbd5e1 1px, transparent 1px);
        background-size: 28px 28px;
      }
    `}} />
  </div>
);
};
