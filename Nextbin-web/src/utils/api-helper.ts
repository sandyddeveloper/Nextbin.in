export const getApiUrl = (): string => {
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  if (envUrl) return envUrl;

  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    // Bind to FastAPI default port 8000 on current hostname
    return `${protocol}//${hostname}:8000`;
  }

  return "http://localhost:8000";
};
