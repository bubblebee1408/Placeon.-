export interface CandidateProfile {
  name: string;
  experience_years: number;
  skills: string[];
  projects: string[];
  education: string;
}

export interface JobProfile {
  role: string;
  company: string;
  level: 'intern' | 'junior' | 'mid' | 'senior';
  required_skills: string[];
  preferred_skills: string[];
}

export interface GenerateQuestionResponse {
  question: string;
  skill: string;
  difficulty: 'easy' | 'medium' | 'hard';
  type: 'conceptual' | 'system_design' | 'behavioral';
  strategy?: string;
  plan_reason?: string;
  tone?: string;
  round?: number;
  tags?: string[];
}

export interface EvaluateAnswerResponse {
  score: number;
  confidence: number;
  strengths: string[];
  weaknesses: string[];
  missing_concepts: string[];
  next_strategy?: string | null;
  current_skill?: string | null;
}

const DEFAULT_BASE_URL = 'http://127.0.0.1:8000';

function getApiBaseUrl(): string {
  const fromEnv = import.meta.env.VITE_API_BASE_URL;
  return (fromEnv && fromEnv.trim()) || DEFAULT_BASE_URL;
}

async function requestJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Request failed (${response.status}): ${detail || response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export async function generateQuestion(params: {
  sessionId: string;
  candidate: CandidateProfile;
  job: JobProfile;
}): Promise<GenerateQuestionResponse> {
  return requestJson<GenerateQuestionResponse>('/generate-question', {
    session_id: params.sessionId,
    candidate: params.candidate,
    job: params.job,
  });
}

export async function evaluateAnswer(params: {
  sessionId: string;
  question: string;
  answer: string;
}): Promise<EvaluateAnswerResponse> {
  return requestJson<EvaluateAnswerResponse>('/evaluate-answer', {
    session_id: params.sessionId,
    question: params.question,
    answer: params.answer,
  });
}
