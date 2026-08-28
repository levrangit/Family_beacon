import React, { useState } from 'react';
import { ChildProfile, ActivityEvent } from '../types';

interface HistoryTabProps {
  child: ChildProfile;
  onApproveRequest: (eventId: string, minutes: number) => void;
  onDenyRequest: (eventId: string) => void;
  onFilterBlockedEvents?: () => void;
}

export const HistoryTab: React.FC<HistoryTabProps> = ({
  child,
  onApproveRequest,
  onDenyRequest,
}) => {
  const [dateRange, setDateRange] = useState('today');
  const [activeTooltip, setActiveTooltip] = useState<number | null>(null);

  // Hourly chart data simulation
  const chartBars = [
    { hour: '8 AM', height: 15, duration: '9m', label: '8:00 - 9:00', cat: 'Учеба / Chrome', color: '#adc7ff' },
    { hour: '10 AM', height: 8, duration: '5m', label: '10:00 - 11:00', cat: 'Scratch 3', color: '#adc7ff' },
    { hour: '12 PM', height: 40, duration: '24m', label: '12:00 - 13:00', cat: 'YouTube (Развлечения)', color: '#1a73e8' },
    { hour: '2 PM', height: 85, duration: '52m', label: '14:00 - 15:00', cat: 'Roblox (Игра)', color: '#005bbf' },
    { hour: '4 PM', height: 60, duration: '36m', label: '16:00 - 17:00', cat: 'Roblox & YouTube', color: '#1a73e8' },
    { hour: '6 PM', height: 12, duration: '1 попытка', label: '18:00 - 19:00', cat: 'Попытка запуска Discord (Блокировка)', color: '#ba1a1a' },
  ];

  return (
    <div className="flex flex-col gap-6 w-full max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
        <div>
          <h1 className="font-display font-bold text-2xl md:text-3xl text-[#181c20]">
            История активности
          </h1>
          <p className="text-sm text-[#414754] mt-1">
            Детальная хронология использования устройств {child.name}.
          </p>
        </div>

        {/* Date Selector */}
        <div className="relative">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="appearance-none bg-white border border-[#dfe3e8] text-[#181c20] text-xs font-semibold rounded-xl py-2.5 pl-4 pr-10 focus:outline-none focus:ring-2 focus:ring-[#005bbf] shadow-sm cursor-pointer"
          >
            <option value="today">Сегодня, 24 окт.</option>
            <option value="yesterday">Вчера, 23 окт.</option>
            <option value="week">Последние 7 дней</option>
          </select>
          <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-[#727785] text-base pointer-events-none">
            calendar_today
          </span>
        </div>
      </div>

      {/* Top Summary Cards (3 Columns) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Card 1: Total Time */}
        <div className="bg-white border border-[#dfe3e8] rounded-2xl p-5 card-shadow flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-[#d8e2ff] flex items-center justify-center shrink-0 text-[#001a41]">
            <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              schedule
            </span>
          </div>
          <div className="flex flex-col flex-1">
            <span className="text-[11px] font-semibold text-[#727785] uppercase tracking-wider">
              ОБЩЕЕ ВРЕМЯ
            </span>
            <div className="flex items-baseline gap-1 mt-1">
              <span className="font-display font-bold text-3xl text-[#181c20]">3h 45m</span>
            </div>
            <div className="w-full bg-[#dfe3e8] h-2 rounded-full mt-3 overflow-hidden">
              <div className="bg-[#005bbf] h-full rounded-full" style={{ width: '75%' }}></div>
            </div>
            <span className="text-[11px] text-[#727785] mt-1.5 text-right font-medium">
              75% от дневного лимита
            </span>
          </div>
        </div>

        {/* Card 2: Peak Activity */}
        <div className="bg-white border border-[#dfe3e8] rounded-2xl p-5 card-shadow flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-[#ffdfa0] flex items-center justify-center shrink-0 text-[#261a00]">
            <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              trending_up
            </span>
          </div>
          <div className="flex flex-col flex-1">
            <span className="text-[11px] font-semibold text-[#727785] uppercase tracking-wider">
              ПИКОВАЯ АКТИВНОСТЬ
            </span>
            <div className="flex items-baseline gap-1 mt-1">
              <span className="font-display font-bold text-3xl text-[#181c20]">3:00 PM</span>
            </div>
            <span className="text-xs text-[#181c20] mt-3">
              В основном <strong>Roblox</strong> &amp; <strong>YouTube</strong>
            </span>
          </div>
        </div>

        {/* Card 3: Blocked Attempts */}
        <div className="bg-white border border-[#dfe3e8] rounded-2xl p-5 card-shadow flex items-start gap-4 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-[#ffdad6] rounded-full opacity-30 group-hover:scale-150 transition-transform duration-500 pointer-events-none"></div>
          <div className="w-12 h-12 rounded-2xl bg-[#ffdad6] flex items-center justify-center shrink-0 text-[#93000a] relative z-10">
            <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              block
            </span>
          </div>
          <div className="flex flex-col relative z-10">
            <span className="text-[11px] font-semibold text-[#727785] uppercase tracking-wider">
              ЗАБЛОКИРОВАНО
            </span>
            <div className="flex items-baseline gap-1.5 mt-1">
              <span className="font-display font-bold text-3xl text-[#181c20]">2</span>
              <span className="text-xs text-[#727785]">Сегодня</span>
            </div>
            <span className="text-xs text-[#ba1a1a] font-semibold mt-3">
              Discord (2 попытки)
            </span>
          </div>
        </div>
      </div>

      {/* Main Layout: Chart & Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Activity Chart (2 cols) */}
        <div className="lg:col-span-2 flex flex-col">
          <div className="bg-white border border-[#dfe3e8] rounded-2xl p-6 card-shadow h-full flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="font-display font-semibold text-lg text-[#181c20]">
                  Распределение активности
                </h2>
                <p className="text-xs text-[#727785] mt-0.5">
                  Использование экрана по часам в течение дня
                </p>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-[#f1f4fa] text-[#414754]">
                Сегодня
              </span>
            </div>

            {/* Custom Bar Chart Canvas */}
            <div className="flex-1 flex flex-col justify-end min-h-[280px] relative pb-8 mt-2">
              {/* Y-axis labels */}
              <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-[#727785] text-[11px] pb-8 w-8 text-right font-medium">
                <span>60m</span>
                <span>45m</span>
                <span>30m</span>
                <span>15m</span>
                <span>0</span>
              </div>

              {/* Grid lines */}
              <div className="absolute left-10 right-0 top-0 h-full flex flex-col justify-between pb-8 pointer-events-none">
                <div className="w-full border-t border-[#dfe3e8] border-dashed"></div>
                <div className="w-full border-t border-[#dfe3e8] border-dashed"></div>
                <div className="w-full border-t border-[#dfe3e8] border-dashed"></div>
                <div className="w-full border-t border-[#dfe3e8] border-dashed"></div>
                <div className="w-full border-t border-[#727785]"></div>
              </div>

              {/* Bars */}
              <div className="ml-10 relative h-full flex items-end justify-around px-2 sm:px-4 z-10 pb-[1px]">
                {chartBars.map((bar, idx) => (
                  <div
                    key={bar.hour}
                    className="w-1/6 max-w-[48px] group relative flex justify-center h-full items-end"
                    onMouseEnter={() => setActiveTooltip(idx)}
                    onMouseLeave={() => setActiveTooltip(null)}
                  >
                    <div
                      className="w-full rounded-t-lg transition-all duration-300 cursor-pointer group-hover:opacity-90 shadow-sm"
                      style={{
                        height: `${bar.height}%`,
                        backgroundColor: bar.color,
                      }}
                    ></div>

                    {/* Tooltip */}
                    {activeTooltip === idx && (
                      <div className="absolute -top-14 left-1/2 -translate-x-1/2 bg-[#2d3135] text-white text-xs py-1.5 px-3 rounded-lg shadow-xl pointer-events-none whitespace-nowrap z-30 animate-in fade-in duration-150">
                        <p className="font-semibold">{bar.duration}</p>
                        <p className="text-[10px] text-[#dfe3e8]">{bar.cat}</p>
                      </div>
                    )}

                    <span className="absolute -bottom-7 text-xs font-medium text-[#727785] whitespace-nowrap">
                      {bar.hour}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Chart Legend */}
            <div className="flex flex-wrap items-center justify-center gap-4 mt-6 pt-4 border-t border-[#f1f4fa] text-xs text-[#414754]">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-[#005bbf]"></span>
                Игры
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-[#1a73e8]"></span>
                Развлечения
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-[#adc7ff]"></span>
                Обучение
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-[#ba1a1a]"></span>
                Блокировка
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Detailed Event Log */}
        <div className="flex flex-col h-full bg-white border border-[#dfe3e8] rounded-2xl card-shadow overflow-hidden">
          <div className="p-5 border-b border-[#dfe3e8] flex justify-between items-center bg-[#f7f9ff]">
            <h2 className="font-display font-semibold text-base text-[#181c20]">
              Журнал событий
            </h2>
            <span className="bg-[#d8e2ff] text-[#001a41] text-[11px] font-semibold px-2 py-1 rounded-md">
              Хронологический
            </span>
          </div>

          <div className="p-5 flex-1 overflow-y-auto max-h-[500px] relative">
            {/* Timeline Line */}
            <div className="absolute left-[54px] top-6 bottom-6 w-0.5 bg-[#dfe3e8]"></div>

            {/* Event Items */}
            <div className="flex flex-col gap-5 relative">
              {child.events.map((event: ActivityEvent) => {
                const isRequest = event.type === 'time_request';
                const isLimitOff = event.type === 'limit_reached';
                const isLock = event.type === 'device_locked';

                return (
                  <div key={event.id} className="flex gap-3 relative">
                    {/* Timestamp */}
                    <div className="w-10 pt-1 flex-shrink-0 text-right">
                      <span className={`text-xs font-semibold ${isLimitOff ? 'text-[#ba1a1a]' : 'text-[#727785]'}`}>
                        {event.time}
                      </span>
                    </div>

                    {/* Timeline Node Icon */}
                    <div
                      className={`w-7 h-7 rounded-full border-2 border-white flex items-center justify-center relative z-10 shrink-0 shadow-sm ${
                        isLimitOff
                          ? 'bg-[#ffdad6] text-[#ba1a1a]'
                          : isRequest
                          ? 'bg-[#ffdfa0] text-[#795900]'
                          : isLock
                          ? 'bg-[#2d3135] text-white'
                          : 'bg-[#f1f4fa] text-[#005bbf]'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[14px]">
                        {isLimitOff
                          ? 'timer_off'
                          : isRequest
                          ? 'front_hand'
                          : isLock
                          ? 'lock'
                          : event.type === 'entertainment_launch'
                          ? 'play_arrow'
                          : 'sports_esports'}
                      </span>
                    </div>

                    {/* Event Content Box */}
                    <div
                      className={`flex-1 p-3 rounded-xl border transition-all ${
                        isRequest
                          ? 'bg-[#fffdfa] border-[#fbbc05] shadow-sm'
                          : isLimitOff
                          ? 'bg-[#ffdad6]/20 border-[#ffdad6]'
                          : 'bg-[#f1f4fa] border-[#dfe3e8]'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-sans font-semibold text-xs md:text-sm text-[#181c20]">
                            {event.title}
                          </h4>
                          <span
                            className={`text-[11px] font-medium ${
                              isLimitOff
                                ? 'text-[#ba1a1a]'
                                : isRequest
                                ? 'text-[#795900]'
                                : 'text-[#727785]'
                            }`}
                          >
                            {event.subtitle}
                          </span>
                        </div>

                        {event.durationMinutes && (
                          <span className="text-[10px] font-medium text-[#414754] bg-white px-2 py-0.5 rounded-md border border-[#dfe3e8] whitespace-nowrap">
                            {event.durationMinutes} мин
                          </span>
                        )}
                      </div>

                      {/* Request Action Buttons if status is pending */}
                      {isRequest && (
                        <div className="mt-2.5 pt-2 border-t border-[#fbbc05]/30">
                          {event.status === 'pending' ? (
                            <div className="flex gap-2">
                              <button
                                onClick={() => onApproveRequest(event.id, event.requestMinutes || 30)}
                                className="flex-1 bg-[#005bbf] hover:bg-[#004493] text-white text-xs font-semibold py-1.5 px-2 rounded-lg transition-colors shadow-sm"
                              >
                                Одобрить (+30м)
                              </button>
                              <button
                                onClick={() => onDenyRequest(event.id)}
                                className="flex-1 bg-[#dfe3e8] hover:bg-[#c1c6d6] text-[#414754] text-xs font-medium py-1.5 px-2 rounded-lg transition-colors"
                              >
                                Отклонить
                              </button>
                            </div>
                          ) : event.status === 'approved' ? (
                            <span className="inline-flex items-center gap-1 text-xs text-[#006e2c] font-semibold">
                              <span className="material-symbols-outlined text-sm">check_circle</span>
                              Запрос одобрен (+30 мин добавлено)
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-xs text-[#ba1a1a] font-medium">
                              <span className="material-symbols-outlined text-sm">cancel</span>
                              Запрос отклонен
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
