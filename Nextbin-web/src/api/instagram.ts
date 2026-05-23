import { apiFetch, ApiResponse } from "./client";

export interface InstagramAccount {
  id: number;
  username: string;
  is_active: boolean;
  status: string; // CONNECTED, DISCONNECTED, ERROR, 2FA_REQUIRED
  last_synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface InstagramRule {
  id: number;
  account_id: number;
  trigger_keyword: string;
  response_text: string;
  is_active: boolean;
  created_at: string;
}

export interface InstagramChatLog {
  id: number;
  account_id: number;
  thread_id: string;
  message_id: string;
  sender_username: string;
  text: string | null;
  direction: string; // INCOMING, OUTGOING
  timestamp: string;
  created_at: string;
}

export interface AuditLogItem {
  id: number;
  user_id: number | null;
  action: string;
  request_id: string;
  platform: string;
  ip_address: string;
  details: string | null;
  created_at: string;
}

export const linkInstagramAccountApi = async (payload: Record<string, any>): Promise<ApiResponse<InstagramAccount>> => {
  return apiFetch<InstagramAccount>("api/v1/instagram/accounts", {
    method: "POST",
    body: payload,
  });
};

export const listInstagramAccountsApi = async (): Promise<ApiResponse<InstagramAccount[]>> => {
  return apiFetch<InstagramAccount[]>("api/v1/instagram/accounts", {
    method: "GET",
  });
};

export const deleteInstagramAccountApi = async (id: number): Promise<ApiResponse<null>> => {
  return apiFetch<null>(`api/v1/instagram/accounts/${id}`, {
    method: "DELETE",
  });
};

export const triggerInstagramConnectionApi = async (id: number): Promise<ApiResponse<{ message: string }>> => {
  return apiFetch<{ message: string }>(`api/v1/instagram/accounts/${id}/connect`, {
    method: "POST",
  });
};

export const createAutoReplyRuleApi = async (accountId: number, payload: Record<string, any>): Promise<ApiResponse<InstagramRule>> => {
  return apiFetch<InstagramRule>(`api/v1/instagram/accounts/${accountId}/rules`, {
    method: "POST",
    body: payload,
  });
};

export const listAutoReplyRulesApi = async (accountId: number): Promise<ApiResponse<InstagramRule[]>> => {
  return apiFetch<InstagramRule[]>(`api/v1/instagram/accounts/${accountId}/rules`, {
    method: "GET",
  });
};

export const getInstagramChatLogsApi = async (accountId: number): Promise<ApiResponse<InstagramChatLog[]>> => {
  return apiFetch<InstagramChatLog[]>(`api/v1/instagram/accounts/${accountId}/logs`, {
    method: "GET",
  });
};

export const sendInstagramDMApi = async (accountId: number, threadId: string, text: string): Promise<ApiResponse<{ message: string }>> => {
  return apiFetch<{ message: string }>(`api/v1/instagram/accounts/${accountId}/send-dm`, {
    method: "POST",
    params: { thread_id: threadId, text },
  });
};

export const getAuditLogsApi = async (limit: number = 100): Promise<ApiResponse<AuditLogItem[]>> => {
  return apiFetch<AuditLogItem[]>("api/v1/auth/audit-logs", {
    method: "GET",
    params: { limit },
  });
};
