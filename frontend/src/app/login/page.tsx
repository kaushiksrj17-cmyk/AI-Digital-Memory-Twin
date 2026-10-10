'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Lock,
  Eye,
  EyeOff,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  UserCheck,
  Users,
  GraduationCap,
  Globe
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { EthicalBanner } from '@/components/EthicalBanner';
import { useToast } from '@/context/ToastContext';

type RoleKey = 'vault_owner' | 'family_member' | 'researcher' | 'visitor';

export default function LoginPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [selectedRole, setSelectedRole] = useState<RoleKey>('vault_owner');
  const [email, setEmail] = useState('guardian@echo-memorial.org');
  const [password, setPassword] = useState('demo-password');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const rolePresets = {
    vault_owner: {
      email: 'guardian@echo-memorial.org',
      password: 'demo-password',
      title: 'Vault Owner / Primary Guardian',
      desc: 'Full administrative sovereignty, consent grants, and editing rights.',
      icon: UserCheck,
      badge: 'Full Clearance',
    },
    family_member: {
      email: 'family@echo.local',
      password: 'password123',
      title: 'Family Circle Member',
      desc: 'View verified memories, contribute stories, listen to authorized voice.',
      icon: Users,
      badge: 'Family Access',
    },
    researcher: {
      email: 'researcher@echo.local',
      password: 'password123',
      title: 'Research Fellow / Ethicist',
      desc: 'De-identified provenance inspection, benchmark evaluation metrics.',
      icon: GraduationCap,
      badge: 'Audit Access',
    },
    visitor: {
      email: 'visitor@echo.local',
      password: 'password123',
      title: 'Memorial Visitor',
      desc: 'Public memorial records only. No access to unverified or private data.',
      icon: Globe,
      badge: 'Read-Only',
    },
  };

  const handleRoleSelect = (roleKey: RoleKey) => {
    setSelectedRole(roleKey);
    setEmail(rolePresets[roleKey].email);
    setPassword(rolePresets[roleKey].password);
    setErrorMsg('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          role: selectedRole,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.access_token) {
          localStorage.setItem('echo_access_token', data.access_token);
          localStorage.setItem('echo_user', JSON.stringify(data.user));
        }
        toast.success(
          'Authenticated successfully',
          `Welcome, ${data.user?.full_name || 'Guardian'}. Vault access granted.`
        );
        router.push('/dashboard');
      } else {
        const err = await response.json();
        setErrorMsg(err.detail || 'Authentication failed. Please verify credentials.');
        toast.error('Authentication error', err.detail);
      }
    } catch (err) {
      // Offline fallback
      localStorage.setItem('echo_role', selectedRole);
      toast.info('Offline Demo Login', `Proceeding as ${rolePresets[selectedRole].title}`);
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-lg space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600/10 dark:bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mx-auto shadow-sm">
            <Lock className="w-6 h-6" />
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Memorial Guardian Sign In
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 max-w-sm mx-auto leading-relaxed">
            Access protected family archives, private evidence vectors, and memory representations.
          </p>
        </div>

        {/* Role Selector Tabs */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
            Select Testing Role / Clearance Level:
          </label>
          <div className="grid grid-cols-2 gap-2">
            {(Object.keys(rolePresets) as RoleKey[]).map((rKey) => {
              const preset = rolePresets[rKey];
              const Icon = preset.icon;
              const isSelected = selectedRole === rKey;
              return (
                <button
                  key={rKey}
                  type="button"
                  onClick={() => handleRoleSelect(rKey)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    isSelected
                      ? 'bg-indigo-50 dark:bg-indigo-950/50 border-indigo-500/50 text-indigo-900 dark:text-indigo-200 shadow-sm ring-1 ring-indigo-500/30'
                      : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <Icon className={`w-4 h-4 ${isSelected ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400'}`} />
                    <Badge variant={isSelected ? 'indigo' : 'neutral'} size="sm">
                      {preset.badge}
                    </Badge>
                  </div>
                  <p className="font-semibold text-xs leading-tight">{preset.title.split(' ')[0]} {preset.title.split(' ')[1]}</p>
                  <p className="text-[10px] text-slate-500 truncate mt-0.5">{preset.desc}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Sign In Form */}
        <form
          onSubmit={handleSubmit}
          className="p-6 sm:p-8 rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 shadow-xl space-y-4"
        >
          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 text-xs text-rose-700 dark:text-rose-300 leading-relaxed">
              {errorMsg}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Authorized Guardian Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full text-xs px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Access Key / Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full text-xs px-3.5 py-2.5 pr-10 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="pt-2">
            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full"
              isLoading={loading}
              iconRight={<ArrowRight className="w-4 h-4" />}
            >
              Sign In as {rolePresets[selectedRole].title.split('/')[0]}
            </Button>
          </div>

          <div className="pt-2 flex items-center justify-between text-[11px] text-slate-500">
            <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Offline USB Verification</span>
            </span>
            <Link href="/" className="hover:text-indigo-600 dark:hover:text-indigo-400">
              Back to Home
            </Link>
          </div>
        </form>

        <EthicalBanner variant="card" />
      </div>
    </div>
  );
}
