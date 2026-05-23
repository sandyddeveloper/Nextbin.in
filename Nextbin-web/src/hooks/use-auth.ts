import { useState, useEffect, useCallback } from "react";
import { loginApi, getMeApi, UserResponse } from "@/api/auth";

export const useAuth = () => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    const { data, error: apiErr } = await getMeApi();
    if (data) {
      setUser(data);
    } else {
      setUser(null);
      // Clean up token if it expired or became invalid
      if (apiErr === "Could not validate credentials" || apiErr === "Not authenticated") {
        localStorage.removeItem("nila_token");
      } else if (apiErr) {
        setError(apiErr);
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, pass: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    const { data, error: apiErr } = await loginApi(email, pass);
    if (data) {
      localStorage.setItem("nila_token", data.access_token);
      await fetchProfile();
      setLoading(false);
      return true;
    } else {
      setError(apiErr || "Login failed");
      setLoading(false);
      return false;
    }
  };

  const logout = useCallback(() => {
    localStorage.removeItem("nila_token");
    setUser(null);
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("nila_token");
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [fetchProfile]);

  return {
    user,
    loading,
    error,
    login,
    logout,
    refreshUser: fetchProfile,
    isAuthenticated: !!user,
  };
};
