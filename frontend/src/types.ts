export type NavigationTab = 'overview' | 'limits' | 'history' | 'devices';

export type AppCategory = 'games' | 'entertainment' | 'education' | 'social' | 'utilities';

export interface AppLimit {
  id: string;
  name: string;
  category: AppCategory;
  categoryLabel: string;
  iconName: string;
  iconBg: string;
  iconColor: string;
  usedMinutes: number;
  limitMinutes: number; // 0 = blocked, -1 = unlimited
  isBlocked: boolean;
  isAlwaysAllowed: boolean;
  scheduleStart?: string;
  scheduleEnd?: string;
  isEnabled: boolean;
}

export interface DeviceItem {
  id: string;
  name: string;
  type: 'phone' | 'laptop' | 'desktop' | 'tablet';
  os: string;
  isOnline: boolean;
  batteryLevel: number;
  lastSync: string;
  isLocked: boolean;
  location: {
    lat: number;
    lng: number;
    address: string;
    city: string;
  };
}

export type EventType = 'app_launch' | 'entertainment_launch' | 'limit_reached' | 'time_request' | 'device_locked' | 'device_unlocked' | 'alert';

export interface ActivityEvent {
  id: string;
  time: string;
  appName?: string;
  category?: string;
  type: EventType;
  durationMinutes?: number;
  title: string;
  subtitle: string;
  status?: 'pending' | 'approved' | 'denied';
  requestMinutes?: number;
}

export interface ChildProfile {
  id: string;
  name: string;
  avatarUrl: string;
  age: number;
  isOnline: boolean;
  monitoringActive: boolean;
  totalTimeMinutes: number;
  dailyLimitMinutes: number;
  bedtimeStart: string;
  bedtimeEnd: string;
  devices: DeviceItem[];
  apps: AppLimit[];
  events: ActivityEvent[];
}

export interface ToastMessage {
  id: string;
  title: string;
  description?: string;
  type?: 'success' | 'warning' | 'error' | 'info';
}
