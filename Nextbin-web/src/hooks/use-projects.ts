import { useState, useCallback } from "react";
import {
  MonitoredProject,
  PerformanceMetric,
  listProjectsApi,
  createProjectApi,
  updateProjectApi,
  deleteProjectApi,
  getProjectMetricsApi,
  triggerManualPingApi,
} from "@/api/projects";

export const useProjects = () => {
  const [projects, setProjects] = useState<MonitoredProject[]>([]);
  const [metrics, setMetrics] = useState<Record<number, PerformanceMetric[]>>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    setError(null);
    const { data, error: apiErr } = await listProjectsApi();
    if (data) {
      setProjects(data);
    } else {
      setError(apiErr);
    }
    setLoading(false);
  }, []);

  const fetchProjectMetrics = useCallback(async (id: number, limit: number = 30) => {
    const { data } = await getProjectMetricsApi(id, limit);
    if (data) {
      setMetrics((prev) => ({ ...prev, [id]: data }));
    }
  }, []);

  const createProject = async (payload: Record<string, any>): Promise<boolean> => {
    setError(null);
    const { data, error: apiErr } = await createProjectApi(payload);
    if (data) {
      setProjects((prev) => [...prev, data]);
      return true;
    } else {
      setError(apiErr);
      return false;
    }
  };

  const updateProject = async (id: number, payload: Record<string, any>): Promise<boolean> => {
    setError(null);
    const { data, error: apiErr } = await updateProjectApi(id, payload);
    if (data) {
      setProjects((prev) => prev.map((p) => (p.id === id ? data : p)));
      return true;
    } else {
      setError(apiErr);
      return false;
    }
  };

  const deleteProject = async (id: number): Promise<boolean> => {
    setError(null);
    const { error: apiErr } = await deleteProjectApi(id);
    if (!apiErr) {
      setProjects((prev) => prev.filter((p) => p.id !== id));
      return true;
    } else {
      setError(apiErr);
      return false;
    }
  };

  const triggerPing = async (id: number): Promise<boolean> => {
    const { data } = await triggerManualPingApi(id);
    if (data) {
      setTimeout(() => {
        fetchProjects();
        fetchProjectMetrics(id);
      }, 1500);
      return true;
    }
    return false;
  };

  return {
    projects,
    metrics,
    loading,
    error,
    fetchProjects,
    fetchProjectMetrics,
    createProject,
    updateProject,
    deleteProject,
    triggerPing,
  };
};
