import React from 'react';
import { SourceType } from '@/types';
import { Image as ImageIcon, Video, Music, FileText, Download, ExternalLink } from 'lucide-react';

interface Props {
  fileName: string;
  mediaType: SourceType;
  fileSize: number;
  description?: string;
  date?: string;
  onPreview?: () => void;
}

export const MediaPreview: React.FC<Props> = ({
  fileName,
  mediaType,
  fileSize,
  description,
  date,
  onPreview,
}) => {
  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getIcon = () => {
    switch (mediaType) {
      case 'PHOTOGRAPH':
        return <ImageIcon className="w-8 h-8 text-blue-400" />;
      case 'VIDEO':
        return <Video className="w-8 h-8 text-purple-400" />;
      case 'AUDIO_RECORDING':
        return <Music className="w-8 h-8 text-teal-400" />;
      default:
        return <FileText className="w-8 h-8 text-amber-400" />;
    }
  };

  return (
    <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm flex flex-col justify-between hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
      <div className="flex items-start gap-3">
        <div className="p-3 rounded-lg bg-slate-100 dark:bg-slate-800/80 shrink-0">
          {getIcon()}
        </div>
        <div className="min-w-0 flex-1">
          <h4 className="text-xs font-semibold text-slate-900 dark:text-slate-100 truncate" title={fileName}>
            {fileName}
          </h4>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
            {description || 'Preserved archival artifact.'}
          </p>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500">
        <span>{formatSize(fileSize)}</span>
        {date && <span>{date}</span>}
      </div>
    </div>
  );
};
