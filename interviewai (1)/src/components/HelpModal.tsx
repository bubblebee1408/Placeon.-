import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Keyboard, MessageSquare, Code2, PenTool, Lightbulb } from 'lucide-react';

interface HelpModalProps {
  open: boolean;
  onClose: () => void;
}

const shortcuts = [
  { keys: ['Enter'], description: 'Submit your response' },
  { keys: ['Shift', 'Enter'], description: 'New line in text box' },
  { keys: ['⌘', 'K'], description: 'Open quick settings' },
];

const features = [
  {
    icon: <MessageSquare size={18} />,
    title: 'Interview Mode',
    description: 'Answer behavioral and conceptual questions with the AI interviewer face-to-face.',
  },
  {
    icon: <Code2 size={18} />,
    title: 'IDE Mode',
    description: 'Write and run code with a built-in editor for coding challenges.',
  },
  {
    icon: <PenTool size={18} />,
    title: 'Whiteboard Mode',
    description: 'Draw system design diagrams and architecture decisions visually.',
  },
];

const tips = [
  'Speak clearly and structure your answers with the STAR method for behavioral questions.',
  'Use the transcript panel on the right to review previous questions and responses.',
  'For system design, start with requirements before diving into architecture.',
  'You can type your answer instead of speaking if you prefer.',
];

export const HelpModal = ({ open, onClose }: HelpModalProps) => {
  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[100]"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-[101] w-[500px] max-w-[90vw] max-h-[85vh] overflow-y-auto bg-white rounded-2xl shadow-2xl border border-slate-200"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <h2 className="text-lg font-bold text-slate-800 tracking-tight">How It Works</h2>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Content */}
            <div className="px-6 py-5 space-y-6">
              {/* Features */}
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Interview Modes</h3>
                <div className="space-y-3">
                  {features.map((feature) => (
                    <div key={feature.title} className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100">
                      <div className="p-2 rounded-lg bg-blue-50 text-blue-600 shrink-0">{feature.icon}</div>
                      <div>
                        <p className="text-sm font-semibold text-slate-700">{feature.title}</p>
                        <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">{feature.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Keyboard Shortcuts */}
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Keyboard size={12} /> Keyboard Shortcuts
                </h3>
                <div className="space-y-2">
                  {shortcuts.map((shortcut, idx) => (
                    <div key={idx} className="flex items-center justify-between py-1.5">
                      <span className="text-sm text-slate-600">{shortcut.description}</span>
                      <div className="flex items-center gap-1">
                        {shortcut.keys.map((key) => (
                          <kbd
                            key={key}
                            className="px-2 py-1 text-[10px] font-bold text-slate-500 bg-slate-100 border border-slate-200 rounded-md shadow-sm"
                          >
                            {key}
                          </kbd>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Tips */}
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Lightbulb size={12} /> Pro Tips
                </h3>
                <ul className="space-y-2">
                  {tips.map((tip, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-xs text-slate-600 leading-relaxed">
                      <span className="w-5 h-5 rounded-full bg-blue-50 text-blue-600 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-slate-100 flex justify-end">
              <button
                onClick={onClose}
                className="px-5 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow-sm"
              >
                Got it
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
