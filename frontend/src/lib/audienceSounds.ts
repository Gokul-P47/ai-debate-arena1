/** Synthesize crowd clap / cheer / murmur with the Web Audio API (no asset files). */

'use client';

let sharedCtx: AudioContext | null = null;

function getCtx(): AudioContext | null {
  if (typeof window === 'undefined') return null;
  const AC =
    window.AudioContext ||
    (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!AC) return null;
  if (!sharedCtx || sharedCtx.state === 'closed') {
    sharedCtx = new AC();
  }
  return sharedCtx;
}

async function resumeCtx(ctx: AudioContext): Promise<void> {
  if (ctx.state === 'suspended') {
    try {
      await ctx.resume();
    } catch {
      // Autoplay policies may block until a user gesture.
    }
  }
}

function noiseBuffer(ctx: AudioContext, seconds: number): AudioBuffer {
  const length = Math.max(1, Math.floor(ctx.sampleRate * seconds));
  const buffer = ctx.createBuffer(1, length, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < length; i += 1) {
    data[i] = Math.random() * 2 - 1;
  }
  return buffer;
}

function playNoiseBurst(
  ctx: AudioContext,
  opts: {
    when: number;
    duration: number;
    gain: number;
    highpass?: number;
    lowpass?: number;
    bandpass?: number;
    q?: number;
  },
): void {
  const src = ctx.createBufferSource();
  src.buffer = noiseBuffer(ctx, opts.duration + 0.05);

  let node: AudioNode = src;
  if (opts.highpass) {
    const hp = ctx.createBiquadFilter();
    hp.type = 'highpass';
    hp.frequency.value = opts.highpass;
    node.connect(hp);
    node = hp;
  }
  if (opts.lowpass) {
    const lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.frequency.value = opts.lowpass;
    node.connect(lp);
    node = lp;
  }
  if (opts.bandpass) {
    const bp = ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = opts.bandpass;
    bp.Q.value = opts.q ?? 1.2;
    node.connect(bp);
    node = bp;
  }

  const g = ctx.createGain();
  g.gain.setValueAtTime(0.0001, opts.when);
  g.gain.exponentialRampToValueAtTime(opts.gain, opts.when + 0.008);
  g.gain.exponentialRampToValueAtTime(0.0001, opts.when + opts.duration);

  node.connect(g);
  g.connect(ctx.destination);
  src.start(opts.when);
  src.stop(opts.when + opts.duration + 0.02);
}

/** Short layered hand-claps (crowd reaction after a speech). */
export async function playApplause(intensity: 'soft' | 'full' = 'soft'): Promise<void> {
  const ctx = getCtx();
  if (!ctx) return;
  await resumeCtx(ctx);

  const now = ctx.currentTime;
  const count = intensity === 'full' ? 28 : 14;
  const span = intensity === 'full' ? 1.6 : 0.85;
  const baseGain = intensity === 'full' ? 0.12 : 0.08;

  for (let i = 0; i < count; i += 1) {
    const t = now + Math.random() * span;
    playNoiseBurst(ctx, {
      when: t,
      duration: 0.04 + Math.random() * 0.05,
      gain: baseGain * (0.55 + Math.random() * 0.7),
      highpass: 1200 + Math.random() * 1800,
      lowpass: 6500,
    });
  }
}

/** Audience cheer / whoop swell. */
export async function playCheer(intensity: 'soft' | 'full' = 'soft'): Promise<void> {
  const ctx = getCtx();
  if (!ctx) return;
  await resumeCtx(ctx);

  const now = ctx.currentTime;
  const duration = intensity === 'full' ? 2.4 : 1.3;
  const voices = intensity === 'full' ? 10 : 6;
  const gainPeak = intensity === 'full' ? 0.09 : 0.055;

  for (let i = 0; i < voices; i += 1) {
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    const start = now + Math.random() * 0.25;
    const freq = 220 + Math.random() * 420;
    osc.type = i % 2 === 0 ? 'sawtooth' : 'triangle';
    osc.frequency.setValueAtTime(freq, start);
    osc.frequency.linearRampToValueAtTime(freq * (1.05 + Math.random() * 0.12), start + duration);

    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = 800 + Math.random() * 900;
    filter.Q.value = 0.7;

    g.gain.setValueAtTime(0.0001, start);
    g.gain.exponentialRampToValueAtTime(gainPeak * (0.5 + Math.random() * 0.5), start + 0.15);
    g.gain.exponentialRampToValueAtTime(0.0001, start + duration);

    osc.connect(filter);
    filter.connect(g);
    g.connect(ctx.destination);
    osc.start(start);
    osc.stop(start + duration + 0.05);
  }

  // Airy crowd noise under the cheer
  playNoiseBurst(ctx, {
    when: now,
    duration: duration * 0.9,
    gain: intensity === 'full' ? 0.045 : 0.028,
    bandpass: 1200,
    q: 0.6,
  });
}

/** Soft room murmur while debate is live and idle between turns. */
export async function playCrowdMurmur(seconds = 1.2): Promise<void> {
  const ctx = getCtx();
  if (!ctx) return;
  await resumeCtx(ctx);
  const now = ctx.currentTime;
  playNoiseBurst(ctx, {
    when: now,
    duration: seconds,
    gain: 0.018,
    lowpass: 900,
    highpass: 120,
  });
}

/** Unlock audio on first user gesture (call from Start Debate). */
export async function unlockAudienceAudio(): Promise<void> {
  const ctx = getCtx();
  if (!ctx) return;
  await resumeCtx(ctx);
}
