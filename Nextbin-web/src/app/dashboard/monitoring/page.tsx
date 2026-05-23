"use client";

import { useEffect, useState } from "react";
import { useProjects } from "@/hooks/use-projects";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import {
  Activity,
  Plus,
  Trash2,
  Play,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Lock,
  Globe,
  Clock
} from "lucide-react";
import { toast } from "sonner";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from "recharts";

export default function MonitoringPage() {
  const {
    projects,
    metrics,
    fetchProjects,
    fetchProjectMetrics,
    createProject,
    deleteProject,
    triggerPing,
  } = useProjects();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [expectedStatus, setExpectedStatus] = useState<number>(200);
  const [interval, setIntervalVal] = useState<number>(300);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  useEffect(() => {
    if (selectedProjectId) {
      fetchProjectMetrics(selectedProjectId);
    }
  }, [selectedProjectId, fetchProjectMetrics]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !url) {
      toast.error("Please fill in name and URL.");
      return;
    }

    const payload = {
      name,
      url,
      expected_status_code: expectedStatus,
      check_interval_seconds: interval,
      is_active: true,
    };

    const success = await createProject(payload);
    if (success) {
      toast.success("Monitored target registered successfully.");
      setName("");
      setUrl("");
      setExpectedStatus(200);
      setIntervalVal(300);
      setIsCreateOpen(false);
      fetchProjects();
    } else {
      toast.error("Failed to register target.");
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this website monitor?")) {
      const success = await deleteProject(id);
      if (success) {
        toast.success("Website monitor deleted.");
        if (selectedProjectId === id) setSelectedProjectId(null);
        fetchProjects();
      } else {
        toast.error("Delete operation failed.");
      }
    }
  };

  const handleTrigger = async (id: number) => {
    toast.info("Enqueuing baseline check to worker...");
    const success = await triggerPing(id);
    if (success) {
      toast.success("Task dispatched. Table will update shortly.");
    } else {
      toast.error("Failed to enqueue task.");
    }
  };

  const currentMetrics = selectedProjectId ? metrics[selectedProjectId] || [] : [];
  const chartData = currentMetrics.slice().reverse().map((m) => ({
    time: new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    latency: m.response_time_ms,
  }));

  return (
    <div className="space-y-8 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Service Monitors
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Configure website ping checks, check latency metrics, and inspect SSL expiries
          </p>
        </div>

        {/* Add Monitor Dialog */}
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger
            className="btn-primary"
          >
            <Plus className="w-4 h-4" /> Add Monitor
          </DialogTrigger>
          <DialogContent className="border-violet-950/20 bg-slate-950/90 backdrop-blur-xl text-slate-200">
            <form onSubmit={handleCreate}>
              <DialogHeader>
                <DialogTitle className="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  Register Monitor Target
                </DialogTitle>
                <DialogDescription className="text-slate-400">
                  Configure details for automatic background ping checks.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 py-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400">Project Name</label>
                  <Input
                    placeholder="e.g. Nextbin Landing"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="bg-slate-900 border-violet-950/30 text-slate-100 focus-visible:ring-violet-500"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400">Website Address (URL)</label>
                  <Input
                    placeholder="https://nextbin.in"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="bg-slate-900 border-violet-950/30 text-slate-100 focus-visible:ring-violet-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-400">Expected HTTP Code</label>
                    <Input
                      type="number"
                      value={expectedStatus}
                      onChange={(e) => setExpectedStatus(parseInt(e.target.value) || 200)}
                      className="bg-slate-900 border-violet-950/30 text-slate-100 focus-visible:ring-violet-500"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-400">Interval (seconds)</label>
                    <Input
                      type="number"
                      value={interval}
                      onChange={(e) => setIntervalVal(parseInt(e.target.value) || 300)}
                      className="bg-slate-900 border-violet-950/30 text-slate-100 focus-visible:ring-violet-500"
                    />
                  </div>
                </div>
              </div>

              <DialogFooter>
                <button
                  type="submit"
                  className="btn-primary"
                >
                  Create Monitor
                </button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Main Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Monitors List */}
        <Card className="lg:col-span-2 cyber-panel">
          <CardHeader className="pb-3">
            <CardTitle>Configured Targets</CardTitle>
            <CardDescription className="text-slate-400">Active background checkers list</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow className="border-violet-950/15 hover:bg-transparent">
                  <TableHead className="text-slate-500 font-semibold w-[80px]">Status</TableHead>
                  <TableHead className="text-slate-500 font-semibold">Monitor Profile</TableHead>
                  <TableHead className="text-slate-500 font-semibold">SSL Expiry</TableHead>
                  <TableHead className="text-slate-500 font-semibold text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projects.length > 0 ? (
                  projects.map((proj) => {
                    const isSelected = selectedProjectId === proj.id;
                    return (
                      <TableRow
                        key={proj.id}
                        onClick={() => setSelectedProjectId(proj.id)}
                        className={`border-violet-950/10 cursor-pointer transition-colors ${
                          isSelected ? "bg-violet-950/10 hover:bg-violet-950/15" : "hover:bg-slate-900/30"
                        }`}
                      >
                        <TableCell>
                          {proj.last_status === "UP" ? (
                            <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 flex w-fit items-center gap-1">
                              <CheckCircle className="w-3 h-3" /> UP
                            </Badge>
                          ) : proj.last_status === "DOWN" ? (
                            <Badge className="bg-rose-500/10 text-rose-400 border-rose-500/20 flex w-fit items-center gap-1">
                              <XCircle className="w-3 h-3" /> DOWN
                            </Badge>
                          ) : (
                            <Badge className="bg-slate-800 text-slate-400 border-slate-700 flex w-fit items-center gap-1">
                              <AlertTriangle className="w-3 h-3" /> PENDING
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="font-semibold text-slate-200">{proj.name}</div>
                          <div className="text-[10px] text-slate-500 flex items-center gap-1 mt-0.5 truncate">
                            <Globe className="w-3 h-3" /> {proj.url}
                          </div>
                        </TableCell>
                        <TableCell>
                          {proj.last_status === "UP" ? (
                            <div className="flex items-center gap-1 text-xs text-slate-400">
                              <Lock className="w-3.5 h-3.5 text-violet-400" />
                              <span>SSL active</span>
                            </div>
                          ) : (
                            <span className="text-slate-600 text-xs">--</span>
                          )}
                        </TableCell>
                        <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleTrigger(proj.id)}
                              title="Ping Now"
                              className="btn-icon success"
                            >
                              <Play className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(proj.id)}
                              title="Delete"
                              className="btn-icon danger"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })
                ) : (
                  <TableRow>
                    <TableCell colSpan={4} className="h-24 text-center text-slate-500">
                      No websites registered to monitor.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Latency Charts Widget */}
        <Card className="cyber-panel h-[396px] flex flex-col">
          <CardHeader className="pb-3 border-b border-violet-950/15">
            <CardTitle className="text-base font-semibold">Latency History</CardTitle>
            <CardDescription className="text-slate-400">
              {selectedProjectId
                ? `Response times for ${projects.find((p) => p.id === selectedProjectId)?.name}`
                : "Select a monitor from the table to view graphs"}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 p-4 flex flex-col justify-center">
            {selectedProjectId ? (
              chartData.length > 0 ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="latencyGlow" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} />
                      <YAxis stroke="#475569" fontSize={10} tickLine={false} label={{ value: 'ms', angle: -90, position: 'insideLeft', fill: '#475569' }} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#090d16",
                          borderColor: "rgba(16, 185, 129, 0.2)",
                          borderRadius: "8px",
                          color: "#f8fafc",
                        }}
                      />
                      <Area type="monotone" dataKey="latency" stroke="#34d399" strokeWidth={2} fillOpacity={1} fill="url(#latencyGlow)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center text-slate-500 text-sm flex flex-col items-center gap-2">
                  <Clock className="w-8 h-8 text-slate-600 animate-pulse" />
                  No pings registered yet. Please trigger a check.
                </div>
              )
            ) : (
              <div className="text-center text-slate-500 text-sm flex flex-col items-center gap-2">
                <Activity className="w-8 h-8 text-slate-600" />
                Select a monitor target to view latency trends.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
