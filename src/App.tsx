import React, { useState } from 'react';
import { INITIAL_CHILDREN } from './data/initialData';
import {
  NavigationTab,
  ChildProfile,
  AppLimit,
  DeviceItem,
  ToastMessage,
} from './types';
import { Sidebar } from './components/Sidebar';
import { OverviewTab } from './components/OverviewTab';
import { LimitsTab } from './components/LimitsTab';
import { HistoryTab } from './components/HistoryTab';
import { DevicesTab } from './components/DevicesTab';
import { ChildLockScreen } from './components/ChildLockScreen';
import { BrandLogo } from './components/BrandLogo';
import {
  EditQuotaModal,
  EditBedtimeModal,
  EditAppRuleModal,
  AddDeviceModal,
  GeolocationModal,
  HelpModal,
  AccountModal,
} from './components/Modals';
import { playSuccessChime, playLockSound, playDevicePingSound } from './utils/sound';
import confetti from 'canvas-confetti';

export default function App() {
  const [children, setChildren] = useState<ChildProfile[]>(INITIAL_CHILDREN);
  const [activeChildId, setActiveChildId] = useState<string>('alex');
  const [currentTab, setCurrentTab] = useState<NavigationTab>('overview');
  const [appMode, setAppMode] = useState<'parent' | 'child_lock'>('parent');
  const [allDevicesLocked, setAllDevicesLocked] = useState<boolean>(false);

  // Toast feedback
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Modals state
  const [isQuotaModalOpen, setIsQuotaModalOpen] = useState(false);
  const [isBedtimeModalOpen, setIsBedtimeModalOpen] = useState(false);
  const [selectedAppForEdit, setSelectedAppForEdit] = useState<AppLimit | null>(null);
  const [isAddDeviceModalOpen, setIsAddDeviceModalOpen] = useState(false);
  const [selectedDeviceForGeo, setSelectedDeviceForGeo] = useState<DeviceItem | null>(null);
  const [isHelpModalOpen, setIsHelpModalOpen] = useState(false);
  const [isAccountModalOpen, setIsAccountModalOpen] = useState(false);

  const activeChild = children.find((c) => c.id === activeChildId) || children[0];

  const showToast = (title: string, description?: string, type: ToastMessage['type'] = 'success') => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    setToasts((prev) => [...prev, { id, title, description, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  // 1. Add +30 Minutes
  const handleAdd30Minutes = () => {
    setChildren((prev) =>
      prev.map((c) => {
        if (c.id === activeChild.id) {
          return {
            ...c,
            dailyLimitMinutes: c.dailyLimitMinutes + 30,
            events: [
              {
                id: `ev-${Date.now()}`,
                time: new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
                title: '+30 мин добавлено',
                subtitle: 'Родитель продлил экранное время',
                type: 'time_request',
                status: 'approved',
                durationMinutes: 30,
              },
              ...c.events,
            ],
          };
        }
        return c;
      })
    );
    playSuccessChime();
    showToast('+30 минут добавлено!', `Дневной лимит для ${activeChild.name} успешно увеличен.`);

    try {
      confetti({
        particleCount: 40,
        spread: 50,
        origin: { y: 0.6 },
      });
    } catch {}
  };

  // 2. Lock/Unlock Single Main Device
  const handleToggleLockMainDevice = () => {
    const mainDevice = activeChild.devices[0];
    if (!mainDevice) return;

    const willLock = !mainDevice.isLocked;
    if (willLock) {
      playLockSound();
    } else {
      playSuccessChime();
    }

    setChildren((prev) =>
      prev.map((c) => {
        if (c.id === activeChild.id) {
          const updatedDevices = c.devices.map((d, i) =>
            i === 0 ? { ...d, isLocked: willLock } : d
          );
          return {
            ...c,
            devices: updatedDevices,
            events: [
              {
                id: `ev-${Date.now()}`,
                time: new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
                title: willLock ? 'ПК заблокирован' : 'ПК разблокирован',
                subtitle: willLock ? 'Родитель заблокировал устройство' : 'Доступ к ПК разрешен',
                type: willLock ? 'device_locked' : 'device_unlocked',
              },
              ...c.events,
            ],
          };
        }
        return c;
      })
    );

    showToast(
      willLock ? 'Компьютер заблокирован' : 'Компьютер разблокирован',
      willLock ? `${mainDevice.name} переведен в режим блокировки` : 'Доступ восстановлен'
    );
  };

  // 3. Lock/Unlock Specific Device
  const handleToggleLockDevice = (deviceId: string) => {
    setChildren((prev) =>
      prev.map((c) => {
        if (c.id === activeChild.id) {
          const dev = c.devices.find((d) => d.id === deviceId);
          const willLock = dev ? !dev.isLocked : false;
          if (willLock) playLockSound();
          else playSuccessChime();

          return {
            ...c,
            devices: c.devices.map((d) =>
              d.id === deviceId ? { ...d, isLocked: willLock } : d
            ),
          };
        }
        return c;
      })
    );
    showToast('Статус блокировки изменен');
  };

  // 4. Lock All Devices (Emergency master button)
  const handleToggleLockAll = () => {
    const nextLocked = !allDevicesLocked;
    setAllDevicesLocked(nextLocked);

    if (nextLocked) {
      playLockSound();
      showToast('Все устройства заблокированы', 'Все подключенные ПК и смартфоны временно заблокированы.', 'error');
    } else {
      playSuccessChime();
      showToast('Все устройства разблокированы', 'Доступ восстановлен по обычному расписанию.', 'success');
    }

    setChildren((prev) =>
      prev.map((c) => ({
        ...c,
        devices: c.devices.map((d) => ({ ...d, isLocked: nextLocked })),
      }))
    );
  };

  // 5. Update App Limit rule
  const handleUpdateAppLimit = (appId: string, updates: Partial<AppLimit>) => {
    setChildren((prev) =>
      prev.map((c) => {
        if (c.id === activeChild.id) {
          return {
            ...c,
            apps: c.apps.map((app) => (app.id === appId ? { ...app, ...updates } : app)),
          };
        }
        return c;
      })
    );
    showToast('Правило сохранено', 'Параметры приложения обновлены.');
  };

  // 6. Ping device sound
  const handlePingDevice = (device: DeviceItem) => {
    playDevicePingSound();
    showToast('Звуковой сигнал отправлен', `На ${device.name} воспроизводится звуковой маяк.`);
  };

  // 7. Approve Child Request
  const handleApproveRequest = (eventId: string, minutes: number = 30) => {
    setChildren((prev) =>
      prev.map((c) => {
        if (c.id === activeChild.id) {
          return {
            ...c,
            dailyLimitMinutes: c.dailyLimitMinutes + minutes,
            events: c.events.map((ev) =>
              ev.id === eventId ? { ...ev, status: 'approved' } : ev
            ),
          };
        }
        return c;
      })
    );
    playSuccessChime();
    showToast('Запрос одобрен', `Добавлено +${minutes} минут для ${activeChild.name}`);

    try {
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.6 },
      });
    } catch {}
  };

  // 8. Deny Child Request
  const handleDenyRequest = (eventId: string) => {
    setChildren((prev) =>
      prev.map((c) => {
        if (c.id === activeChild.id) {
          return {
            ...c,
            events: c.events.map((ev) =>
              ev.id === eventId ? { ...ev, status: 'denied' } : ev
            ),
          };
        }
        return c;
      })
    );
    showToast('Запрос отклонен', 'Уведомление отправлено на устройство ребенка.', 'warning');
  };

  // 9. Child sends time request from Lock Screen
  const handleChildRequestTime = (reason: string) => {
    setChildren((prev) =>
      prev.map((c) => {
        if (c.id === activeChild.id) {
          return {
            ...c,
            events: [
              {
                id: `ev-${Date.now()}`,
                time: new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
                title: 'Запрос на +30 мин',
                subtitle: `«${reason}»`,
                type: 'time_request',
                status: 'pending',
                requestMinutes: 30,
              },
              ...c.events,
            ],
          };
        }
        return c;
      })
    );
    showToast(`Новый запрос от ${activeChild.name}`, `«${reason}»`, 'info');
  };

  // Render Child Lock Screen if in Lock mode
  if (appMode === 'child_lock') {
    return (
      <ChildLockScreen
        child={activeChild}
        onExitLockScreen={() => setAppMode('parent')}
        onRequestTime={handleChildRequestTime}
      />
    );
  }

  const isMainDeviceLocked = activeChild.devices[0]?.isLocked || allDevicesLocked;

  return (
    <div className="bg-[#f7f9ff] text-[#181c20] min-h-screen flex antialiased">
      {/* Toast Notification Container */}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none max-w-sm w-full">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`p-4 rounded-2xl shadow-xl border backdrop-blur-md pointer-events-auto flex items-start gap-3 animate-in fade-in slide-in-from-bottom-3 duration-200 ${
              toast.type === 'error'
                ? 'bg-[#ffdad6] text-[#93000a] border-[#ffb4ab]'
                : toast.type === 'warning'
                ? 'bg-[#ffdfa0] text-[#795900] border-[#ffdfa0]'
                : toast.type === 'info'
                ? 'bg-[#d8e2ff] text-[#001a41] border-[#adc7ff]'
                : 'bg-white text-[#181c20] border-[#dfe3e8]'
            }`}
          >
            <span className="material-symbols-outlined text-xl mt-0.5 text-[#005bbf]">
              {toast.type === 'error' ? 'error' : toast.type === 'warning' ? 'warning' : 'info'}
            </span>
            <div className="flex-1">
              <p className="text-xs font-bold">{toast.title}</p>
              {toast.description && (
                <p className="text-xs text-[#414754] mt-0.5">{toast.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Desktop Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        childrenList={children}
        activeChild={activeChild}
        onSelectChild={setActiveChildId}
        allDevicesLocked={allDevicesLocked}
        onToggleLockAll={handleToggleLockAll}
        onOpenHelp={() => setIsHelpModalOpen(true)}
        onOpenAccount={() => setIsAccountModalOpen(true)}
        onOpenChildScreen={() => setAppMode('child_lock')}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col md:ml-64 min-h-screen">
        {/* Mobile Top App Bar */}
        <header className="md:hidden sticky top-0 bg-white/95 backdrop-blur-md z-40 px-4 py-3 flex justify-between items-center border-b border-[#dfe3e8]">
          <BrandLogo size="sm" subtitle="" />

          <div className="flex items-center gap-2">
            <button
              onClick={() => setAppMode('child_lock')}
              className="bg-[#d8e2ff] text-[#001a41] text-[11px] font-bold px-2.5 py-1 rounded-lg"
            >
              Режим ребенка
            </button>
            <img
              src={activeChild.avatarUrl}
              alt={activeChild.name}
              className="w-8 h-8 rounded-full object-cover border border-[#dfe3e8]"
            />
          </div>
        </header>

        {/* Dynamic Tab View */}
        <main className="flex-1 p-4 md:p-8 max-w-[1240px] w-full mx-auto pb-24 md:pb-8">
          {currentTab === 'overview' && (
            <OverviewTab
              child={activeChild}
              onAdd30Minutes={handleAdd30Minutes}
              onToggleLockDevice={handleToggleLockMainDevice}
              isMainDeviceLocked={isMainDeviceLocked}
              onOpenEditLimits={() => setIsQuotaModalOpen(true)}
              onNavigateToLimits={() => setCurrentTab('limits')}
              onSelectApp={(app) => setSelectedAppForEdit(app)}
            />
          )}

          {currentTab === 'limits' && (
            <LimitsTab
              child={activeChild}
              onUpdateAppLimit={handleUpdateAppLimit}
              onOpenEditQuota={() => setIsQuotaModalOpen(true)}
              onOpenEditBedtime={() => setIsBedtimeModalOpen(true)}
              onOpenAppModal={(app) => setSelectedAppForEdit(app)}
              onAddNewAppRule={() => {
                const newApp: AppLimit = {
                  id: `app-${Date.now()}`,
                  name: 'Новое приложение',
                  category: 'games',
                  categoryLabel: 'Игры',
                  iconName: 'apps',
                  iconBg: '#E5F2FF',
                  iconColor: '#005bbf',
                  usedMinutes: 0,
                  limitMinutes: 60,
                  isBlocked: false,
                  isAlwaysAllowed: false,
                  scheduleStart: '16:00',
                  scheduleEnd: '18:00',
                  isEnabled: true,
                };
                setChildren((prev) =>
                  prev.map((c) =>
                    c.id === activeChild.id ? { ...c, apps: [newApp, ...c.apps] } : c
                  )
                );
                setSelectedAppForEdit(newApp);
              }}
            />
          )}

          {currentTab === 'history' && (
            <HistoryTab
              child={activeChild}
              onApproveRequest={handleApproveRequest}
              onDenyRequest={handleDenyRequest}
            />
          )}

          {currentTab === 'devices' && (
            <DevicesTab
              child={activeChild}
              onToggleLockDevice={handleToggleLockDevice}
              onPingDevice={handlePingDevice}
              onViewLocation={(dev) => setSelectedDeviceForGeo(dev)}
              onAddNewDevice={() => setIsAddDeviceModalOpen(true)}
            />
          )}
        </main>

        {/* Mobile Bottom Navigation Bar */}
        <nav className="md:hidden fixed bottom-0 w-full bg-white/95 backdrop-blur-md border-t border-[#dfe3e8] z-40 flex justify-around items-center px-2 py-2">
          {[
            { id: 'overview', label: 'Обзор', icon: 'dashboard' },
            { id: 'limits', label: 'Лимиты', icon: 'timer' },
            { id: 'history', label: 'История', icon: 'history' },
            { id: 'devices', label: 'Устройства', icon: 'devices_other' },
          ].map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id as NavigationTab)}
                className={`flex flex-col items-center p-2 rounded-xl transition-all ${
                  isActive ? 'text-[#005bbf] font-bold' : 'text-[#414754]'
                }`}
              >
                <span
                  className="material-symbols-outlined text-2xl"
                  style={{ fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}
                >
                  {item.icon}
                </span>
                <span className="text-[10px] mt-0.5">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Modals */}
      <EditQuotaModal
        isOpen={isQuotaModalOpen}
        onClose={() => setIsQuotaModalOpen(false)}
        currentMinutes={activeChild.dailyLimitMinutes}
        childName={activeChild.name}
        onSave={(mins) => {
          setChildren((prev) =>
            prev.map((c) => (c.id === activeChild.id ? { ...c, dailyLimitMinutes: mins } : c))
          );
          showToast('Лимит обновлен', `Новый дневной лимит: ${Math.floor(mins / 60)}ч ${mins % 60}м`);
        }}
      />

      <EditBedtimeModal
        isOpen={isBedtimeModalOpen}
        onClose={() => setIsBedtimeModalOpen(false)}
        bedtimeStart={activeChild.bedtimeStart}
        bedtimeEnd={activeChild.bedtimeEnd}
        onSave={(start, end) => {
          setChildren((prev) =>
            prev.map((c) => (c.id === activeChild.id ? { ...c, bedtimeStart: start, bedtimeEnd: end } : c))
          );
          showToast('Время отдыха обновлено', `Блокировка с ${start} до ${end}`);
        }}
      />

      <EditAppRuleModal
        isOpen={!!selectedAppForEdit}
        app={selectedAppForEdit}
        onClose={() => setSelectedAppForEdit(null)}
        onSave={handleUpdateAppLimit}
      />

      <AddDeviceModal
        isOpen={isAddDeviceModalOpen}
        onClose={() => setIsAddDeviceModalOpen(false)}
        childName={activeChild.name}
        onDeviceAdded={(newDev) => {
          setChildren((prev) =>
            prev.map((c) =>
              c.id === activeChild.id ? { ...c, devices: [...c.devices, newDev] } : c
            )
          );
          showToast('Устройство подключено', `${newDev.name} успешно добавлено в профиль.`);
        }}
      />

      <GeolocationModal
        isOpen={!!selectedDeviceForGeo}
        device={selectedDeviceForGeo}
        onClose={() => setSelectedDeviceForGeo(null)}
      />

      <HelpModal isOpen={isHelpModalOpen} onClose={() => setIsHelpModalOpen(false)} />

      <AccountModal isOpen={isAccountModalOpen} onClose={() => setIsAccountModalOpen(false)} />
    </div>
  );
}
