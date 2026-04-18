import { User, Shield, Activity, Check, AlertCircle, Play, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router';

export function ProfileScreen() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-6 animate-[pulse-glow_0.5s_ease-out]">
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-[Manrope,sans-serif] text-[28px] font-bold text-[#1F2430] tracking-tight">
          AI Verified Profile
        </h2>
        <div className="px-4 py-1.5 rounded-full bg-[#10B981]/10 text-[#10B981] text-[13px] font-bold uppercase tracking-wider flex items-center gap-1.5 shadow-sm border border-[#10B981]/20">
          <Shield className="w-4 h-4" />
          Verified Identity
        </div>
      </div>

      <div className="relative overflow-hidden rounded-[2.5rem] glass-dark p-8 md:p-12 flex flex-col group min-h-[500px]">
        {/* Dark Mode Glowing Orbs inside the card */}
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-tr from-[#3E63F5] to-[#FF007A] rounded-full blur-[100px] opacity-20 pointer-events-none" />
        <div className="absolute bottom-[-20%] left-[-10%] w-[350px] h-[350px] bg-gradient-to-tr from-[#10B981] to-[#3E63F5] rounded-full blur-[90px] opacity-10 pointer-events-none" />
        
        {/* Top breaking badge */}
        <div className="absolute top-0 right-12 px-5 py-2 rounded-b-xl bg-[#3E63F5] text-white text-[13px] font-bold tracking-wide uppercase shadow-[0_8px_16px_rgba(62,99,245,0.4)] flex items-center gap-2 z-20">
          <Sparkles className="w-4 h-4" /> Top 5% Developer
        </div>
        
        <div className="relative z-10 flex items-center justify-between mb-12">
          <div>
            <h3 className="font-[Manrope,sans-serif] text-[28px] font-bold text-white mb-2">Alex Chen</h3>
            <p className="text-[16px] font-medium text-white/50 flex items-center gap-1.5">
              Frontend Architecture • Next.js • React
            </p>
          </div>
          <div className="w-20 h-20 rounded-full border-[3px] border-white/20 bg-white/5 backdrop-blur-xl flex items-center justify-center shadow-inner overflow-hidden">
            <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop&crop=faces&q=80" alt="Profile" className="w-full h-full object-cover opacity-90" />
          </div>
        </div>

        {/* Profile Stats */}
        <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-4 mb-12 flex-1">
          <div className="flex flex-col p-5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md gap-3">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-[#3E63F5]/20 flex items-center justify-center text-[#8C9EFF]">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <span className="block text-[15px] font-bold text-white">Frontend Dev</span>
                <span className="block text-[12px] text-white/40">Assessed 2h ago</span>
              </div>
            </div>
            <div className="w-full h-2 rounded-full bg-white/10 overflow-hidden"><div className="w-[98%] h-full bg-[#8C9EFF] rounded-full" /></div>
            <div className="flex justify-between items-center text-[13px] font-bold text-[#8C9EFF]">
              <span>Expert Tier</span>
              <span>98%</span>
            </div>
          </div>
          
          <div className="flex flex-col p-5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md gap-3">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-[#10B981]/20 flex items-center justify-center text-[#34D399]">
                <Check className="w-5 h-5" />
              </div>
              <div>
                <span className="block text-[15px] font-bold text-white">System Design</span>
                <span className="block text-[12px] text-white/40">Assessed 2h ago</span>
              </div>
            </div>
            <div className="w-full h-2 rounded-full bg-white/10 overflow-hidden"><div className="w-[85%] h-full bg-[#34D399] rounded-full" /></div>
            <div className="flex justify-between items-center text-[13px] font-bold text-[#34D399]">
              <span>Strong Tier</span>
              <span>85%</span>
            </div>
          </div>

          <div className="md:col-span-2 flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-[#D4183D]/30 backdrop-blur-md relative overflow-hidden group/weakness cursor-pointer hover:bg-white/10 transition-colors" onClick={() => navigate('/pre-interview')}>
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#D4183D]/10 to-transparent translate-x-[-100%] group-hover/weakness:animate-[shimmer_2s_infinite]" />
            <div className="relative z-10 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-[#D4183D]/20 flex items-center justify-center text-[#F43F5E]">
                <AlertCircle className="w-6 h-6" />
              </div>
              <div>
                <span className="block text-[16px] font-bold text-white mb-1">Team Play</span>
                <span className="block text-[13px] font-medium text-white/50">Needs verification to unlock top tiers.</span>
              </div>
            </div>
            <div className="relative z-10 flex items-center gap-4">
              <span className="hidden md:block text-[14px] font-bold text-[#F43F5E]">Developing (45%)</span>
              <button className="px-5 py-2.5 rounded-xl bg-white text-[#1F2430] font-bold text-[13px] hover:bg-[#F3F2F0] hover:-translate-y-0.5 transition-all flex items-center gap-2">
                <Play className="w-3.5 h-3.5 fill-current" /> Challenge
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}