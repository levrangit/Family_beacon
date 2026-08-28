import React, { useState } from 'react';
import { NavigationTab, ChildProfile } from '../types';
import { BrandLogo } from './BrandLogo';

interface SidebarProps {
  currentTab: NavigationTab;
  onSelectTab: (tab: NavigationTab) => void;
  childrenList: ChildProfile[];
  activeChild: ChildProfile;
  onSelectChild: (childId: string) => void;
  allDevicesLocked: boolean;
  onToggleLockAll: () => void;
  onOpenHelp: () => void;
  onOpenAccount: () => void;
  onOpenChildScreen: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  childrenList,
  activeChild,
  onSelectChild,
  allDevicesLocked,
  onToggleLockAll,
  onOpenHelp,
  onOpenAccount,
  onOpenChildScreen,
}) => {
  const [childMenuOpen, setChildMenuOpen] = useState(false);

  const navItems: { id: NavigationTab; label: string; icon: string }[] = [
    { id: 'overview', label: 'Обзор', icon: 'dashboard' },
    { id: 'limits', label: 'Лимиты', icon: 'timer' },
    { id: 'history', label: 'История', icon: 'history' },
    { id: 'devices', label: 'Устройства', icon: 'devices_other' },
  ];

  return (
    <aside className="hidden md:flex flex-col h-screen w-64 fixed left-0 top-0 bg-white border-r border-[#dfe3e8] p-4 gap-4 z-40 select-none">
      {/* Brand Header */}
      <div className="pt-2 px-1">
        <BrandLogo size="md" subtitle="Панель родителя" />
      </div>

      {/* Child Selector Dropdown */}
      <div className="relative mt-2">
        <div
          onClick={() => setChildMenuOpen(!childMenuOpen)}
          className="flex items-center gap-3 p-2.5 bg-[#f1f4fa] hover:bg-[#e5e8ee] transition-all rounded-xl border border-[#dfe3e8] cursor-pointer"
        >
          <img
            src={activeChild.avatarUrl}
            alt={activeChild.name}
            className="w-10 h-10 rounded-full object-cover border border-[#c1c6d6]"
          />
          <div className="flex-1 min-w-0">
            <p className="font-sans font-semibold text-[#181c20] text-sm truncate">
              {activeChild.name}
            </p>
            <p className="text-xs text-[#006e2c] font-medium flex items-center gap-1.5 truncate">
              <span className="w-2 h-2 rounded-full bg-[#006e2c] inline-block animate-pulse"></span>
              {activeChild.monitoringActive ? 'Мониторинг активен' : 'Отключен'}
            </p>
          </div>
          <span className="material-symbols-outlined text-[#727785] text-lg">
            {childMenuOpen ? 'expand_less' : 'expand_more'}
          </span>
        </div>

        {/* Dropdown Menu */}
        {childMenuOpen && (
          <div className="absolute top-full left-0 w-full mt-1.5 bg-white rounded-xl border border-[#dfe3e8] shadow-lg py-1.5 z-50 animate-in fade-in zoom-in-95 duration-150">
            <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-[#727785]">
              Дети в семье
            </div>
            {childrenList.map((child) => (
              <button
                key={child.id}
                onClick={() => {
                  onSelectChild(child.id);
                  setChildMenuOpen(false);
                }}
                className={`w-full flex items-center gap-2.5 px-3 py-2 text-left text-sm hover:bg-[#f1f4fa] transition-colors ${
                  child.id === activeChild.id ? 'bg-[#d8e2ff]/40 text-[#005bbf] font-medium' : 'text-[#181c20]'
                }`}
              >
                <img src={child.avatarUrl} alt={child.name} className="w-7 h-7 rounded-full object-cover" />
                <span className="flex-1">{child.name}</span>
                {child.id === activeChild.id && (
                  <span className="material-symbols-outlined text-sm text-[#005bbf]">check</span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex flex-col gap-1 mt-2 flex-1">
        {navItems.map((item) => {
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl font-sans text-sm transition-all text-left ${
                isActive
                  ? 'bg-[#1a73e8] text-white font-semibold shadow-sm shadow-[#1a73e8]/20'
                  : 'text-[#414754] hover:bg-[#f1f4fa] hover:text-[#181c20] font-medium'
              }`}
            >
              <span
                className="material-symbols-outlined text-xl"
                style={{ fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}
              >
                {item.icon}
              </span>
              <span>{item.label}</span>
            </button>
          );
        })}

        {/* Demo Switch to Child Screen */}
        <div className="mt-4 pt-3 border-t border-[#f1f4fa]">
          <button
            onClick={onOpenChildScreen}
            className="w-full flex items-center gap-2 px-3 py-2.5 bg-[#f1f4fa] hover:bg-[#e5e8ee] text-[#005bbf] rounded-xl text-xs font-semibold transition-all border border-[#adc7ff]"
          >
            <span className="material-symbols-outlined text-base">screen_lock_portrait</span>
            <span>Экран блокировки</span>
          </button>
        </div>
      </nav>

      {/* Footer & Global Emergency Lock */}
      <div className="flex flex-col gap-2.5 mt-auto pt-2 border-t border-[#dfe3e8]">
        <button
          onClick={onToggleLockAll}
          className={`w-full py-2.5 px-3 rounded-xl flex items-center justify-center gap-2 text-xs font-semibold transition-all shadow-sm ${
            allDevicesLocked
              ? 'bg-[#006e2c] text-white hover:bg-[#005320]'
              : 'bg-[#ffdad6] text-[#93000a] hover:bg-[#ba1a1a] hover:text-white'
          }`}
        >
          <span className="material-symbols-outlined text-base">
            {allDevicesLocked ? 'lock_open' : 'lock'}
          </span>
          <span>{allDevicesLocked ? 'Разблокировать все' : 'Заблокировать все устройства'}</span>
        </button>

        <div className="flex flex-col gap-0.5">
          <button
            onClick={onOpenHelp}
            className="flex items-center gap-3 px-3 py-2 text-[#414754] hover:bg-[#f1f4fa] hover:text-[#181c20] rounded-xl text-xs font-medium transition-colors text-left"
          >
            <span className="material-symbols-outlined text-base">help</span>
            <span>Помощь</span>
          </button>
          <button
            onClick={onOpenAccount}
            className="flex items-center gap-3 px-3 py-2 text-[#414754] hover:bg-[#f1f4fa] hover:text-[#181c20] rounded-xl text-xs font-medium transition-colors text-left"
          >
            <span className="material-symbols-outlined text-base">person</span>
            <span>Аккаунт</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
