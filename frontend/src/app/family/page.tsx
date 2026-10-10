'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Users,
  Shield,
  Heart,
  UserPlus,
  Mail,
  Copy,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowRight,
  ShieldAlert,
  BarChart3,
  FileText,
  KeyRound,
  Sparkles
} from 'lucide-react';
import {
  FamilyMember,
  FamilyInvitation,
  FamilyRole,
  Phase8Metrics
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function FamilyPage() {
  const [members, setMembers] = useState<FamilyMember[]>([]);
  const [invitations, setInvitations] = useState<FamilyInvitation[]>([]);
  const [metrics, setMetrics] = useState<Phase8Metrics | null>(null);
  const [currentRole, setCurrentRole] = useState<FamilyRole>('OWNER');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  // Invitation Modal State
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<FamilyRole>('CONTRIBUTOR');
  const [inviteRelationship, setInviteRelationship] = useState('');
  const [inviteExpiresDays, setInviteExpiresDays] = useState(7);
  const [generatedInviteUrl, setGeneratedInviteUrl] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchFamilyData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch workspace summary
      const wsRes = await fetch(`${API_BASE}/family/workspace`, {
        headers: { 'x-user-id': 'demo-user-001' }
      });
      if (wsRes.ok) {
        const wsData = await wsRes.json();
        setCurrentRole(wsData.current_user_role || 'OWNER');
      }

      // 2. Fetch members
      const memRes = await fetch(`${API_BASE}/family/members`, {
        headers: { 'x-user-id': 'demo-user-001' }
      });
      if (memRes.ok) {
        const memData = await memRes.json();
        setMembers(memData);
      }

      // 3. Fetch invitations
      const invRes = await fetch(`${API_BASE}/family/invitations`, {
        headers: { 'x-user-id': 'demo-user-001' }
      });
      if (invRes.ok) {
        const invData = await invRes.json();
        setInvitations(invData);
      }

      // 4. Fetch metrics
      const metRes = await fetch(`${API_BASE}/family/metrics`, {
        headers: { 'x-user-id': 'demo-user-001' }
      });
      if (metRes.ok) {
        const metData = await metRes.json();
        setMetrics(metData);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error communicating with family service');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFamilyData();
  }, [fetchFamilyData]);

  // Handle Create Invitation
  const handleCreateInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/family/invitations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-user-id': 'demo-user-001'
        },
        body: JSON.stringify({
          email: inviteEmail,
          role: inviteRole,
          relationship_to_subject: inviteRelationship || undefined,
          expires_in_days: inviteExpiresDays
        })
      });
      if (!res.ok) {
        const errJson = await res.json();
        throw new Error(errJson.detail || 'Failed to create invitation');
      }
      const invResp = await res.json();
      setGeneratedInviteUrl(invResp.invite_url || null);
      setFeedback(`Single-use invitation generated for ${inviteEmail}.`);
      setInviteEmail('');
      setInviteRelationship('');
      await fetchFamilyData();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle Revoke Invitation
  const handleRevokeInvite = async (invId: string) => {
    try {
      const res = await fetch(`${API_BASE}/family/invitations/${invId}`, {
        method: 'DELETE',
        headers: { 'x-user-id': 'demo-user-001' }
      });
      if (!res.ok) throw new Error('Revocation failed');
      setFeedback('Invitation successfully revoked.');
      await fetchFamilyData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Handle Role Change
  const handleUpdateRole = async (memberId: string, newRole: FamilyRole) => {
    try {
      const res = await fetch(`${API_BASE}/family/members/${memberId}/role`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-user-id': 'demo-user-001'
        },
        body: JSON.stringify({ role: newRole })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Role update failed');
      }
      setFeedback('Member role permissions updated.');
      await fetchFamilyData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Handle Member Removal
  const handleRemoveMember = async (memberId: string) => {
    if (!confirm('Are you sure you want to remove this family member from the memorial workspace?')) return;
    try {
      const res = await fetch(`${API_BASE}/family/members/${memberId}`, {
        method: 'DELETE',
        headers: { 'x-user-id': 'demo-user-001' }
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Removal failed');
      }
      setFeedback('Member removed from workspace.');
      await fetchFamilyData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Role Badge Renderer
  const renderRoleBadge = (role: FamilyRole) => {
    switch (role) {
      case 'OWNER':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">
            Archive Owner
          </span>
        );
      case 'FAMILY_ADMIN':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
            Family Admin
          </span>
        );
      case 'CONTRIBUTOR':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
            Contributor
          </span>
        );
      case 'VIEWER':
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
            Viewer
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 w-full space-y-6 animate-fadeIn">
      {/* Alerts */}
        {feedback && (
          <div className="p-4 rounded-xl border border-indigo-500/30 bg-indigo-950/40 text-indigo-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>{feedback}</span>
            </div>
            <button onClick={() => setFeedback(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
        )}

        {error && (
          <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-950/40 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
        )}

        {/* Current User Role Header Banner */}
        <div className="p-5 rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-indigo-950/30 to-slate-900 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center font-bold">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-serif text-base font-bold text-white">Your Workspace Access</h3>
                {renderRoleBadge(currentRole)}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Authenticated as Eleanor Vance (Memorial Guardian). Full sovereign authority over members, privacy tiers, and verification.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/family/contributions"
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-colors"
            >
              <FileText className="w-4 h-4" />
              <span>Review Contributions Queue</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>

            <button
              onClick={() => {
                setGeneratedInviteUrl(null);
                setShowInviteModal(true);
              }}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl border border-slate-700 hover:border-slate-600 bg-slate-800 text-slate-200 text-xs font-semibold transition-colors"
            >
              <UserPlus className="w-4 h-4 text-indigo-400" />
              <span>Invite Family Member</span>
            </button>
          </div>
        </div>

        {/* Research Metrics Telemetry Grid */}
        {metrics && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60">
              <span className="text-[11px] font-medium text-slate-400">Evidence Coverage</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-bold font-serif text-emerald-400">
                  {metrics.relationship_evidence_coverage_pct}%
                </span>
                <span className="text-[10px] text-slate-400">Certified Grounding</span>
              </div>
            </div>

            <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60">
              <span className="text-[11px] font-medium text-slate-400">Review Turnaround</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-bold font-serif text-white">
                  {metrics.review_turnaround_time_hours_avg}h
                </span>
                <span className="text-[10px] text-slate-400">Average Review Time</span>
              </div>
            </div>

            <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60">
              <span className="text-[11px] font-medium text-slate-400">Active Kinship Members</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-bold font-serif text-indigo-400">
                  {metrics.active_family_members_count}
                </span>
                <span className="text-[10px] text-slate-400">Authorized Custodians</span>
              </div>
            </div>

            <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60">
              <span className="text-[11px] font-medium text-slate-400">Unauthorized Blocks</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-bold font-serif text-rose-400">
                  {metrics.unauthorized_access_attempts_count}
                </span>
                <span className="text-[10px] text-rose-500/80">RBAC Enforcement</span>
              </div>
            </div>
          </div>
        )}

        {/* Family Members Table */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h3 className="font-serif text-base font-bold text-white flex items-center gap-2">
                <Users className="w-4 h-4 text-indigo-400" />
                <span>Authorized Family Members</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Members with certified rights to access, contribute, or verify memorial recollections.
              </p>
            </div>
            <span className="text-xs text-slate-500 font-mono">
              Total: {members.length} members
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
                  <th className="py-3 px-2">Member</th>
                  <th className="py-3 px-2">Kinship Relationship</th>
                  <th className="py-3 px-2">Role &amp; Permissions</th>
                  <th className="py-3 px-2">Joined</th>
                  <th className="py-3 px-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {members.map((member) => (
                  <tr key={member.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 px-2">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-indigo-600/20 text-indigo-400 flex items-center justify-center font-bold">
                          {member.full_name.charAt(0)}
                        </div>
                        <div>
                          <div className="font-semibold text-white">{member.full_name}</div>
                          <span className="text-[11px] text-slate-400">{member.email}</span>
                        </div>
                      </div>
                    </td>

                    <td className="py-3.5 px-2 text-slate-300">
                      {member.relationship_to_subject || 'Family Relative'}
                    </td>

                    <td className="py-3.5 px-2">
                      {currentRole === 'OWNER' && member.role !== 'OWNER' ? (
                        <select
                          value={member.role}
                          onChange={(e) => handleUpdateRole(member.id, e.target.value as FamilyRole)}
                          className="px-2.5 py-1 rounded-lg border border-slate-700 bg-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500 font-medium"
                        >
                          <option value="FAMILY_ADMIN">Family Admin</option>
                          <option value="CONTRIBUTOR">Contributor</option>
                          <option value="VIEWER">Viewer</option>
                        </select>
                      ) : (
                        renderRoleBadge(member.role)
                      )}
                    </td>

                    <td className="py-3.5 px-2 text-slate-400 font-mono text-[11px]">
                      {new Date(member.joined_at).toLocaleDateString()}
                    </td>

                    <td className="py-3.5 px-2 text-right">
                      {currentRole === 'OWNER' && member.role !== 'OWNER' && (
                        <button
                          onClick={() => handleRemoveMember(member.id)}
                          className="p-1.5 rounded-lg border border-rose-900/40 text-rose-400 hover:bg-rose-950/60 text-xs transition-colors"
                          title="Remove member"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pending Invitations Table */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h3 className="font-serif text-base font-bold text-white flex items-center gap-2">
                <KeyRound className="w-4 h-4 text-amber-400" />
                <span>Single-Use Invitations</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Secure invitation tokens are cryptographically hashed and automatically expire after validity period.
              </p>
            </div>
            <span className="text-xs text-slate-500 font-mono">
              Pending: {invitations.filter((i) => i.status === 'PENDING').length}
            </span>
          </div>

          {invitations.length === 0 ? (
            <p className="text-xs text-slate-500 py-6 text-center italic">
              No pending or historical invitations found.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
                    <th className="py-3 px-2">Recipient Email</th>
                    <th className="py-3 px-2">Role Offered</th>
                    <th className="py-3 px-2">Status</th>
                    <th className="py-3 px-2">Expires At</th>
                    <th className="py-3 px-2">Invited By</th>
                    <th className="py-3 px-2 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-200">
                  {invitations.map((inv) => (
                    <tr key={inv.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3.5 px-2 font-mono text-slate-200">{inv.email}</td>
                      <td className="py-3.5 px-2">{renderRoleBadge(inv.role)}</td>
                      <td className="py-3.5 px-2">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                            inv.status === 'PENDING'
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                              : inv.status === 'ACCEPTED'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          }`}
                        >
                          {inv.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-2 font-mono text-slate-400 text-[11px]">
                        {new Date(inv.expires_at).toLocaleDateString()}
                      </td>
                      <td className="py-3.5 px-2 text-slate-400">{inv.invited_by_name}</td>
                      <td className="py-3.5 px-2 text-right">
                        {inv.status === 'PENDING' && (
                          <button
                            onClick={() => handleRevokeInvite(inv.id)}
                            className="px-2.5 py-1 rounded-lg border border-rose-900/60 text-rose-300 hover:bg-rose-950 text-[11px]"
                          >
                            Revoke
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-lg p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="font-serif text-base font-bold text-white flex items-center gap-2">
                <UserPlus className="w-4 h-4 text-indigo-400" />
                <span>Invite Family Contributor or Custodian</span>
              </h3>
              <button onClick={() => setShowInviteModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            {generatedInviteUrl ? (
              <div className="p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/30 space-y-3">
                <div className="flex items-center gap-2 text-emerald-300 text-xs font-semibold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Invitation Link Generated Successfully!</span>
                </div>
                <p className="text-[11px] text-slate-300 leading-relaxed">
                  Share this single-use link directly with the recipient. For security, this link can only be redeemed once and is not displayed again.
                </p>
                <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-950 border border-slate-800">
                  <input
                    type="text"
                    readOnly
                    value={`${window.location.origin}${generatedInviteUrl}`}
                    className="flex-1 bg-transparent text-xs font-mono text-emerald-400 focus:outline-none"
                  />
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(`${window.location.origin}${generatedInviteUrl}`);
                      setFeedback('Link copied to clipboard!');
                    }}
                    className="p-1.5 rounded-md hover:bg-slate-800 text-slate-300 hover:text-white"
                    title="Copy Link"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                </div>
                <div className="text-right pt-2">
                  <button
                    onClick={() => {
                      setShowInviteModal(false);
                      setGeneratedInviteUrl(null);
                    }}
                    className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Done
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleCreateInvite} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Recipient Email Address
                  </label>
                  <input
                    type="email"
                    required
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="relative@echo-memorial.org"
                    className="w-full p-2.5 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      Assigned Role
                    </label>
                    <select
                      value={inviteRole}
                      onChange={(e) => setInviteRole(e.target.value as FamilyRole)}
                      className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="CONTRIBUTOR">Contributor (Submissions &amp; Suggestions)</option>
                      <option value="FAMILY_ADMIN">Family Admin (Review &amp; Manage)</option>
                      <option value="VIEWER">Viewer (Read-Only Certified Records)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      Invitation Expiry
                    </label>
                    <select
                      value={inviteExpiresDays}
                      onChange={(e) => setInviteExpiresDays(Number(e.target.value))}
                      className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value={3}>3 Days</option>
                      <option value={7}>7 Days (Recommended)</option>
                      <option value={14}>14 Days</option>
                      <option value={30}>30 Days</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Kinship Relationship to Subject (Optional)
                  </label>
                  <input
                    type="text"
                    value={inviteRelationship}
                    onChange={(e) => setInviteRelationship(e.target.value)}
                    placeholder="e.g. Granddaughter, Niece, Lifelong Colleague"
                    className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="flex justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowInviteModal(false)}
                    className="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-300 hover:bg-slate-800"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50"
                  >
                    {isSubmitting ? 'Generating...' : 'Generate Invitation Token'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
