import React from 'react';
import { 
  MessageSquare, 
  Clock, 
  CheckCircle2, 
  Send
} from 'lucide-react';
import { motion } from 'motion/react';
import { cn } from '../lib/utils';
import type { EvaluateAnswerResponse } from '../lib/interviewApi';

interface Message {
  id: string;
  sender: 'AI Mentor' | 'You';
  time: string;
  text: string;
  isLive?: boolean;
}

interface SidebarProps {
  view: 'interview' | 'ide' | 'whiteboard';
  messages: Message[];
  isSpeaking: boolean;
  setIsSpeaking: (val: boolean) => void;
  timer: number;
  status: 'connecting' | 'ready' | 'thinking' | 'error';
  errorMessage: string | null;
  currentQuestion: string;
  lastEvaluation: EvaluateAnswerResponse | null;
  onSubmitAnswer: (answer: string) => Promise<void>;
}

export const Sidebar = ({
  view,
  messages,
  isSpeaking,
  setIsSpeaking,
  timer,
  status,
  errorMessage,
  currentQuestion,
  lastEvaluation,
  onSubmitAnswer,
}: SidebarProps) => {
  const [quickAnswer, setQuickAnswer] = React.useState('');

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const submit = async () => {
    if (!quickAnswer.trim()) {
      return;
    }
    const outgoing = quickAnswer;
    setQuickAnswer('');
    await onSubmitAnswer(outgoing);
  };

  const statusLabel = status === 'connecting' ? 'Connecting' : status === 'thinking' ? 'Processing' : status === 'error' ? 'Error' : 'Live';
  const statusColor = status === 'error' 
    ? 'text-red-500 bg-red-50 border-red-200' 
    : status === 'connecting' 
      ? 'text-amber-500 bg-amber-50 border-amber-200'
      : status === 'thinking'
        ? 'text-violet-500 bg-violet-50 border-violet-200'
        : 'text-emerald-500 bg-emerald-50 border-emerald-200';

  return (
    <aside className="flex-1 flex flex-col gap-3 min-w-[320px] h-full overflow-hidden">
      {/* Timer + Status Bar */}
      <div className="rounded-2xl px-4 py-3 border border-slate-200/80 bg-slate-100/80 shadow-sm flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Clock size={14} className="text-blue-500" />
          <span className="text-sm font-bold text-slate-800 tabular-nums tracking-tight">
            {formatTime(timer)}
          </span>
        </div>
        <div className={cn(
          'px-2.5 py-1 rounded-full text-[10px] font-semibold border capitalize',
          statusColor
        )}>
          {statusLabel}
        </div>
      </div>

      {/* Transcript Panel */}
      <div className="flex-1 rounded-2xl flex flex-col overflow-hidden border border-slate-200/80 bg-slate-100/80 shadow-sm">
        <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-blue-50 rounded-lg text-blue-600">
              <MessageSquare size={14} />
            </div>
            <h3 className="font-bold text-sm text-slate-800 tracking-tight">Transcript</h3>
          </div>
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-white border border-slate-200">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
            <span className="text-[9px] font-bold uppercase tracking-widest text-rose-500">Live</span>
          </div>
        </div>
        
        <div className="flex-1 p-3 space-y-2.5 overflow-y-auto custom-scrollbar">
          {/* Current prompt */}
          <div className="text-[11px] text-slate-600 bg-white border border-slate-200 rounded-xl p-3">
            <div className="font-semibold uppercase tracking-wider text-[9px] text-slate-400 mb-1">Current Prompt</div>
            {currentQuestion || 'Waiting for first question...'}
          </div>

          {/* Error */}
          {errorMessage && (
            <div className="text-[11px] text-red-600 bg-red-50 border border-red-200 rounded-xl p-2.5">
              Backend Error: {errorMessage}
            </div>
          )}

          {/* Messages */}
          {messages.map(msg => (
            <div key={msg.id} className="space-y-1">
              <span className={cn(
                'text-[9px] font-semibold uppercase tracking-wider',
                msg.sender === 'AI Mentor' ? 'text-blue-600' : 'text-slate-500'
              )}>
                {msg.sender} • {msg.time}
              </span>
              <p className={cn(
                'text-xs leading-relaxed p-2.5 rounded-xl border',
                msg.sender === 'AI Mentor' 
                  ? 'bg-blue-50 text-slate-700 border-blue-100 rounded-tl-none'
                  : 'bg-white text-slate-600 border-slate-200 rounded-tr-none italic'
              )}>
                {msg.text}
              </p>
            </div>
          ))}
          
          {/* Speaking indicator */}
          {isSpeaking && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-1.5 text-blue-600/60 italic"
            >
              <div className="flex gap-0.5">
                <motion.span animate={{ height: [3, 9, 3] }} transition={{ repeat: Infinity, duration: 0.6 }} className="w-0.5 bg-blue-400 rounded-full" />
                <motion.span animate={{ height: [6, 3, 6] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.1 }} className="w-0.5 bg-blue-400 rounded-full" />
                <motion.span animate={{ height: [3, 7, 3] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} className="w-0.5 bg-blue-400 rounded-full" />
              </div>
              <span className="text-[10px] font-bold tracking-tight">User is speaking...</span>
            </motion.div>
          )}

          {/* Last evaluation */}
          {lastEvaluation && (
            <div className="text-[11px] text-slate-600 bg-white border border-slate-200 rounded-xl p-2.5 space-y-1">
              <div className="font-semibold text-[9px] uppercase tracking-wider text-slate-400 mb-1">Evaluation</div>
              <div>Score: {(lastEvaluation.score * 100).toFixed(0)}%</div>
              <div>Confidence: {(lastEvaluation.confidence * 100).toFixed(0)}%</div>
              {lastEvaluation.missing_concepts.length > 0 && (
                <div>Missing: {lastEvaluation.missing_concepts.slice(0, 3).join(', ')}</div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Controls Panel */}
      <div className="rounded-2xl p-3 space-y-2.5 border border-slate-200/80 shadow-sm bg-slate-100/80 shrink-0">
        <button 
          onClick={() => setIsSpeaking(!isSpeaking)}
          className={cn(
            'w-full py-2.5 rounded-full font-semibold text-sm shadow-md flex items-center justify-center gap-2 transition-all active:scale-[0.98]',
            isSpeaking 
              ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-blue-200'
              : 'bg-white text-slate-500 shadow-none border border-slate-200'
          )}
        >
          <span>{isSpeaking ? "Done Speaking" : "Start Speaking"}</span>
          <CheckCircle2 size={16} />
        </button>

        <div className="flex gap-2">
          <textarea
            value={quickAnswer}
            onChange={(event) => setQuickAnswer(event.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
            placeholder={view === 'ide' ? 'Describe your approach...' : view === 'whiteboard' ? 'Describe your decisions...' : 'Type your answer...'}
            className="flex-1 min-h-[72px] bg-white rounded-xl p-2.5 text-xs text-slate-700 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-200 resize-none"
          />
        </div>
        <button
          onClick={submit}
          disabled={status === 'connecting' || status === 'thinking' || !quickAnswer.trim()}
          className="w-full py-2.5 rounded-xl font-semibold text-xs bg-blue-600 hover:bg-blue-700 text-white disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          <Send size={13} />
          {status === 'thinking' ? 'Submitting...' : 'Submit Response'}
        </button>
      </div>
    </aside>
  );
};
