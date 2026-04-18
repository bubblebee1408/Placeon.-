import { Briefcase, ChevronRight, Star, ArrowUpRight } from 'lucide-react';

export function ApplicationsScreen() {
  const activeApps = [
    { company: "OpenAI", role: "Frontend AI Integration", status: "Reviewing Profile", dotColor: "bg-[#F59E0B]", icon: "O", color: "bg-[#10A37F] text-white" },
    { company: "Linear", role: "Product Engineer", status: "Interviewing", dotColor: "bg-[#3E63F5]", icon: "L", color: "bg-[#5E6AD2] text-white" },
    { company: "Stripe", role: "Frontend Engineer", status: "Waiting on Challenge", dotColor: "bg-[#D4183D]", icon: "S", color: "bg-[#635BFF] text-white" },
  ];

  return (
    <div className="flex flex-col gap-6 animate-[pulse-glow_0.5s_ease-out]">
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-[Manrope,sans-serif] text-[28px] font-bold text-[#1F2430] tracking-tight">
          Your Pipeline
        </h2>
      </div>

      <div className="rounded-[2.5rem] glass-card p-8">
        <div className="flex items-center justify-between mb-8">
          <h3 className="font-[Manrope,sans-serif] text-[20px] font-bold text-[#1F2430]">Active Applications</h3>
        </div>

        <div className="flex flex-col gap-4">
          {activeApps.map((app, i) => (
            <div key={i} className="group flex items-center justify-between p-4 rounded-2xl bg-white/50 border border-white/60 shadow-[0_2px_8px_rgba(30,35,60,0.01)] hover:bg-white/80 transition-all cursor-pointer hover:shadow-[0_8px_24px_rgba(30,35,60,0.04)] hover:-translate-y-0.5">
              <div className="flex items-center gap-4">
                <div className={`w-14 h-14 rounded-xl ${app.color} shadow-sm flex items-center justify-center text-[20px] font-bold font-[Manrope,sans-serif]`}>
                  {app.icon}
                </div>
                <div>
                  <h4 className="text-[16px] font-bold text-[#1F2430] leading-tight mb-1">{app.company}</h4>
                  <p className="text-[14px] font-medium text-[#1F2430]/60">{app.role}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/60 border border-white shadow-sm">
                  <div className={`w-2 h-2 rounded-full ${app.dotColor} shadow-sm animate-pulse`} />
                  <span className="text-[13px] font-bold text-[#1F2430]/80">{app.status}</span>
                </div>
                <div className="w-10 h-10 rounded-full bg-white shadow-sm flex items-center justify-center text-[#1F2430]/40 group-hover:text-[#1F2430] group-hover:bg-[#F3F2F0] transition-colors">
                  <ChevronRight className="w-5 h-5" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-[2.5rem] glass-card p-8 border border-[#10B981]/20 bg-gradient-to-r from-white/40 to-[#10B981]/5 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-1/3 h-full bg-gradient-to-l from-[#10B981]/10 to-transparent pointer-events-none" />
        <div className="flex items-center justify-between mb-6 relative z-10">
          <h3 className="font-[Manrope,sans-serif] text-[20px] font-bold text-[#1F2430]">Offers Received</h3>
        </div>
        
        <div className="group flex items-center justify-between p-5 rounded-2xl bg-gradient-to-r from-[#10B981]/10 to-transparent border border-[#10B981]/30 shadow-[0_4px_12px_rgba(16,185,129,0.08)] hover:bg-[#10B981]/20 transition-all cursor-pointer relative z-10 hover:-translate-y-0.5">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-[#10B981] shadow-[0_4px_16px_rgba(16,185,129,0.3)] flex items-center justify-center text-white">
              <Star className="w-6 h-6 fill-current" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h4 className="text-[16px] font-bold text-[#1F2430] leading-tight">Vercel</h4>
                <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-[#10B981] text-white uppercase tracking-wider">Active Offer</span>
              </div>
              <p className="text-[14px] font-medium text-[#1F2430]/60">Design Engineer • Respond by Friday</p>
            </div>
          </div>
          <div className="w-10 h-10 rounded-full bg-white shadow-sm flex items-center justify-center text-[#10B981] group-hover:bg-[#10B981] group-hover:text-white transition-colors">
            <ArrowUpRight className="w-5 h-5" />
          </div>
        </div>
      </div>
    </div>
  );
}