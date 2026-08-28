import React from 'react';
import { ChildProfile, AppLimit } from '../types';

interface OverviewTabProps {
  child: ChildProfile;
  onAdd30Minutes: () => void;
  onToggleLockDevice: () => void;
  isMainDeviceLocked: boolean;
  onOpenEditLimits: () => void;
  onNavigateToLimits: () => void;
  onSelectApp: (app: AppLimit) => void;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({
  child,
  onAdd30Minutes,
  onToggleLockDevice,
  isMainDeviceLocked,
  onOpenEditLimits,
  onNavigateToLimits,
  onSelectApp,
}) => {
  const totalHours = Math.floor(child.totalTimeMinutes / 60);
  const totalMins = child.totalTimeMinutes % 60;
  const limitHours = Math.floor(child.dailyLimitMinutes / 60);
  const limitMins = child.dailyLimitMinutes % 60;

  const usagePercent = Math.min(100, Math.round((child.totalTimeMinutes / child.dailyLimitMinutes) * 100));
  const remainingMinutes = Math.max(0, child.dailyLimitMinutes - child.totalTimeMinutes);
  const remainingHours = Math.floor(remainingMinutes / 60);
  const remainingMinsRem = remainingMinutes % 60;

  const isNearLimit = usagePercent >= 80 && usagePercent < 100;
  const isOverLimit = usagePercent >= 100;

  // SVG Circle calculations (radius 45, circumference 2 * PI * 45 = 282.74)
  const circumference = 282.74;
  const strokeDashoffset = circumference - (circumference * usagePercent) / 100;

  // Top app by used minutes
  const mostUsedApp = [...child.apps].sort((a, b) => b.usedMinutes - a.usedMinutes)[0] || child.apps[0];

  return (
    <div className="flex flex-col gap-6 w-full max-w-6xl mx-auto">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="font-display font-bold text-2xl md:text-3xl text-[#181c20]">
            Активность {child.name} сегодня
          </h1>
          <p className="text-sm md:text-base text-[#414754] mt-1 flex items-center gap-2">
            <span>Вторник, 24 окт.</span>
            <span className="w-1.5 h-1.5 rounded-full bg-[#727785]"></span>
            <span className="text-[#006e2c] flex items-center gap-1 font-medium">
              <span className="w-2 h-2 rounded-full bg-[#006e2c] inline-block animate-ping"></span>
              Синхронизация в реальном времени
            </span>
          </p>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={onOpenEditLimits}
            className="bg-white border border-[#dfe3e8] text-[#005bbf] hover:bg-[#f1f4fa] transition-colors rounded-xl py-2 px-3.5 flex items-center gap-1.5 text-xs font-semibold shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">edit</span>
            <span>Изменить лимиты</span>
          </button>

          <button
            onClick={onAdd30Minutes}
            className="bg-[#e8f0fe] text-[#005bbf] hover:bg-[#d8e2ff] transition-colors rounded-xl py-2 px-3.5 flex items-center gap-1.5 text-xs font-semibold shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">add_circle</span>
            <span>+30 минут</span>
          </button>

          <button
            onClick={onToggleLockDevice}
            className={`transition-colors rounded-xl py-2 px-3.5 flex items-center gap-1.5 text-xs font-semibold shadow-sm ${
              isMainDeviceLocked
                ? 'bg-[#006e2c] text-white hover:bg-[#005320]'
                : 'bg-[#ffdad6] text-[#93000a] hover:bg-[#ba1a1a] hover:text-white'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">
              {isMainDeviceLocked ? 'lock_open' : 'lock'}
            </span>
            <span>{isMainDeviceLocked ? 'Разблокировать ПК' : 'Заблокировать ПК'}</span>
          </button>
        </div>
      </header>

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Daily Progress Card (Spans 8 cols) */}
        <section className="col-span-1 md:col-span-8 bg-white rounded-2xl border border-[#dfe3e8] card-shadow p-6 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="font-display font-semibold text-lg text-[#181c20]">
                Дневной лимит экранного времени
              </h2>
              <p className="text-xs text-[#727785] mt-0.5">
                Использовано {totalHours}ч {totalMins > 0 ? `${totalMins}м` : ''} из общего лимита {limitHours}ч {limitMins > 0 ? `${limitMins}м` : ''}
              </p>
            </div>
            <span className="material-symbols-outlined text-[#727785] text-xl cursor-help" title="Экранное время суммируется со всех подключенных устройств ребенка">
              info
            </span>
          </div>

          <div className="flex flex-col md:flex-row items-center gap-8 flex-1 justify-center my-2">
            {/* Circular Progress Gauge */}
            <div className="relative w-48 h-48 flex items-center justify-center flex-shrink-0">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                {/* Background Track */}
                <circle
                  cx="50"
                  cy="50"
                  fill="none"
                  r="45"
                  stroke="#E8EAED"
                  strokeLinecap="round"
                  strokeWidth="8"
                />
                {/* Progress Fill */}
                <circle
                  cx="50"
                  cy="50"
                  fill="none"
                  r="45"
                  stroke={isOverLimit || isNearLimit ? '#ba1a1a' : '#005bbf'}
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  strokeWidth="8"
                  className="transition-all duration-700 ease-out"
                />
              </svg>
              <div className="absolute flex flex-col items-center justify-center text-center">
                <span className="font-display font-bold text-4xl text-[#181c20] leading-none tracking-tight">
                  {totalHours}h
                </span>
                <span className="text-sm font-medium text-[#414754] mt-1">
                  of {limitHours}h limit
                </span>
              </div>
            </div>

            {/* Warning or Status Info */}
            <div className="flex flex-col gap-4 flex-1">
              {isNearLimit || isOverLimit ? (
                <div className="bg-[#ffdad6] text-[#93000a] rounded-xl p-4 flex items-start gap-3 border border-[#ffb4ab]">
                  <span className="material-symbols-outlined text-xl mt-0.5 text-[#ba1a1a]">
                    warning
                  </span>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider">
                      {isOverLimit ? 'Лимит превышен' : 'Лимит почти исчерпан'}
                    </p>
                    <p className="text-xs text-[#414754] mt-1 leading-relaxed">
                      {isOverLimit
                        ? `Время истекло. Устройства автоматически переведены в режим блокировки.`
                        : `У ${child.name} остался ${remainingHours > 0 ? `${remainingHours} час ` : ''}${remainingMinsRem} мин сегодня. Подумайте о продлении времени или подготовке к выключению.`}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="bg-[#e5f5e9] text-[#006e2c] rounded-xl p-4 flex items-start gap-3 border border-[#86f898]">
                  <span className="material-symbols-outlined text-xl mt-0.5 text-[#006e2c]">
                    check_circle
                  </span>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider">В пределах нормы</p>
                    <p className="text-xs text-[#414754] mt-1 leading-relaxed">
                      Осталось {remainingHours > 0 ? `${remainingHours}ч ` : ''}{remainingMinsRem}м доступного экранного времени.
                    </p>
                  </div>
                </div>
              )}

              <div className="flex justify-between items-center text-[#414754] text-xs font-medium border-t border-[#dfe3e8] pt-3 px-1">
                <span className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm text-[#727785]">wb_sunny</span>
                  Начало: 8:00 AM
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm text-[#727785]">bedtime</span>
                  Конец: 8:00 PM
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* Summary Stack (Spans 4 cols) */}
        <section className="col-span-1 md:col-span-4 flex flex-col gap-4">
          {/* Status Card */}
          <div className="bg-white rounded-2xl border border-[#dfe3e8] card-shadow p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-[#414754] mb-1">Текущий статус</p>
              <div className="flex items-center gap-2">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#006e2c] opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-[#006e2c]"></span>
                </span>
                <span className="font-display font-semibold text-lg text-[#181c20]">
                  {child.isOnline ? 'В сети' : 'Не в сети'}
                </span>
              </div>
            </div>
            <div className="w-11 h-11 rounded-xl bg-[#e5f5e9] flex items-center justify-center text-[#006e2c]">
              <span className="material-symbols-outlined text-2xl">computer</span>
            </div>
          </div>

          {/* Total Time Card */}
          <div className="bg-white rounded-2xl border border-[#dfe3e8] card-shadow p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-[#414754] mb-1">Общее время</p>
              <p className="font-display font-bold text-2xl text-[#181c20]">
                {totalHours}h {totalMins}m
              </p>
              <p className="text-xs text-[#ba1a1a] font-medium flex items-center gap-1 mt-1">
                <span className="material-symbols-outlined text-sm">trending_up</span>
                <span>30m больше, чем вчера</span>
              </p>
            </div>
            <div className="w-11 h-11 rounded-xl bg-[#e8f0fe] flex items-center justify-center text-[#005bbf]">
              <span className="material-symbols-outlined text-2xl">schedule</span>
            </div>
          </div>

          {/* Most Used App Card */}
          <div className="bg-white rounded-2xl border border-[#dfe3e8] card-shadow p-5 flex flex-col justify-center flex-1">
            <p className="text-xs font-medium text-[#414754] mb-2">Чаще всего</p>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-[#f1f4fa] border border-[#dfe3e8] flex items-center justify-center text-[#005bbf]">
                <span className="material-symbols-outlined text-2xl">{mostUsedApp?.iconName || 'apps'}</span>
              </div>
              <div>
                <p className="font-display font-semibold text-lg text-[#181c20]">
                  {mostUsedApp?.name || 'Roblox'}
                </p>
                <p className="text-xs text-[#727785]">
                  {Math.floor((mostUsedApp?.usedMinutes || 0) / 60)}h {(mostUsedApp?.usedMinutes || 0) % 60}m сегодня
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Top Apps List Table (Spans full 12 cols) */}
        <section className="col-span-1 md:col-span-12 bg-white rounded-2xl border border-[#dfe3e8] card-shadow overflow-hidden">
          <div className="p-5 border-b border-[#dfe3e8] flex justify-between items-center bg-[#f7f9ff]">
            <h2 className="font-display font-semibold text-base md:text-lg text-[#181c20]">
              Статистика по приложениям
            </h2>
            <button
              onClick={onNavigateToLimits}
              className="text-[#005bbf] hover:text-[#004493] text-xs font-semibold transition-colors flex items-center gap-1 cursor-pointer"
            >
              <span>Смотреть все</span>
              <span className="material-symbols-outlined text-base">arrow_forward</span>
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#f7f9ff] text-[#414754] text-[11px] uppercase tracking-wider font-semibold border-b border-[#dfe3e8]">
                  <th className="py-3 px-5">ПРИЛОЖЕНИЕ</th>
                  <th className="py-3 px-4">ВРЕМЯ</th>
                  <th className="py-3 px-4 w-1/3">ЛИМИТ</th>
                  <th className="py-3 px-5 text-right">СТАТУС</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f1f4fa]">
                {child.apps.map((app) => {
                  const usedH = Math.floor(app.usedMinutes / 60);
                  const usedM = app.usedMinutes % 60;
                  const limitH = Math.floor(app.limitMinutes / 60);
                  const limitM = app.limitMinutes % 60;

                  const isBlocked = app.isBlocked || app.limitMinutes === 0;
                  const isAlways = app.isAlwaysAllowed || app.limitMinutes === -1;
                  const isOver = !isAlways && !isBlocked && app.usedMinutes >= app.limitMinutes;
                  const pct = isAlways ? 0 : isBlocked ? 100 : Math.min(100, Math.round((app.usedMinutes / (app.limitMinutes || 1)) * 100));

                  return (
                    <tr
                      key={app.id}
                      onClick={() => onSelectApp(app)}
                      className={`hover:bg-[#f1f4fa] transition-colors cursor-pointer group ${
                        isBlocked ? 'opacity-70' : ''
                      }`}
                    >
                      {/* App Name & Icon */}
                      <td className="py-3.5 px-5 flex items-center gap-3">
                        <div
                          className="w-9 h-9 rounded-xl flex items-center justify-center border border-[#dfe3e8]"
                          style={{ backgroundColor: app.iconBg, color: app.iconColor }}
                        >
                          <span className="material-symbols-outlined text-lg">{app.iconName}</span>
                        </div>
                        <div>
                          <span className={`font-sans font-semibold text-sm text-[#181c20] ${isBlocked ? 'line-through' : ''}`}>
                            {app.name}
                          </span>
                          <span className="block text-[11px] text-[#727785]">{app.categoryLabel}</span>
                        </div>
                      </td>

                      {/* Time Spent */}
                      <td className="py-3.5 px-4 font-sans text-sm text-[#181c20] font-medium whitespace-nowrap">
                        {usedH > 0 ? `${usedH}h ` : ''}{usedM}m
                      </td>

                      {/* Limit Bar */}
                      <td className="py-3.5 px-4">
                        {isAlways ? (
                          <span className="text-xs text-[#727785] italic">No limit set</span>
                        ) : isBlocked ? (
                          <div className="flex items-center gap-2.5">
                            <div className="flex-1 h-2 bg-[#e8eaed] rounded-full overflow-hidden">
                              <div className="h-full bg-[#727785] rounded-full" style={{ width: '100%' }}></div>
                            </div>
                            <span className="text-xs text-[#727785] whitespace-nowrap">0m Лимит установлен</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2.5">
                            <div className="flex-1 h-2 bg-[#e8eaed] rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all ${
                                  isOver ? 'bg-[#ba1a1a]' : 'bg-[#005bbf]'
                                }`}
                                style={{ width: `${pct}%` }}
                              ></div>
                            </div>
                            <span
                              className={`text-xs whitespace-nowrap ${
                                isOver ? 'text-[#ba1a1a] font-semibold' : 'text-[#414754]'
                              }`}
                            >
                              {limitH > 0 ? `${limitH}h ` : ''}{limitM > 0 ? `${limitM}m ` : ''}
                              {isOver ? '(Лимит превышен)' : 'Лимит установлен'}
                            </span>
                          </div>
                        )}
                      </td>

                      {/* Status Chip */}
                      <td className="py-3.5 px-5 text-right">
                        {isBlocked ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#dfe3e8] text-[#414754] text-xs font-medium">
                            <span className="material-symbols-outlined text-[14px]">block</span>
                            Заблокировано
                          </span>
                        ) : isOver ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#ffdad6] text-[#ba1a1a] text-xs font-semibold">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#ba1a1a]"></span>
                            Предупреждение
                          </span>
                        ) : isAlways ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#dfe3e8] text-[#414754] text-xs font-medium">
                            Без ограничений
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#e5f5e9] text-[#006e2c] text-xs font-medium">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#006e2c]"></span>
                            Разрешено
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};
