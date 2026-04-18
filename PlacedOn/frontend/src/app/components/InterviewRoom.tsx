import React, { useState, useEffect } from "react";
import { Mic, Pause, Keyboard, Phone, Wifi, MoreHorizontal, Video, Pencil, Square, Type, Eraser, Target, Lock, Play, FileText, Code2, Presentation, MessageCircle } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

type AIState = "listening" | "thinking" | "speaking";
type InterviewMode = "conversation" | "whiteboard" | "code";

const MOCK_TRANSCRIPT = [
  { id: 1, speaker: "ai", text: "Welcome to PlacedOn. I'm excited to learn more about your experience.", time: "14:10" },
  { id: 2, speaker: "candidate", text: "Thanks, it's great to be here.", time: "14:12" },
  { id: 3, speaker: "ai", text: "Let's jump right in. Walk me through how you’d approach finding why orders are reaching the wrong address. Feel free to use the whiteboard.", time: "14:15" },
];

export function InterviewRoom() {
  const [aiState, setAiState] = useState<AIState>("listening");
  const [micActive, setMicActive] = useState(true);
  const [activeMode, setActiveMode] = useState<InterviewMode>("conversation");

  useEffect(() => {
    const cycle = setInterval(() => {
      setAiState((current) => {
        if (current === "listening") return "thinking";
        if (current === "thinking") return "speaking";
        return "listening";
      });
    }, 4000);
    return () => clearInterval(cycle);
  }, []);

  return (
    <div className="relative h-screen w-screen bg-[#F5F2EC] overflow-hidden flex items-center justify-center p-3 md:p-6 lg:p-8 font-[Inter,sans-serif] text-[#1F2430] selection:bg-[#EAEAFE] selection:text-[#3E63F5]">
      
      {/* 1. Atmosphere Layer - Ambient Wash */}
      <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] bg-[#EAEAFE] rounded-full blur-[140px] opacity-70 pointer-events-none z-0" />
      <div className="absolute bottom-[-15%] right-[-10%] w-[60vw] h-[60vw] bg-[#F8EDEB] rounded-full blur-[160px] opacity-70 pointer-events-none z-0" />
      <div className="absolute top-[20%] right-[10%] w-[40vw] h-[40vw] bg-[#F7F4EF] rounded-full blur-[120px] opacity-80 pointer-events-none z-0" />

      {/* 2. Outer Shell */}
      <div className="relative w-full h-full max-w-[1600px] flex flex-col bg-[#F7F5F1]/95 backdrop-blur-3xl rounded-[2.5rem] md:rounded-[3rem] p-3 md:p-4 shadow-[0_30px_80px_rgba(38,35,30,0.08)] ring-1 ring-white/60 overflow-hidden isolate z-10">
        
        {/* Subtle Inner Highlight on Shell */}
        <div className="absolute inset-0 rounded-[3rem] ring-1 ring-inset ring-white/80 pointer-events-none z-0 mix-blend-overlay" />
        <div className="absolute inset-0 bg-gradient-to-br from-white/30 via-transparent to-black/[0.01] pointer-events-none z-0" />

        {/* Header - Integrated into the shell */}
        <header className="flex items-center justify-between px-6 py-4 shrink-0 mb-2 relative z-20">
          <div className="flex items-center gap-6">
            <div className="font-[Manrope,sans-serif] font-bold text-2xl tracking-tight text-[#1F2430]">
              Placed<span className="text-[#3E63F5]">On</span>
            </div>
            <div className="w-[1px] h-6 bg-[#1F2430]/[0.08]" />
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-[#1F2430]">Product Manager</span>
              <span className="text-xs font-medium text-[#1F2430]/60">Round 1: Technical & Behavioral</span>
            </div>
          </div>

          <div className="flex items-center gap-5">
            {/* Dimensional AI State Pill */}
            <button 
              onClick={() => setAiState(s => s === "listening" ? "thinking" : s === "thinking" ? "speaking" : "listening")}
              className="group flex items-center gap-3 px-5 py-2.5 rounded-full transition-all duration-500 ease-out hover:scale-[1.02] shadow-[0_4px_12px_rgba(30,35,60,0.06),inset_0_1px_1px_rgba(255,255,255,0.9)] ring-1 ring-[#1F2430]/[0.03]"
              style={{
                backgroundColor: aiState === "speaking" ? "rgba(243,244,251,0.85)" : aiState === "thinking" ? "rgba(248,237,235,0.85)" : "rgba(255,255,255,0.85)",
                backdropFilter: "blur(16px)"
              }}
            >
              <AIIndicator state={aiState} />
              <span className="text-sm font-semibold transition-colors duration-500" style={{
                color: aiState === "speaking" ? "#3E63F5" : aiState === "thinking" ? "#D97B94" : "#1F2430"
              }}>
                {aiState === "listening" ? "AI is listening" : aiState === "thinking" ? "AI is thinking" : "AI is speaking"}
              </span>
            </button>

            <div className="w-[1px] h-6 bg-[#1F2430]/[0.08]" />

            <div className="flex items-center gap-4 text-sm font-semibold text-[#1F2430]/60">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/80 backdrop-blur-md shadow-[0_4px_12px_rgba(30,35,60,0.06),inset_0_1px_1px_rgba(255,255,255,0.9)] ring-1 ring-[#1F2430]/[0.03]">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
                <span className="text-[#1F2430] font-medium tracking-wide w-12 tabular-nums">14:23</span>
              </div>
              <div className="flex items-center gap-2">
                <Wifi className="w-4 h-4 text-[#3E63F5]" />
                <span>Excellent</span>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex-1 flex gap-4 min-h-0 w-full relative z-20">
          
          {/* 3. Primary Panel - Main Stage */}
          <div 
            className="flex-1 rounded-[2rem] md:rounded-[2.5rem] relative overflow-hidden shadow-[0_12px_30px_rgba(60,70,110,0.08)] ring-1 ring-white/80 flex flex-col isolate min-h-0 min-w-0"
            style={{ background: "linear-gradient(180deg, #FFFFFF 0%, #FBFAF8 100%)" }}
          >
            {/* Subtle Inner Glow */}
            <div className="absolute inset-0 shadow-[inset_0_2px_40px_rgba(255,255,255,0.8)] pointer-events-none z-0" />
            <div className="absolute top-0 left-0 w-full h-[30%] bg-gradient-to-b from-white/60 to-transparent pointer-events-none z-0 mix-blend-overlay" />

            {/* Mode Switcher - Top Centered */}
            <div className="absolute top-6 left-1/2 -translate-x-1/2 z-40 flex items-center p-1.5 bg-white/70 backdrop-blur-2xl rounded-full shadow-[0_8px_24px_rgba(30,35,60,0.08),inset_0_1px_1px_rgba(255,255,255,1)] ring-1 ring-[#1F2430]/[0.04]">
              <button 
                onClick={() => setActiveMode("conversation")}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-[13px] font-semibold transition-all duration-300 ${activeMode === 'conversation' ? 'bg-white shadow-[0_2px_8px_rgba(30,35,60,0.06),0_1px_2px_rgba(30,35,60,0.04)] text-[#1F2430] ring-1 ring-[#1F2430]/[0.02]' : 'text-[#1F2430]/50 hover:text-[#1F2430] hover:bg-white/40'}`}
              >
                <MessageCircle className="w-4 h-4" />
                Conversation
              </button>
              <button 
                onClick={() => setActiveMode("whiteboard")}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-[13px] font-semibold transition-all duration-300 ${activeMode === 'whiteboard' ? 'bg-white shadow-[0_2px_8px_rgba(30,35,60,0.06),0_1px_2px_rgba(30,35,60,0.04)] text-[#1F2430] ring-1 ring-[#1F2430]/[0.02]' : 'text-[#1F2430]/50 hover:text-[#1F2430] hover:bg-white/40'}`}
              >
                <Presentation className="w-4 h-4" />
                Whiteboard
              </button>
              <div className="w-[1px] h-4 bg-[#1F2430]/[0.06] mx-1" />
              <button 
                onClick={() => setActiveMode("code")}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-[13px] font-semibold transition-all duration-300 ${activeMode === 'code' ? 'bg-white shadow-[0_2px_8px_rgba(30,35,60,0.06),0_1px_2px_rgba(30,35,60,0.04)] text-[#1F2430] ring-1 ring-[#1F2430]/[0.02]' : 'text-[#1F2430]/40 hover:text-[#1F2430] hover:bg-white/40'}`}
              >
                {activeMode !== 'code' ? <Lock className="w-3.5 h-3.5" /> : <Code2 className="w-4 h-4" />}
                Code IDE
              </button>
            </div>

            {/* Dynamic Stage Content based on activeMode */}
            <div className="flex-1 relative z-10 w-full h-full">
              <AnimatePresence mode="wait">
                
                {/* Conversation Mode */}
                {activeMode === "conversation" && (
                  <motion.div 
                    key="conversation"
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.98 }}
                    transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                    className="absolute inset-0 flex flex-col items-center justify-center p-12 md:p-24"
                  >
                    <div className="max-w-4xl w-full flex flex-col items-center text-center space-y-10">
                      {/* Question Accents */}
                      <div className="flex items-center gap-3 text-[#3E63F5] font-semibold tracking-wider text-[13px] uppercase">
                        <div className="w-8 h-[2px] bg-[#3E63F5]/30 rounded-full shadow-[0_1px_2px_rgba(62,99,245,0.2)]" />
                        Current Question
                        <div className="w-8 h-[2px] bg-[#3E63F5]/30 rounded-full shadow-[0_1px_2px_rgba(62,99,245,0.2)]" />
                      </div>

                      <h1 className="font-[Manrope,sans-serif] text-4xl md:text-5xl lg:text-[52px] leading-[1.25] font-semibold text-[#1F2430] tracking-tight text-balance drop-shadow-[0_2px_4px_rgba(255,255,255,0.8)]">
                        “Walk me through how you’d approach finding why orders are reaching the wrong address.”
                      </h1>
                      
                      <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-white/60 backdrop-blur-xl text-[#1F2430]/70 text-[15px] font-medium border border-[#1F2430]/[0.04] shadow-[0_4px_12px_rgba(30,35,60,0.06),inset_0_1px_1px_rgba(255,255,255,0.9)]">
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#3E63F5] opacity-30"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-[#3E63F5]/70 shadow-[0_0_4px_rgba(62,99,245,0.5)]"></span>
                        </span>
                        You have access to the Whiteboard above.
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Whiteboard Mode */}
                {activeMode === "whiteboard" && (
                  <motion.div 
                    key="whiteboard"
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.98 }}
                    transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                    className="absolute inset-0 pt-24 pb-32 px-8 flex flex-col"
                  >
                    <div className="absolute inset-0 bg-[linear-gradient(rgba(31,36,48,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(31,36,48,0.03)_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none z-0" />
                    
                    {/* Floating Toolbar */}
                    <div className="absolute left-8 top-1/2 -translate-y-1/2 flex flex-col gap-2 p-2 bg-white/80 backdrop-blur-xl rounded-2xl shadow-[0_8px_24px_rgba(30,35,60,0.08),inset_0_1px_1px_rgba(255,255,255,0.9)] ring-1 ring-[#1F2430]/[0.03] z-20">
                      <button className="p-2.5 rounded-xl bg-[#EEF1F8] text-[#3E63F5] shadow-[0_2px_4px_rgba(62,99,245,0.1),inset_0_1px_1px_rgba(255,255,255,0.9)] ring-1 ring-[#3E63F5]/10"><Pencil className="w-5 h-5" /></button>
                      <button className="p-2.5 rounded-xl text-[#1F2430]/50 hover:text-[#1F2430] hover:bg-white transition-colors"><Square className="w-5 h-5" /></button>
                      <button className="p-2.5 rounded-xl text-[#1F2430]/50 hover:text-[#1F2430] hover:bg-white transition-colors"><Type className="w-5 h-5" /></button>
                      <div className="w-6 h-[1px] bg-[#1F2430]/[0.06] mx-auto my-1" />
                      <button className="p-2.5 rounded-xl text-[#1F2430]/50 hover:text-[#1F2430] hover:bg-white transition-colors"><Eraser className="w-5 h-5" /></button>
                    </div>

                    {/* Fake Drawing / Canvas Area */}
                    <div className="relative flex-1 rounded-[1.5rem] border border-dashed border-[#1F2430]/10 bg-white/40 shadow-[inset_0_2px_12px_rgba(30,35,60,0.02)] backdrop-blur-sm z-10 overflow-hidden">
                      <svg className="absolute inset-0 w-full h-full pointer-events-none z-0" viewBox="0 0 800 600" preserveAspectRatio="xMidYMid meet">
                        {/* Connecting Line */}
                        <path d="M 250 280 C 350 280, 400 180, 500 180" stroke="#3E63F5" strokeWidth="2.5" fill="none" strokeLinecap="round" className="opacity-80 drop-shadow-md" />
                        
                        {/* Box 1 */}
                        <rect x="90" y="250" width="160" height="60" rx="16" fill="white" stroke="#1F2430" strokeWidth="1.5" strokeOpacity="0.1" style={{filter: 'drop-shadow(0 8px 24px rgba(30,35,60,0.06))'}} />
                        <text x="170" y="285" textAnchor="middle" fill="#1F2430" fontSize="13" fontWeight="600" fontFamily="Inter">API Gateway</text>
                        
                        {/* Box 2 */}
                        <rect x="500" y="150" width="160" height="60" rx="16" fill="#F3F4FB" stroke="#3E63F5" strokeWidth="1.5" strokeOpacity="0.2" style={{filter: 'drop-shadow(0 8px 24px rgba(62,99,245,0.08))'}} />
                        <text x="580" y="185" textAnchor="middle" fill="#3E63F5" fontSize="13" fontWeight="600" fontFamily="Inter">Validation Service</text>
                        
                        {/* AI Cursor */}
                        <g transform="translate(600, 200)" style={{filter: 'drop-shadow(0 4px 12px rgba(217,123,148,0.2))'}}>
                          <path d="M0 0 L14 14 L6 16 L0 24 Z" fill="#D97B94" stroke="white" strokeWidth="2" strokeLinejoin="round" />
                          <rect x="12" y="18" width="80" height="24" rx="12" fill="#D97B94" />
                          <text x="52" y="34" textAnchor="middle" fill="white" fontSize="10" fontWeight="700" letterSpacing="1px">PlacedOn AI</text>
                        </g>
                      </svg>
                    </div>
                  </motion.div>
                )}

                {/* Code IDE Mode */}
                {activeMode === "code" && (
                  <motion.div 
                    key="code"
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.98 }}
                    transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                    className="absolute inset-0 pt-24 pb-32 px-8 flex gap-4 z-10"
                  >
                    {/* Left: Prompt Area */}
                    <div className="w-[280px] bg-white/60 backdrop-blur-md rounded-[1.5rem] shadow-[0_4px_12px_rgba(30,35,60,0.04)] ring-1 ring-[#1F2430]/[0.03] p-6 flex flex-col shrink-0 overflow-y-auto">
                      <h4 className="font-bold text-[#1F2430] mb-4 text-[17px]">Address Validation</h4>
                      <p className="text-[14px] text-[#1F2430]/70 leading-relaxed mb-6">
                        Write a function that validates an incoming address object and returns standard errors for missing fields. Ensure you catch any edge cases.
                      </p>
                      <div className="mt-auto">
                        <div className="text-[11px] font-bold text-[#1F2430]/40 uppercase tracking-wider mb-2">Test Cases</div>
                        <div className="bg-[#EEF1F8]/60 rounded-xl p-3 text-[12px] font-mono text-[#1F2430]/80 shadow-inner ring-1 ring-[#1F2430]/[0.02] overflow-x-auto">
                          <span className="text-[#D97B94]">assert</span>(validate(&#123; street: "" &#125;) === <span className="text-[#3E63F5]">false</span>)
                        </div>
                      </div>
                    </div>

                    {/* Right: Code Editor & Output */}
                    <div className="flex-1 flex flex-col gap-4 min-w-0">
                      {/* Editor Panel */}
                      <div className="flex-1 bg-white/80 backdrop-blur-xl rounded-[1.5rem] shadow-[0_8px_24px_rgba(30,35,60,0.06),inset_0_1px_1px_rgba(255,255,255,0.9)] ring-1 ring-[#1F2430]/[0.03] flex flex-col min-h-0 overflow-hidden">
                        <div className="flex items-center justify-between px-5 py-3 border-b border-[#1F2430]/[0.04] bg-white/50 shrink-0">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-400/20 ring-1 ring-red-400/40" />
                            <div className="w-3 h-3 rounded-full bg-amber-400/20 ring-1 ring-amber-400/40" />
                            <div className="w-3 h-3 rounded-full bg-green-400/20 ring-1 ring-green-400/40" />
                          </div>
                          <span className="text-[13px] font-medium text-[#1F2430]/40 font-mono">validate.ts</span>
                          <button className="flex items-center gap-1.5 px-3 py-1.5 bg-[#EEF1F8] text-[#3E63F5] rounded-lg text-xs font-bold hover:bg-[#EAEAFE] transition-colors ring-1 ring-[#3E63F5]/10">
                            <Play className="w-3.5 h-3.5 fill-current" /> Run Code
                          </button>
                        </div>
                        <div className="flex-1 p-5 font-mono text-[14px] leading-relaxed text-[#1F2430]/80 flex gap-4 overflow-auto min-h-0">
                          <div className="text-[#1F2430]/20 text-right select-none flex flex-col shrink-0">
                            <span>1</span><span>2</span><span>3</span><span>4</span><span>5</span>
                          </div>
                          <div className="flex-1 whitespace-pre-wrap break-words min-w-0">
                            <span className="text-[#D97B94]">export function</span> <span className="text-[#3E63F5]">validateAddress</span>(address: Address) &#123;<br/>
                            &nbsp;&nbsp;<span className="text-[#1F2430]/40">// TODO: Implement validation logic</span><br/>
                            &nbsp;&nbsp;<span className="text-[#D97B94]">return</span> <span className="text-[#3E63F5]">true</span>;<br/>
                            &#125;
                          </div>
                        </div>
                      </div>

                      {/* Output Panel */}
                      <div className="h-32 shrink-0 bg-[#1A1D24] rounded-[1.5rem] shadow-[0_12px_32px_rgba(30,35,60,0.16)] ring-1 ring-white/10 p-5 font-mono text-[13px] flex flex-col overflow-y-auto">
                        <div className="text-white/40 text-[11px] font-bold mb-3 uppercase tracking-wider">Console Output</div>
                        <div className="flex items-center gap-2">
                          <span className="text-[#10B981] font-medium">Ready. Waiting for execution...</span>
                          <span className="w-1.5 h-3 bg-[#10B981] animate-pulse" />
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}

              </AnimatePresence>
            </div>

            {/* 4. Floating Object - Bottom Control Bar */}
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-40 w-[95%] md:w-auto flex justify-center pointer-events-none">
              <div className="flex items-center justify-center gap-1.5 md:gap-2.5 p-1.5 md:p-2.5 rounded-full shadow-[0_18px_40px_rgba(30,35,60,0.14),inset_0_1px_1px_rgba(255,255,255,0.9)] ring-1 ring-white/60 pointer-events-auto"
                   style={{ backgroundColor: "rgba(255,255,255,0.82)", backdropFilter: "blur(24px)" }}>
                
                <button 
                  onClick={() => setMicActive(!micActive)}
                  className={`group flex items-center gap-2 px-3 md:px-5 py-2.5 rounded-full transition-all duration-300 ease-out shadow-[0_2px_8px_rgba(30,35,60,0.04)] shrink-0 ${
                    micActive 
                      ? 'bg-[#EEF1F8] text-[#3E63F5] hover:bg-[#EAEAFE] ring-1 ring-[#3E63F5]/10' 
                      : 'bg-[#FFF0F4] text-[#E11D48] hover:bg-[#FFE4EC] ring-1 ring-[#E11D48]/10'
                  }`}
                >
                  <div className="relative">
                    <Mic className="w-4 h-4 md:w-5 md:h-5 relative z-10" />
                    {!micActive && (
                      <motion.div 
                        layoutId="slash"
                        className="absolute top-1/2 left-1/2 w-5 md:w-6 h-[2px] bg-current -translate-x-1/2 -translate-y-1/2 rotate-45 z-20" 
                      />
                    )}
                  </div>
                  <span className="font-semibold text-[13px] md:text-[14px] hidden sm:block">{micActive ? 'Mic is on' : 'Muted'}</span>
                </button>
                
                <div className="w-[1px] h-6 md:h-8 bg-[#1F2430]/[0.08] mx-0.5 md:mx-1" />
                
                <button className="p-2.5 md:p-3 rounded-full text-[#1F2430]/60 hover:text-[#1F2430] hover:bg-white/80 transition-all duration-300 relative group shadow-none hover:shadow-[0_2px_8px_rgba(30,35,60,0.04)] shrink-0">
                  <Pause className="w-4 h-4 md:w-5 md:h-5" />
                  <span className="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-[#1F2430] text-white text-xs font-semibold rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-[0_8px_16px_rgba(30,35,60,0.12)]">
                    Pause interview
                  </span>
                </button>
                
                <button className="p-2.5 md:p-3 rounded-full text-[#1F2430]/60 hover:text-[#1F2430] hover:bg-white/80 transition-all duration-300 relative group shadow-none hover:shadow-[0_2px_8px_rgba(30,35,60,0.04)] shrink-0">
                  <Keyboard className="w-4 h-4 md:w-5 md:h-5" />
                  <span className="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-[#1F2430] text-white text-xs font-semibold rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-[0_8px_16px_rgba(30,35,60,0.12)]">
                    Switch to text
                  </span>
                </button>

                <button className="p-2.5 md:p-3 rounded-full text-[#1F2430]/60 hover:text-[#1F2430] hover:bg-white/80 transition-all duration-300 relative group shadow-none hover:shadow-[0_2px_8px_rgba(30,35,60,0.04)] shrink-0">
                  <FileText className="w-4 h-4 md:w-5 md:h-5" />
                  <span className="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-[#1F2430] text-white text-xs font-semibold rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-[0_8px_16px_rgba(30,35,60,0.12)]">
                    Notes & Resources
                  </span>
                </button>
                
                <button className="p-2.5 md:p-3 rounded-full text-[#1F2430]/60 hover:text-[#1F2430] hover:bg-white/80 transition-all duration-300 relative group shadow-none hover:shadow-[0_2px_8px_rgba(30,35,60,0.04)] shrink-0">
                  <Video className="w-4 h-4 md:w-5 md:h-5" />
                  <span className="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-[#1F2430] text-white text-xs font-semibold rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-[0_8px_16px_rgba(30,35,60,0.12)]">
                    Camera settings
                  </span>
                </button>

                <div className="w-[1px] h-6 md:h-8 bg-[#1F2430]/[0.08] mx-0.5 md:mx-1" />
                
                <button className="flex items-center gap-2 px-4 py-2.5 md:px-5 md:py-3 rounded-full bg-[#1F2430] text-white hover:bg-black hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 shadow-[0_8px_20px_rgba(30,35,60,0.16),inset_0_1px_1px_rgba(255,255,255,0.2)] shrink-0">
                  <Phone className="w-4 h-4 fill-white" />
                  <span className="font-semibold text-[13px] md:text-[14px] hidden sm:block">End</span>
                </button>
              </div>
            </div>

            {/* 4. Floating Object - Camera Tile */}
            <div className="absolute bottom-8 right-8 z-40 group cursor-pointer">
              <div className="w-56 lg:w-64 aspect-[4/3] rounded-[1.5rem] overflow-hidden shadow-[0_18px_40px_rgba(30,35,60,0.14)] relative group-hover:-translate-y-1 transition-transform duration-500 bg-[#F7F5F1]">
                {/* Tiny glass reflection & darker edge */}
                <div className="absolute inset-0 rounded-[1.5rem] ring-1 ring-inset ring-white/60 shadow-[inset_0_2px_12px_rgba(0,0,0,0.06)] pointer-events-none z-20" />
                <div className="absolute inset-0 rounded-[1.5rem] ring-1 ring-[#1F2430]/10 pointer-events-none z-20" />
                
                <ImageWithFallback 
                  src="https://images.unsplash.com/photo-1738566495427-bb6427cfbab3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBjYW5kaWRhdGUlMjB2aWRlbyUyMGNhbGx8ZW58MXx8fHwxNzc2MTc3NjYwfDA&ixlib=rb-4.1.0&q=80&w=1080" 
                  alt="Candidate" 
                  className="w-full h-full object-cover z-0"
                />
                
                <div className="absolute inset-0 bg-gradient-to-t from-[#1F2430]/60 via-transparent to-transparent pointer-events-none z-10 opacity-80" />
                
                <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between z-20">
                  <span className="text-white text-[15px] font-medium drop-shadow-[0_2px_4px_rgba(0,0,0,0.4)]">You</span>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center backdrop-blur-md transition-colors shadow-[0_4px_12px_rgba(0,0,0,0.2),inset_0_1px_1px_rgba(255,255,255,0.3)] ring-1 ring-white/10 ${micActive ? 'bg-white/20 text-white' : 'bg-[#E11D48]/90 text-white shadow-[0_4px_16px_rgba(225,29,72,0.4)]'}`}>
                    {micActive ? <Mic className="w-4 h-4" /> : <Mic className="w-4 h-4 opacity-50" />}
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* 3. Primary Panel - Workspace Rail (Transcript + Context) */}
          <div 
            className="w-[320px] lg:w-[380px] shrink-0 rounded-[2rem] md:rounded-[2.5rem] flex flex-col relative overflow-hidden shadow-[0_12px_30px_rgba(60,70,110,0.08),inset_0_2px_20px_rgba(60,70,110,0.03)] ring-1 ring-white/80 ring-inset isolate min-h-0"
            style={{ background: "linear-gradient(180deg, #F3F4FB 0%, #EEF1F8 100%)" }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-7 py-7 shrink-0 z-20">
              <h3 className="font-[Manrope,sans-serif] font-bold text-[19px] text-[#1F2430] tracking-tight drop-shadow-[0_1px_2px_rgba(255,255,255,0.8)]">Session</h3>
              <button className="w-10 h-10 rounded-full flex items-center justify-center bg-white/70 text-[#1F2430]/60 hover:text-[#1F2430] hover:bg-white transition-all shadow-[0_4px_12px_rgba(30,35,60,0.06),inset_0_1px_1px_rgba(255,255,255,0.9)] ring-1 ring-[#1F2430]/[0.03] backdrop-blur-md">
                <MoreHorizontal className="w-5 h-5" />
              </button>
            </div>

            {/* Active Objective Context Card */}
            <div className="px-7 shrink-0 z-20 mb-2">
              <div className="p-4 rounded-[1.25rem] bg-white/70 shadow-[0_4px_12px_rgba(30,35,60,0.04),inset_0_1px_1px_rgba(255,255,255,0.9)] ring-1 ring-[#1F2430]/[0.03] backdrop-blur-xl relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-[#3E63F5] rounded-l-[1.25rem] opacity-80" />
                <div className="flex items-center gap-2 mb-2 text-[#3E63F5] text-[10px] font-bold uppercase tracking-wider pl-2">
                  <Target className="w-3.5 h-3.5" /> Current Objective
                </div>
                <p className="text-[14px] text-[#1F2430]/80 font-medium leading-[1.6] pl-2">
                  {activeMode === 'conversation' ? "Discuss address validation edge cases." : activeMode === 'whiteboard' ? "Diagram the order tracking data flow and address edge cases." : "Write a function to handle incoming address object validation."}
                </p>
              </div>
            </div>

            {/* Transcript Divider */}
            <div className="flex items-center gap-4 px-7 py-3 opacity-50 z-20 shrink-0">
              <div className="h-[1px] flex-1 bg-[#1F2430]/[0.1]" />
              <span className="text-[10px] font-bold text-[#1F2430]/60 uppercase tracking-widest">Transcript</span>
              <div className="h-[1px] flex-1 bg-[#1F2430]/[0.1]" />
            </div>

            {/* Messages Area - 5. Micro Objects (Bubbles) */}
            <div className="flex-1 overflow-y-auto flex flex-col gap-6 px-7 pr-4 scrollbar-hide pb-24 z-10 relative">
              {MOCK_TRANSCRIPT.map((msg, idx) => (
                <motion.div 
                  key={msg.id} 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: idx * 0.1 }}
                  className={`flex flex-col shrink-0 ${msg.speaker === 'candidate' ? 'items-end' : 'items-start'}`}
                >
                  <div className="flex items-center gap-2 mb-2 px-1">
                    <span className="text-[11px] font-bold text-[#1F2430]/50 uppercase tracking-wider">
                      {msg.speaker === 'candidate' ? 'You' : 'PlacedOn AI'}
                    </span>
                    <span className="text-[11px] font-semibold text-[#1F2430]/40 tabular-nums">{msg.time}</span>
                  </div>
                  <div 
                    className={`p-4 max-w-[94%] text-[14px] leading-[1.6] font-medium break-words shadow-[0_4px_12px_rgba(30,35,60,0.06),inset_0_1px_1px_rgba(255,255,255,0.8)] ring-1 ring-[#1F2430]/[0.03] backdrop-blur-xl ${
                      msg.speaker === 'candidate' 
                        ? 'bg-white/95 text-[#1F2430] rounded-[1.25rem] rounded-tr-sm' 
                        : 'bg-[#EAEAFE]/80 text-[#1F2430] rounded-[1.25rem] rounded-tl-sm ring-inset ring-white/60'
                    }`}
                  >
                    {msg.text}
                  </div>
                </motion.div>
              ))}
              
              {/* Active AI Indicator Bubble */}
              <AnimatePresence>
                {aiState !== 'listening' && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
                    className="flex flex-col items-start mt-1 shrink-0"
                  >
                    <div className="flex items-center gap-2 mb-2 px-1">
                      <span className="text-[11px] font-bold text-[#3E63F5] uppercase tracking-wider">
                        PlacedOn AI
                      </span>
                    </div>
                    <div className="px-4 py-3 bg-[#EAEAFE]/80 backdrop-blur-xl rounded-[1.25rem] rounded-tl-sm flex items-center justify-center min-h-[48px] min-w-[64px] shadow-[0_4px_12px_rgba(30,35,60,0.06),inset_0_1px_1px_rgba(255,255,255,0.8)] ring-1 ring-[#1F2430]/[0.03] ring-inset ring-white/60">
                      {aiState === 'thinking' ? (
                        <div className="flex gap-1.5">
                          <motion.div animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.2, delay: 0 }} className="w-2 h-2 rounded-full bg-[#3E63F5]/70" />
                          <motion.div animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.2, delay: 0.2 }} className="w-2 h-2 rounded-full bg-[#3E63F5]/70" />
                          <motion.div animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.2, delay: 0.4 }} className="w-2 h-2 rounded-full bg-[#3E63F5]/70" />
                        </div>
                      ) : (
                        <div className="flex items-center gap-[3px]">
                          <motion.div animate={{ height: [6, 14, 6] }} transition={{ repeat: Infinity, duration: 0.8, ease: "easeInOut" }} className="w-1.5 bg-[#3E63F5]/90 rounded-full" />
                          <motion.div animate={{ height: [6, 20, 6] }} transition={{ repeat: Infinity, duration: 0.8, delay: 0.15, ease: "easeInOut" }} className="w-1.5 bg-[#3E63F5]/90 rounded-full" />
                          <motion.div animate={{ height: [6, 10, 6] }} transition={{ repeat: Infinity, duration: 0.8, delay: 0.3, ease: "easeInOut" }} className="w-1.5 bg-[#3E63F5]/90 rounded-full" />
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            
            {/* Transcript Bottom Soft Fade */}
            <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#EEF1F8] via-[#EEF1F8]/90 to-transparent pointer-events-none z-20" />
          </div>
        </div>
      </div>
    </div>
  );
}

// Dimensional AI Artifact
function AIIndicator({ state }: { state: AIState }) {
  return (
    <div className="relative w-6 h-6 flex items-center justify-center shrink-0">
      {state === "listening" && (
        <>
          <motion.div
            animate={{ scale: [1, 1.8, 1], opacity: [0.2, 0, 0.2] }}
            transition={{ repeat: Infinity, duration: 2.5, ease: "easeInOut" }}
            className="absolute inset-0 rounded-full bg-[#3E63F5]"
          />
          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ repeat: Infinity, duration: 2.5, ease: "easeInOut" }}
            className="w-3 h-3 rounded-full bg-[#3E63F5] relative z-10 shadow-[0_0_8px_rgba(62,99,245,0.4),inset_0_1px_1px_rgba(255,255,255,0.4)]"
          />
        </>
      )}
      
      {state === "thinking" && (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
          className="w-5 h-5 rounded-full border-[2.5px] border-transparent border-t-[#D97B94] border-r-[#D97B94] border-b-[#D97B94]/20 border-l-[#D97B94]/20 shadow-[0_0_8px_rgba(217,123,148,0.2)]"
        />
      )}

      {state === "speaking" && (
        <div className="flex gap-[3px] items-center h-[18px]">
          <motion.div animate={{ height: ["25%", "85%", "25%"] }} transition={{ repeat: Infinity, duration: 1.2, ease: "easeInOut" }} className="w-[3px] bg-[#3E63F5] rounded-full shadow-[0_0_4px_rgba(62,99,245,0.3)]" />
          <motion.div animate={{ height: ["45%", "100%", "45%"] }} transition={{ repeat: Infinity, duration: 1.2, delay: 0.2, ease: "easeInOut" }} className="w-[3px] bg-[#3E63F5] rounded-full shadow-[0_0_4px_rgba(62,99,245,0.3)]" />
          <motion.div animate={{ height: ["30%", "65%", "30%"] }} transition={{ repeat: Infinity, duration: 1.2, delay: 0.4, ease: "easeInOut" }} className="w-[3px] bg-[#3E63F5] rounded-full shadow-[0_0_4px_rgba(62,99,245,0.3)]" />
        </div>
      )}
    </div>
  );
}
