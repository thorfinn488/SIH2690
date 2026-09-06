import React, { useState, useRef } from 'react';
import { Mic, Square, Volume2, CheckCircle2, RefreshCw } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface AudioRecorderProps {
  onAudioReady: (audioBlob: Blob) => void;
  onTranscriptReady?: (transcript: string) => void;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionInstance {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  start: () => void;
  stop: () => void;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognitionInstance;
}

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({ onAudioReady, onTranscriptReady }) => {
  const { language, t } = useLanguage();
  const [isRecording, setIsRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [liveTranscript, setLiveTranscript] = useState('');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const transcriptRef = useRef('');
  const timerRef = useRef<any>(null);

  const getRecognition = () => {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) return null;

    const recognition = new Recognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
    recognition.onresult = (event) => {
      let transcript = '';
      for (let index = 0; index < event.results.length; index += 1) {
        transcript += event.results[index][0].transcript;
      }
      transcriptRef.current = transcript.trim();
      setLiveTranscript(transcriptRef.current);
    };
    recognition.onerror = () => undefined;
    return recognition;
  };

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
        onTranscriptReady?.(transcriptRef.current);
        stream.getTracks().forEach((track) => track.stop());
      };

      transcriptRef.current = '';
      setLiveTranscript('');
      const recognition = getRecognition();
      recognitionRef.current = recognition;
      try {
        recognition?.start();
      } catch (err) {
        recognitionRef.current = null;
      }
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
      recognitionRef.current?.stop();
      recognitionRef.current = null;
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) clearInterval(timerRef.current);
    }
  };

  const simulateRecording = () => {
    transcriptRef.current = '';
    setLiveTranscript('');
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
          onTranscriptReady?.(transcriptRef.current);
          return 5;
        }
        return prev + 1;
      });
    }, 800);
  };

  const resetRecording = () => {
    recognitionRef.current?.stop();
    recognitionRef.current = null;
    transcriptRef.current = '';
    setAudioUrl(null);
    setRecordingTime(0);
    setLiveTranscript('');
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

      {(isRecording || liveTranscript) && (
        <div className="w-full max-w-xl bg-white border border-amber-200 rounded-xl p-4 text-left shadow-sm">
          <p className="text-xs font-extrabold uppercase tracking-wider text-amber-800 mb-2">Live transcript</p>
          <p className="text-sm text-slate-700 min-h-6">
            {liveTranscript || 'Listening for speech...'}
          </p>
        </div>
      )}
    </div>
  );
};
