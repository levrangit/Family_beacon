import React, { useState, useEffect } from 'react';
import { BrandLogo } from './BrandLogo';
import { ChildProfile } from '../types';
import { playSuccessChime } from '../utils/sound';
import confetti from 'canvas-confetti';

interface ChildLockScreenProps {
  child: ChildProfile;
  onExitLockScreen: () => void;
  onRequestTime: (reason: string) => void;
}

export const ChildLockScreen: React.FC<ChildLockScreenProps> = ({
  child,
  onExitLockScreen,
  onRequestTime,
}) => {
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [requestReason, setRequestReason] = useState('');
  const [hasRequested, setHasRequested] = useState(false);
  const [isShuttingDown, setIsShuttingDown] = useState(false);

  // Live countdown ticker simulation (e.g. 14h 30m)
  const [secondsRemaining, setSecondsRemaining] = useState(14 * 3600 + 30 * 60);

  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsRemaining((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const hours = Math.floor(secondsRemaining / 3600);
  const minutes = Math.floor((secondsRemaining % 3600) / 60);
  const seconds = secondsRemaining % 60;

  const handleSubmitRequest = (e: React.FormEvent) => {
    e.preventDefault();
    onRequestTime(requestReason || 'Хочу закончить задание / игру');
    setHasRequested(true);
    setShowRequestModal(false);
    playSuccessChime();

    try {
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.7 },
      });
    } catch {}
  };

  const handleShutdown = () => {
    setIsShuttingDown(true);
    setTimeout(() => {
      setIsShuttingDown(false);
    }, 3000);
  };

  if (isShuttingDown) {
    return (
      <div className="fixed inset-0 bg-[#0d1117] text-white flex flex-col items-center justify-center z-50 animate-in fade-in duration-500">
        <div className="w-12 h-12 rounded-full border-4 border-t-[#005bbf] border-[#2d3135] animate-spin mb-4"></div>
        <p className="font-display font-medium text-lg text-[#dfe3e8]">Завершение работы компьютера...</p>
        <p className="text-xs text-[#727785] mt-1">Отдыхайте от экрана! До завтра.</p>
        <button
          onClick={() => setIsShuttingDown(false)}
          className="mt-6 text-xs text-[#adc7ff] hover:underline"
        >
          Отмена
        </button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-[#f7f9ff] text-[#181c20] min-h-screen flex flex-col items-center justify-center p-4 md:p-8 floating-bg overflow-y-auto z-50">
      {/* Ambient background glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[45%] h-[45%] bg-[#d8e2ff] rounded-full blur-3xl opacity-50 pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[35%] h-[35%] bg-[#6ddd81] rounded-full blur-3xl opacity-25 pointer-events-none"></div>

      {/* Top Bar Switcher to Exit */}
      <div className="absolute top-4 right-4 z-20">
        <button
          onClick={onExitLockScreen}
          className="bg-white/80 backdrop-blur border border-[#dfe3e8] hover:bg-white text-[#005bbf] text-xs font-semibold px-3 py-1.5 rounded-xl transition-all shadow-sm flex items-center gap-1.5"
        >
          <span className="material-symbols-outlined text-base">admin_panel_settings</span>
          <span>Панель родителя</span>
        </button>
      </div>

      {/* Main Lock Screen Card (Matches Screenshot 5) */}
      <main className="w-full max-w-2xl bg-white rounded-3xl shadow-[0px_8px_30px_rgba(0,91,191,0.08)] border border-[#dfe3e8] p-6 md:p-10 flex flex-col items-center text-center relative z-10 my-auto">
        {/* Brand Logo Header */}
        <div className="mb-6 flex flex-col items-center">
          <BrandLogo size="lg" subtitle="Экран блокировки" />
        </div>

        {/* Big Supportive Heading */}
        <h1 className="font-display font-bold text-2xl md:text-3xl text-[#181c20] mb-3">
          Время на сегодня вышло, {child.name}!
        </h1>

        {/* Encouraging Message */}
        <p className="text-sm md:text-base text-[#414754] max-w-lg mb-6 leading-relaxed">
          Ты отлично потрудился и поиграл сегодня. Пора отдохнуть от экрана и заняться чем-нибудь другим.
        </p>

        {/* Countdown Box */}
        <div className="bg-[#f1f4fa] rounded-2xl p-4 mb-6 flex items-center justify-center gap-3 w-full max-w-md border border-[#dfe3e8]">
          <span className="material-symbols-outlined text-[#005bbf] text-2xl">timer</span>
          <span className="font-display font-semibold text-base md:text-lg text-[#181c20]">
            Доступ откроется через{' '}
            <span className="text-[#005bbf] font-bold">
              {hours}ч {minutes}м {seconds < 10 ? `0${seconds}` : seconds}с
            </span>
          </span>
        </div>

        {/* Daily Usage Summary (ИТОГИ ДНЯ) */}
        <div className="w-full mb-8">
          <h2 className="text-[11px] font-semibold text-[#727785] mb-3 uppercase tracking-wider">
            ИТОГИ ДНЯ
          </h2>
          <div className="flex flex-wrap justify-center gap-3">
            <div className="bg-[#f1f4fa] rounded-xl p-3 flex items-center gap-3 min-w-[150px] border border-[#dfe3e8]/60">
              <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center shadow-xs text-[#005bbf]">
                <span className="material-symbols-outlined text-lg">sports_esports</span>
              </div>
              <div className="text-left">
                <div className="text-xs font-semibold text-[#181c20]">Roblox</div>
                <div className="text-[11px] text-[#727785]">2 часа</div>
              </div>
            </div>

            <div className="bg-[#f1f4fa] rounded-xl p-3 flex items-center gap-3 min-w-[150px] border border-[#dfe3e8]/60">
              <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center shadow-xs text-[#ba1a1a]">
                <span className="material-symbols-outlined text-lg">play_circle</span>
              </div>
              <div className="text-left">
                <div className="text-xs font-semibold text-[#181c20]">YouTube</div>
                <div className="text-[11px] text-[#727785]">1 час</div>
              </div>
            </div>

            <div className="bg-[#f1f4fa] rounded-xl p-3 flex items-center gap-3 min-w-[150px] border border-[#dfe3e8]/60">
              <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center shadow-xs text-[#006e2c]">
                <span className="material-symbols-outlined text-lg">public</span>
              </div>
              <div className="text-left">
                <div className="text-xs font-semibold text-[#181c20]">Chrome</div>
                <div className="text-[11px] text-[#727785]">45 минут</div>
              </div>
            </div>
          </div>
        </div>

        {/* Confirmation Banner if Requested */}
        {hasRequested && (
          <div className="w-full max-w-md bg-[#e5f5e9] border border-[#86f898] text-[#006e2c] p-3 rounded-xl mb-6 text-xs font-medium flex items-center gap-2">
            <span className="material-symbols-outlined text-base">mark_email_read</span>
            <span>Запрос на +30 минут отправлен родителям на смартфон!</span>
          </div>
        )}

        {/* Primary Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3.5 w-full justify-center">
          <button
            onClick={() => setShowRequestModal(true)}
            disabled={hasRequested}
            className={`font-display font-semibold text-sm py-3 px-6 rounded-2xl transition-all shadow-sm flex-1 max-w-[280px] ${
              hasRequested
                ? 'bg-[#dfe3e8] text-[#727785] cursor-not-allowed'
                : 'bg-[#005bbf] hover:bg-[#004493] text-white hover:shadow-md'
            }`}
          >
            {hasRequested ? 'Запрос отправлен' : 'Запросить еще 30 минут'}
          </button>

          <button
            onClick={handleShutdown}
            className="bg-transparent border border-[#dfe3e8] hover:bg-[#f1f4fa] text-[#414754] font-display font-semibold text-sm py-3 px-6 rounded-2xl transition-colors flex-1 max-w-[280px]"
          >
            Выключить компьютер
          </button>
        </div>
      </main>

      {/* Time Request Dialog */}
      {showRequestModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-[#dfe3e8]">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-[#005bbf]">
                <span className="material-symbols-outlined text-2xl">add_alarm</span>
                <h3 className="font-display font-bold text-lg text-[#181c20]">Запрос дополнительного времени</h3>
              </div>
              <button
                onClick={() => setShowRequestModal(false)}
                className="text-[#727785] hover:text-[#181c20] p-1"
              >
                <span className="material-symbols-outlined text-lg">close</span>
              </button>
            </div>

            <p className="text-xs text-[#414754] mb-4">
              Напиши родителям, почему тебе нужно еще 30 минут за экраном (например: доделать домашнее задание или доиграть раунд):
            </p>

            <form onSubmit={handleSubmitRequest} className="flex flex-col gap-4">
              <textarea
                rows={3}
                value={requestReason}
                onChange={(e) => setRequestReason(e.target.value)}
                placeholder="Например: Доделываю проект в Scratch для школы..."
                className="w-full bg-[#f1f4fa] border border-[#dfe3e8] rounded-xl p-3 text-xs text-[#181c20] focus:ring-2 focus:ring-[#005bbf] focus:bg-white transition-all resize-none"
                autoFocus
              ></textarea>

              <div className="flex justify-end gap-2.5">
                <button
                  type="button"
                  onClick={() => setShowRequestModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-[#414754] hover:bg-[#f1f4fa]"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-[#005bbf] hover:bg-[#004493] text-white shadow-sm transition-colors"
                >
                  Отправить запрос
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
