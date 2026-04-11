import React from 'react';
import { motion } from 'motion/react';
import { AIBlob } from './AIBlob';

interface InterviewViewProps {
  question: string;
  status: 'connecting' | 'ready' | 'thinking' | 'error';
}

export const InterviewView = ({ question, status }: InterviewViewProps) => {
  const content = question || 'Connecting to interview backend...';
  const sizeClass =
    content.length > 240
      ? 'text-xl md:text-2xl'
      : content.length > 160
        ? 'text-2xl md:text-3xl'
        : 'text-3xl md:text-4xl';

  return (
    <div className="flex-1 rounded-3xl flex flex-col items-center justify-center relative overflow-hidden border border-slate-200/80 bg-[#eef3f8] shadow-inner p-8">
      <AIBlob />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-12 text-center max-w-4xl w-full"
      >
        <h2 className={`${sizeClass} font-semibold text-[#2563eb] leading-tight tracking-tight mb-4 transition-all duration-200`}>
          "{content}"
        </h2>
        <div className="flex items-center justify-center gap-2 text-slate-500 font-medium text-sm mb-6">
          <span className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
          {status === 'thinking' ? 'AI Mentor is evaluating your response...' : 'AI Mentor is listening and taking notes...'}
        </div>
      </motion.div>
    </div>
  );
};
