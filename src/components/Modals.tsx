import React, { useState } from 'react';
import { AppLimit, ChildProfile, DeviceItem } from '../types';

// 1. Edit Daily Quota Modal
export const EditQuotaModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  currentMinutes: number;
  onSave: (minutes: number) => void;
  childName: string;
}> = ({ isOpen, onClose, currentMinutes, onSave, childName }) => {
  const [hours, setHours] = useState(Math.floor(currentMinutes / 60));
  const [mins, setMins] = useState(currentMinutes % 60);

  if (!isOpen) return null;

  const presets = [120, 180, 210, 240, 300, 360];

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-[#dfe3e8]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-[#005bbf]">
            <span className="material-symbols-outlined text-2xl">hourglass_top</span>
            <h3 className="font-display font-bold text-lg text-[#181c20]">
              Дневной лимит для {childName}
            </h3>
          </div>
          <button onClick={onClose} className="text-[#727785] hover:text-[#181c20] p-1">
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        <p className="text-xs text-[#414754] mb-4">
          Установите максимальное суммарное время использования всех устройств в день:
        </p>

        {/* Hour & Minute Selectors */}
        <div className="flex items-center justify-center gap-4 bg-[#f1f4fa] p-4 rounded-2xl mb-4">
          <div className="flex flex-col items-center">
            <label className="text-[11px] text-[#727785] uppercase font-semibold mb-1">Часы</label>
            <input
              type="number"
              min="0"
              max="12"
              value={hours}
              onChange={(e) => setHours(Math.max(0, parseInt(e.target.value) || 0))}
              className="w-16 text-center text-2xl font-display font-bold bg-white border border-[#dfe3e8] rounded-xl py-2 focus:ring-2 focus:ring-[#005bbf]"
            />
          </div>
          <span className="text-2xl font-bold text-[#727785] pt-4">:</span>
          <div className="flex flex-col items-center">
            <label className="text-[11px] text-[#727785] uppercase font-semibold mb-1">Минуты</label>
            <input
              type="number"
              min="0"
              max="59"
              step="5"
              value={mins}
              onChange={(e) => setMins(Math.max(0, Math.min(59, parseInt(e.target.value) || 0)))}
              className="w-16 text-center text-2xl font-display font-bold bg-white border border-[#dfe3e8] rounded-xl py-2 focus:ring-2 focus:ring-[#005bbf]"
            />
          </div>
        </div>

        {/* Quick Presets */}
        <div className="flex flex-wrap gap-2 mb-6">
          {presets.map((total) => {
            const h = Math.floor(total / 60);
            const m = total % 60;
            return (
              <button
                key={total}
                type="button"
                onClick={() => {
                  setHours(h);
                  setMins(m);
                }}
                className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                  hours * 60 + mins === total
                    ? 'bg-[#005bbf] text-white border-[#005bbf]'
                    : 'bg-[#f1f4fa] text-[#414754] border-[#dfe3e8] hover:bg-[#dfe3e8]'
                }`}
              >
                {h}ч {m > 0 ? `${m}м` : ''}
              </button>
            );
          })}
        </div>

        <div className="flex justify-end gap-2.5">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-[#414754] hover:bg-[#f1f4fa]"
          >
            Отмена
          </button>
          <button
            onClick={() => {
              onSave(hours * 60 + mins);
              onClose();
            }}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-[#005bbf] hover:bg-[#004493] text-white shadow-sm transition-colors"
          >
            Сохранить лимит
          </button>
        </div>
      </div>
    </div>
  );
};

// 2. Edit Bedtime / Downtime Modal
export const EditBedtimeModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  bedtimeStart: string;
  bedtimeEnd: string;
  onSave: (start: string, end: string) => void;
}> = ({ isOpen, onClose, bedtimeStart, bedtimeEnd, onSave }) => {
  const [start, setStart] = useState(bedtimeStart);
  const [end, setEnd] = useState(bedtimeEnd);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-[#dfe3e8]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-[#795900]">
            <span className="material-symbols-outlined text-2xl">bedtime</span>
            <h3 className="font-display font-bold text-lg text-[#181c20]">
              Время отдыха и сон
            </h3>
          </div>
          <button onClick={onClose} className="text-[#727785] hover:text-[#181c20] p-1">
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        <p className="text-xs text-[#414754] mb-4">
          В этот период экран будет заблокирован, чтобы ребенок спокойно готовился ко сну:
        </p>

        <div className="grid grid-cols-2 gap-4 bg-[#f1f4fa] p-4 rounded-2xl mb-6">
          <div>
            <label className="text-[11px] text-[#727785] uppercase font-semibold mb-1 block">
              Начало отдыха
            </label>
            <input
              type="time"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              className="w-full bg-white border border-[#dfe3e8] rounded-xl px-3 py-2 text-sm font-semibold text-[#181c20] focus:ring-2 focus:ring-[#005bbf]"
            />
          </div>
          <div>
            <label className="text-[11px] text-[#727785] uppercase font-semibold mb-1 block">
              Окончание отдыха
            </label>
            <input
              type="time"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
              className="w-full bg-white border border-[#dfe3e8] rounded-xl px-3 py-2 text-sm font-semibold text-[#181c20] focus:ring-2 focus:ring-[#005bbf]"
            />
          </div>
        </div>

        <div className="flex justify-end gap-2.5">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-[#414754] hover:bg-[#f1f4fa]"
          >
            Отмена
          </button>
          <button
            onClick={() => {
              onSave(start, end);
              onClose();
            }}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-[#005bbf] hover:bg-[#004493] text-white shadow-sm transition-colors"
          >
            Сохранить расписание
          </button>
        </div>
      </div>
    </div>
  );
};

// 3. Edit App Rule Modal
export const EditAppRuleModal: React.FC<{
  isOpen: boolean;
  app: AppLimit | null;
  onClose: () => void;
  onSave: (appId: string, updates: Partial<AppLimit>) => void;
}> = ({ isOpen, app, onClose, onSave }) => {
  if (!isOpen || !app) return null;

  const [mode, setMode] = useState<'limit' | 'always' | 'blocked'>(
    app.isBlocked
      ? 'blocked'
      : app.isAlwaysAllowed || app.limitMinutes === -1
      ? 'always'
      : 'limit'
  );
  const [limitMinutes, setLimitMinutes] = useState(
    app.limitMinutes > 0 ? app.limitMinutes : 60
  );
  const [scheduleStart, setScheduleStart] = useState(app.scheduleStart || '16:00');
  const [scheduleEnd, setScheduleEnd] = useState(app.scheduleEnd || '18:00');

  const handleSave = () => {
    if (mode === 'blocked') {
      onSave(app.id, { isBlocked: true, isAlwaysAllowed: false, limitMinutes: 0 });
    } else if (mode === 'always') {
      onSave(app.id, { isBlocked: false, isAlwaysAllowed: true, limitMinutes: -1 });
    } else {
      onSave(app.id, {
        isBlocked: false,
        isAlwaysAllowed: false,
        limitMinutes,
        scheduleStart,
        scheduleEnd,
        isEnabled: true,
      });
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-[#dfe3e8]">
        {/* Modal Header with App Icon */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center border border-[#dfe3e8]"
              style={{ backgroundColor: app.iconBg, color: app.iconColor }}
            >
              <span className="material-symbols-outlined text-2xl">{app.iconName}</span>
            </div>
            <div>
              <h3 className="font-display font-bold text-lg text-[#181c20]">
                {app.name}
              </h3>
              <p className="text-xs text-[#727785]">{app.categoryLabel}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-[#727785] hover:text-[#181c20] p-1">
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        {/* Rule Type Selector */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          <button
            type="button"
            onClick={() => setMode('limit')}
            className={`p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 transition-all ${
              mode === 'limit'
                ? 'bg-[#d8e2ff] border-[#005bbf] text-[#001a41]'
                : 'bg-[#f1f4fa] border-[#dfe3e8] text-[#414754]'
            }`}
          >
            <span className="material-symbols-outlined text-lg">timer</span>
            <span>Дневной лимит</span>
          </button>

          <button
            type="button"
            onClick={() => setMode('always')}
            className={`p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 transition-all ${
              mode === 'always'
                ? 'bg-[#e5f5e9] border-[#006e2c] text-[#006e2c]'
                : 'bg-[#f1f4fa] border-[#dfe3e8] text-[#414754]'
            }`}
          >
            <span className="material-symbols-outlined text-lg">check_circle</span>
            <span>Всегда можно</span>
          </button>

          <button
            type="button"
            onClick={() => setMode('blocked')}
            className={`p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 transition-all ${
              mode === 'blocked'
                ? 'bg-[#ffdad6] border-[#ba1a1a] text-[#93000a]'
                : 'bg-[#f1f4fa] border-[#dfe3e8] text-[#414754]'
            }`}
          >
            <span className="material-symbols-outlined text-lg">block</span>
            <span>Заблокировать</span>
          </button>
        </div>

        {/* Mode Dependent Controls */}
        {mode === 'limit' && (
          <div className="flex flex-col gap-4 bg-[#f1f4fa] p-4 rounded-2xl mb-4">
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-semibold text-[#181c20]">
                  Лимит времени: {Math.floor(limitMinutes / 60)}ч {limitMinutes % 60}м
                </label>
              </div>
              <input
                type="range"
                min="15"
                max="240"
                step="15"
                value={limitMinutes}
                onChange={(e) => setLimitMinutes(parseInt(e.target.value))}
                className="w-full accent-[#005bbf] cursor-pointer"
              />
            </div>

            <div className="grid grid-cols-2 gap-3 pt-2 border-t border-[#dfe3e8]">
              <div>
                <label className="text-[11px] font-semibold text-[#727785] block mb-1">
                  Разрешено с:
                </label>
                <input
                  type="time"
                  value={scheduleStart}
                  onChange={(e) => setScheduleStart(e.target.value)}
                  className="w-full bg-white border border-[#dfe3e8] rounded-xl px-2.5 py-1.5 text-xs font-semibold text-[#181c20]"
                />
              </div>
              <div>
                <label className="text-[11px] font-semibold text-[#727785] block mb-1">
                  До:
                </label>
                <input
                  type="time"
                  value={scheduleEnd}
                  onChange={(e) => setScheduleEnd(e.target.value)}
                  className="w-full bg-white border border-[#dfe3e8] rounded-xl px-2.5 py-1.5 text-xs font-semibold text-[#181c20]"
                />
              </div>
            </div>
          </div>
        )}

        {mode === 'always' && (
          <div className="bg-[#e5f5e9] p-4 rounded-2xl mb-4 text-xs text-[#006e2c] leading-relaxed flex items-start gap-2.5">
            <span className="material-symbols-outlined text-lg shrink-0">info</span>
            <span>Приложение будет доступно без ограничений по времени и даже во время периода отдыха (подходит для учебных платформ и звонков родителям).</span>
          </div>
        )}

        {mode === 'blocked' && (
          <div className="bg-[#ffdad6] p-4 rounded-2xl mb-4 text-xs text-[#93000a] leading-relaxed flex items-start gap-2.5">
            <span className="material-symbols-outlined text-lg shrink-0">warning</span>
            <span>Приложение будет полностью заблокировано на всех устройствах ребенка. При попытке запуска появится сообщение о запрете.</span>
          </div>
        )}

        <div className="flex justify-end gap-2.5">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-[#414754] hover:bg-[#f1f4fa]"
          >
            Отмена
          </button>
          <button
            onClick={handleSave}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-[#005bbf] hover:bg-[#004493] text-white shadow-sm transition-colors"
          >
            Сохранить правила
          </button>
        </div>
      </div>
    </div>
  );
};

// 4. Add Device Pairing Modal
export const AddDeviceModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onDeviceAdded: (device: DeviceItem) => void;
  childName: string;
}> = ({ isOpen, onClose, onDeviceAdded, childName }) => {
  const [selectedOS, setSelectedOS] = useState<'windows' | 'macos' | 'ios' | 'android'>('windows');
  const [deviceName, setDeviceName] = useState('Новый компьютер');
  const [pinCode] = useState('849-217');

  if (!isOpen) return null;

  const handleAdd = () => {
    const newDevice: DeviceItem = {
      id: `dev-${Date.now()}`,
      name: deviceName || 'Новое устройство',
      type: selectedOS === 'windows' ? 'desktop' : selectedOS === 'macos' ? 'laptop' : 'phone',
      os: selectedOS === 'windows' ? 'Windows 11' : selectedOS === 'macos' ? 'macOS Sonoma' : selectedOS === 'ios' ? 'iOS 17' : 'Android 14',
      isOnline: true,
      batteryLevel: 95,
      lastSync: 'Только что подключено',
      isLocked: false,
      location: {
        lat: 55.7558,
        lng: 37.6173,
        address: 'Домашняя сеть',
        city: 'Москва',
      },
    };
    onDeviceAdded(newDevice);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-[#dfe3e8]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-[#005bbf]">
            <span className="material-symbols-outlined text-2xl">devices_other</span>
            <h3 className="font-display font-bold text-lg text-[#181c20]">
              Подключение устройства для {childName}
            </h3>
          </div>
          <button onClick={onClose} className="text-[#727785] hover:text-[#181c20] p-1">
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        {/* OS Selector */}
        <div className="grid grid-cols-4 gap-2 mb-4">
          {[
            { id: 'windows', label: 'Windows', icon: 'desktop_windows' },
            { id: 'macos', label: 'macOS', icon: 'laptop_mac' },
            { id: 'ios', label: 'iPhone/iPad', icon: 'smartphone' },
            { id: 'android', label: 'Android', icon: 'phone_android' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setSelectedOS(item.id as typeof selectedOS)}
              className={`p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 transition-all ${
                selectedOS === item.id
                  ? 'bg-[#d8e2ff] border-[#005bbf] text-[#001a41]'
                  : 'bg-[#f1f4fa] border-[#dfe3e8] text-[#414754]'
              }`}
            >
              <span className="material-symbols-outlined text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </div>

        {/* Pairing Instructions & QR Code */}
        <div className="bg-[#f1f4fa] rounded-2xl p-4 flex flex-col items-center text-center gap-3 mb-4">
          <p className="text-xs text-[#414754]">
            1. Установите приложение «Семейный маяк» на устройство ребенка.<br />
            2. Введите код сопряжения или отсканируйте QR-код:
          </p>

          <div className="w-32 h-32 bg-white rounded-xl border border-[#dfe3e8] p-2 flex items-center justify-center shadow-xs">
            {/* SVG QR Code Simulation */}
            <svg viewBox="0 0 100 100" className="w-full h-full">
              <rect width="100" height="100" fill="white" />
              <rect x="10" y="10" width="25" height="25" fill="#001a41" />
              <rect x="15" y="15" width="15" height="15" fill="white" />
              <rect x="19" y="19" width="7" height="7" fill="#001a41" />

              <rect x="65" y="10" width="25" height="25" fill="#001a41" />
              <rect x="70" y="15" width="15" height="15" fill="white" />
              <rect x="74" y="19" width="7" height="7" fill="#001a41" />

              <rect x="10" y="65" width="25" height="25" fill="#001a41" />
              <rect x="15" y="70" width="15" height="15" fill="white" />
              <rect x="19" y="74" width="7" height="7" fill="#001a41" />

              <rect x="42" y="15" width="8" height="8" fill="#005bbf" />
              <rect x="45" y="45" width="10" height="10" fill="#005bbf" />
              <rect x="65" y="55" width="12" height="12" fill="#001a41" />
              <rect x="45" y="75" width="8" height="8" fill="#001a41" />
            </svg>
          </div>

          <div className="bg-white px-4 py-1.5 rounded-xl border border-[#dfe3e8] font-mono font-bold text-base text-[#005bbf] tracking-widest">
            {pinCode}
          </div>
        </div>

        <div className="mb-4">
          <label className="text-xs font-semibold text-[#414754] block mb-1">
            Название устройства
          </label>
          <input
            type="text"
            value={deviceName}
            onChange={(e) => setDeviceName(e.target.value)}
            className="w-full bg-[#f1f4fa] border border-[#dfe3e8] rounded-xl px-3 py-2 text-xs font-medium text-[#181c20]"
          />
        </div>

        <div className="flex justify-end gap-2.5">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-[#414754] hover:bg-[#f1f4fa]"
          >
            Отмена
          </button>
          <button
            onClick={handleAdd}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-[#005bbf] hover:bg-[#004493] text-white shadow-sm transition-colors"
          >
            Завершить сопряжение
          </button>
        </div>
      </div>
    </div>
  );
};

// 5. Geolocation Modal
export const GeolocationModal: React.FC<{
  isOpen: boolean;
  device: DeviceItem | null;
  onClose: () => void;
}> = ({ isOpen, device, onClose }) => {
  if (!isOpen || !device) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-[#dfe3e8]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-[#005bbf]">
            <span className="material-symbols-outlined text-2xl">location_on</span>
            <h3 className="font-display font-bold text-lg text-[#181c20]">
              Геолокация: {device.name}
            </h3>
          </div>
          <button onClick={onClose} className="text-[#727785] hover:text-[#181c20] p-1">
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        {/* Map Canvas Simulation */}
        <div className="relative w-full h-56 bg-[#e8eef8] rounded-2xl overflow-hidden border border-[#dfe3e8] mb-4 flex items-center justify-center">
          {/* Stylized vector map grid */}
          <div className="absolute inset-0 opacity-40 bg-[radial-gradient(#c1c6d6_1px,transparent_1px)] [background-size:16px_16px]"></div>

          {/* Roads & River */}
          <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0 120 Q 150 80 300 130 T 600 100" fill="none" stroke="#adc7ff" strokeWidth="16" />
            <path d="M 120 0 L 140 240" fill="none" stroke="#ffffff" strokeWidth="6" />
            <path d="M 0 160 L 500 150" fill="none" stroke="#ffffff" strokeWidth="8" />
            <path d="M 280 0 L 260 240" fill="none" stroke="#ffffff" strokeWidth="6" />
          </svg>

          {/* Pulsing Pin Location */}
          <div className="relative z-10 flex flex-col items-center">
            <div className="relative flex items-center justify-center">
              <span className="animate-ping absolute inline-flex h-12 w-12 rounded-full bg-[#005bbf] opacity-40"></span>
              <div className="w-10 h-10 rounded-full bg-[#005bbf] text-white flex items-center justify-center shadow-lg border-2 border-white">
                <span className="material-symbols-outlined text-xl">person_pin_circle</span>
              </div>
            </div>
            <div className="mt-2 bg-[#2d3135] text-white text-[11px] font-semibold px-2.5 py-1 rounded-lg shadow-md whitespace-nowrap">
              {device.name} • {device.lastSync}
            </div>
          </div>
        </div>

        <div className="bg-[#f1f4fa] p-3.5 rounded-xl text-xs text-[#181c20] flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-lg text-[#006e2c]">my_location</span>
            <span>{device.location.address}</span>
          </div>
          <span className="text-[#006e2c] font-semibold text-[11px]">Точность ~10 м</span>
        </div>

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-[#005bbf] text-white hover:bg-[#004493]"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  );
};

// 6. Help Modal
export const HelpModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-[#dfe3e8]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-[#005bbf]">
            <span className="material-symbols-outlined text-2xl">help</span>
            <h3 className="font-display font-bold text-lg text-[#181c20]">
              Справка «Семейный маяк»
            </h3>
          </div>
          <button onClick={onClose} className="text-[#727785] hover:text-[#181c20] p-1">
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        <div className="flex flex-col gap-3 text-xs text-[#414754] leading-relaxed mb-6">
          <div className="p-3 bg-[#f1f4fa] rounded-xl">
            <p className="font-semibold text-[#181c20] mb-1">Как работают дневные лимиты?</p>
            <p>Дневной лимит автоматически суммирует экранное время со всех компьютеров и планшетов ребенка. Когда лимит исчерпан, включается экран блокировки.</p>
          </div>
          <div className="p-3 bg-[#f1f4fa] rounded-xl">
            <p className="font-semibold text-[#181c20] mb-1">Что такое «Время отдыха»?</p>
            <p>Период отдыха (например, 21:00 — 07:00) блокирует доступ к развлекательным играм и приложениям на ночь, сохраняя только возможность звонка родителям.</p>
          </div>
          <div className="p-3 bg-[#f1f4fa] rounded-xl">
            <p className="font-semibold text-[#181c20] mb-1">Экстренная блокировка</p>
            <p>Кнопка «Заблокировать все устройства» в нижнем левом углу мгновенно переводит все гаджеты в режим ожидания до вашего разрешения.</p>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-[#005bbf] text-white hover:bg-[#004493]"
          >
            Понятно
          </button>
        </div>
      </div>
    </div>
  );
};

// 7. Account Settings Modal
export const AccountModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-[#dfe3e8]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-[#005bbf]">
            <span className="material-symbols-outlined text-2xl">person</span>
            <h3 className="font-display font-bold text-lg text-[#181c20]">
              Аккаунт родителя
            </h3>
          </div>
          <button onClick={onClose} className="text-[#727785] hover:text-[#181c20] p-1">
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        <div className="flex items-center gap-3 p-3 bg-[#f1f4fa] rounded-2xl mb-4">
          <div className="w-12 h-12 rounded-full bg-[#d8e2ff] text-[#001a41] flex items-center justify-center font-bold text-lg">
            Р
          </div>
          <div>
            <p className="font-semibold text-sm text-[#181c20]">Родительский профиль</p>
            <p className="text-xs text-[#727785]">parent.beacon@family.org</p>
          </div>
        </div>

        <div className="flex flex-col gap-2.5 text-xs text-[#414754] mb-6">
          <div className="flex justify-between items-center p-2.5 border-b border-[#f1f4fa]">
            <span>Родительский PIN-код для разблокировки</span>
            <span className="font-mono font-bold text-[#005bbf]">•••• (4 знака)</span>
          </div>
          <div className="flex justify-between items-center p-2.5 border-b border-[#f1f4fa]">
            <span>Уведомления на телефон</span>
            <span className="text-[#006e2c] font-semibold">Включены</span>
          </div>
          <div className="flex justify-between items-center p-2.5">
            <span>Язык интерфейса</span>
            <span className="font-semibold text-[#181c20]">Русский (RU)</span>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-[#005bbf] text-white hover:bg-[#004493]"
          >
            Готово
          </button>
        </div>
      </div>
    </div>
  );
};
