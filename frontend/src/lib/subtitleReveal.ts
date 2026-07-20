/** Split text into speakable chunks (words + trailing whitespace). */

export function splitSubtitleChunks(text: string): string[] {
  const chunks = text.match(/\S+\s*/g);
  return chunks && chunks.length > 0 ? chunks : text ? [text] : [];
}

/** Reveal the first `ratio` fraction of words (0–1). */
export function revealTextByRatio(text: string, ratio: number): string {
  if (!text) return '';
  if (ratio >= 1) return text;
  if (ratio <= 0) return '';

  const chunks = splitSubtitleChunks(text);
  if (chunks.length === 0) return '';

  const count = Math.min(chunks.length, Math.max(1, Math.ceil(chunks.length * Math.min(1, ratio))));
  return chunks.slice(0, count).join('');
}

/** Get the currently spoken sentence based on the reveal ratio (line-by-line). */
export function getCurrentSubtitle(content: string, revealRatio: number): string {
  if (!content) return '';
  if (revealRatio <= 0) return '';

  const revealedText = revealTextByRatio(content, revealRatio);
  if (!revealedText) return '';

  // Split by sentence-ending punctuation, keeping them with the sentence
  const sentences = content.match(/[^.!?]+[.!?]*\s*/g) || [content];
  let cumulativeLength = 0;
  let currentSentenceIndex = 0;

  for (let i = 0; i < sentences.length; i++) {
    cumulativeLength += sentences[i].length;
    if (revealedText.length <= cumulativeLength) {
      currentSentenceIndex = i;
      break;
    }
  }

  let startOffset = 0;
  for (let i = 0; i < currentSentenceIndex; i++) {
    startOffset += sentences[i].length;
  }

  return revealedText.slice(startOffset).trim();
}
