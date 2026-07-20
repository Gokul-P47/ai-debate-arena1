/** Browser speech recognition for dictating the show topic. */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

interface SpeechRecognitionResultLike {
  readonly isFinal: boolean;
  readonly [index: number]: { transcript: string };
}

interface SpeechRecognitionEventLike extends Event {
  readonly resultIndex: number;
  readonly results: ArrayLike<SpeechRecognitionResultLike> & {
    readonly length: number;
  };
}

interface SpeechRecognitionErrorEventLike extends Event {
  readonly error: string;
  readonly message?: string;
}

interface SpeechRecognitionLike extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEventLike) => void) | null;
  onend: (() => void) | null;
}

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

/** Map app language codes to BCP-47 tags used by Web Speech API. */
const SPEECH_LANG: Record<string, string> = {
  en: 'en-IN',
  ta: 'ta-IN',
  hi: 'hi-IN',
  te: 'te-IN',
  ml: 'ml-IN',
  kn: 'kn-IN',
};

function getSpeechRecognitionCtor(): SpeechRecognitionConstructor | null {
  if (typeof window === 'undefined') return null;
  return window.SpeechRecognition ?? window.webkitSpeechRecognition ?? null;
}

function errorMessage(code: string): string {
  switch (code) {
    case 'not-allowed':
    case 'service-not-allowed':
      return 'Microphone permission denied. Allow mic access and try again.';
    case 'no-speech':
      return 'No speech detected. Try again.';
    case 'audio-capture':
      return 'No microphone found.';
    case 'network':
      return 'Speech recognition needs a network connection.';
    case 'aborted':
      return '';
    default:
      return 'Voice input failed. Try again.';
  }
}

interface UseSpeechInputOptions {
  language: string;
  disabled?: boolean;
  /** Called with the latest transcript (interim or final). */
  onTranscript: (text: string, isFinal: boolean) => void;
}

/**
 * Toggle dictation via the Web Speech API (Chrome / Edge).
 * Uses the form language so Tamil/Hindi/etc. recognition matches the show.
 */
export function useSpeechInput({ language, disabled = false, onTranscript }: UseSpeechInputOptions) {
  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const onTranscriptRef = useRef(onTranscript);
  const intentionalStopRef = useRef(false);

  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  useEffect(() => {
    setSupported(Boolean(getSpeechRecognitionCtor()));
  }, []);

  const stop = useCallback(() => {
    intentionalStopRef.current = true;
    const recognition = recognitionRef.current;
    if (recognition) {
      try {
        recognition.stop();
      } catch {
        // already stopped
      }
      recognitionRef.current = null;
    }
    setListening(false);
  }, []);

  const start = useCallback(() => {
    if (disabled) return;

    const Ctor = getSpeechRecognitionCtor();
    if (!Ctor) {
      setError('Voice input is not supported in this browser. Try Chrome or Edge.');
      return;
    }

    stop();
    intentionalStopRef.current = false;
    setError(null);

    const recognition = new Ctor();
    recognition.lang = SPEECH_LANG[language] ?? language;
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      let interim = '';
      let finalText = '';

      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i];
        const piece = result?.[0]?.transcript ?? '';
        if (result?.isFinal) {
          finalText += piece;
        } else {
          interim += piece;
        }
      }

      if (finalText) {
        onTranscriptRef.current(finalText.trim(), true);
      } else if (interim) {
        onTranscriptRef.current(interim.trim(), false);
      }
    };

    recognition.onerror = (event) => {
      const message = errorMessage(event.error);
      if (message) setError(message);
      setListening(false);
      recognitionRef.current = null;
    };

    recognition.onend = () => {
      setListening(false);
      recognitionRef.current = null;
      intentionalStopRef.current = false;
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
      setListening(true);
    } catch {
      setError('Could not start voice input. Try again.');
      setListening(false);
      recognitionRef.current = null;
    }
  }, [disabled, language, stop]);

  const toggle = useCallback(() => {
    if (listening) {
      stop();
    } else {
      start();
    }
  }, [listening, start, stop]);

  useEffect(() => {
    if (disabled && listening) stop();
  }, [disabled, listening, stop]);

  useEffect(() => () => stop(), [stop]);

  return {
    supported,
    listening,
    error,
    clearError: () => setError(null),
    toggle,
    stop,
  };
}
