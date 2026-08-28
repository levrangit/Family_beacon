import React from 'react';

interface BrandLogoProps {
  className?: string;
  showText?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  subtitle?: string;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({
  className = '',
  showText = true,
  size = 'md',
  subtitle = 'Панель родителя',
}) => {
  const iconDimensions = {
    sm: 'w-8 h-8',
    md: 'w-11 h-11',
    lg: 'w-14 h-14',
    xl: 'w-20 h-20',
  }[size];

  const titleSize = {
    sm: 'text-base font-bold',
    md: 'text-xl font-bold tracking-tight',
    lg: 'text-2xl font-bold tracking-tight',
    xl: 'text-3xl font-extrabold tracking-tight',
  }[size];

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* SVG Lighthouse & Family Beacon Icon */}
      <div className={`${iconDimensions} relative flex-shrink-0 flex items-center justify-center`}>
        <svg viewBox="0 0 100 100" className="w-full h-full drop-shadow-sm" fill="none" xmlns="http://www.w3.org/2000/svg">
          {/* Yellow/Amber Sun Arc Glow */}
          <path
            d="M50 10 C28 10 12 28 12 50 C12 72 28 88 50 88 C72 88 88 72 88 50 C88 28 72 10 50 10 Z"
            fill="#FBBC05"
            fillOpacity="0.85"
          />
          {/* Outer Protective Blue Ring Shield */}
          <path
            d="M50 6 C25.7 6 6 25.7 6 50 C6 74.3 25.7 94 50 94 C74.3 94 94 74.3 94 50 C94 25.7 74.3 6 50 6 Z M50 14 C69.9 14 86 30.1 86 50 C86 69.9 69.9 86 50 86 C30.1 86 14 69.9 14 50 C14 30.1 30.1 14 50 14 Z"
            fill="#3B5998"
            fillOpacity="0.95"
          />
          {/* Lighthouse Tower Structure (Teal/Cyan) */}
          <path
            d="M45 22 C45 19.8 47.2 18 50 18 C52.8 18 55 19.8 55 22 L56 26 L44 26 Z"
            fill="#20B2AA"
          />
          {/* Light Lantern Room */}
          <rect x="42" y="26" width="16" height="8" rx="2" fill="#3B5998" />
          <circle cx="50" cy="30" r="3.5" fill="#FFF275" />
          {/* Tower Body */}
          <path
            d="M43 34 L38 65 L62 65 L57 34 Z"
            fill="#20B2AA"
          />
          {/* Tower Door / Window */}
          <rect x="47" y="42" width="6" height="8" rx="3" fill="#3B5998" />

          {/* Green Hill / Island Base */}
          <ellipse cx="50" cy="85" rx="38" ry="10" fill="#00A86B" />
          <ellipse cx="60" cy="88" rx="10" ry="3" fill="#FBBC05" />

          {/* Family Silhouettes: Left Parent */}
          <circle cx="30" cy="54" r="5" fill="#3B5998" />
          <path
            d="M20 78 C20 66 26 62 34 62 C37 62 42 66 43 72 C41 77 34 80 20 78 Z"
            fill="#3B5998"
          />

          {/* Right Parent */}
          <circle cx="70" cy="54" r="5" fill="#3B5998" />
          <path
            d="M80 78 C80 66 74 62 66 62 C63 62 58 66 57 72 C59 77 66 80 80 78 Z"
            fill="#3B5998"
          />

          {/* Center Child */}
          <circle cx="50" cy="65" r="4.5" fill="#3B5998" />
          <path
            d="M45 74 C43 74 41 78 41 82 C41 84 43 85 45 85 L46 88 L54 88 L55 85 C57 85 59 84 59 82 C59 78 57 74 55 74 Z"
            fill="#3B5998"
          />
        </svg>
      </div>

      {showText && (
        <div className="flex flex-col">
          <span className={`font-display text-[#005bbf] leading-tight ${titleSize}`}>
            Семейный маяк
          </span>
          {subtitle && (
            <span className="font-sans text-[11px] font-semibold text-[#414754] uppercase tracking-wider mt-0.5">
              {subtitle}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
