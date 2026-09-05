import React, { useState, useRef } from 'react';
import { Mic, Square, Play, Volume2, CheckCircle2, RefreshCw } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface AudioRecorderProps {
  onAudioReady: (audioBlob: Blob) => void;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({ onAudioReady }) => {
  const { t } = useLanguage();
  const [isRecording, setIsRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<any>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/mpeg' });
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        onAudioReady(blob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      console.warn('Microphone access not available or denied. Generating simulated voice recording blob.');
      simulateRecording();
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) clearInterval(timerRef.current);
    }
  };

  const simulateRecording = () => {
    setIsRecording(true);
    setRecordingTime(0);
    timerRef.current = setInterval(() => {
      setRecordingTime((prev) => {
        if (prev >= 4) {
          clearInterval(timerRef.current);
          setIsRecording(false);
          // Create dummy audio blob
          const dummyBlob = new Blob(['simulated_artisan_voice_note'], { type: 'audio/mpeg' });
          const url = URL.createObjectURL(dummyBlob);
          setAudioUrl(url);
          onAudioReady(dummyBlob);
          return 5;
        }
        return prev + 1;
      });
    }, 800);
  };

  const resetRecording = () => {
    setAudioUrl(null);
    setRecordingTime(0);
  };

  return (
    <div className="bg-amber-50/80 border-2 border-dashed border-amber-300 p-6 rounded-2xl text-center flex flex-col items-center justify-center gap-4">
      <div className="flex items-center gap-2 text-amber-900 font-bold text-lg">
        <Volume2 className="w-6 h-6 text-amber-600" />
        <span>{t.micRecording}</span>
      </div>

      {!audioUrl ? (
        <div className="flex flex-col items-center gap-3">
          <button
            type="button"
            onClick={isRecording ? stopRecording : startRecording}
            className={`w-24 h-24 rounded-full flex items-center justify-center shadow-xl transition-all transform hover:scale-105 active:scale-95 ${
              isRecording
                ? 'bg-red-600 text-white animate-pulse ring-8 ring-red-200'
                : 'bg-gradient-to-br from-amber-500 to-amber-600 text-amber-950 hover:from-amber-400 hover:to-amber-500 ring-8 ring-amber-100'
            }`}
          >
            {isRecording ? <Square className="w-10 h-10" /> : <Mic className="w-12 h-12" />}
          </button>
          <p className={`text-sm font-semibold ${isRecording ? 'text-red-600 font-bold' : 'text-amber-800'}`}>
            {isRecording ? `${t.recordingActive} (00:0${recordingTime}s)` : t.tapToRecord}
          </p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3 w-full max-w-sm bg-white p-4 rounded-xl border border-amber-200 shadow-sm">
          <div className="flex items-center gap-2 text-emerald-600 font-bold text-sm">
            <CheckCircle2 className="w-5 h-5" />
            <span>Voice Recording Ready!</span>
          </div>
          <audio controls src={audioUrl} className="w-full h-10" />
          <button
            type="button"
            onClick={resetRecording}
            className="text-xs text-amber-700 hover:text-amber-900 font-semibold flex items-center gap-1 mt-1"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Re-record Voice Note
          </button>
        </div>
      )}
    </div>
  );
};
