import React from 'react';
import { Play, RotateCcw, Terminal, ChevronDown } from 'lucide-react';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-c';
import 'prismjs/components/prism-cpp';
import 'prismjs/components/prism-go';
import 'prismjs/components/prism-rust';

interface IDEViewProps {
  question: string;
  status: 'connecting' | 'ready' | 'thinking' | 'error';
}

interface LanguageOption {
  id: string;
  label: string;
  version: string;
  prismLang: string;
  fileName: string;
  dotColor: string;
  starterCode: string;
}

const languages: LanguageOption[] = [
  {
    id: 'python',
    label: 'Python',
    version: '3.12',
    prismLang: 'python',
    fileName: 'main.py',
    dotColor: 'bg-yellow-400',
    starterCode: `def solution(nums, k):
    """
    Solve the problem here.
    """
    # Write your code below
    nums.sort()

    count = 0
    last_selected = -float('inf')

    for num in nums:
        if num - last_selected > k:
            count += 1
            last_selected = num

    return count
`,
  },
  {
    id: 'javascript',
    label: 'JavaScript',
    version: 'ES2024',
    prismLang: 'javascript',
    fileName: 'solution.js',
    dotColor: 'bg-amber-400',
    starterCode: `function solution(nums, k) {
  // Write your code below
  nums.sort((a, b) => a - b);

  let count = 0;
  let lastSelected = -Infinity;

  for (const num of nums) {
    if (num - lastSelected > k) {
      count++;
      lastSelected = num;
    }
  }

  return count;
}
`,
  },
  {
    id: 'typescript',
    label: 'TypeScript',
    version: '5.8',
    prismLang: 'typescript',
    fileName: 'solution.ts',
    dotColor: 'bg-blue-500',
    starterCode: `function solution(nums: number[], k: number): number {
  // Write your code below
  nums.sort((a, b) => a - b);

  let count = 0;
  let lastSelected = -Infinity;

  for (const num of nums) {
    if (num - lastSelected > k) {
      count++;
      lastSelected = num;
    }
  }

  return count;
}
`,
  },
  {
    id: 'java',
    label: 'Java',
    version: '21',
    prismLang: 'java',
    fileName: 'Solution.java',
    dotColor: 'bg-red-500',
    starterCode: `import java.util.Arrays;

class Solution {
    public int solution(int[] nums, int k) {
        // Write your code below
        Arrays.sort(nums);

        int count = 0;
        int lastSelected = Integer.MIN_VALUE;

        for (int num : nums) {
            if ((long) num - lastSelected > k) {
                count++;
                lastSelected = num;
            }
        }

        return count;
    }
}
`,
  },
  {
    id: 'cpp',
    label: 'C++',
    version: 'C++23',
    prismLang: 'cpp',
    fileName: 'solution.cpp',
    dotColor: 'bg-blue-700',
    starterCode: `#include <vector>
#include <algorithm>
#include <climits>

using namespace std;

class Solution {
public:
    int solution(vector<int>& nums, int k) {
        // Write your code below
        sort(nums.begin(), nums.end());

        int count = 0;
        long long lastSelected = LLONG_MIN;

        for (int num : nums) {
            if (num - lastSelected > k) {
                count++;
                lastSelected = num;
            }
        }

        return count;
    }
};
`,
  },
  {
    id: 'c',
    label: 'C',
    version: 'C17',
    prismLang: 'c',
    fileName: 'solution.c',
    dotColor: 'bg-gray-500',
    starterCode: `#include <stdlib.h>
#include <limits.h>

int compare(const void* a, const void* b) {
    return (*(int*)a - *(int*)b);
}

int solution(int* nums, int numsSize, int k) {
    // Write your code below
    qsort(nums, numsSize, sizeof(int), compare);

    int count = 0;
    long long lastSelected = LLONG_MIN;

    for (int i = 0; i < numsSize; i++) {
        if (nums[i] - lastSelected > k) {
            count++;
            lastSelected = nums[i];
        }
    }

    return count;
}
`,
  },
  {
    id: 'go',
    label: 'Go',
    version: '1.23',
    prismLang: 'go',
    fileName: 'solution.go',
    dotColor: 'bg-cyan-500',
    starterCode: `package main

import (
\t"math"
\t"sort"
)

func solution(nums []int, k int) int {
\t// Write your code below
\tsort.Ints(nums)

\tcount := 0
\tlastSelected := math.MinInt64

\tfor _, num := range nums {
\t\tif num-lastSelected > k {
\t\t\tcount++
\t\t\tlastSelected = num
\t\t}
\t}

\treturn count
}
`,
  },
  {
    id: 'rust',
    label: 'Rust',
    version: '1.82',
    prismLang: 'rust',
    fileName: 'solution.rs',
    dotColor: 'bg-orange-600',
    starterCode: `fn solution(nums: &mut Vec<i32>, k: i32) -> i32 {
    // Write your code below
    nums.sort();

    let mut count = 0;
    let mut last_selected = i64::MIN;

    for &num in nums.iter() {
        if (num as i64) - last_selected > k as i64 {
            count += 1;
            last_selected = num as i64;
        }
    }

    count
}
`,
  },
];

export const IDEView = ({ question, status }: IDEViewProps) => {
  const [selectedLangId, setSelectedLangId] = React.useState('python');
  const [codeMap, setCodeMap] = React.useState<Record<string, string>>(() => {
    const map: Record<string, string> = {};
    languages.forEach(lang => { map[lang.id] = lang.starterCode; });
    return map;
  });
  const [isRunning, setIsRunning] = React.useState(false);
  const [consoleOutput, setConsoleOutput] = React.useState('Console: Ready for execution...');
  const [langDropdownOpen, setLangDropdownOpen] = React.useState(false);
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  const lang = languages.find(l => l.id === selectedLangId)!;
  const code = codeMap[selectedLangId];

  const setCode = (val: string) => {
    setCodeMap(prev => ({ ...prev, [selectedLangId]: val }));
  };

  const lineCount = React.useMemo(() => {
    return Math.max(1, code.split('\n').length);
  }, [code]);

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setLangDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const switchLanguage = (langId: string) => {
    setSelectedLangId(langId);
    setLangDropdownOpen(false);
    setConsoleOutput(`Console: Switched to ${languages.find(l => l.id === langId)!.label}.`);
  };

  const resetEditor = () => {
    setCodeMap(prev => ({ ...prev, [selectedLangId]: lang.starterCode }));
    setConsoleOutput('Console: Editor reset to starter template.');
  };

  const runTests = () => {
    if (isRunning) {
      return;
    }

    setIsRunning(true);
    setConsoleOutput(`Console: Running ${lang.label} checks...`);

    window.setTimeout(() => {
      const hasFunction = code.includes('solution') || code.includes('def ') || code.includes('function ') || code.includes('fn ') || code.includes('func ');
      const hasReturn = /return/.test(code);
      const hasLogic = code.length > lang.starterCode.length * 0.3;

      const checks = [
        { label: 'Function definition', ok: hasFunction },
        { label: 'Return statement', ok: hasReturn },
        { label: 'Solution logic', ok: hasLogic },
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

  const highlightCode = (input: string) => {
    const grammar = Prism.languages[lang.prismLang];
    if (!grammar) return input;
    return Prism.highlight(input, grammar, lang.prismLang);
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
          {/* Language Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setLangDropdownOpen(!langDropdownOpen)}
              className="flex items-center gap-2 px-2.5 py-1.5 bg-white rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50/50 transition-all"
            >
              <span className={`w-2 h-2 rounded-full ${lang.dotColor}`} />
              <span className="text-[11px] font-bold text-slate-700">{lang.label} {lang.version}</span>
              <ChevronDown size={12} className={`text-slate-400 transition-transform ${langDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {langDropdownOpen && (
              <div className="absolute top-full left-0 mt-1 w-52 bg-white rounded-xl border border-slate-200 shadow-xl z-50 py-1 max-h-72 overflow-y-auto">
                {languages.map((l) => (
                  <button
                    key={l.id}
                    onClick={() => switchLanguage(l.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-blue-50 transition-colors ${
                      l.id === selectedLangId ? 'bg-blue-50' : ''
                    }`}
                  >
                    <span className={`w-2 h-2 rounded-full shrink-0 ${l.dotColor}`} />
                    <div className="flex-1 min-w-0">
                      <span className={`text-xs font-semibold ${l.id === selectedLangId ? 'text-blue-600' : 'text-slate-700'}`}>{l.label}</span>
                      <span className="text-[10px] text-slate-400 ml-2">{l.version}</span>
                    </div>
                    {l.id === selectedLangId && (
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
          <span className="text-[10px] text-slate-400 font-medium italic">{lang.fileName}</span>
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
            highlight={highlightCode}
            padding={0}
            tabSize={4}
            insertSpaces
            textareaId="ide-code-editor"
            preClassName={`language-${lang.prismLang}`}
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
          .ide-code-editor .token.class-name {
            color: #4ec9b0;
          }
        `,
      }}
    />
  </div>
);
};
