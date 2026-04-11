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
  strategy?: 'intro' | 'help' | 'probe' | 'challenge' | string;
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
const DEFAULT_TIMEOUT_MS = 15000;

function getApiBaseUrl(): string {
  const fromEnv = import.meta.env.VITE_API_BASE_URL;
  return (fromEnv && fromEnv.trim()) || DEFAULT_BASE_URL;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function isGenerateQuestionResponse(value: unknown): value is GenerateQuestionResponse {
  if (!isObject(value)) {
    return false;
  }
  const difficulty = value.difficulty;
  const kind = value.type;
  return (
    typeof value.question === 'string' &&
    typeof value.skill === 'string' &&
    (difficulty === 'easy' || difficulty === 'medium' || difficulty === 'hard') &&
    (kind === 'conceptual' || kind === 'system_design' || kind === 'behavioral')
  );
}

function isEvaluateAnswerResponse(value: unknown): value is EvaluateAnswerResponse {
  if (!isObject(value)) {
    return false;
  }
  return (
    typeof value.score === 'number' &&
    typeof value.confidence === 'number' &&
    Array.isArray(value.strengths) &&
    Array.isArray(value.weaknesses) &&
    Array.isArray(value.missing_concepts)
  );
}

async function requestJson<T>(
  path: string,
  body: unknown,
  isValid: (value: unknown) => value is T,
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    signal: controller.signal,
    body: JSON.stringify(body),
  }).finally(() => {
    window.clearTimeout(timeoutId);
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Request failed (${response.status}): ${detail || response.statusText}`);
  }

  const payload: unknown = await response.json();
  if (!isValid(payload)) {
    throw new Error(`Invalid response payload for ${path}`);
  }

  return payload;
}

export async function generateQuestion(params: {
  sessionId: string;
  candidate: CandidateProfile;
  job: JobProfile;
}): Promise<GenerateQuestionResponse> {
  return requestJson<GenerateQuestionResponse>(
    '/generate-question',
    {
      session_id: params.sessionId,
      candidate: params.candidate,
      job: params.job,
    },
    isGenerateQuestionResponse,
  );
}

export async function evaluateAnswer(params: {
  sessionId: string;
  question: string;
  answer: string;
}): Promise<EvaluateAnswerResponse> {
  return requestJson<EvaluateAnswerResponse>(
    '/evaluate-answer',
    {
      session_id: params.sessionId,
      question: params.question,
      answer: params.answer,
    },
    isEvaluateAnswerResponse,
  );
}
