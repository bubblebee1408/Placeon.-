import React from 'react';
import { 
  MessageSquare, 
  Clock, 
  CheckCircle2, 
  FileText, 
  Layers
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

  return (
    <aside className="flex-1 flex flex-col gap-3 min-w-[320px] h-full overflow-hidden">
      <div className="flex-1 rounded-2xl flex flex-col overflow-hidden border border-slate-200/80 bg-slate-100/80 shadow-sm">
        <div className="p-3 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-blue-50 rounded-lg text-blue-600">
              <MessageSquare size={16} />
            </div>
            <h3 className="font-bold text-sm text-slate-800 tracking-tight">Transcript</h3>
          </div>
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-white border border-slate-200">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
            <span className="text-[9px] font-bold uppercase tracking-widest text-rose-500">Live</span>
          </div>
        </div>
        
        <div className="flex-1 p-3 space-y-3 overflow-y-auto custom-scrollbar">
          <div className="text-[10px] text-slate-500 bg-white border border-slate-200 rounded-xl p-2.5">
            <div className="font-semibold uppercase tracking-wider text-slate-400 mb-1">Current Prompt</div>
            {currentQuestion || 'Waiting for first question...'}
          </div>

          {errorMessage && (
            <div className="text-[11px] text-red-600 bg-red-50 border border-red-200 rounded-xl p-2.5">
              Backend Error: {errorMessage}
            </div>
          )}

          {messages.map(msg => (
            <div key={msg.id} className="space-y-1">
              <div className="flex items-center justify-between">
                <span className={cn(
                  'text-[9px] font-semibold uppercase tracking-wider',
                  msg.sender === 'AI Mentor' ? 'text-blue-600' : 'text-slate-500'
                )}>
                  {msg.sender} • {msg.time}
                </span>
              </div>
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

          <div className="text-[11px] text-slate-500 bg-white border border-slate-200 rounded-xl p-2.5">
            {status === 'thinking' ? 'Analyzing response...' : 'Latency stable'}
          </div>
        </div>
      </div>

      <div className="rounded-2xl p-3 space-y-3 border border-slate-200/80 shadow-sm bg-slate-100/80 shrink-0">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Interview Duration</span>
            <div className="flex items-center gap-1.5">
              <Clock size={12} className="text-blue-500" />
              <span className="text-base font-bold text-slate-800 tabular-nums">
                {formatTime(timer)}
              </span>
            </div>
          </div>
          <div className={cn(
            'px-2 py-1 rounded-full text-[10px] font-semibold border',
            status === 'error' ? 'text-red-500 bg-red-50 border-red-200' : 'text-blue-600 bg-blue-50 border-blue-200'
          )}>
            {status}
          </div>
        </div>

        <button 
          onClick={() => setIsSpeaking(!isSpeaking)}
          className={cn(
            'w-full py-3 rounded-full font-semibold text-sm shadow-md flex items-center justify-center gap-2 transition-all active:scale-[0.98]',
            isSpeaking 
              ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-blue-200'
              : 'bg-white text-slate-500 shadow-none border border-slate-200'
          )}
        >
          <span>{isSpeaking ? "Done Speaking" : "Start Speaking"}</span>
          <CheckCircle2 size={18} />
        </button>

        <textarea
          value={quickAnswer}
          onChange={(event) => setQuickAnswer(event.target.value)}
          placeholder={view === 'ide' ? 'Describe your coding approach...' : view === 'whiteboard' ? 'Describe your architecture decisions...' : 'Type your answer...'}
          className="w-full min-h-20 bg-white rounded-xl p-2.5 text-xs text-slate-700 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-200"
        />
        <button
          onClick={submit}
          disabled={status === 'connecting' || status === 'thinking' || !quickAnswer.trim()}
          className="w-full py-2.5 rounded-xl font-semibold text-xs bg-blue-600 hover:bg-blue-700 text-white disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
        >
          {status === 'thinking' ? 'Submitting...' : 'Submit Response'}
        </button>

        {lastEvaluation && (
          <div className="text-[11px] text-slate-600 bg-white border border-slate-200 rounded-xl p-2.5 space-y-1">
            <div>Score: {(lastEvaluation.score * 100).toFixed(0)}%</div>
            <div>Confidence: {(lastEvaluation.confidence * 100).toFixed(0)}%</div>
            {lastEvaluation.missing_concepts.length > 0 && (
              <div>Missing: {lastEvaluation.missing_concepts.slice(0, 3).join(', ')}</div>
            )}
          </div>
        )}

        <div className="flex gap-2">
          <button className="flex-1 py-2 bg-white rounded-lg text-xs font-semibold text-slate-600 border border-slate-200 hover:bg-slate-50 transition-colors flex items-center justify-center gap-1.5">
            <FileText size={14} />
            Notes
          </button>
          <button className="flex-1 py-2 bg-white rounded-lg text-xs font-semibold text-slate-600 border border-slate-200 hover:bg-slate-50 transition-colors flex items-center justify-center gap-1.5">
            <Layers size={14} />
            Resources
          </button>
        </div>

        <button className="w-full py-2 rounded-full text-xs font-semibold text-rose-600 bg-white border border-rose-200 hover:bg-rose-50 transition-colors">
          End Interview
        </button>
      </div>
    </aside>
  );
};
