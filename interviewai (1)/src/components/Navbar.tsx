import React, { useState } from 'react';
import { Settings, HelpCircle } from 'lucide-react';
import { cn } from '../lib/utils';
import { SettingsModal } from './SettingsModal';
import { HelpModal } from './HelpModal';

interface NavbarProps {
  currentView: 'interview' | 'ide' | 'whiteboard';
  onViewChange: (view: 'interview' | 'ide' | 'whiteboard') => void;
}

export const Navbar = ({ currentView, onViewChange }: NavbarProps) => {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  return (
    <>
      <header className="flex justify-between items-center w-full px-6 md:px-8 h-14 md:h-16 sticky top-0 z-50 bg-slate-50/90 border-b border-slate-200/80">
        <div className="flex items-center gap-6 md:gap-8">
          <span className="text-[28px] leading-none font-black tracking-tight text-[#2563eb]">
            PlacedOn
          </span>
          <nav className="hidden md:flex gap-6">
            {[
              { id: 'interview', label: 'Interview' },
              { id: 'ide', label: 'IDE' },
              { id: 'whiteboard', label: 'Whiteboard' }
            ].map((view) => (
              <button
                key={view.id}
                onClick={() => onViewChange(view.id as any)}
                className={cn(
                  'text-[15px] transition-all pb-1',
                  currentView === view.id 
                    ? 'text-[#1d4ed8] border-b-2 border-[#2563eb] font-semibold'
                    : 'text-slate-500 hover:text-[#2563eb]'
                )}
              >
                {view.label}
              </button>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3 md:gap-4">
          <button
            onClick={() => setSettingsOpen(true)}
            className="p-2 text-slate-500 hover:bg-slate-200/70 rounded-full transition-all"
            title="Settings"
          >
            <Settings size={16} />
          </button>
          <button
            onClick={() => setHelpOpen(true)}
            className="p-2 text-slate-500 hover:bg-slate-200/70 rounded-full transition-all"
            title="Help"
          >
            <HelpCircle size={16} />
          </button>
          <button className="bg-[#2563eb] text-white px-5 py-2 rounded-full font-semibold hover:bg-[#1d4ed8] transition-all shadow-md shadow-blue-200 text-sm">
            End Interview
          </button>
          <div className="w-9 h-9 rounded-full bg-slate-200 overflow-hidden border border-slate-200 shadow-sm ml-2">
            <img 
              src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&q=80&w=100&h=100" 
              alt="User Profile" 
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          </div>
        </div>
      </header>

      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
      <HelpModal open={helpOpen} onClose={() => setHelpOpen(false)} />
    </>
  );
};
