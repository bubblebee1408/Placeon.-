import { Outlet, useNavigate } from 'react-router';
import { Bell, Shield, Home, Briefcase, User, Settings } from 'lucide-react';
import Dock from './Dock';

export function DashboardLayout() {
  const navigate = useNavigate();

  const dockItems = [
    { icon: <Home size={22} strokeWidth={2.5} />, label: 'Home', onClick: () => navigate('/') },
    { icon: <Briefcase size={22} strokeWidth={2.5} />, label: 'Applications', onClick: () => navigate('/applications') },
    { icon: <User size={22} strokeWidth={2.5} />, label: 'Profile', onClick: () => navigate('/profile') },
    { icon: <Settings size={22} strokeWidth={2.5} />, label: 'Settings', onClick: () => navigate('/settings') },
  ];

  return (
    <div className="min-h-screen w-full bg-[#F3F2F0] relative overflow-hidden font-[Inter,sans-serif] selection:bg-[#3E63F5] selection:text-white">
      {/* Global CSS for floating animations and noise */}
      <style>{`
        @keyframes float-slow {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-10px) scale(1.02); }
        }
        @keyframes float-fast {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          50% { transform: translateY(-15px) rotate(2deg); }
        }
        @keyframes pulse-glow {
          0%, 100% { opacity: 0.6; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(1.1); }
        }
        @keyframes shimmer { 100% { transform: translateX(100%); } }
        
        .animate-float-slow { animation: float-slow 6s ease-in-out infinite; }
        .animate-float-fast { animation: float-fast 4s ease-in-out infinite; }
        .animate-pulse-glow { animation: pulse-glow 8s ease-in-out infinite; }
        .animate-shimmer { animation: shimmer 2s infinite; }
        
        .noise-overlay {
          position: absolute;
          inset: 0;
          opacity: 0.25;
          mix-blend-mode: overlay;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
          pointer-events: none;
          z-index: 1;
        }

        .dot-grid {
          position: absolute;
          inset: 0;
          background-size: 24px 24px;
          background-image: radial-gradient(circle at 1px 1px, rgba(31,36,48,0.08) 1px, transparent 0);
          pointer-events: none;
          z-index: 0;
        }

        .glass-card {
          background: rgba(255, 255, 255, 0.45);
          backdrop-filter: blur(40px);
          -webkit-backdrop-filter: blur(40px);
          border: 1px solid rgba(255, 255, 255, 0.7);
          box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.9), 0 12px 40px rgba(30, 35, 60, 0.04);
        }
        
        .glass-dark {
          background: rgba(30, 35, 48, 0.85);
          backdrop-filter: blur(40px);
          -webkit-backdrop-filter: blur(40px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1), 0 20px 50px rgba(0, 0, 0, 0.2);
        }
      `}</style>

      {/* Ambient Background Washes */}
      <div className="absolute top-[-15%] left-[-10%] w-[60vw] h-[60vw] bg-[#E3E8F8] rounded-full mix-blend-multiply blur-[120px] opacity-70 pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] bg-[#F4EBE3] rounded-full mix-blend-multiply blur-[120px] opacity-60 pointer-events-none" />
      <div className="absolute top-[20%] right-[15%] w-[40vw] h-[40vw] bg-[#E9E4F5] rounded-full mix-blend-multiply blur-[100px] opacity-50 pointer-events-none" />
      
      {/* Texture Layers */}
      <div className="dot-grid pointer-events-none" />
      <div className="noise-overlay pointer-events-none" />

      {/* Main Content Wrapper */}
      <div className="relative z-10 w-full max-w-[1400px] mx-auto px-6 py-8 md:px-12 md:py-12 pb-32">
        
        {/* Navigation & Header */}
        <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div className="flex items-center gap-5">
            <div className="relative group cursor-pointer">
              <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-[#3E63F5] to-[#8C9EFF] p-[2px] shadow-[0_8px_24px_rgba(62,99,245,0.25)] transition-transform duration-300 group-hover:scale-105">
                <div className="w-full h-full rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-white">
                  <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=faces&q=80" alt="Profile" className="w-full h-full object-cover" />
                </div>
              </div>
              <div className="absolute bottom-0 right-0 w-4 h-4 bg-[#10B981] rounded-full border-[3px] border-[#F3F2F0] shadow-sm flex items-center justify-center">
                 <div className="w-1 h-1 bg-white rounded-full animate-pulse" />
              </div>
            </div>
            <div>
              <p className="text-[14px] font-medium text-[#1F2430]/50 mb-1 flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-[#3E63F5]" />
                Profile Verified • 2h ago
              </p>
              <h1 className="font-[Manrope,sans-serif] text-[28px] font-bold text-[#1F2430] tracking-tight leading-none">
                Alex Chen
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button className="w-11 h-11 rounded-[1.25rem] glass-card flex items-center justify-center text-[#1F2430]/60 hover:text-[#1F2430] hover:bg-white/80 transition-all hover:-translate-y-0.5 relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-3 right-3 w-2 h-2 bg-[#3E63F5] rounded-full shadow-[0_0_8px_rgba(62,99,245,0.8)] animate-pulse" />
            </button>
            <button className="w-11 h-11 rounded-[1.25rem] glass-card flex items-center justify-center text-[#1F2430]/60 hover:text-[#1F2430] hover:bg-white/80 transition-all hover:-translate-y-0.5 relative" onClick={() => navigate('/settings')}>
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Dynamic Outlet Content */}
        <Outlet />

      </div>

      {/* Floating Bottom Dock */}
      <Dock 
        items={dockItems} 
        panelHeight={68} 
        baseItemSize={50} 
        magnification={70} 
      />
    </div>
  );
}