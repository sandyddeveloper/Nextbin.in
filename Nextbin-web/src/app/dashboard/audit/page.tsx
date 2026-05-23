"use client";

import { useEffect, useState } from "react";
import { useInstagram } from "@/hooks/use-instagram";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ShieldCheck, RefreshCw, Copy, Check, Terminal } from "lucide-react";
import { toast } from "sonner";

export default function AuditPage() {
  const { auditLogs, fetchAuditLogs, loading } = useInstagram();
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    fetchAuditLogs(100);
  }, [fetchAuditLogs]);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    toast.success("Request ID copied to clipboard.");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getActionBadgeColor = (action: string) => {
    if (action.includes("SUCCESS") || action.includes("LINKED") || action.includes("ADDED")) {
      return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    }
    if (action.includes("FAILED") || action.includes("DELETED") || action.includes("UNLINKED")) {
      return "bg-rose-500/10 text-rose-400 border-rose-500/20";
    }
    return "bg-violet-500/10 text-violet-400 border-violet-500/20";
  };

  return (
    <div className="space-y-8 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            System Security Audit Logs
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Fintech-grade administrative trace logging records and network signatures
          </p>
        </div>

        <Button
          onClick={() => fetchAuditLogs(100)}
          disabled={loading}
          variant="outline"
          className="border-violet-950/20 bg-slate-950/40 text-slate-300 hover:bg-slate-900/60 cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh Audit Streams
        </Button>
      </div>

      {/* Logs Table Card */}
      <Card className="cyber-panel">
        <CardHeader>
          <CardTitle className="text-base font-semibold">Immutable Access Records</CardTitle>
          <CardDescription className="text-slate-400">
            Immutable SQLite records tracking operational event headers, client IPs, and UUID trace codes
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-violet-950/15 hover:bg-transparent">
                  <TableHead className="text-slate-500 font-semibold w-[160px]">Timestamp</TableHead>
                  <TableHead className="text-slate-500 font-semibold">Action Trigger</TableHead>
                  <TableHead className="text-slate-500 font-semibold">IP Address</TableHead>
                  <TableHead className="text-slate-500 font-semibold">Client Platform</TableHead>
                  <TableHead className="text-slate-500 font-semibold">Trace Request-ID</TableHead>
                  <TableHead className="text-slate-500 font-semibold">Additional Details</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {auditLogs.length > 0 ? (
                  auditLogs.map((log) => (
                    <TableRow key={log.id} className="border-violet-950/10 hover:bg-slate-900/30 font-medium">
                      <TableCell className="text-xs text-slate-400">
                        {new Date(log.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Badge className={`${getActionBadgeColor(log.action)} text-[10px] py-0.5 border`}>
                          {log.action}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs text-slate-300">
                        {log.ip_address}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="border-slate-800 text-slate-500 uppercase text-[9px] py-0.5">
                          {log.platform}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1.5 font-mono text-[10px] text-slate-400 bg-slate-950/50 border border-violet-950/15 py-1 px-2 rounded-lg w-fit">
                          <span className="truncate max-w-[80px]" title={log.request_id}>
                            {log.request_id}
                          </span>
                          <button
                            onClick={() => handleCopy(log.request_id)}
                            className="text-slate-500 hover:text-slate-200 transition-colors"
                          >
                            {copiedId === log.request_id ? (
                              <Check className="w-3 h-3 text-emerald-400" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </button>
                        </div>
                      </TableCell>
                      <TableCell className="text-xs text-slate-400 max-w-[200px] truncate" title={log.details || ""}>
                        {log.details ? (
                          <span className="flex items-center gap-1 font-mono text-[10px] text-slate-500">
                            <Terminal className="w-3.5 h-3.5 text-violet-600" />
                            {log.details}
                          </span>
                        ) : (
                          <span className="text-slate-600 font-mono text-[10px]">--</span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="h-24 text-center text-slate-500">
                      No security audit records logged yet.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
