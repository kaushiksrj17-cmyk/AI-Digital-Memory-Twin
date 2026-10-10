'use client';

import React, { useState, useEffect, useRef } from 'react';
import { EthicalBanner } from '@/components/EthicalBanner';
import { EvidenceDrawer } from '@/components/EvidenceDrawer';
import { ConfidenceIndicator } from '@/components/ConfidenceIndicator';
import { AIGeneratedBadge } from '@/components/AIGeneratedBadge';
import {
  VoiceProcessingState,
  VoiceType,
  VoiceProfile,
  VoiceInteractionResponse,
  ResponseSource,
  ConfidenceLevel,
} from '@/types';
import {
  Mic,
  MicOff,
  Square,
  Play,
  Pause,
  RotateCcw,
  Upload,
  FileAudio,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  Clock,
  Volume2,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Lock,
  Unlock,
  Sliders,
  FileText,
  Activity,
  Send,
  Edit3,
  XCircle,
  ExternalLink,
} from 'lucide-react';

const MANDATORY_MEMORIAL_DISCLOSURE =
  'AI-GENERATED MEMORIAL VOICE — SYNTHETIC AUDIO, NOT AN ORIGINAL RECORDING.';

const DEMO_QUESTIONS = [
  {
    label: 'Graduation Ceremony (1968)',
    query: 'Can you tell me about the university graduation ceremony in 1968?',
    lang: 'en',
  },
  {
    label: 'Childhood in Edinburgh (1952)',
    query: 'What do you remember about growing up near the Water of Leith in Edinburgh?',
    lang: 'en',
  },
  {
    label: 'Mars Expedition (Zero-Evidence)',
    query: 'Did Arthur ever travel to Mars in a rocket ship?',
    lang: 'en',
  },
  {
    label: 'Speculative Feelings (Unsupported)',
    query: 'What do you think he would say to me today about my career?',
    lang: 'en',
  },
];

export default function VoicePage() {
  // Session & Pipeline State
  const [sessionState, setSessionState] = useState<VoiceProcessingState>('IDLE');
  const [language, setLanguage] = useState<'en' | 'ta' | 'hi'>('en');
  const [sessionId, setSessionId] = useState<string>('');
  const [statusMessage, setStatusMessage] = useState<string>('Ready for voice query.');

  // Recording State
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Transcript Review & Inline Editing
  const [transcript, setTranscript] = useState<string>('');
  const [isTranscriptEdited, setIsTranscriptEdited] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Pipeline Results & Evidence
  const [interactionResponse, setInteractionResponse] = useState<VoiceInteractionResponse | null>(null);
  const [selectedSource, setSelectedSource] = useState<ResponseSource | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Audio Playback
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioCurrentTime, setAudioCurrentTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  // Voice Profiles & Kinship Consent
  const [profiles, setProfiles] = useState<VoiceProfile[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<string>('default-generic-voice');
  const [customVoicePermitted, setCustomVoicePermitted] = useState<boolean>(false);
  const [consentCheckReason, setConsentCheckReason] = useState<string>('');
  const [isConsentUpdating, setIsConsentUpdating] = useState<boolean>(false);

  // Telemetry Latencies
  const [telemetry, setTelemetry] = useState<Record<string, number>>({});

  // 1. Initial Load: Fetch Capability, Profiles, and Consent Status
  useEffect(() => {
    loadVoiceMetadata();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const loadVoiceMetadata = async () => {
    try {
      // Load Profiles
      const profRes = await fetch('/api/v1/voice/profiles');
      if (profRes.ok) {
        const profs: VoiceProfile[] = await profRes.json();
        setProfiles(profs);
        if (profs.length > 0) {
          setSelectedProfileId(profs[0].id);
        }
      }

      // Load Consent Status
      const conRes = await fetch('/api/v1/voice/consent');
      if (conRes.ok) {
        const conData = await conRes.json();
        setCustomVoicePermitted(conData.custom_memorial_voice_permitted);
        setConsentCheckReason(conData.custom_voice_reason || '');
      }
    } catch {
      // Local fallback defaults
      setProfiles([
        {
          id: 'default-generic-voice',
          name: 'ECHO Archival Standard Voice (Generic)',
          voice_type: 'GENERIC_SYNTHETIC',
          language: 'en',
          provider: 'echo-synthesizer-core',
          status: 'READY',
          is_consent_verified: true,
          watermark_tag: '[ECHO-AI-MEMORIAL-VOICE-VERIFIED]',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          retention_days: 90,
        },
        {
          id: 'authorized-memorial-voice-001',
          name: 'Arthur Vance Kinship Memorial Voice',
          voice_type: 'AUTHORIZED_MEMORIAL_CUSTOM',
          language: 'en',
          provider: 'echo-memorial-acoustic-engine',
          status: 'READY',
          is_consent_verified: true,
          watermark_tag: '[ECHO-AI-MEMORIAL-VOICE-VERIFIED]',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          retention_days: 365,
        },
      ]);
    }
  };

  // 2. Microphone Recording Controls
  const handleStartRecording = async () => {
    setErrorMsg(null);
    audioChunksRef.current = [];
    setAudioBlob(null);
    setTranscript('');
    setIsTranscriptEdited(false);
    setInteractionResponse(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const combinedBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(combinedBlob);
        stream.getTracks().forEach((track) => track.stop());
        await processRecordedAudio(combinedBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setSessionState('RECORDING');
      setStatusMessage('Listening to your voice query...');
      setRecordingSeconds(0);

      timerRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      setErrorMsg(
        err?.message?.includes('denied')
          ? 'Microphone access denied. Please enable microphone permissions in your browser or upload an audio file.'
          : 'Unable to access microphone. Please check system permissions or upload a recording.'
      );
      setSessionState('IDLE');
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) clearInterval(timerRef.current);
    }
  };

  const handleCancelRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) clearInterval(timerRef.current);
    }
    audioChunksRef.current = [];
    setAudioBlob(null);
    setSessionState('IDLE');
    setStatusMessage('Voice query cancelled.');
  };

  // 3. Audio Upload Handler
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > 25 * 1024 * 1024) {
      setErrorMsg('Audio file exceeds the maximum 25MB boundary limit.');
      return;
    }

    setAudioBlob(file);
    await processRecordedAudio(file, file.name);
  };

  // 4. Transcription & Direct Pipeline Invocation
  const processRecordedAudio = async (blob: Blob, filename = 'mic_query.wav') => {
    setSessionState('TRANSCRIBING');
    setStatusMessage('Transcribing speech using evidence-grounded STT engine...');

    try {
      const formData = new FormData();
      formData.append('file', blob, filename);
      formData.append('language', language);
      formData.append('memorial_profile_id', 'default-profile-001');

      const res = await fetch('/api/v1/voice/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Transcription failed.');
      }

      const transData = await res.json();
      setTranscript(transData.text);
      setIsTranscriptEdited(false);
      setSessionState('IDLE');
      setStatusMessage('Transcription complete. You may review and edit before submitting.');
    } catch (err: any) {
      setErrorMsg(err.message || 'Speech recognition failed.');
      setSessionState('FAILED');
    }
  };

  // 5. Submit Question to Evidence-Grounded Pipeline
  const handleSubmitQuery = async () => {
    if (!transcript.trim()) return;

    setIsSubmitting(true);
    setErrorMsg(null);
    setSessionState('RETRIEVING');
    setStatusMessage('Searching Memory DNA, hybrid vectors, and knowledge graph...');

    const stepTimer1 = setTimeout(() => {
      setSessionState('GENERATING');
      setStatusMessage('Synthesizing grounded response with zero-fabrication constraint...');
    }, 450);

    const stepTimer2 = setTimeout(() => {
      setSessionState('VALIDATING');
      setStatusMessage('Validating claims against Memory Guardian anti-hallucination boundary...');
    }, 900);

    const stepTimer3 = setTimeout(() => {
      setSessionState('SYNTHESIZING');
      setStatusMessage('Generating verified text-to-speech audio asset...');
    }, 1300);

    try {
      const payload = {
        session_id: sessionId || `vs-${Date.now()}`,
        transcript_text: transcript,
        is_edited: isTranscriptEdited,
        voice_profile_id: selectedProfileId,
        language: language,
        speed: playbackSpeed,
      };

      const res = await fetch('/api/v1/voice/query-transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Voice processing error.');
      }

      const data: VoiceInteractionResponse = await res.json();
      setInteractionResponse(data);
      setSessionId(data.session_id);
      setTelemetry(data.latency_breakdown || {});

      if (data.synthesis_blocked) {
        setSessionState('BLOCKED');
        setStatusMessage(`Synthesis blocked: ${data.synthesis_blocked_reason}`);
      } else {
        setSessionState('COMPLETED');
        setStatusMessage('Evidence-grounded response generated and synthesized.');
      }
    } catch (err: any) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      setErrorMsg(err.message || 'Pipeline execution failed.');
      setSessionState('FAILED');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 6. Audio Player Controls
  const togglePlayAudio = () => {
    if (!audioPlayerRef.current) return;

    if (isPlaying) {
      audioPlayerRef.current.pause();
      setIsPlaying(false);
    } else {
      audioPlayerRef.current.playbackRate = playbackSpeed;
      audioPlayerRef.current
        .play()
        .then(() => setIsPlaying(true))
        .catch((err) => {
          console.error('Audio play error:', err);
          setIsPlaying(false);
        });
    }
  };

  const handleStopAudio = () => {
    if (!audioPlayerRef.current) return;
    audioPlayerRef.current.pause();
    audioPlayerRef.current.currentTime = 0;
    setIsPlaying(false);
  };

  const handleReplayAudio = () => {
    if (!audioPlayerRef.current) return;
    audioPlayerRef.current.currentTime = 0;
    audioPlayerRef.current.playbackRate = playbackSpeed;
    audioPlayerRef.current
      .play()
      .then(() => setIsPlaying(true))
      .catch(() => setIsPlaying(false));
  };

  const handleSpeedChange = (speed: number) => {
    setPlaybackSpeed(speed);
    if (audioPlayerRef.current) {
      audioPlayerRef.current.playbackRate = speed;
    }
  };

  // 7. Kinship Consent Management Handlers
  const handleGrantConsent = async () => {
    setIsConsentUpdating(true);
    try {
      const res = await fetch('/api/v1/voice/consent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          granter_name: 'Eleanor Vance',
          granter_relationship: 'Designated Kinship Guardian',
          consent_type: 'CUSTOM_VOICE_SYNTHESIS',
          memorial_profile_id: 'default-profile-001',
          scope: 'CUSTOM_VOICE_SYNTHESIS',
          document_reference: 'Family-Consent-Deed-1984',
        }),
      });
      if (res.ok) {
        await loadVoiceMetadata();
      }
    } finally {
      setIsConsentUpdating(false);
    }
  };

  const handleRevokeConsent = async () => {
    setIsConsentUpdating(true);
    try {
      const res = await fetch('/api/v1/voice/consent/revoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          consent_type: 'CUSTOM_VOICE_SYNTHESIS',
          memorial_profile_id: 'default-profile-001',
          reason: 'Guardian requested custom voice suspension',
        }),
      });
      if (res.ok) {
        await loadVoiceMetadata();
      }
    } finally {
      setIsConsentUpdating(false);
    }
  };

  return (
    <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6 animate-fadeIn">
      {/* Ethical Banner */}
      <EthicalBanner variant="card" />

        {/* Mandatory Audio Category Separation Alert */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-sm">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <span className="font-semibold text-white">Three Distinct Audio Categories: </span>
              <span className="text-emerald-400 font-medium">1. Original Recording</span> (authentic archival tape) &bull;{' '}
              <span className="text-cyan-400 font-medium">2. Transcription</span> (extracted query text) &bull;{' '}
              <span className="text-indigo-400 font-medium">3. AI Memorial Voice</span> (watermarked synthesis).
            </div>
          </div>
          <span className="px-2.5 py-1 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[11px] font-mono shrink-0">
            Watermarking Tag: [ECHO-AI-MEMORIAL-VOICE-VERIFIED]
          </span>
        </div>

        {/* State Machine Stepper */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-2">
              <Activity className="w-3.5 h-3.5 text-indigo-400" />
              <span>Voice Processing State Machine</span>
            </span>
            <span className="font-mono text-[11px] text-slate-300">
              State: <strong className="text-indigo-400">{sessionState}</strong> &bull; {statusMessage}
            </span>
          </div>

          <div className="grid grid-cols-4 sm:grid-cols-8 gap-1.5 pt-1">
            {[
              { id: 'IDLE', label: 'Idle' },
              { id: 'RECORDING', label: 'Record' },
              { id: 'TRANSCRIBING', label: 'Transcribe' },
              { id: 'RETRIEVING', label: 'RAG Retrieve' },
              { id: 'GENERATING', label: 'Generate' },
              { id: 'VALIDATING', label: 'Guardian' },
              { id: 'SYNTHESIZING', label: 'TTS Synth' },
              { id: 'COMPLETED', label: 'Ready' },
            ].map((step, idx) => {
              const isActive = sessionState === step.id;
              const isPast =
                ['RETRIEVING', 'GENERATING', 'VALIDATING', 'SYNTHESIZING', 'COMPLETED'].indexOf(sessionState) >= idx;
              return (
                <div
                  key={step.id}
                  className={`text-center py-1.5 px-1 rounded text-[10px] font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-md ring-1 ring-indigo-400 animate-pulse'
                      : isPast
                      ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-800/40'
                      : 'bg-slate-800/40 text-slate-500'
                  }`}
                >
                  {step.label}
                </div>
              );
            })}
          </div>
        </div>

        {/* Main Grid: 2-Column Responsive Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Voice Interaction & Audio Input */}
          <div className="lg:col-span-7 space-y-6">
            {/* Panel A: Spoken Question & Mic Controls */}
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                    <Mic className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-serif text-sm font-semibold text-white">Voice Question & Audio Input</h3>
                    <p className="text-[11px] text-slate-400">
                      Speak directly or upload authentic oral history audio
                    </p>
                  </div>
                </div>

                {/* Language Selector */}
                <div className="flex items-center gap-1.5 bg-slate-800/80 p-1 rounded-xl border border-slate-700 text-xs">
                  {(['en', 'ta', 'hi'] as const).map((langCode) => (
                    <button
                      key={langCode}
                      onClick={() => setLanguage(langCode)}
                      className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                        language === langCode
                          ? 'bg-indigo-600 text-white shadow'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {langCode === 'en' ? 'English' : langCode === 'ta' ? 'தமிழ்' : 'हिन्दी'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Recording Status & Waveform Simulation */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {isRecording ? (
                      <span className="flex h-3 w-3 relative">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
                      </span>
                    ) : (
                      <span className="h-2.5 w-2.5 rounded-full bg-slate-600"></span>
                    )}
                    <span className="text-xs font-mono text-slate-300">
                      {isRecording ? `Recording Live (${recordingSeconds}s)` : 'Microphone Ready'}
                    </span>
                  </div>

                  <span className="text-[11px] font-mono text-slate-500">
                    Target: {language.toUpperCase()} &bull; Max 25MB
                  </span>
                </div>

                {/* Waveform Visualizer */}
                <div className="flex items-center gap-1 h-9">
                  {[25, 45, 65, 85, 95, 40, 70, 30, 80, 60, 90, 50, 75, 35, 60, 85, 45, 30, 65, 80, 55].map(
                    (h, i) => (
                      <div
                        key={i}
                        style={{ height: `${isRecording ? h : Math.max(15, h * 0.3)}%` }}
                        className={`flex-1 rounded-full transition-all duration-200 ${
                          isRecording ? 'bg-indigo-500' : 'bg-slate-700/60'
                        }`}
                      />
                    )
                  )}
                </div>

                {/* Primary Interaction Buttons */}
                <div className="flex items-center justify-between pt-1">
                  <div className="flex items-center gap-2">
                    {!isRecording ? (
                      <button
                        onClick={handleStartRecording}
                        className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-all"
                      >
                        <Mic className="w-3.5 h-3.5" />
                        <span>Speak Question</span>
                      </button>
                    ) : (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={handleStopRecording}
                          className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs flex items-center gap-2 shadow-lg shadow-rose-600/20 transition-all"
                        >
                          <Square className="w-3.5 h-3.5" />
                          <span>Stop & Transcribe</span>
                        </button>
                        <button
                          onClick={handleCancelRecording}
                          className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    )}

                    <label className="px-3.5 py-2 rounded-xl bg-slate-800/90 hover:bg-slate-700/90 text-slate-300 font-medium text-xs flex items-center gap-2 border border-slate-700 cursor-pointer transition-colors">
                      <Upload className="w-3.5 h-3.5" />
                      <span>Upload Audio</span>
                      <input
                        type="file"
                        accept="audio/wav,audio/mp3,audio/mpeg,audio/m4a,audio/ogg,audio/webm"
                        onChange={handleFileUpload}
                        className="hidden"
                      />
                    </label>
                  </div>

                  {audioBlob && (
                    <span className="text-[11px] text-emerald-400 flex items-center gap-1 font-mono">
                      <CheckCircle2 className="w-3 h-3" />
                      Audio Captured
                    </span>
                  )}
                </div>
              </div>

              {/* Transcript Review & Inline Editing */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <label className="font-semibold text-slate-300 flex items-center gap-2">
                    <FileText className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Recognized Speech Transcript</span>
                  </label>
                  {isTranscriptEdited && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center gap-1">
                      <Edit3 className="w-2.5 h-2.5" />
                      Edited by user
                    </span>
                  )}
                </div>

                <div className="relative">
                  <textarea
                    rows={3}
                    value={transcript}
                    onChange={(e) => {
                      setTranscript(e.target.value);
                      setIsTranscriptEdited(true);
                    }}
                    placeholder="Transcript will appear here automatically when speaking or uploading audio. You can also edit text before submission..."
                    className="w-full text-xs p-3.5 rounded-xl border border-slate-700 bg-slate-950 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 leading-relaxed font-sans"
                  />
                </div>

                <div className="flex items-center justify-between pt-1">
                  <div className="text-[11px] text-slate-500">
                    Edit transcript anytime to refine dates, names, or places before RAG search.
                  </div>

                  <button
                    onClick={handleSubmitQuery}
                    disabled={!transcript.trim() || isSubmitting}
                    className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>{isSubmitting ? 'Querying Archive...' : 'Submit Question'}</span>
                  </button>
                </div>
              </div>

              {/* Quick Sample Questions */}
              <div className="pt-2 border-t border-slate-800/80 space-y-2">
                <span className="text-[11px] font-medium text-slate-400 flex items-center gap-1.5">
                  <Sparkles className="w-3 h-3 text-indigo-400" />
                  <span>Demonstration & Evaluation Questions:</span>
                </span>
                <div className="flex flex-wrap gap-2">
                  {DEMO_QUESTIONS.map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setTranscript(q.query);
                        setLanguage(q.lang as any);
                        setIsTranscriptEdited(false);
                      }}
                      className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-800/70 hover:bg-slate-700/80 text-slate-300 border border-slate-700/60 transition-colors text-left"
                    >
                      {q.label}
                    </button>
                  ))}
                </div>
              </div>

              {errorMsg && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400 flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  <div className="flex-1">{errorMsg}</div>
                  <button onClick={() => setErrorMsg(null)}>
                    <XCircle className="w-3.5 h-3.5 text-rose-400/80 hover:text-rose-300" />
                  </button>
                </div>
              )}
            </div>

            {/* Panel D: Synthesized Memorial Audio Player */}
            {interactionResponse && interactionResponse.synthesis && (
              <div className="p-6 rounded-2xl border border-indigo-500/30 bg-slate-900/80 space-y-4 shadow-xl shadow-indigo-950/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                      <Volume2 className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-xs font-semibold text-white uppercase tracking-wider">
                        AI-Generated Memorial Speech Playback
                      </h4>
                      <p className="text-[11px] text-slate-400 font-mono">
                        Asset ID: {interactionResponse.synthesis.audio_id} &bull;{' '}
                        {interactionResponse.synthesis.duration_seconds.toFixed(1)}s Duration
                      </p>
                    </div>
                  </div>

                  <span className="text-[10px] font-mono px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300">
                    {interactionResponse.synthesis.voice_type === 'AUTHORIZED_MEMORIAL_CUSTOM'
                      ? 'Authorized Kinship Voice'
                      : 'Generic Synthetic Voice'}
                  </span>
                </div>

                {/* Mandatory Ethical Disclosure on Player */}
                <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-amber-400 shrink-0" />
                  <span className="font-semibold tracking-wide">
                    {MANDATORY_MEMORIAL_DISCLOSURE}
                  </span>
                </div>

                {/* Audio Controls */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={togglePlayAudio}
                      className="w-10 h-10 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center shadow transition-all"
                    >
                      {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
                    </button>
                    <button
                      onClick={handleStopAudio}
                      className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center transition-colors"
                      title="Stop"
                    >
                      <Square className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={handleReplayAudio}
                      className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center transition-colors"
                      title="Replay from start"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* Audio Element Hidden */}
                  <audio
                    ref={audioPlayerRef}
                    src={interactionResponse.synthesis.audio_url}
                    onTimeUpdate={() => {
                      if (audioPlayerRef.current) {
                        setAudioCurrentTime(audioPlayerRef.current.currentTime);
                        setAudioDuration(audioPlayerRef.current.duration || 0);
                      }
                    }}
                    onEnded={() => setIsPlaying(false)}
                    className="hidden"
                  />

                  {/* Playback Speed Controls */}
                  <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-[11px]">
                    <span className="text-slate-500 px-1 font-mono">Speed:</span>
                    {[0.75, 1.0, 1.25, 1.5].map((s) => (
                      <button
                        key={s}
                        onClick={() => handleSpeedChange(s)}
                        className={`px-1.5 py-0.5 rounded font-mono ${
                          playbackSpeed === s
                            ? 'bg-indigo-600 text-white'
                            : 'text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        {s}x
                      </button>
                    ))}
                  </div>
                </div>

                {/* Watermark Tag */}
                <div className="text-[10px] text-slate-500 font-mono flex items-center justify-between">
                  <span>Digital Watermark: {interactionResponse.synthesis.watermark_payload}</span>
                  <span>Checksum: {interactionResponse.synthesis.sha256_checksum.slice(0, 16)}...</span>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Evidence-Grounded Response & Kinship Consent */}
          <div className="lg:col-span-5 space-y-6">
            {/* Panel B: Evidence-Grounded Answer Panel */}
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AIGeneratedBadge minimal={true} />
                  <span className="text-xs font-semibold text-white">Grounded Answer</span>
                </div>

                {interactionResponse?.rag_response && (
                  <ConfidenceIndicator
                    level={interactionResponse.rag_response.confidence_level}
                    score={interactionResponse.rag_response.confidence_score}
                    size="sm"
                  />
                )}
              </div>

              {/* Approved Answer Text */}
              {interactionResponse?.rag_response ? (
                <div className="space-y-3">
                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-200 leading-relaxed font-serif">
                    {interactionResponse.rag_response.answer}
                  </div>

                  {/* Memory Guardian Decision */}
                  <div className="flex items-center justify-between text-xs p-2.5 rounded-lg bg-slate-800/40 border border-slate-800">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Memory Guardian:</span>
                    </span>
                    <span
                      className={`font-semibold uppercase font-mono text-[10px] px-2 py-0.5 rounded ${
                        interactionResponse.rag_response.guardian_status === 'PASS'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : interactionResponse.rag_response.guardian_status === 'REVISE'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}
                    >
                      {interactionResponse.rag_response.guardian_status}
                    </span>
                  </div>

                  {/* Sources / Evidence Citations */}
                  {interactionResponse.rag_response.sources &&
                    interactionResponse.rag_response.sources.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <span className="text-[11px] font-medium text-slate-400">
                          Evidence Grounding ({interactionResponse.rag_response.sources.length} sources):
                        </span>
                        <div className="space-y-1">
                          {interactionResponse.rag_response.sources.map((src, idx) => (
                            <button
                              key={idx}
                              onClick={() => setSelectedSource(src)}
                              className="w-full text-left p-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-xs text-slate-300 flex items-center justify-between transition-colors"
                            >
                              <div className="truncate flex-1">
                                <span className="font-semibold text-white">{src.source_title}</span> &bull;{' '}
                                <span className="text-slate-400">{src.source_type}</span>
                              </div>
                              <ExternalLink className="w-3 h-3 text-slate-400 shrink-0 ml-2" />
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                </div>
              ) : (
                <div className="py-8 text-center text-xs text-slate-500 space-y-1">
                  <HelpCircle className="w-6 h-6 mx-auto text-slate-600" />
                  <p>No response yet. Speak a question or select a demo prompt to begin.</p>
                </div>
              )}
            </div>

            {/* Panel E: Voice Likeness Profile & Kinship Consent Panel */}
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-semibold text-white flex items-center gap-2">
                  <Lock className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Authorized Memorial Voice Profile</span>
                </h4>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                    customVoicePermitted
                      ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                      : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                  }`}
                >
                  {customVoicePermitted ? 'Kinship Likeness Active' : 'Generic Voice Fallback'}
                </span>
              </div>

              {/* Profile Selection */}
              <div className="space-y-1.5 text-xs">
                <label className="text-slate-400">Active Synthesis Profile:</label>
                <select
                  value={selectedProfileId}
                  onChange={(e) => setSelectedProfileId(e.target.value)}
                  className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-700 text-slate-200 text-xs focus:ring-1 focus:ring-indigo-500"
                >
                  {profiles.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.voice_type})
                    </option>
                  ))}
                </select>
              </div>

              {/* Required Consent Scopes */}
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
                <span className="font-medium text-slate-300 text-[11px]">Required Consent Scopes:</span>
                <div className="grid grid-cols-2 gap-1.5 text-[10px] font-mono">
                  {[
                    { scope: 'VOICE_PROCESSING', status: 'GRANTED' },
                    { scope: 'AI_PROCESSING', status: 'GRANTED' },
                    { scope: 'CUSTOM_VOICE_SYNTHESIS', status: customVoicePermitted ? 'GRANTED' : 'REVOKED' },
                    { scope: 'AUDIO_STORAGE', status: 'GRANTED' },
                    { scope: 'FAMILY_ACCESS', status: 'GRANTED' },
                  ].map((s) => (
                    <div
                      key={s.scope}
                      className="flex items-center justify-between p-1.5 rounded bg-slate-900 border border-slate-800"
                    >
                      <span className="text-slate-400 truncate">{s.scope}</span>
                      <span
                        className={s.status === 'GRANTED' ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}
                      >
                        {s.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Kinship Authorization Actions */}
              <div className="flex items-center justify-between pt-1">
                <button
                  onClick={customVoicePermitted ? handleRevokeConsent : handleGrantConsent}
                  disabled={isConsentUpdating}
                  className={`px-3 py-1.5 rounded-xl font-medium text-xs transition-colors flex items-center gap-1.5 ${
                    customVoicePermitted
                      ? 'bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20'
                      : 'bg-emerald-600 hover:bg-emerald-500 text-white'
                  }`}
                >
                  {customVoicePermitted ? (
                    <>
                      <Lock className="w-3 h-3" />
                      <span>Revoke Kinship Likeness</span>
                    </>
                  ) : (
                    <>
                      <Unlock className="w-3 h-3" />
                      <span>Grant Kinship Likeness</span>
                    </>
                  )}
                </button>

                <span className="text-[10px] text-slate-500 font-mono">
                  {customVoicePermitted ? 'Protected under Consent #CR-1984' : 'Generic fallback enforced'}
                </span>
              </div>
            </div>

            {/* Research Latency Telemetry */}
            {Object.keys(telemetry).length > 0 && (
              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 space-y-2 text-xs">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="font-medium text-[11px]">Research Telemetry (Latencies):</span>
                  <span className="font-mono text-[10px]">
                    Total E2E: <strong>{telemetry.total_e2e_ms || 0}ms</strong>
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-1 text-[10px] font-mono text-slate-400">
                  <div>STT: {telemetry.stt_latency_ms || 0}ms</div>
                  <div>RAG: {telemetry.retrieval_latency_ms || 0}ms</div>
                  <div>LLM: {telemetry.generation_latency_ms || 0}ms</div>
                  <div>Guardian: {telemetry.guardian_latency_ms || 0}ms</div>
                  <div>TTS: {telemetry.tts_latency_ms || 0}ms</div>
                </div>
              </div>
            )}
          </div>
        </div>

      {/* Slide-out Evidence Drawer */}
      <EvidenceDrawer source={selectedSource} onClose={() => setSelectedSource(null)} />
    </div>
  );
}
