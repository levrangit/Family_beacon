import React from 'react';
import { ChildProfile, DeviceItem } from '../types';

interface DevicesTabProps {
  child: ChildProfile;
  onToggleLockDevice: (deviceId: string) => void;
  onPingDevice: (device: DeviceItem) => void;
  onViewLocation: (device: DeviceItem) => void;
  onAddNewDevice: () => void;
}

export const DevicesTab: React.FC<DevicesTabProps> = ({
  child,
  onToggleLockDevice,
  onPingDevice,
  onViewLocation,
  onAddNewDevice,
}) => {
  return (
    <div className="flex flex-col gap-6 w-full max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="font-display font-bold text-2xl md:text-3xl text-[#181c20]">
            Подключенные устройства
          </h1>
          <p className="text-sm text-[#414754] mt-1">
            Управление и мониторинг доступа к оборудованию {child.name}.
          </p>
        </div>

        <button
          onClick={onAddNewDevice}
          className="bg-[#005bbf] hover:bg-[#004493] text-white text-xs md:text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors flex items-center gap-1.5 shadow-sm"
        >
          <span className="material-symbols-outlined text-lg">add</span>
          <span>Добавить устройство</span>
        </button>
      </div>

      {/* Grid: Main Devices (2 cols) + Security Status Widget (1 col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Devices List (2 cols) */}
        <div className="lg:col-span-2 flex flex-col gap-5">
          {child.devices.map((device) => {
            const isOnline = device.isOnline;
            const isLocked = device.isLocked;

            return (
              <div
                key={device.id}
                className={`bg-white border border-[#dfe3e8] rounded-2xl p-6 card-shadow transition-all ${
                  !isOnline ? 'opacity-90 hover:opacity-100' : 'hover:elevated-shadow'
                }`}
              >
                {/* Device Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3.5">
                    <div className="w-12 h-12 rounded-xl bg-[#f1f4fa] border border-[#dfe3e8] flex items-center justify-center text-[#005bbf]">
                      <span className="material-symbols-outlined text-2xl">
                        {device.type === 'phone'
                          ? 'smartphone'
                          : device.type === 'laptop'
                          ? 'laptop_mac'
                          : device.type === 'tablet'
                          ? 'tablet_mac'
                          : 'desktop_windows'}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-display font-semibold text-base md:text-lg text-[#181c20]">
                        {device.name}
                      </h3>
                      <p className="text-xs text-[#727785]">
                        {device.os} • Синхронизация: {device.lastSync}
                      </p>
                    </div>
                  </div>

                  {/* Status Badge */}
                  {isOnline ? (
                    <div className="bg-[#e5f5e9] text-[#006e2c] px-3 py-1 rounded-full flex items-center gap-1.5 border border-[#86f898]">
                      <div className="w-2 h-2 rounded-full bg-[#006e2c] animate-pulse"></div>
                      <span className="text-xs font-semibold">В сети — Мониторинг активен</span>
                    </div>
                  ) : (
                    <div className="bg-[#dfe3e8]/60 text-[#414754] px-3 py-1 rounded-full flex items-center gap-1.5 border border-[#c1c6d6]">
                      <div className="w-2 h-2 rounded-full bg-[#727785]"></div>
                      <span className="text-xs font-semibold">Не в сети</span>
                    </div>
                  )}
                </div>

                {/* Battery & Hardware Info */}
                <div className="flex items-center gap-2 mb-5 border-b border-[#dfe3e8] pb-4">
                  <span className="material-symbols-outlined text-[#727785] text-lg">
                    {device.batteryLevel > 80
                      ? 'battery_full'
                      : device.batteryLevel > 50
                      ? 'battery_5_bar'
                      : device.batteryLevel > 20
                      ? 'battery_3_bar'
                      : 'battery_1_bar'}
                  </span>
                  <span className="text-xs font-medium text-[#181c20]">
                    {device.batteryLevel}% заряд
                  </span>
                  <span className="text-[#727785] text-xs ml-2">
                    {device.location.address}
                  </span>
                </div>

                {/* Device Actions */}
                <div className="flex flex-wrap gap-2.5">
                  <button
                    onClick={() => onToggleLockDevice(device.id)}
                    className={`text-xs font-semibold px-4 py-2 rounded-xl transition-colors flex items-center gap-1.5 shadow-sm ${
                      isLocked
                        ? 'bg-[#006e2c] text-white hover:bg-[#005320]'
                        : isOnline
                        ? 'bg-[#ffdad6] text-[#93000a] hover:bg-[#ba1a1a] hover:text-white'
                        : 'bg-[#f1f4fa] text-[#005bbf] hover:bg-[#d8e2ff]'
                    }`}
                  >
                    <span className="material-symbols-outlined text-base">
                      {isLocked ? 'lock_open' : 'lock'}
                    </span>
                    <span>
                      {isLocked
                        ? 'Разблокировать'
                        : isOnline
                        ? 'Заблокировать'
                        : 'Блокировка (ожидание)'}
                    </span>
                  </button>

                  <button
                    onClick={() => onPingDevice(device)}
                    className="bg-white text-[#005bbf] border border-[#dfe3e8] hover:bg-[#f1f4fa] text-xs font-semibold px-4 py-2 rounded-xl transition-colors flex items-center gap-1.5 shadow-sm"
                  >
                    <span className="material-symbols-outlined text-base">volume_up</span>
                    <span>Звуковой сигнал</span>
                  </button>

                  <button
                    onClick={() => onViewLocation(device)}
                    className="bg-white text-[#005bbf] border border-[#dfe3e8] hover:bg-[#f1f4fa] text-xs font-semibold px-4 py-2 rounded-xl transition-colors flex items-center gap-1.5 shadow-sm"
                  >
                    <span className="material-symbols-outlined text-base">location_on</span>
                    <span>Геолокация</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Security & System Status Widget */}
        <div className="flex flex-col gap-5">
          {/* Security Status Box */}
          <div className="bg-white border border-[#dfe3e8] rounded-2xl p-6 card-shadow flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#e5f5e9] text-[#006e2c] flex items-center justify-center">
                <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                  verified_user
                </span>
              </div>
              <div>
                <h3 className="font-display font-semibold text-base text-[#181c20]">
                  Безопасность системы
                </h3>
                <p className="text-xs text-[#006e2c] font-medium">Все устройства защищены</p>
              </div>
            </div>

            <div className="flex flex-col gap-2.5 pt-2 text-xs text-[#414754]">
              <div className="flex items-center justify-between p-2 rounded-lg bg-[#f1f4fa]">
                <span className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-base text-[#006e2c]">shield</span>
                  Блокировка опасных сайтов
                </span>
                <span className="font-semibold text-[#006e2c]">Вкл</span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-[#f1f4fa]">
                <span className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-base text-[#006e2c]">search_check</span>
                  Безопасный поиск (SafeSearch)
                </span>
                <span className="font-semibold text-[#006e2c]">Вкл</span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-[#f1f4fa]">
                <span className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-base text-[#005bbf]">sync</span>
                  Фоновый агент «Маяк»
                </span>
                <span className="font-semibold text-[#005bbf]">v2.4.1</span>
              </div>
            </div>
          </div>

          {/* Quick Guidance Info Box */}
          <div className="bg-[#e8f0fe] border border-[#adc7ff] rounded-2xl p-5 flex flex-col gap-3">
            <div className="flex items-center gap-2 text-[#005bbf]">
              <span className="material-symbols-outlined text-xl">lightbulb</span>
              <span className="font-display font-semibold text-sm">Совет родителя</span>
            </div>
            <p className="text-xs text-[#181c20] leading-relaxed">
              На ПК и смартфонах ребенка агент «Семейный маяк» защищен от удаления родительским PIN-кодом.
              При попытке выключить фоновую службу родителю мгновенно отправляется уведомление.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
