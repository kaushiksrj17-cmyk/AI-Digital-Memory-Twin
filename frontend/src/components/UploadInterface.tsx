'use client';

import React, { useState } from 'react';
import {
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  FileText,
  Image as ImageIcon,
  Film,
  Music,
  Lock,
  Copy,
  Sparkles,
  ShieldCheck,
  X
} from 'lucide-react';
import { MemoryCategory, SourceType, PrivacyLevel, ConsentType } from '@/types';

interface UploadInterfaceProps {
  onUploadSuccess?: () => void;
}

export const UploadInterface: React.FC<UploadInterfaceProps> = ({ onUploadSuccess }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  
  // Metadata Form Fields
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState<MemoryCategory>('FAMILY');
  const [sourceType, setSourceType] = useState<SourceType>('ORIGINAL_PHOTO');
  const [date, setDate] = useState('');
  const [approximateDate, setApproximateDate] = useState('');
  const [location, setLocation] = useState('');
  const [peopleText, setPeopleText] = useState('');
  const [privacyLevel, setPrivacyLevel] = useState<PrivacyLevel>('PRIVATE');
  
  // Consent Scopes
  const [consents, setConsents] = useState<Record<ConsentType, boolean>>({
    MEDIA_PROCESSING: true,
    AI_PROCESSING: false,
    VOICE_PROCESSING: false,
    AVATAR_PROCESSING: false,
    FAMILY_ACCESS: false,
  });

  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'duplicate' | 'error'>('idle');
  const [resultMessage, setResultMessage] = useState('');
  const [duplicateInfo, setDuplicateInfo] = useState<{ checksum?: string; storage_path?: string } | null>(null);

  const handleFileSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const fileList = Array.from(files);
    setSelectedFiles(fileList);

    // Auto-infer title and source type from first file if not set
    const first = fileList[0];
    if (!title) {
      const baseName = first.name.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' ');
      setTitle(baseName.charAt(0).toUpperCase() + baseName.slice(1));
    }

    const ext = first.name.toLowerCase();
    if (ext.endsWith('.jpg') || ext.endsWith('.jpeg') || ext.endsWith('.png') || ext.endsWith('.webp')) {
      setSourceType('ORIGINAL_PHOTO');
    } else if (ext.endsWith('.mp4') || ext.endsWith('.mov') || ext.endsWith('.webm')) {
      setSourceType('ORIGINAL_VIDEO');
    } else if (ext.endsWith('.mp3') || ext.endsWith('.wav') || ext.endsWith('.m4a')) {
      setSourceType('ORIGINAL_AUDIO');
    } else {
      setSourceType('DOCUMENT');
    }

    // Generate previews for images
    const urls = fileList.map((f) => {
      if (f.type.startsWith('image/')) {
        return URL.createObjectURL(f);
      }
      return '';
    });
    setPreviewUrls(urls);
  };

  const toggleConsent = (type: ConsentType) => {
    setConsents((prev) => ({ ...prev, [type]: !prev[type] }));
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFiles.length === 0) return;

    setUploadStatus('uploading');
    setDuplicateInfo(null);

    try {
      const file = selectedFiles[0];
      const formData = new FormData();
      formData.append('file', file);
      if (description) formData.append('description', description);
      if (date) formData.append('captured_date', date);
      formData.append('privacy_level', privacyLevel);

      // 1. Upload raw media file with validation and duplicate detection
      const mediaRes = await fetch('/api/v1/media/upload', {
        method: 'POST',
        body: formData,
      });

      if (!mediaRes.ok) {
        const errData = await mediaRes.json().catch(() => ({}));
        throw new Error(errData.detail || 'Upload failed');
      }

      const mediaData = await mediaRes.json();

      // Check if duplicate detected
      if (mediaData.is_duplicate) {
        setUploadStatus('duplicate');
        setDuplicateInfo({
          checksum: mediaData.checksum,
          storage_path: mediaData.storage_path,
        });
        setResultMessage(
          `Duplicate file detected! Re-referencing existing vault asset without duplicate physical storage.`
        );
      } else {
        setUploadStatus('success');
        setResultMessage(`Preserved securely in vault: ${mediaData.file_name}`);
      }

      // 2. Create the associated Memory entry in the vault
      const peopleList = peopleText
        ? peopleText.split(',').map((p) => p.trim()).filter(Boolean)
        : [];

      await fetch('/api/v1/memories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title || file.name,
          description: description || `Preserved archival evidence file: ${file.name}`,
          narrative: description || `Preserved archival evidence file: ${file.name}`,
          category,
          source_type: sourceType,
          date: date || undefined,
          approximate_date: approximateDate || undefined,
          location: location || undefined,
          people: peopleList,
          privacy_level: privacyLevel,
          verification_status: 'PENDING_REVIEW',
          checksum: mediaData.checksum,
          original_filename: mediaData.file_name,
          file_size: mediaData.file_size_bytes,
          storage_path: mediaData.storage_path,
          thumbnail_path: mediaData.thumbnail_path,
        }),
      });

      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err: any) {
      setUploadStatus('error');
      setResultMessage(err.message || 'Error occurred while saving file to vault.');
    }
  };

  const removeFile = (idx: number) => {
    const updated = selectedFiles.filter((_, i) => i !== idx);
    setSelectedFiles(updated);
    const updatedUrls = previewUrls.filter((_, i) => i !== idx);
    setPreviewUrls(updatedUrls);
    if (updated.length === 0) {
      setUploadStatus('idle');
    }
  };

  return (
    <form
      onSubmit={handleUpload}
      className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-6"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 dark:text-slate-300">
          <Lock className="w-4 h-4 text-emerald-500" />
          <span>Private Multimodal Ingestion (D:\ECHO\storage\originals)</span>
        </div>
        <span className="text-[11px] font-mono text-slate-500">SHA-256 Validated</span>
      </div>

      {/* Drag & Drop Area */}
      <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl p-8 text-center hover:border-indigo-500 transition-colors cursor-pointer relative bg-slate-50 dark:bg-slate-950/40">
        <input
          type="file"
          multiple
          onChange={(e) => handleFileSelect(e.target.files)}
          className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
        />
        <UploadCloud className="w-10 h-10 text-indigo-400 mx-auto mb-3" />
        <p className="text-xs font-medium text-slate-700 dark:text-slate-200">
          {selectedFiles.length > 0
            ? `${selectedFiles.length} file(s) selected for preservation`
            : 'Click or drag photographs, videos, audio recordings, or documents here'}
        </p>
        <p className="text-[11px] text-slate-400 mt-1">
          Supported: JPG, PNG, WEBP &bull; MP4, MOV, WEBM &bull; MP3, WAV, M4A &bull; PDF, TXT, DOCX &bull; Max 100 MB
        </p>
      </div>

      {/* Selected Files Preview Strip */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Selected Archival Assets ({selectedFiles.length})
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {selectedFiles.map((file, idx) => (
              <div
                key={idx}
                className="relative p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-800/80 flex items-center gap-2 text-xs"
              >
                {previewUrls[idx] ? (
                  <img
                    src={previewUrls[idx]}
                    alt="preview"
                    className="w-8 h-8 rounded object-cover shrink-0"
                  />
                ) : file.type.startsWith('video/') ? (
                  <Film className="w-8 h-8 text-purple-400 shrink-0 p-1 bg-purple-500/10 rounded" />
                ) : file.type.startsWith('audio/') ? (
                  <Music className="w-8 h-8 text-cyan-400 shrink-0 p-1 bg-cyan-500/10 rounded" />
                ) : (
                  <FileText className="w-8 h-8 text-amber-400 shrink-0 p-1 bg-amber-500/10 rounded" />
                )}
                <div className="min-w-0 flex-1">
                  <p className="font-medium truncate text-slate-800 dark:text-slate-200">{file.name}</p>
                  <p className="text-[10px] text-slate-400 font-mono">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(idx)}
                  className="p-1 text-slate-400 hover:text-rose-500"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metadata Form */}
      {selectedFiles.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-slate-800">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {/* Title */}
            <div className="space-y-1">
              <label className="font-semibold text-slate-700 dark:text-slate-300">Memory Title *</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. 1968 Graduation Day Ceremony"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            {/* Category */}
            <div className="space-y-1">
              <label className="font-semibold text-slate-700 dark:text-slate-300">Category *</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as MemoryCategory)}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="CHILDHOOD">Childhood</option>
                <option value="EDUCATION">Education</option>
                <option value="CAREER">Career</option>
                <option value="FAMILY">Family</option>
                <option value="FRIENDS">Friends</option>
                <option value="TRAVEL">Travel</option>
                <option value="HOBBIES">Hobbies</option>
                <option value="ACHIEVEMENTS">Achievements</option>
                <option value="SPECIAL_EVENTS">Special Events</option>
                <option value="PERSONAL_STORIES">Personal Stories</option>
                <option value="OTHER">Other</option>
              </select>
            </div>

            {/* Source Type */}
            <div className="space-y-1">
              <label className="font-semibold text-slate-700 dark:text-slate-300">Source Type *</label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value as SourceType)}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="ORIGINAL_PHOTO">Original Photo</option>
                <option value="ORIGINAL_VIDEO">Original Video</option>
                <option value="ORIGINAL_AUDIO">Original Audio</option>
                <option value="DOCUMENT">Document / Letter</option>
                <option value="FAMILY_STORY">Family Story</option>
                <option value="USER_ENTRY">User Entry</option>
                <option value="AI_GENERATED">AI Generated (Clearly labeled)</option>
              </select>
            </div>

            {/* Privacy Level */}
            <div className="space-y-1">
              <label className="font-semibold text-slate-700 dark:text-slate-300">Privacy Tier *</label>
              <select
                value={privacyLevel}
                onChange={(e) => setPrivacyLevel(e.target.value as PrivacyLevel)}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="PRIVATE">Private (Vault Guardian Only)</option>
                <option value="FAMILY">Family (Kinship Circle)</option>
                <option value="AUTHORIZED_USERS">Authorized Researchers/Kin</option>
              </select>
            </div>

            {/* Exact Date */}
            <div className="space-y-1">
              <label className="font-semibold text-slate-700 dark:text-slate-300">Exact Date (Optional)</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            {/* Approximate Date */}
            <div className="space-y-1">
              <label className="font-semibold text-slate-700 dark:text-slate-300">Approximate Date / Period</label>
              <input
                type="text"
                value={approximateDate}
                onChange={(e) => setApproximateDate(e.target.value)}
                placeholder="e.g. Summer 1968, Early 1970s"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            {/* Location */}
            <div className="space-y-1">
              <label className="font-semibold text-slate-700 dark:text-slate-300">Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Cambridge, UK or Lake Windermere"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            {/* People Mentioned */}
            <div className="space-y-1">
              <label className="font-semibold text-slate-700 dark:text-slate-300">People Mentioned (Comma-separated)</label>
              <input
                type="text"
                value={peopleText}
                onChange={(e) => setPeopleText(e.target.value)}
                placeholder="e.g. Eleanor Vance, Arthur Vance"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          {/* Description / Story Narrative */}
          <div className="space-y-1 text-xs">
            <label className="font-semibold text-slate-700 dark:text-slate-300">
              Description & Context Notes
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Provide background context, stories, or excerpts associated with this archival item..."
              className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          {/* Granular Consent Checkboxes */}
          <div className="space-y-2 pt-2 border-t border-slate-200 dark:border-slate-800 text-xs">
            <div className="flex items-center gap-2 font-semibold text-slate-700 dark:text-slate-300">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>Explicit Guardian Consent Controls (Never Assumed)</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-[11px]">
              <label className="flex items-center gap-2 p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consents.MEDIA_PROCESSING}
                  onChange={() => toggleConsent('MEDIA_PROCESSING')}
                  className="rounded text-indigo-600"
                />
                <span className="text-slate-700 dark:text-slate-300">Media Ingestion & Archiving</span>
              </label>

              <label className="flex items-center gap-2 p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consents.AI_PROCESSING}
                  onChange={() => toggleConsent('AI_PROCESSING')}
                  className="rounded text-indigo-600"
                />
                <span className="text-slate-700 dark:text-slate-300">AI Dialogue Grounding</span>
              </label>

              <label className="flex items-center gap-2 p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consents.VOICE_PROCESSING}
                  onChange={() => toggleConsent('VOICE_PROCESSING')}
                  className="rounded text-indigo-600"
                />
                <span className="text-slate-700 dark:text-slate-300">Voice Synthesis (Phase 6)</span>
              </label>

              <label className="flex items-center gap-2 p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consents.AVATAR_PROCESSING}
                  onChange={() => toggleConsent('AVATAR_PROCESSING')}
                  className="rounded text-indigo-600"
                />
                <span className="text-slate-700 dark:text-slate-300">Visual Presence (Phase 7)</span>
              </label>

              <label className="flex items-center gap-2 p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consents.FAMILY_ACCESS}
                  onChange={() => toggleConsent('FAMILY_ACCESS')}
                  className="rounded text-indigo-600"
                />
                <span className="text-slate-700 dark:text-slate-300">Family Circle Access</span>
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={uploadStatus === 'uploading'}
            className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {uploadStatus === 'uploading' ? (
              <span>Preserving in Secure Vault (SHA-256 Checksumming)...</span>
            ) : (
              <>
                <UploadCloud className="w-4 h-4" />
                <span>Ingest & Preserve Archival Memory</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Success Banner */}
      {uploadStatus === 'success' && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{resultMessage}</span>
        </div>
      )}

      {/* Duplicate Detected Banner */}
      {uploadStatus === 'duplicate' && (
        <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-600 dark:text-amber-400 space-y-1">
          <div className="flex items-center gap-2 font-semibold">
            <Copy className="w-4 h-4 shrink-0" />
            <span>Duplicate File Detected</span>
          </div>
          <p className="text-[11px] text-amber-500/90">{resultMessage}</p>
          {duplicateInfo?.checksum && (
            <p className="text-[10px] font-mono text-slate-400">
              SHA-256 Digest: {duplicateInfo.checksum}
            </p>
          )}
        </div>
      )}

      {/* Error Banner */}
      {uploadStatus === 'error' && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-600 dark:text-rose-400 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{resultMessage}</span>
        </div>
      )}
    </form>
  );
};
