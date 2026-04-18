import { Bell, Shield, Key, Eye, Monitor, LogOut } from 'lucide-react';

export function SettingsScreen() {
  const settingGroups = [
    {
      title: "Account",
      items: [
        { icon: <Shield className="w-5 h-5 text-[#1F2430]/70" />, label: "Security & Privacy", desc: "Manage your verification data" },
        { icon: <Key className="w-5 h-5 text-[#1F2430]/70" />, label: "Password", desc: "Update your credentials" },
      ]
    },
    {
      title: "Preferences",
      items: [
        { icon: <Bell className="w-5 h-5 text-[#1F2430]/70" />, label: "Notifications", desc: "Push, email, and match alerts" },
        { icon: <Monitor className="w-5 h-5 text-[#1F2430]/70" />, label: "Appearance", desc: "Dark mode, themes, accessibility" },
        { icon: <Eye className="w-5 h-5 text-[#1F2430]/70" />, label: "Profile Visibility", desc: "Who can see your verified stats" },
      ]
    }
  ];

  return (
    <div className="flex flex-col gap-6 animate-[pulse-glow_0.5s_ease-out]">
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-[Manrope,sans-serif] text-[28px] font-bold text-[#1F2430] tracking-tight">
          Settings
        </h2>
      </div>

      <div className="flex flex-col gap-8">
        {settingGroups.map((group, i) => (
          <div key={i} className="flex flex-col gap-4">
            <h3 className="font-[Manrope,sans-serif] text-[18px] font-bold text-[#1F2430]/80 px-2">{group.title}</h3>
            <div className="rounded-[2rem] glass-card p-2 flex flex-col overflow-hidden">
              {group.items.map((item, j) => (
                <button key={j} className={`group flex items-center justify-between p-5 rounded-2xl bg-transparent hover:bg-white/60 transition-all cursor-pointer border border-transparent hover:border-white/80 hover:shadow-sm text-left`}>
                  <div className="flex items-center gap-5">
                    <div className="w-12 h-12 rounded-xl bg-[#F3F2F0] border border-white shadow-inner flex items-center justify-center group-hover:scale-105 transition-transform">
                      {item.icon}
                    </div>
                    <div>
                      <h4 className="text-[16px] font-bold text-[#1F2430] leading-tight mb-1">{item.label}</h4>
                      <p className="text-[13px] font-medium text-[#1F2430]/50">{item.desc}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}

        <div className="pt-4 border-t border-[#1F2430]/10">
          <button className="w-full md:w-auto px-8 py-3.5 rounded-2xl border-2 border-[#D4183D]/20 text-[#D4183D] font-bold text-[14px] hover:bg-[#D4183D]/10 hover:border-[#D4183D]/40 transition-all flex items-center justify-center gap-2">
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}