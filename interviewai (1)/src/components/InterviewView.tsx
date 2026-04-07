import React, { useMemo } from 'react';
import { motion } from 'motion/react';
import { AIBlob } from './AIBlob';

interface InterviewViewProps {
  question: string;
  status: 'connecting' | 'ready' | 'thinking' | 'error';
}

export const InterviewView = ({ question, status }: InterviewViewProps) => {
  const displayText = question || 'Connecting to interview backend...';

  // Dynamically compute font size based on text length so long questions
  // shrink to fit while short ones stay large and prominent.
  const fontStyle = useMemo(() => {
    const len = displayText.length;
    if (len <= 60) {
      // Short text – big and bold
      return { fontSize: 'clamp(1.5rem, 4vw, 2.25rem)', lineHeight: 1.25 };
    }
    if (len <= 150) {
      // Medium text
      return { fontSize: 'clamp(1.25rem, 3vw, 1.75rem)', lineHeight: 1.35 };
    }
    if (len <= 300) {
      // Long text
      return { fontSize: 'clamp(1rem, 2.4vw, 1.375rem)', lineHeight: 1.45 };
    }
    // Very long text
    return { fontSize: 'clamp(0.875rem, 2vw, 1.125rem)', lineHeight: 1.55 };
  }, [displayText]);

  return (
    <div className="flex-1 rounded-3xl flex flex-col items-center justify-center relative overflow-hidden border border-slate-200/80 bg-[#eef3f8] shadow-inner p-8">
      <AIBlob />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-12 text-center max-w-4xl w-full px-4"
      >
        <h2
          className="font-semibold text-[#2563eb] tracking-tight mb-4 break-words"
          style={fontStyle}
        >
          "{displayText}"
        </h2>
        <div className="flex items-center justify-center gap-2 text-slate-500 font-medium text-sm mb-6">
          <span className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
          {status === 'thinking' ? 'AI Mentor is evaluating your response...' : 'AI Mentor is listening and taking notes...'}
        </div>
      </motion.div>
    </div>
  );
};
