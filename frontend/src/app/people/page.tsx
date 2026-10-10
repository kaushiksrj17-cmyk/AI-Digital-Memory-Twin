'use client';

import React from 'react';
import { PeopleCard } from '@/components/PeopleCard';
import { Person } from '@/types';
import { Users, UserPlus } from 'lucide-react';

export default function PeoplePage() {
  const people: Person[] = [
    {
      id: 'demo-person-001',
      memorial_profile_id: 'demo-profile-001',
      full_name: 'Arthur Vance',
      relationship_to_subject: 'Spouse',
      biographical_note: 'Married in Oxford in 1970; preserved personal sailing journals and correspondence.',
      is_deceased: true,
    },
    {
      id: 'demo-person-002',
      memorial_profile_id: 'demo-profile-001',
      full_name: 'Eleanor Vance',
      nickname: 'Ellie',
      relationship_to_subject: 'Daughter',
      biographical_note: 'Primary archival custodian and memorial trustee.',
      is_deceased: false,
    },
    {
      id: 'demo-person-003',
      memorial_profile_id: 'demo-profile-001',
      full_name: 'Thomas Vance',
      relationship_to_subject: 'Son',
      biographical_note: 'Contributed 1984 oral history cassette interviews.',
      is_deceased: false,
    },
    {
      id: 'demo-person-004',
      memorial_profile_id: 'demo-profile-001',
      full_name: 'Prof. Harold Davies',
      relationship_to_subject: 'Academic Mentor',
      biographical_note: 'Literary tutor at Trinity College, Cambridge during the 1960s.',
      is_deceased: true,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
          <Users className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
          <span>Preserved Social Circle ({people.length} individuals recorded)</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {people.map((p) => (
          <PeopleCard key={p.id} person={p} />
        ))}
      </div>
    </div>
  );
}
