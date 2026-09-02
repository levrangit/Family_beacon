const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export interface ParentRegistrationRequest {
  telegram_id: number;
  login: string;
  password: string;
}

export interface ParentRegistrationResponse {
  user_id: string;
  access_token: string;
}

export interface FamilyInviteResponse {
  invite_id: string;
  family_id: string;
  code: string;
  expires_at: string;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });

  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(body.detail || `Request failed with status ${response.status}`);
  }

  return body as T;
}

export function registerParent(
  requestData: ParentRegistrationRequest,
): Promise<ParentRegistrationResponse> {
  return request('/auth/register-parent', {
    method: 'POST',
    body: JSON.stringify(requestData),
  });
}

export function createFamilyInvite(
  accessToken: string,
  familyId: string,
): Promise<FamilyInviteResponse> {
  return request(`/families/${familyId}/invite`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export function redeemFamilyInvite(
  accessToken: string,
  code: string,
): Promise<{ invite_id: string; family_id: string }> {
  return request('/families/redeem-invite', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ code }),
  });
}
