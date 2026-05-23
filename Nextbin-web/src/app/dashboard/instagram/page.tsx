"use client";

import { useEffect, useState } from "react";
import { useInstagram } from "@/hooks/use-instagram";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  Instagram,
  Plus,
  Trash2,
  RefreshCw,
  Send,
  MessageSquare,
  BookOpen,
  UserCheck,
  AlertTriangle,
  Play,
  Key,
  Clock
} from "lucide-react";
import { toast } from "sonner";

export default function InstagramPage() {
  const {
    accounts,
    rules,
    chatLogs,
    fetchAccounts,
    linkAccount,
    deleteAccount,
    triggerConnect,
    fetchRules,
    createRule,
    fetchChatLogs,
    sendDM,
  } = useInstagram();

  const [isLinkOpen, setIsLinkOpen] = useState(false);
  const [isRuleOpen, setIsRuleOpen] = useState(false);
  const [selectedAccId, setSelectedAccId] = useState<number | null>(null);

  // Link Form State
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Rule Form State
  const [triggerKeyword, setTriggerKeyword] = useState("");
  const [responseText, setResponseText] = useState("");

  // Message Form State
  const [threadId, setThreadId] = useState("");
  const [msgText, setMsgText] = useState("");
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  useEffect(() => {
    if (selectedAccId) {
      fetchRules(selectedAccId);
      fetchChatLogs(selectedAccId);
    }
  }, [selectedAccId, fetchRules, fetchChatLogs]);

  const handleLink = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      toast.error("Please fill in username and password.");
      return;
    }

    const success = await linkAccount({ username, password, is_active: true });
    if (success) {
      toast.success("Instagram account linked. Now submit a connection task.");
      setUsername("");
      setPassword("");
      setIsLinkOpen(false);
      fetchAccounts();
    } else {
      toast.error("Failed to link Instagram account.");
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to unlink this Instagram account?")) {
      const success = await deleteAccount(id);
      if (success) {
        toast.success("Instagram account unlinked.");
        if (selectedAccId === id) setSelectedAccId(null);
        fetchAccounts();
      } else {
        toast.error("Failed to unlink account.");
      }
    }
  };

  const handleConnect = async (id: number) => {
    toast.info("Enqueuing login task to background worker...");
    const success = await triggerConnect(id);
    if (success) {
      toast.success("Connection task queued. Table status will update shortly.");
    } else {
      toast.error("Failed to queue connection task.");
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAccId) return;
    if (!triggerKeyword || !responseText) {
      toast.error("Please fill in trigger keyword and response text.");
      return;
    }

    const success = await createRule(selectedAccId, {
      trigger_keyword: triggerKeyword,
      response_text: responseText,
      is_active: true,
    });

    if (success) {
      toast.success("Keyword reply rule added.");
      setTriggerKeyword("");
      setResponseText("");
      setIsRuleOpen(false);
      fetchRules(selectedAccId);
    } else {
      toast.error("Failed to add rule.");
    }
  };

  const handleSendDM = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAccId) return;
    if (!threadId || !msgText) {
      toast.error("Please fill in Thread ID and message text.");
      return;
    }

    setSending(true);
    toast.info("Submitting Direct Message command to worker...");
    const success = await sendDM(selectedAccId, threadId, msgText);
    if (success) {
      toast.success("Message task submitted. Sent logs will record once completed.");
      setMsgText("");
    } else {
      toast.error("Failed to submit message task.");
    }
    setSending(false);
  };

  const activeRules = selectedAccId ? rules[selectedAccId] || [] : [];
  const activeChatLogs = selectedAccId ? chatLogs[selectedAccId] || [] : [];

  return (
    <div className="space-y-8 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Instagram Automation Agent
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Link Instagram channels, configure auto-reply rule mappings, and audit direct chats
          </p>
        </div>

        {/* Link Account Dialog */}
        <Dialog open={isLinkOpen} onOpenChange={setIsLinkOpen}>
          <DialogTrigger
            className="btn-primary"
          >
            <Plus className="w-4 h-4" /> Link Account
          </DialogTrigger>
          <DialogContent className="border-violet-950/20 bg-slate-950/90 backdrop-blur-xl text-slate-200">
            <form onSubmit={handleLink}>
              <DialogHeader>
                <DialogTitle className="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  Link Instagram channel
                </DialogTitle>
                <DialogDescription className="text-slate-400">
                  Provide credentials. Passwords are encrypted via AES before SQLite save.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 py-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400">Instagram Username / Email</label>
                  <Input
                    placeholder="sandy.webdev18@gmail.com"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="bg-slate-900 border-violet-950/30 text-slate-100 focus-visible:ring-violet-500"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400">Password</label>
                  <Input
                    type="password"
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-slate-900 border-violet-950/30 text-slate-100 focus-visible:ring-violet-500"
                  />
                </div>
              </div>

              <DialogFooter>
                <button type="submit" className="btn-primary">
                  Link Account
                </button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Main Grid Layout */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Linked Accounts List */}
        <Card className="cyber-panel">
          <CardHeader className="pb-3 flex flex-row items-center justify-between space-y-0">
            <div>
              <CardTitle>Linked Channels</CardTitle>
              <CardDescription className="text-slate-400">Select account to configure</CardDescription>
            </div>
            <button
              onClick={fetchAccounts}
              title="Refresh"
              className="btn-icon"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow className="border-violet-950/15 hover:bg-transparent">
                  <TableHead className="text-slate-500 font-semibold">Account</TableHead>
                  <TableHead className="text-slate-500 font-semibold">Status</TableHead>
                  <TableHead className="text-slate-500 font-semibold text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {accounts.length > 0 ? (
                  accounts.map((acc) => {
                    const isSelected = selectedAccId === acc.id;
                    return (
                      <TableRow
                        key={acc.id}
                        onClick={() => setSelectedAccId(acc.id)}
                        className={`border-violet-950/10 cursor-pointer transition-colors ${
                          isSelected ? "bg-violet-950/10 hover:bg-violet-950/15" : "hover:bg-slate-900/30"
                        }`}
                      >
                        <TableCell>
                          <div className="font-semibold text-slate-200 truncate max-w-[120px]" title={acc.username}>
                            {acc.username}
                          </div>
                        </TableCell>
                        <TableCell>
                          {acc.status === "CONNECTED" ? (
                            <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px] py-0.5">
                              CONNECTED
                            </Badge>
                          ) : acc.status === "DISCONNECTED" ? (
                            <Badge className="bg-slate-800 text-slate-400 border-slate-700 text-[10px] py-0.5">
                              UNLINKED
                            </Badge>
                          ) : acc.status === "2FA_REQUIRED" ? (
                            <Badge className="bg-yellow-500/10 text-yellow-400 border-yellow-500/20 text-[10px] py-0.5">
                              2FA REQUIRED
                            </Badge>
                          ) : (
                            <Badge className="bg-rose-500/10 text-rose-400 border-rose-500/20 text-[10px] py-0.5">
                              ERROR
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                          <div className="flex items-center justify-end gap-1">
                            <button
                              onClick={() => handleConnect(acc.id)}
                              title="Connect Login"
                              className="btn-icon success"
                            >
                              <Play className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDelete(acc.id)}
                              title="Unlink"
                              className="btn-icon danger"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })
                ) : (
                  <TableRow>
                    <TableCell colSpan={3} className="h-24 text-center text-slate-500 text-xs">
                      No Instagram channels linked.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Configuration Workspace (Tabs) */}
        <Card className="lg:col-span-2 cyber-panel flex flex-col min-h-[460px]">
          {selectedAccId ? (
            <Tabs defaultValue="chat" className="flex-1 flex flex-col">
              <div className="px-6 py-3 border-b border-violet-950/15 flex items-center justify-between">
                <TabsList className="bg-slate-900 border border-violet-950/20">
                  <TabsTrigger value="chat" className="text-xs flex items-center gap-1.5 cursor-pointer">
                    <MessageSquare className="w-3.5 h-3.5" /> Chat Audit
                  </TabsTrigger>
                  <TabsTrigger value="rules" className="text-xs flex items-center gap-1.5 cursor-pointer">
                    <BookOpen className="w-3.5 h-3.5" /> Auto-Reply Rules
                  </TabsTrigger>
                  <TabsTrigger value="send" className="text-xs flex items-center gap-1.5 cursor-pointer">
                    <Send className="w-3.5 h-3.5" /> Test Dispatch
                  </TabsTrigger>
                </TabsList>
              </div>

              {/* Chat Log Audit */}
              <TabsContent value="chat" className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-4 max-h-[380px]">
                {activeChatLogs.length > 0 ? (
                  <div className="space-y-3">
                    {activeChatLogs.map((log) => (
                      <div
                        key={log.id}
                        className={`p-3 rounded-xl border max-w-[80%] flex flex-col gap-1 ${
                          log.direction === "INCOMING"
                            ? "bg-slate-900/60 border-violet-950/10 self-start text-left mr-auto"
                            : "bg-violet-950/15 border-violet-500/20 self-end text-left ml-auto"
                        }`}
                      >
                        <div className="flex items-center gap-2 text-[10px] text-slate-500">
                          <span className="font-semibold text-slate-400">
                            {log.sender_username}
                          </span>
                          <span>•</span>
                          <span>{new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                        <p className="text-sm text-slate-200">{log.text}</p>
                        <div className="text-[9px] text-slate-600 font-mono mt-0.5 truncate max-w-[200px]" title={log.thread_id}>
                          Thread: {log.thread_id}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="h-48 flex flex-col items-center justify-center text-slate-500 text-xs gap-1">
                    <MessageSquare className="w-8 h-8 text-slate-600" />
                    No direct chat histories logged yet.
                  </div>
                )}
              </TabsContent>

              {/* Rules List */}
              <TabsContent value="rules" className="flex-1 p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-300">Keyword Responder Nodes</h3>
                  
                  {/* Create Rule Dialog */}
                  <Dialog open={isRuleOpen} onOpenChange={setIsRuleOpen}>
                    <DialogTrigger
                      className="btn-primary"
                      style={{ padding: "7px 14px", fontSize: "12px" }}
                    >
                      <Plus className="w-3.5 h-3.5" /> Add Rule
                    </DialogTrigger>
                    <DialogContent className="border-violet-950/20 bg-slate-950/90 backdrop-blur-xl text-slate-200">
                      <form onSubmit={handleCreateRule}>
                        <DialogHeader>
                          <DialogTitle className="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                            Add Auto-Reply Rule
                          </DialogTitle>
                          <DialogDescription className="text-slate-400">
                            Provide matching keyword and the text that should respond automatically.
                          </DialogDescription>
                        </DialogHeader>

                        <div className="space-y-4 py-4">
                          <div className="space-y-1.5">
                            <label className="text-xs font-semibold text-slate-400">Trigger Keyword</label>
                            <Input
                              placeholder="e.g. price"
                              value={triggerKeyword}
                              onChange={(e) => setTriggerKeyword(e.target.value)}
                              className="bg-slate-900 border-violet-950/30 text-slate-100 focus-visible:ring-violet-500"
                            />
                          </div>
                          <div className="space-y-1.5">
                            <label className="text-xs font-semibold text-slate-400">Response Text</label>
                            <Input
                              placeholder="e.g. Our rates start at $20/month. Link in bio!"
                              value={responseText}
                              onChange={(e) => setResponseText(e.target.value)}
                              className="bg-slate-900 border-violet-950/30 text-slate-100 focus-visible:ring-violet-500"
                            />
                          </div>
                        </div>

                        <DialogFooter>
                          <button type="submit" className="btn-primary">
                            Save Rule
                          </button>
                        </DialogFooter>
                      </form>
                    </DialogContent>
                  </Dialog>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  {activeRules.length > 0 ? (
                    activeRules.map((rule) => (
                      <div
                        key={rule.id}
                        className="p-3.5 rounded-xl bg-slate-900/40 border border-violet-950/15 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <Badge className="bg-violet-500/10 text-violet-400 border-violet-500/20 text-xs">
                            Keyword: "{rule.trigger_keyword}"
                          </Badge>
                          <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px]">
                            ACTIVE
                          </Badge>
                        </div>
                        <p className="text-xs text-slate-300 leading-normal">{rule.response_text}</p>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-2 py-12 text-center text-slate-500 text-xs flex flex-col items-center gap-1">
                      <BookOpen className="w-8 h-8 text-slate-600" />
                      No responder rules registered. Auto-reply logic is inactive.
                    </div>
                  )}
                </div>
              </TabsContent>

              {/* Test Dispatch Form */}
              <TabsContent value="send" className="flex-1 p-6">
                <form onSubmit={handleSendDM} className="max-w-md space-y-4">
                  <div className="space-y-1">
                    <h3 className="text-sm font-semibold text-slate-300">Dispatch Direct Message</h3>
                    <p className="text-xs text-slate-500">
                      Submit a Direct Message send command directly to Huey's background task runner
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-400">Target Thread ID</label>
                    <Input
                      placeholder="e.g. 3402823668417103009491281223947"
                      value={threadId}
                      onChange={(e) => setThreadId(e.target.value)}
                      className="bg-slate-900 border-violet-950/30 text-slate-100 focus-visible:ring-violet-500"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-400">Message Text</label>
                    <Input
                      placeholder="Enter test message payload..."
                      value={msgText}
                      onChange={(e) => setMsgText(e.target.value)}
                      className="bg-slate-900 border-violet-950/30 text-slate-100 focus-visible:ring-violet-500"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={sending}
                    className="btn-primary"
                    style={{ opacity: sending ? 0.6 : 1, cursor: sending ? "not-allowed" : "pointer" }}
                  >
                    <Send className="w-4 h-4" />
                    {sending ? "Sending..." : "Dispatch DM"}
                  </button>
                </form>
              </TabsContent>
            </Tabs>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-sm gap-2">
              <Instagram className="w-10 h-10 text-slate-700 animate-pulse-slow" />
              Select a linked Instagram account from the panel to manage automations
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
