import React from 'react';
import {
  LayoutDashboard,
  Watch,
  Calendar,
  Sparkles,
  Utensils,
  Moon,
  HeartPulse,
  LifeBuoy,
  BarChart3,
  ShieldCheck,
  X
} from 'lucide-react';

export type NavTab =
  | 'dashboard'
  | 'wearable'
  | 'calendar'
  | 'scheduler'
  | 'nutrition'
  | 'sleep'
  | 'recovery'
  | 'rescue'
  | 'insights'
  | 'privacy';

interface SidebarProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  isOpen,
  onClose,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'wearable', label: 'Wearable Monitoring', icon: Watch },
    { id: 'calendar', label: 'Academic Calendar', icon: Calendar },
    { id: 'scheduler', label: 'Smart Scheduler', icon: Sparkles },
    { id: 'nutrition', label: 'Nutrition & Hydration', icon: Utensils },
    { id: 'sleep', label: 'Sleep & Recovery', icon: Moon },
    { id: 'recovery', label: 'Recovery Guide', icon: HeartPulse },
    { id: 'rescue', label: 'Priority Rescue Mode', icon: LifeBuoy, highlight: true },
    { id: 'insights', label: 'Weekly Insights', icon: BarChart3 },
    { id: 'privacy', label: 'Privacy & Settings', icon: ShieldCheck },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-40 lg:hidden backdrop-blur-xs"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-white border-r border-bordercolor flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Logo and Brand */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-bordercolor">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center text-white font-bold text-lg shadow-sm">
              DW
            </div>
            <div>
              <span className="font-bold text-lg text-dualtext-primary tracking-tight">
                Dual<span className="text-primary">Well</span>
              </span>
              <span className="block text-[10px] text-dualtext-secondary uppercase tracking-widest font-semibold">
                Student Athlete
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-dualtext-secondary hover:bg-dualbg lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation list */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
          <div className="px-3 py-1 text-[11px] font-semibold text-dualtext-secondary uppercase tracking-wider">
            Main Menu
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id as NavTab);
                  onClose();
                }}
                className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all text-left ${
                  isActive
                    ? 'bg-primary text-white shadow-sm'
                    : item.highlight
                    ? 'text-risk-red bg-red-50 hover:bg-red-100 font-semibold'
                    : 'text-dualtext-primary hover:bg-dualbg hover:text-primary'
                }`}
              >
                <Icon
                  className={`w-5 h-5 shrink-0 ${
                    isActive
                      ? 'text-white'
                      : item.highlight
                      ? 'text-risk-red'
                      : 'text-dualtext-secondary group-hover:text-primary'
                  }`}
                />
                <span className="truncate">{item.label}</span>
                {item.highlight && (
                  <span className="ml-auto text-[10px] bg-risk-red text-white font-bold px-1.5 py-0.5 rounded-full uppercase">
                    SOS
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* System version badge */}
        <div className="p-4 border-t border-bordercolor bg-dualbg/50">
          <div className="flex items-center justify-between text-xs text-dualtext-secondary">
            <span>DualWell Core</span>
            <span className="bg-white border border-bordercolor font-mono px-2 py-0.5 rounded text-[11px]">
              v1.0.0
            </span>
          </div>
        </div>
      </aside>
    </>
  );
};
