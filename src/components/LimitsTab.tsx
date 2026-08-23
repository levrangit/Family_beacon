import React, { useState } from 'react';
import { ChildProfile, AppLimit, AppCategory } from '../types';

interface LimitsTabProps {
  child: ChildProfile;
  onUpdateAppLimit: (appId: string, updates: Partial<AppLimit>) => void;
  onOpenEditQuota: () => void;
  onOpenEditBedtime: () => void;
  onOpenAppModal: (app: AppLimit) => void;
  onAddNewAppRule: () => void;
}

export const LimitsTab: React.FC<LimitsTabProps> = ({
  child,
  onUpdateAppLimit,
  onOpenEditQuota,
  onOpenEditBedtime,
  onOpenAppModal,
  onAddNewAppRule,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [globalLimitEnabled, setGlobalLimitEnabled] = useState(true);
  const [bedtimeEnabled, setBedtimeEnabled] = useState(true);

  const limitHours = Math.floor(child.dailyLimitMinutes / 60);
  const limitMins = child.dailyLimitMinutes % 60;

  const categories: { id: string; label: string }[] = [
    { id: 'all', label: 'Все' },
    { id: 'games', label: 'Игры' },
    { id: 'entertainment', label: 'Развлечения' },
    { id: 'education', label: 'Образование' },
    { id: 'social', label: 'Общение' },
  ];

  const filteredApps = child.apps.filter((app) => {
    const matchesSearch = app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.categoryLabel.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = selectedCategory === 'all' || app.category === selectedCategory;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="flex flex-col gap-6 w-full max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-end gap-3">
        <div>
          <h1 className="font-display font-bold text-2xl md:text-3xl text-[#181c20]">
            Лимиты приложений и расписание
          </h1>
          <p className="text-sm text-[#414754] mt-1">
            Управляйте правилами экранного времени и дневными границами для {child.name}.
          </p>
        </div>
      </div>

      {/* Global Settings Bento Box (2 Cards) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Total Screen Time Card */}
        <div className="bg-white rounded-2xl border border-[#dfe3e8] card-shadow p-6 flex flex-col gap-4 relative overflow-hidden group hover:border-[#adc7ff] transition-all">
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-[#d8e2ff] text-[#001a41] flex items-center justify-center">
                <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                  hourglass_top
                </span>
              </div>
              <div>
                <h3 className="font-display font-semibold text-base md:text-lg text-[#181c20]">
                  Общее время экрана
                </h3>
                <p className="text-xs text-[#414754]">Общий дневной лимит</p>
              </div>
            </div>

            {/* Toggle Switch */}
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={globalLimitEnabled}
                onChange={() => setGlobalLimitEnabled(!globalLimitEnabled)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-[#dfe3e8] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#005bbf]"></div>
            </label>
          </div>

          <div className="flex items-end justify-between mt-2 pt-2 border-t border-[#f1f4fa]">
            <div className="flex flex-col">
              <span className={`font-display font-bold text-3xl md:text-4xl ${globalLimitEnabled ? 'text-[#005bbf]' : 'text-[#727785]'}`}>
                {limitHours}ч {limitMins > 0 ? `${limitMins}м` : ''}
              </span>
              <span className="text-xs text-[#414754] mt-0.5">
                {globalLimitEnabled ? 'Лимит на сегодня' : 'Ограничение выключено'}
              </span>
            </div>
            <button
              onClick={onOpenEditQuota}
              className="text-[#005bbf] hover:bg-[#d8e2ff]/50 transition-colors text-xs font-semibold px-3 py-1.5 rounded-lg"
            >
              Изм.
            </button>
          </div>
        </div>

        {/* Downtime / Bedtime Card */}
        <div className="bg-white rounded-2xl border border-[#dfe3e8] card-shadow p-6 flex flex-col gap-4 relative overflow-hidden group hover:border-[#ffdfa0] transition-all">
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-[#ffdfa0] text-[#261a00] flex items-center justify-center">
                <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                  bedtime
                </span>
              </div>
              <div>
                <h3 className="font-display font-semibold text-base md:text-lg text-[#181c20]">
                  Время отдыха
                </h3>
                <p className="text-xs text-[#414754]">Период блокировки устройства</p>
              </div>
            </div>

            {/* Toggle Switch */}
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={bedtimeEnabled}
                onChange={() => setBedtimeEnabled(!bedtimeEnabled)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-[#dfe3e8] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#005bbf]"></div>
            </label>
          </div>

          <div className="flex items-end justify-between mt-2 pt-2 border-t border-[#f1f4fa]">
            <div className="flex flex-col">
              <span className={`font-display font-bold text-2xl md:text-3xl ${bedtimeEnabled ? 'text-[#181c20]' : 'text-[#727785]'}`}>
                {child.bedtimeStart} — {child.bedtimeEnd}
              </span>
              <span className="text-xs text-[#414754] mt-0.5">Ежедневно</span>
            </div>
            <button
              onClick={onOpenEditBedtime}
              className="text-[#795900] hover:bg-[#ffdfa0]/60 transition-colors text-xs font-semibold px-3 py-1.5 rounded-lg"
            >
              Изм.
            </button>
          </div>
        </div>
      </div>

      {/* App Specific Limits Section */}
      <div className="flex flex-col gap-4 mt-2">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
          <h3 className="font-display font-semibold text-lg text-[#181c20]">
            Лимиты для приложений
          </h3>

          {/* Search and Category Filters */}
          <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
            <div className="relative w-full md:w-60">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#727785] text-lg">
                search
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Поиск приложений..."
                className="w-full bg-[#f1f4fa] border-none rounded-xl pl-9 pr-3 py-2 text-xs text-[#181c20] placeholder-[#727785] focus:ring-2 focus:ring-[#005bbf] focus:bg-white transition-all"
              />
            </div>

            {/* Category pills */}
            <div className="flex items-center gap-1 overflow-x-auto py-1">
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                    selectedCategory === cat.id
                      ? 'bg-[#005bbf] text-white'
                      : 'bg-[#f1f4fa] text-[#414754] hover:bg-[#dfe3e8]'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            <button
              onClick={onAddNewAppRule}
              className="bg-[#005bbf] hover:bg-[#004493] text-white text-xs font-semibold px-3 py-2 rounded-xl flex items-center gap-1 shadow-sm transition-colors shrink-0 ml-auto md:ml-0"
            >
              <span className="material-symbols-outlined text-sm">add</span>
              <span>Добавить</span>
            </button>
          </div>
        </div>

        {/* Apps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredApps.map((app) => {
            const isAlways = app.isAlwaysAllowed || app.limitMinutes === -1;
            const isBlocked = app.isBlocked || app.limitMinutes === 0;
            const limitH = Math.floor(app.limitMinutes / 60);
            const limitM = app.limitMinutes % 60;

            return (
              <div
                key={app.id}
                className="bg-white rounded-2xl border border-[#dfe3e8] card-shadow p-4 flex flex-col gap-3 hover:elevated-shadow transition-all group"
              >
                {/* Header of Card */}
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden shrink-0 border border-[#dfe3e8]"
                      style={{ backgroundColor: app.iconBg, color: app.iconColor }}
                    >
                      <span className="material-symbols-outlined text-2xl">{app.iconName}</span>
                    </div>
                    <div>
                      <h4 className="font-display font-semibold text-base text-[#181c20] leading-tight">
                        {app.name}
                      </h4>
                      <span className="text-[11px] font-medium text-[#414754] bg-[#f1f4fa] px-2 py-0.5 rounded-md mt-1 inline-block">
                        {app.categoryLabel}
                      </span>
                    </div>
                  </div>

                  {/* Toggle Switch */}
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={app.isEnabled && !isBlocked}
                      onChange={(e) => {
                        onUpdateAppLimit(app.id, {
                          isEnabled: e.target.checked,
                          isBlocked: !e.target.checked && isBlocked ? false : isBlocked,
                        });
                      }}
                      className="sr-only peer"
                    />
                    <div className="w-10 h-5 bg-[#dfe3e8] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#005bbf]"></div>
                  </label>
                </div>

                {/* Details Box */}
                <div className="bg-[#f1f4fa] rounded-xl p-3 flex flex-col gap-2 min-h-[72px] justify-center">
                  {isAlways ? (
                    <div className="flex items-center justify-center gap-1.5 text-[#006e2c] text-xs font-semibold py-1">
                      <span className="material-symbols-outlined text-base">check_circle</span>
                      <span>Всегда разрешено</span>
                    </div>
                  ) : isBlocked ? (
                    <div className="flex items-center justify-center gap-1.5 text-[#ba1a1a] text-xs font-semibold py-1">
                      <span className="material-symbols-outlined text-base">block</span>
                      <span>Заблокировано для запуска</span>
                    </div>
                  ) : (
                    <>
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-[#414754] flex items-center gap-1">
                          <span className="material-symbols-outlined text-sm text-[#727785]">timer</span>
                          Дневной лимит
                        </span>
                        <span className="font-semibold text-[#181c20]">
                          {limitH > 0 ? `${limitH}ч ` : ''}{limitM > 0 ? `${limitM}м` : ''}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-[#414754] flex items-center gap-1">
                          <span className="material-symbols-outlined text-sm text-[#727785]">event_available</span>
                          Расписание
                        </span>
                        <span className="text-[#181c20]">
                          {app.scheduleStart && app.scheduleEnd
                            ? `${app.scheduleStart} - ${app.scheduleEnd}`
                            : 'В любое время'}
                        </span>
                      </div>
                    </>
                  )}
                </div>

                {/* Action button */}
                <button
                  onClick={() => onOpenAppModal(app)}
                  className={`w-full py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1 transition-colors ${
                    isAlways
                      ? 'text-[#414754] hover:bg-[#f1f4fa]'
                      : 'text-[#005bbf] hover:bg-[#d8e2ff]/50'
                  }`}
                >
                  <span>{isAlways ? 'Добавить лимит' : 'Изменить правила'}</span>
                  <span className="material-symbols-outlined text-sm">
                    {isAlways ? 'add' : 'edit'}
                  </span>
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
