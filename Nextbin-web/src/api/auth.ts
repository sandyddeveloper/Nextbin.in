import { apiFetch, ApiResponse } from "./client";

export interface UserResponse {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const loginApi = async (username: string, password: string): Promise<ApiResponse<TokenResponse>> => {
  const body = new URLSearchParams();
  body.append("username", username);
  body.append("password", password);

  return apiFetch<TokenResponse>("api/v1/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });
};

export const registerApi = async (payload: Record<string, any>): Promise<ApiResponse<UserResponse>> => {
  return apiFetch<UserResponse>("api/v1/auth/register", {
    method: "POST",
    body: payload,
  });
};

export const getMeApi = async (): Promise<ApiResponse<UserResponse>> => {
  return apiFetch<UserResponse>("api/v1/auth/me", {
    method: "GET",
  });
};
