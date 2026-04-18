import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Video, Mic, Wifi, Shield, ArrowRight, Keyboard, Pencil, Eye, RefreshCw, CheckCircle2, Sparkles, MessageSquare } from 'lucide-react';

export function PreInterviewScreen() {
  const navigate = useNavigate();
  const [consentAi, setConsentAi] = useState(false);
  const [consentAnalysis, setConsentAnalysis] = useState(false);
  const [consentProfile, setConsentProfile] = useState(false);

  const allConsented = consentAi && consentAnalysis && consentProfile;

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 sm:p-8 bg-[#F9F8F6] relative overflow-hidden font-[Inter,sans-serif]">
      {/* Soft Ambient Background Washes */}
      <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-[#EEF1F8] rounded-full mix-blend-multiply filter blur-[100px] opacity-70" />
      <div className="absolute bottom-[-10%] right-[-5%] w-[50%] h-[50%] bg-[#F3EFEA] rounded-full mix-blend-multiply filter blur-[100px] opacity-60" />
      <div className="absolute top-[20%] right-[10%] w-[30%] h-[30%] bg-[#E6EAF5] rounded-full mix-blend-multiply filter blur-[100px] opacity-40" />
      
      {/* App Shell */}
      <div className="w-full max-w-[1440px] h-auto md:h-[90vh] md:min-h-[700px] md:max-h-[940px] bg-white/70 backdrop-blur-2xl rounded-[2.5rem] shadow-[0_24px_80px_rgba(30,35,60,0.06),inset_0_2px_4px_rgba(255,255,255,0.9)] ring-1 ring-[#1F2430]/[0.04] flex flex-col md:flex-row overflow-hidden relative z-10">
        
        {/* Left Column: Content & Process */}
        <div className="w-full md:w-[60%] lg:w-[65%] md:h-full md:overflow-y-auto px-6 py-10 md:px-16 md:py-16 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-[#1F2430]/10 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-[#1F2430]/20 flex flex-col relative z-20">
          
          {/* Header */}
          <header className="flex items-center justify-between mb-20 shrink-0">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-[#3E63F5] to-[#7190FF] shadow-[0_4px_12px_rgba(62,99,245,0.2)] flex items-center justify-center shrink-0">
                <Sparkles className="w-4 h-4 text-white opacity-90" />
              </div>
              <div>
                <h2 className="font-[Manrope,sans-serif] font-bold text-[#1F2430] text-[17px] tracking-tight">PlacedOn</h2>
                <div className="flex items-center gap-2 text-[13px] font-medium text-[#1F2430]/50">
                  <span>Product Manager</span>
                  <div className="w-1 h-1 rounded-full bg-[#1F2430]/20" />
                  <span>Round 1: Technical & Behavioral</span>
                </div>
              </div>
            </div>
            
            <div className="hidden lg:flex items-center gap-3 px-4 py-2.5 bg-white/60 rounded-full ring-1 ring-[#1F2430]/[0.04] shadow-[0_2px_8px_rgba(30,35,60,0.02)]">
              <div className="flex items-center gap-1.5 text-[12px] font-semibold text-[#1F2430]/60">
                <RefreshCw className="w-3.5 h-3.5" />
                AI interview
              </div>
              <div className="w-[1px] h-3 bg-[#1F2430]/10" />
              <div className="text-[12px] font-semibold text-[#1F2430]/60">~30 min</div>
              <div className="w-[1px] h-3 bg-[#1F2430]/10" />
              <div className="flex items-center gap-1.5 text-[12px] font-semibold text-[#10B981]">
                <Shield className="w-3.5 h-3.5" />
                Secure & private
              </div>
            </div>
          </header>

          {/* Hero Section */}
          <div className="max-w-[600px] shrink-0 mb-auto">
            <h1 className="font-[Manrope,sans-serif] text-4xl md:text-[46px] leading-[1.1] font-bold text-[#1F2430] tracking-tight mb-6">
              Before we begin
            </h1>
            <p className="text-[17px] md:text-[18px] leading-[1.6] text-[#1F2430]/70 font-medium mb-16 text-balance">
              You're about to start a 30-minute AI-led interview with PlacedOn.<br/><br/>
              This is a conversation, not a test. There are no trick questions or perfect answers. We're here to understand how you think, communicate, and approach problems.
            </p>

            {/* What to expect */}
            <div className="mb-14">
              <h3 className="font-[Manrope,sans-serif] text-[13px] font-bold text-[#1F2430]/40 mb-6 uppercase tracking-widest">What to expect</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                {[
                  { title: "Warm-up", desc: "A short opening to help you settle in." },
                  { title: "Situational questions", desc: "You'll talk through how you would approach realistic problems." },
                  { title: "Deeper follow-ups", desc: "The interview may go deeper where your thinking shows the strongest signal." },
                  { title: "Profile review", desc: "After the interview, you'll be able to review the profile created from the conversation." }
                ].map((step, idx) => (
                  <div key={idx} className="p-6 rounded-[1.5rem] bg-white/60 border border-[#1F2430]/[0.04] shadow-[0_4px_16px_rgba(30,35,60,0.02)] transition-colors hover:bg-white/80 flex flex-col gap-4">
                    <div className="w-9 h-9 rounded-full bg-[#EEF1F8] text-[#3E63F5] flex items-center justify-center text-[14px] font-bold shadow-[inset_0_1px_2px_rgba(255,255,255,0.8)]">
                      {idx + 1}
                    </div>
                    <div>
                      <h4 className="font-[Manrope,sans-serif] font-bold text-[#1F2430] text-[15px] mb-1.5">{step.title}</h4>
                      <p className="text-[14px] text-[#1F2430]/60 leading-[1.5]">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* How your information is used */}
            <div className="p-7 md:p-8 rounded-[1.75rem] bg-gradient-to-b from-[#F9F8F6] to-white/50 border border-[#1F2430]/[0.04] shadow-[0_4px_24px_rgba(30,35,60,0.02)]">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-[#F3EFEA] rounded-xl text-[#8B7355]">
                  <Eye className="w-5 h-5" />
                </div>
                <h3 className="font-[Manrope,sans-serif] text-[17px] font-bold text-[#1F2430] tracking-tight">How your information is used</h3>
              </div>
              <ul className="space-y-4">
                {[
                  "Your transcript is used to generate your interview profile",
                  "Employers can view your profile, not the raw transcript",
                  "You'll be able to review your profile and flag anything that feels inaccurate",
                  "Your information is handled securely"
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3.5">
                    <div className="mt-2 w-1.5 h-1.5 rounded-full bg-[#3E63F5]/40 shrink-0 shadow-[0_0_4px_rgba(62,99,245,0.2)]" />
                    <span className="text-[15px] text-[#1F2430]/70 leading-[1.4] font-medium">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="h-8" />
          </div>
        </div>

        {/* Right Column: Readiness Panel */}
        <div className="w-full md:w-[40%] lg:w-[35%] md:h-full bg-white/95 md:border-l border-[#1F2430]/[0.04] shadow-[[-20px_0_40px_rgba(30,35,60,0.02)]] flex flex-col relative z-30 border-t md:border-t-0">
          <div className="flex-1 px-6 py-10 md:px-12 md:py-12 flex flex-col">
            
            <div className="mb-10">
              <h2 className="font-[Manrope,sans-serif] text-[24px] font-bold text-[#1F2430] mb-2.5 tracking-tight">You're ready to begin</h2>
              <p className="text-[14px] text-[#1F2430]/60 font-medium leading-relaxed">Everything looks good. You can still adjust your setup before starting.</p>
            </div>

            {/* Readiness Checks */}
            <div className="flex flex-col gap-3 mb-10">
              {/* System & Network */}
              <div className="group flex items-center justify-between p-4 rounded-2xl bg-[#F8F9FC]/70 border border-[#EEF1F8]/60 transition-all hover:bg-[#F3F5FA]">
                <div className="flex items-center gap-4">
                  <div className="flex -space-x-2.5">
                    <div className="w-8 h-8 rounded-full bg-white shadow-[0_2px_8px_rgba(30,35,60,0.06)] ring-2 ring-[#F8F9FC] group-hover:ring-[#F3F5FA] transition-colors flex items-center justify-center text-[#1F2430]/50 relative z-30"><Video className="w-3.5 h-3.5" /></div>
                    <div className="w-8 h-8 rounded-full bg-white shadow-[0_2px_8px_rgba(30,35,60,0.06)] ring-2 ring-[#F8F9FC] group-hover:ring-[#F3F5FA] transition-colors flex items-center justify-center text-[#1F2430]/50 relative z-20"><Mic className="w-3.5 h-3.5" /></div>
                    <div className="w-8 h-8 rounded-full bg-white shadow-[0_2px_8px_rgba(30,35,60,0.06)] ring-2 ring-[#F8F9FC] group-hover:ring-[#F3F5FA] transition-colors flex items-center justify-center text-[#1F2430]/50 relative z-10"><Wifi className="w-3.5 h-3.5" /></div>
                  </div>
                  <div className="flex flex-col gap-0.5">
                    <span className="text-[14px] font-semibold text-[#1F2430]/80 leading-none">System & Network</span>
                    <span className="text-[12px] font-medium text-[#1F2430]/50 leading-none">Camera, mic & connection ready</span>
                  </div>
                </div>
                <CheckCircle2 className="w-5 h-5 text-[#10B981] drop-shadow-[0_2px_4px_rgba(16,185,129,0.2)] shrink-0" />
              </div>

              {/* Workspace & Tools */}
              <div className="group flex items-center justify-between p-4 rounded-2xl bg-[#F8F9FC]/70 border border-[#EEF1F8]/60 transition-all hover:bg-[#F3F5FA]">
                <div className="flex items-center gap-4">
                  <div className="flex -space-x-2.5">
                    <div className="w-8 h-8 rounded-full bg-white shadow-[0_2px_8px_rgba(30,35,60,0.06)] ring-2 ring-[#F8F9FC] group-hover:ring-[#F3F5FA] transition-colors flex items-center justify-center text-[#1F2430]/50 relative z-30"><Shield className="w-3.5 h-3.5" /></div>
                    <div className="w-8 h-8 rounded-full bg-white shadow-[0_2px_8px_rgba(30,35,60,0.06)] ring-2 ring-[#F8F9FC] group-hover:ring-[#F3F5FA] transition-colors flex items-center justify-center text-[#1F2430]/50 relative z-20"><Pencil className="w-3.5 h-3.5" /></div>
                    <div className="w-8 h-8 rounded-full bg-white shadow-[0_2px_8px_rgba(30,35,60,0.06)] ring-2 ring-[#F8F9FC] group-hover:ring-[#F3F5FA] transition-colors flex items-center justify-center text-[#1F2430]/50 relative z-10"><MessageSquare className="w-3.5 h-3.5" /></div>
                  </div>
                  <div className="flex flex-col gap-0.5">
                    <span className="text-[14px] font-semibold text-[#1F2430]/80 leading-none">Workspace Tools</span>
                    <span className="text-[12px] font-medium text-[#1F2430]/50 leading-none">Permissions & tools available</span>
                  </div>
                </div>
                <CheckCircle2 className="w-5 h-5 text-[#10B981] drop-shadow-[0_2px_4px_rgba(16,185,129,0.2)] shrink-0" />
              </div>
            </div>

            {/* Consents */}
            <div className="flex flex-col gap-5 mt-auto pt-4">
              <ConsentItem 
                checked={consentAi} 
                onChange={() => setConsentAi(!consentAi)} 
                label="I understand this is an AI interview" 
              />
              <ConsentItem 
                checked={consentAnalysis} 
                onChange={() => setConsentAnalysis(!consentAnalysis)} 
                label="I consent to transcript analysis for profile generation" 
              />
              <ConsentItem 
                checked={consentProfile} 
                onChange={() => setConsentProfile(!consentProfile)} 
                label="I understand employers will see my profile, not the raw transcript" 
              />
            </div>

          </div>

          {/* CTA Footer (Fixed) */}
          <div className="p-8 md:px-12 md:py-8 bg-white border-t border-[#1F2430]/[0.04] shrink-0 shadow-[0_-8px_32px_rgba(30,35,60,0.02)]">
            <button 
              onClick={() => navigate('/interview')}
              disabled={!allConsented}
              className={`w-full py-4 rounded-2xl flex items-center justify-center gap-2 font-bold text-[16px] transition-all duration-300 ${
                allConsented 
                  ? 'bg-[#3E63F5] text-white hover:bg-[#2A44B0] hover:scale-[1.01] active:scale-[0.99] shadow-[0_8px_24px_rgba(62,99,245,0.24),inset_0_1px_1px_rgba(255,255,255,0.2)] cursor-pointer' 
                  : 'bg-[#EEF1F8] text-[#1F2430]/30 shadow-none cursor-not-allowed'
              }`}
            >
              Start interview
              <ArrowRight className="w-4 h-4" />
            </button>
            
            <div className="mt-6 flex items-center justify-center gap-4 text-[14px] font-semibold">
              <button className="text-[#1F2430]/60 hover:text-[#1F2430] transition-colors">Switch to text</button>
              <div className="w-1 h-1 rounded-full bg-[#1F2430]/10" />
              <button className="text-[#1F2430]/60 hover:text-[#1F2430] transition-colors">Resume later</button>
            </div>
            
            <p className="text-center text-[12px] text-[#1F2430]/40 mt-5 font-medium flex items-center justify-center gap-1.5">
              <Shield className="w-3 h-3" />
              You can pause or switch formats later if needed.
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}

function ConsentItem({ checked, onChange, label }: { checked: boolean, onChange: () => void, label: string }) {
  return (
    <label className="flex items-start gap-3.5 cursor-pointer group">
      <div className="relative flex items-center justify-center mt-[2px] shrink-0">
        <input 
          type="checkbox" 
          className="peer sr-only" 
          checked={checked}
          onChange={onChange}
        />
        <div className={`w-[22px] h-[22px] rounded-lg border transition-all duration-200 flex items-center justify-center ${
          checked 
            ? 'bg-[#3E63F5] border-[#3E63F5] text-white shadow-[0_4px_12px_rgba(62,99,245,0.3)]' 
            : 'bg-white border-[#1F2430]/20 text-transparent group-hover:border-[#3E63F5]/50 shadow-sm'
        }`}>
          <CheckCircle2 className="w-4 h-4" strokeWidth={2.5} />
        </div>
      </div>
      <span className={`text-[14px] leading-[1.5] font-medium transition-colors duration-200 ${checked ? 'text-[#1F2430]' : 'text-[#1F2430]/60 group-hover:text-[#1F2430]/80'}`}>
        {label}
      </span>
    </label>
  );
}
