import { apiFetch, ApiResponse } from "./client";

export interface MonitoredProject {
  id: number;
  name: string;
  url: string;
  is_active: boolean;
  check_interval_seconds: number;
  expected_status_code: number;
  last_status: string;
  last_checked_at: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
}

export interface PerformanceMetric {
  id: number;
  project_id: number;
  response_time_ms: number;
  status_code: number | null;
  ssl_days_remaining: number | null;
  is_up: boolean;
  error_message: string | null;
  timestamp: string;
  created_at: string;
}

export const createProjectApi = async (payload: Record<string, any>): Promise<ApiResponse<MonitoredProject>> => {
  return apiFetch<MonitoredProject>("api/v1/projects/", {
    method: "POST",
    body: payload,
  });
};

export const listProjectsApi = async (): Promise<ApiResponse<MonitoredProject[]>> => {
  return apiFetch<MonitoredProject[]>("api/v1/projects/", {
    method: "GET",
  });
};

export const getProjectApi = async (id: number): Promise<ApiResponse<MonitoredProject>> => {
  return apiFetch<MonitoredProject>(`api/v1/projects/${id}`, {
    method: "GET",
  });
};

export const updateProjectApi = async (id: number, payload: Record<string, any>): Promise<ApiResponse<MonitoredProject>> => {
  return apiFetch<MonitoredProject>(`api/v1/projects/${id}`, {
    method: "PUT",
    body: payload,
  });
};

export const deleteProjectApi = async (id: number): Promise<ApiResponse<null>> => {
  return apiFetch<null>(`api/v1/projects/${id}`, {
    method: "DELETE",
  });
};

export const getProjectMetricsApi = async (id: number, limit: number = 100): Promise<ApiResponse<PerformanceMetric[]>> => {
  return apiFetch<PerformanceMetric[]>(`api/v1/projects/${id}/metrics`, {
    method: "GET",
    params: { limit },
  });
};

export const triggerManualPingApi = async (id: number): Promise<ApiResponse<{ message: string }>> => {
  return apiFetch<{ message: string }>(`api/v1/projects/${id}/trigger`, {
    method: "POST",
  });
};
