import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { InterviewView } from './components/InterviewView';
import { IDEView } from './components/IDEView';
import { WhiteboardView } from './components/WhiteboardView';
import { MobileNav } from './components/MobileNav';
import {
  evaluateAnswer,
  generateQuestion,
  type CandidateProfile,
  type EvaluateAnswerResponse,
  type GenerateQuestionResponse,
  type JobProfile,
} from './lib/interviewApi';

type View = 'interview' | 'ide' | 'whiteboard';

interface Message {
  id: string;
  sender: 'AI Mentor' | 'You';
  time: string;
  text: string;
}

type SessionStatus = 'connecting' | 'ready' | 'thinking' | 'error';

const candidateProfile: CandidateProfile = {
  name: 'Alex',
  experience_years: 1,
  skills: ['python', 'prompt engineering', 'llm api basics', 'ml fundamentals'],
  projects: ['retrieval qa assistant', 'resume-screening prototype'],
  education: 'B.Tech in Computer Science',
};

const jobProfile: JobProfile = {
  role: 'Junior AI Developer',
  company: 'PlacedOn',
  level: 'junior',
  required_skills: ['python', 'prompt engineering', 'llm api integration'],
  preferred_skills: ['vector databases', 'evaluation basics'],
};

function formatClockTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}

function makeSessionId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}`;
}

function resolveViewForQuestion(question: GenerateQuestionResponse): View {
  if (question.type === 'system_design') {
    return 'whiteboard';
  }

  const haystack = [
    question.question,
    question.skill,
    question.strategy ?? '',
    question.plan_reason ?? '',
    ...(question.tags ?? []),
  ]
    .join(' ')
    .toLowerCase();

  const codingSignals = [
    'code',
    'coding',
    'programming',
    'implement',
    'algorithm',
    'function',
    'debug',
    'python',
    'java',
    'javascript',
    'leetcode',
  ];

  if (codingSignals.some(signal => haystack.includes(signal))) {
    return 'ide';
  }

  return 'interview';
}

export default function App() {
  const [currentView, setCurrentView] = useState<View>('interview');
  const [sessionId] = useState<string>(() => makeSessionId());
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<string>('');
  const [status, setStatus] = useState<SessionStatus>('connecting');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastEvaluation, setLastEvaluation] = useState<EvaluateAnswerResponse | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(true);
  const [timer, setTimer] = useState(764);

  useEffect(() => {
    const interval = setInterval(() => {
      setTimer(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const appendMessage = (sender: Message['sender'], text: string) => {
    setMessages(prev => [
      ...prev,
      {
        id: `${sender}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        sender,
        time: formatClockTime(new Date()),
        text,
      },
    ]);
  };

  const fetchNextQuestion = async () => {
    const nextQuestion = await generateQuestion({
      sessionId,
      candidate: candidateProfile,
      job: jobProfile,
    });
    setCurrentQuestion(nextQuestion.question);
    setCurrentView(resolveViewForQuestion(nextQuestion));
    appendMessage('AI Mentor', nextQuestion.question);
  };

  useEffect(() => {
    let cancelled = false;

    const bootstrap = async () => {
      try {
        setStatus('connecting');
        setErrorMessage(null);
        const firstQuestion = await generateQuestion({
          sessionId,
          candidate: candidateProfile,
          job: jobProfile,
        });

        if (cancelled) {
          return;
        }

        setCurrentQuestion(firstQuestion.question);
        setCurrentView(resolveViewForQuestion(firstQuestion));
        setMessages([
          {
            id: 'initial-ai-question',
            sender: 'AI Mentor',
            time: formatClockTime(new Date()),
            text: firstQuestion.question,
          },
        ]);
        setStatus('ready');
      } catch (error) {
        if (cancelled) {
          return;
        }
        setStatus('error');
        setErrorMessage(error instanceof Error ? error.message : 'Unable to connect to backend.');
      }
    };

    bootstrap();

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const handleSubmitAnswer = async (answer: string) => {
    const trimmed = answer.trim();
    if (!trimmed || status === 'connecting' || status === 'thinking') {
      return;
    }

    appendMessage('You', trimmed);
    setIsSpeaking(false);

    try {
      setStatus('thinking');
      setErrorMessage(null);

      if (currentQuestion) {
        const evaluation = await evaluateAnswer({
          sessionId,
          question: currentQuestion,
          answer: trimmed,
        });
        setLastEvaluation(evaluation);
      }

      await fetchNextQuestion();
      setStatus('ready');
    } catch (error) {
      setStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Could not process your answer.');
    }
  };

  const renderView = () => {
    switch (currentView) {
      case 'interview':
        return <InterviewView question={currentQuestion} status={status} />;
      case 'ide':
        return <IDEView question={currentQuestion} status={status} />;
      case 'whiteboard':
        return <WhiteboardView question={currentQuestion} status={status} />;
      default:
        return <InterviewView question={currentQuestion} status={status} />;
    }
  };

  return (
    <div className="h-screen bg-app-shell px-3 py-3 md:px-5 md:py-4 overflow-hidden">
      <div className="h-full w-full rounded-2xl border border-slate-200/80 bg-white/90 shadow-[0_18px_70px_rgba(15,23,42,0.12)] backdrop-blur-sm overflow-hidden flex flex-col">
        <Navbar currentView={currentView} onViewChange={setCurrentView} />

        <main className="flex-1 flex p-3 md:p-4 gap-4 overflow-hidden pb-24 md:pb-4 relative">
          <section className="flex-[4] flex flex-col overflow-hidden h-full relative">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentView}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2, ease: 'easeOut' }}
                className="flex-1 flex overflow-hidden"
              >
                {renderView()}
              </motion.div>
            </AnimatePresence>
          </section>

          <div className="hidden md:flex flex-1 h-full overflow-hidden min-w-[320px] max-w-[360px]">
            <Sidebar
              view={currentView}
              messages={messages}
              isSpeaking={isSpeaking}
              setIsSpeaking={setIsSpeaking}
              timer={timer}
              status={status}
              errorMessage={errorMessage}
              currentQuestion={currentQuestion}
              lastEvaluation={lastEvaluation}
              onSubmitAnswer={handleSubmitAnswer}
            />
          </div>
        </main>

        <MobileNav currentView={currentView} onViewChange={setCurrentView} />
      </div>

      <style
        dangerouslySetInnerHTML={{
          __html: `
          .custom-scrollbar::-webkit-scrollbar {
            width: 5px;
          }
          .custom-scrollbar::-webkit-scrollbar-track {
            background: transparent;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 10px;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
          }
        `,
        }}
      />
    </div>
  );
}
