import { useState, useCallback } from "react";
import {
  InstagramAccount,
  InstagramRule,
  InstagramChatLog,
  AuditLogItem,
  listInstagramAccountsApi,
  linkInstagramAccountApi,
  deleteInstagramAccountApi,
  triggerInstagramConnectionApi,
  listAutoReplyRulesApi,
  createAutoReplyRuleApi,
  getInstagramChatLogsApi,
  sendInstagramDMApi,
  getAuditLogsApi,
} from "@/api/instagram";

export const useInstagram = () => {
  const [accounts, setAccounts] = useState<InstagramAccount[]>([]);
  const [rules, setRules] = useState<Record<number, InstagramRule[]>>({});
  const [chatLogs, setChatLogs] = useState<Record<number, InstagramChatLog[]>>({});
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAccounts = useCallback(async () => {
    setLoading(true);
    setError(null);
    const { data, error: apiErr } = await listInstagramAccountsApi();
    if (data) {
      setAccounts(data);
    } else {
      setError(apiErr);
    }
    setLoading(false);
  }, []);

  const linkAccount = async (payload: Record<string, any>): Promise<boolean> => {
    setError(null);
    const { data, error: apiErr } = await linkInstagramAccountApi(payload);
    if (data) {
      setAccounts((prev) => [...prev, data]);
      return true;
    } else {
      setError(apiErr);
      return false;
    }
  };

  const deleteAccount = async (id: number): Promise<boolean> => {
    setError(null);
    const { error: apiErr } = await deleteInstagramAccountApi(id);
    if (!apiErr) {
      setAccounts((prev) => prev.filter((acc) => acc.id !== id));
      return true;
    } else {
      setError(apiErr);
      return false;
    }
  };

  const triggerConnect = async (id: number): Promise<boolean> => {
    const { data } = await triggerInstagramConnectionApi(id);
    if (data) {
      setTimeout(() => {
        fetchAccounts();
      }, 2000);
      return true;
    }
    return false;
  };

  const fetchRules = useCallback(async (accountId: number) => {
    const { data } = await listAutoReplyRulesApi(accountId);
    if (data) {
      setRules((prev) => ({ ...prev, [accountId]: data }));
    }
  }, []);

  const createRule = async (accountId: number, payload: Record<string, any>): Promise<boolean> => {
    setError(null);
    const { data, error: apiErr } = await createAutoReplyRuleApi(accountId, payload);
    if (data) {
      setRules((prev) => ({
        ...prev,
        [accountId]: [...(prev[accountId] || []), data],
      }));
      return true;
    } else {
      setError(apiErr);
      return false;
    }
  };

  const fetchChatLogs = useCallback(async (accountId: number) => {
    const { data } = await getInstagramChatLogsApi(accountId);
    if (data) {
      setChatLogs((prev) => ({ ...prev, [accountId]: data }));
    }
  }, []);

  const sendDM = async (accountId: number, threadId: string, text: string): Promise<boolean> => {
    const { data, error: apiErr } = await sendInstagramDMApi(accountId, threadId, text);
    if (data) {
      setTimeout(() => {
        fetchChatLogs(accountId);
      }, 1500);
      return true;
    } else {
      setError(apiErr);
      return false;
    }
  };

  const fetchAuditLogs = useCallback(async (limit: number = 100) => {
    const { data } = await getAuditLogsApi(limit);
    if (data) {
      setAuditLogs(data);
    }
  }, []);

  return {
    accounts,
    rules,
    chatLogs,
    auditLogs,
    loading,
    error,
    fetchAccounts,
    linkAccount,
    deleteAccount,
    triggerConnect,
    fetchRules,
    createRule,
    fetchChatLogs,
    sendDM,
    fetchAuditLogs,
  };
};
