import React from 'react';
import { Play, RotateCcw, Terminal } from 'lucide-react';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';

interface IDEViewProps {
  question: string;
  status: 'connecting' | 'ready' | 'thinking' | 'error';
}

const starterCode = `def max_k_sparse_elements(nums, k):
    # Sort the array to process in linear time
    nums.sort()

    count = 0
    last_selected = -float('inf')

    for num in nums:
        if num - last_selected > k:
            count += 1
            last_selected = num

    return count
`;

export const IDEView = ({ question, status }: IDEViewProps) => {
  const [code, setCode] = React.useState(starterCode);
  const [isRunning, setIsRunning] = React.useState(false);
  const [consoleOutput, setConsoleOutput] = React.useState('Console: Ready for execution...');

  const lineCount = React.useMemo(() => {
    return Math.max(1, code.split('\n').length);
  }, [code]);

  const resetEditor = () => {
    setCode(starterCode);
    setConsoleOutput('Console: Editor reset to starter template.');
  };

  const runTests = () => {
    if (isRunning) {
      return;
    }

    setIsRunning(true);
    setConsoleOutput('Console: Running quick checks...');

    window.setTimeout(() => {
      const checks = [
        {
          label: 'Function signature',
          ok: /def\s+max_k_sparse_elements\s*\(\s*nums\s*,\s*k\s*\)/.test(code),
        },
        {
          label: 'Sort step present',
          ok: code.includes('nums.sort()'),
        },
        {
          label: 'Return statement present',
          ok: /return\s+count/.test(code),
        },
      ];

      const passed = checks.filter(item => item.ok).length;
      const failedNames = checks.filter(item => !item.ok).map(item => item.label);

      if (passed === checks.length) {
        setConsoleOutput(`Console: ${passed}/${checks.length} checks passed. Structure looks good.`);
      } else {
        setConsoleOutput(
          `Console: ${passed}/${checks.length} checks passed. Fix: ${failedNames.join(', ')}.`
        );
      }
      setIsRunning(false);
    }, 550);
  };

  return (
  <div className="flex-1 flex flex-col gap-4 overflow-hidden h-full">
    {/* Problem Statement Panel */}
    <div className="rounded-2xl p-4 flex flex-col gap-2 border border-slate-200/80 bg-[#eef3f8] shrink-0">
      <div className="flex justify-between items-start">
        <div className="flex flex-col gap-0.5">
          <span className="text-[10px] font-extrabold text-blue-500 tracking-widest uppercase">Current Challenge</span>
          <h1 className="text-lg font-bold text-slate-800 tracking-tight">Array Manipulation: The K-Sparse Problem</h1>
        </div>
        <div className="flex gap-2">
          <span className="px-2.5 py-0.5 bg-blue-100 text-blue-600 rounded-full text-[10px] font-bold">Hard</span>
          <span className="px-2.5 py-0.5 bg-white/60 border border-slate-100 text-slate-500 rounded-full text-[10px] font-bold">45:00 Remaining</span>
        </div>
      </div>
      <p className="text-slate-600 text-xs leading-relaxed max-w-4xl">
        Given an array of integers <code className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded border border-blue-100">nums</code> and an integer <code className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded border border-blue-100">k</code>, return the maximum number of elements you can choose such that no two chosen elements have an absolute difference less than or equal to <code className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded border border-blue-100">k</code>.
      </p>
      <p className="text-[11px] text-slate-500 bg-white/60 rounded-lg border border-slate-100 px-3 py-2">
        Interview Prompt: {question || 'Waiting for backend question...'}
      </p>
    </div>

    {/* Editor Module */}
    <div className="flex-1 rounded-2xl overflow-hidden flex flex-col border border-slate-200/80 bg-white">
      {/* Editor Header */}
      <div className="px-4 h-12 bg-slate-50 flex justify-between items-center border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-2.5 py-1 bg-white rounded-lg border border-slate-200">
            <span className="w-1.5 h-1.5 rounded-full bg-yellow-400"></span>
            <span className="text-[10px] font-bold text-slate-700">Python 3.11</span>
          </div>
          <span className="text-[10px] text-slate-400 font-medium italic">main.py</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={resetEditor}
            className="flex items-center gap-2 px-3 py-1.5 hover:bg-white/40 transition-colors rounded-lg text-[10px] font-bold text-slate-600 border border-slate-100"
          >
            <RotateCcw size={12} />
            Reset
          </button>
          <button
            onClick={runTests}
            disabled={isRunning}
            className="flex items-center gap-2 px-4 py-1.5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 disabled:cursor-not-allowed text-white rounded-lg text-[10px] font-bold shadow transition-all active:scale-95"
          >
            <Play size={12} fill="currentColor" />
            {isRunning ? 'Running...' : 'Run Tests'}
          </button>
        </div>
      </div>

      {/* Dark Code Editor */}
      <div className="flex-1 bg-[#0d1117] p-6 font-mono text-sm leading-6 overflow-auto custom-scrollbar">
        <div className="flex gap-6">
          <div className="text-slate-600 text-right select-none pr-4 border-r border-slate-800/50">
            {Array.from({ length: lineCount }, (_, index) => (
              <div key={index}>{index + 1}</div>
            ))}
          </div>
          <Editor
            value={code}
            onValueChange={setCode}
            highlight={(input) => Prism.highlight(input, Prism.languages.python, 'python')}
            padding={0}
            tabSize={4}
            insertSpaces
            textareaId="ide-python-editor"
            preClassName="language-python"
            textareaClassName="outline-none"
            className="flex-1 min-h-full bg-transparent text-slate-100 ide-code-editor"
          />
        </div>
      </div>

      {/* Console Output */}
      <div className="h-10 bg-[#0b1221] flex items-center px-4 gap-2 border-t border-slate-800 shrink-0">
        <Terminal size={14} className="text-blue-400" />
        <span className="text-blue-300/90 font-mono text-[11px]">
          {status === 'thinking' ? 'Console: Sending explanation to backend...' : consoleOutput}
        </span>
      </div>
    </div>

    <style
      dangerouslySetInnerHTML={{
        __html: `
          .ide-code-editor {
            font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
            line-height: 1.5rem;
          }
          .ide-code-editor textarea,
          .ide-code-editor pre {
            min-height: 100%;
            margin: 0;
            white-space: pre;
            word-break: normal;
            overflow-wrap: normal;
          }
          .ide-code-editor textarea {
            color: transparent;
            caret-color: #e5e7eb;
            background: transparent;
          }
          .ide-code-editor pre {
            color: #d4d4d4;
            pointer-events: none;
          }
          .ide-code-editor .token.comment {
            color: #6a9955;
          }
          .ide-code-editor .token.keyword {
            color: #c586c0;
          }
          .ide-code-editor .token.function {
            color: #dcdcaa;
          }
          .ide-code-editor .token.number {
            color: #b5cea8;
          }
          .ide-code-editor .token.string {
            color: #ce9178;
          }
          .ide-code-editor .token.operator,
          .ide-code-editor .token.punctuation {
            color: #d4d4d4;
          }
          .ide-code-editor .token.builtin {
            color: #4ec9b0;
          }
        `,
      }}
    />
  </div>
);
};
