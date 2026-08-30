import { useEffect, useState } from "react";
import {
  PageHeader,
  SectionLabel,
  LoadingState,
  ErrorState,
  EmptyState,
} from "@/components/common/States";
import { api } from "@/api/client";
import { useAuthStore } from "@/store";

type Role = "operator" | "reviewer" | "admin";
type UserRow = {
  id: string;
  email: string;
  name: string;
  role: Role;
  active: boolean;
};

export function AdminUsersPage() {
  const current = useAuthStore((s) => s.user);
  const [users, setUsers] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<string | null>(null);

  useEffect(() => {
    if (current?.role !== "admin") return;
    void api
      .getAdminUsers()
      .then(setUsers)
      .catch((e) =>
        setError(e instanceof Error ? e.message : "Unable to load users."),
      )
      .finally(() => setLoading(false));
  }, [current?.role]);

  async function update(id: string, role: Role) {
    setBusy(id);
    setError("");
    try {
      const updated = await api.updateUserRole(id, role);
      setUsers((items) =>
        items.map((item) => (item.id === id ? updated : item)),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to update role.");
    } finally {
      setBusy(null);
    }
  }

  if (current?.role !== "admin")
    return (
      <ErrorState
        title="Administrator access required"
        description="Only administrators can manage platform roles."
      />
    );
  if (loading) return <LoadingState label="Loading users…" />;
  if (error)
    return (
      <ErrorState
        title="User management unavailable"
        description={error}
        onRetry={() => window.location.reload()}
      />
    );

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Administration"
        title="Users & roles"
        description="Backend-authoritative role assignment for the local PRAMAAN installation."
      />
      {users.length === 0 ? (
        <EmptyState title="No users" />
      ) : (
        <section className="border border-border bg-panel">
          <SectionLabel>{users.length} users</SectionLabel>
          <div className="divide-y divide-border">
            {users.map((u) => (
              <div
                key={u.id}
                className="grid gap-3 px-4 py-3 sm:grid-cols-[minmax(0,1fr)_160px_90px] sm:items-center"
              >
                <div className="min-w-0">
                  <div className="truncate text-[12px] font-medium text-text">
                    {u.name}
                  </div>
                  <div className="truncate text-[10px] text-text-muted">
                    {u.email}
                  </div>
                </div>
                <select
                  value={u.role}
                  disabled={busy === u.id}
                  onChange={(e) => void update(u.id, e.target.value as Role)}
                  className="h-8 border border-border bg-surface px-2 text-[11px] text-text"
                >
                  <option value="operator">Operator</option>
                  <option value="reviewer">Reviewer</option>
                  <option value="admin">Administrator</option>
                </select>
                <span className="text-[10px] text-text-muted">
                  {u.active ? "Active" : "Inactive"}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
