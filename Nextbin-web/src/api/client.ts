import { getApiUrl } from "@/utils/api-helper";

export interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
  body?: any;
}

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  status: number;
}

export const apiFetch = async <T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> => {
  const baseUrl = getApiUrl();
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint.slice(1) : endpoint;
  let url = `${baseUrl}/${cleanEndpoint}`;

  if (options.params) {
    const searchParams = new URLSearchParams();
    Object.entries(options.params).forEach(([key, val]) => {
      if (val !== undefined && val !== null) {
        searchParams.append(key, String(val));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  // Generate UUID Request ID
  const requestId = typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      });

  let token = null;
  if (typeof window !== "undefined") {
    token = localStorage.getItem("nila_token");
  }

  const headers = new Headers(options.headers);
  headers.set("X-Platform", "web");
  headers.set("X-Request-ID", requestId);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let body = options.body;
  if (
    options.body &&
    typeof options.body === "object" &&
    !(options.body instanceof FormData) &&
    !(options.body instanceof URLSearchParams)
  ) {
    if (!headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    body = JSON.stringify(options.body);
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      body,
    });

    const status = response.status;

    if (status === 204) {
      return { data: null, error: null, status };
    }

    const text = await response.text();
    let data = null;
    let error = null;

    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = text as any;
    }

    if (!response.ok) {
      const apiErrorMsg = data?.detail || data?.message || "An error occurred during the API request.";
      error = typeof apiErrorMsg === "object" ? JSON.stringify(apiErrorMsg) : String(apiErrorMsg);
      data = null;
    }

    return { data, error, status };
  } catch (err: any) {
    return {
      data: null,
      error: err?.message || "Network request failed. Please check backend connection.",
      status: 500,
    };
  }
};
