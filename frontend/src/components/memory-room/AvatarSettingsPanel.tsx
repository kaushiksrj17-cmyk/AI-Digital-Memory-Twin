'use client';

import React, { useState } from 'react';
import { AvatarConfig, AvatarModelType, AvatarPose, AvatarSpeechResponse } from '@/types';
import {
  Sparkles,
  Shield,
  Volume2,
  X,
  Play,
  RotateCcw,
  Check,
  AlertTriangle,
  User,
  HelpCircle,
} from 'lucide-react';

interface AvatarSettingsPanelProps {
  avatarConfig: AvatarConfig;
  onUpdateConfig: (updated: Partial<AvatarConfig>) => Promise<void>;
  onTriggerSpeech: (text: string) => Promise<AvatarSpeechResponse | null>;
  onClose: () => void;
}

export function AvatarSettingsPanel({
  avatarConfig,
  onUpdateConfig,
  onTriggerSpeech,
  onClose,
}: AvatarSettingsPanelProps) {
  const [modelType, setModelType] = useState<AvatarModelType>(avatarConfig.model_type);
  const [enabled, setEnabled] = useState<boolean>(avatarConfig.enabled);
  const [speechText, setSpeechText] = useState<string>(
    'This room holds photographs and personal notes preserved by my family across the decades.'
  );
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [speechResult, setSpeechResult] = useState<AvatarSpeechResponse | null>(null);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState<boolean>(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onUpdateConfig({
        enabled,
        model_type: modelType,
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleSpeak = async () => {
    if (!speechText.trim()) return;
    setIsSpeaking(true);
    setSpeechError(null);
    try {
      const res = await onTriggerSpeech(speechText);
      setSpeechResult(res);
    } catch (err: any) {
      setSpeechError(err.message || 'Speech request was blocked or failed.');
    } finally {
      setIsSpeaking(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md"
      role="dialog"
      aria-modal="true"
    >
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-serif text-base font-semibold text-slate-100">
                Memorial Avatar Configuration
              </h3>
              <p className="text-xs text-slate-400">
                Visual presence settings & evidence-grounded speech
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mandatory Ethical Disclosure Banner */}
        <div className="p-4 rounded-2xl bg-amber-950/30 border border-amber-500/40 text-amber-200 text-xs space-y-1.5 shadow-inner">
          <div className="flex items-center gap-2 font-bold tracking-wide uppercase text-[11px] text-amber-400">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>Mandatory Ethical Transparency Disclosure</span>
          </div>
          <p className="text-xs leading-relaxed text-amber-200/90 font-medium">
            AI-GENERATED MEMORIAL REPRESENTATION — NOT THE ACTUAL PERSON.
          </p>
          <p className="text-[11px] text-amber-300/70 leading-normal">
            The visual avatar does not possess consciousness, human feelings, independent intent,
            or supernatural connection. It is an evidence-grounded spatial user interface.
          </p>
        </div>

        {/* Enable / Disable Toggle */}
        <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-950 border border-slate-800">
          <div>
            <div className="text-xs font-semibold text-slate-200">Enable 3D Memorial Avatar</div>
            <div className="text-[11px] text-slate-400">
              Display stylized avatar presence in the central room
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
          </label>
        </div>

        {/* Model Type Selector */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 block">
            Representation Model Style
          </label>
          <div className="grid grid-cols-3 gap-2">
            {[
              {
                id: 'STYLIZED_GENERIC',
                label: 'Stylized Character',
                desc: 'Geometric warm figurine',
              },
              {
                id: 'NEUTRAL_SILHOUETTE',
                label: 'Neutral Silhouette',
                desc: 'Translucent memorial form',
              },
              {
                id: 'AUTHORIZED_KINSHIP_MODEL',
                label: 'Kinship Model',
                desc: 'Verified likeness consent',
              },
            ].map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setModelType(opt.id as AvatarModelType)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  modelType === opt.id
                    ? 'bg-indigo-950/60 border-indigo-500 text-white shadow-md'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-semibold text-xs leading-tight mb-1">{opt.label}</div>
                <div className="text-[10px] opacity-75">{opt.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Speech Synthesis & Memory Guardian Test */}
        <div className="space-y-3 p-4 rounded-2xl bg-slate-950 border border-slate-800">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-200 flex items-center gap-1.5">
              <Volume2 className="w-4 h-4 text-cyan-400" />
              <span>Voice Playback & Memory Guardian Safety</span>
            </span>
            <span className="text-[10px] text-emerald-400">Guardian Protected</span>
          </div>

          <textarea
            value={speechText}
            onChange={(e) => setSpeechText(e.target.value)}
            rows={2}
            className="w-full p-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            placeholder="Enter response text to synthesize through approved memorial voice..."
          />

          <div className="flex items-center justify-between gap-3">
            <button
              onClick={handleSpeak}
              disabled={isSpeaking || !speechText.trim()}
              className="px-3.5 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-xs font-medium text-white flex items-center gap-1.5 shadow-md shadow-cyan-600/20 transition-colors"
            >
              {isSpeaking ? (
                <span>Synthesizing...</span>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5" />
                  <span>Synthesize & Speak</span>
                </>
              )}
            </button>

            {speechResult?.audio_url && (
              <audio controls className="h-7 w-48" src={speechResult.audio_url}>
                Your browser does not support audio.
              </audio>
            )}
          </div>

          {speechError && (
            <div className="p-2 rounded-lg bg-red-950/30 border border-red-500/30 text-[11px] text-red-400">
              {speechError}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={async () => {
              await handleSave();
              onClose();
            }}
            disabled={isSaving}
            className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white flex items-center gap-1.5 shadow-lg shadow-indigo-600/20 transition-colors"
          >
            <Check className="w-3.5 h-3.5" />
            <span>{isSaving ? 'Saving...' : 'Apply Avatar Settings'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
