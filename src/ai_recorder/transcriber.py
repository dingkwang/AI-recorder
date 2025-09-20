from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import assemblyai as aai


@dataclass
class Utterance:
	speaker: Optional[str]
	start: int
	end: int
	text: str


@dataclass
class TranscriptResult:
	text: str
	utterances: List[Utterance]
	# raw JSON payload (primitive serializable) for future use
	raw: dict


def _ms_to_srt_time(ms: int) -> str:
	seconds, milli = divmod(ms, 1000)
	minutes, sec = divmod(seconds, 60)
	hours, minute = divmod(minutes, 60)
	return f"{hours:02d}:{minute:02d}:{sec:02d},{milli:03d}"


def _ms_to_vtt_time(ms: int) -> str:
	seconds, milli = divmod(ms, 1000)
	minutes, sec = divmod(seconds, 60)
	hours, minute = divmod(minutes, 60)
	return f"{hours:02d}:{minute:02d}:{sec:02d}.{milli:03d}"


def transcribe(
	audio_path_or_url: str,
	api_key: str,
	use_universal: bool = True,
	use_speaker_labels: bool = True,
	speakers_expected: Optional[int] = None,
) -> TranscriptResult:
	"""Run AssemblyAI transcription, optionally enabling diarization.

	Returns a simplified `TranscriptResult` with utterances.
	"""
	aai.settings.api_key = api_key
	transcriber = aai.Transcriber()
	model_name = "universal" if use_universal else None
	config = aai.TranscriptionConfig(
		model=model_name,
		speaker_labels=use_speaker_labels,
		speakers_expected=speakers_expected,
	)
	result = transcriber.transcribe(audio_path_or_url, config=config)

	# Build utterances list; if diarization disabled, fall back to words->one block
	utterances: List[Utterance] = []
	if getattr(result, "utterances", None):
		for utt in result.utterances:
			utterances.append(
				Utterance(
					speaker=str(utt.speaker) if getattr(utt, "speaker", None) is not None else None,
					start=int(utt.start),
					end=int(utt.end),
					text=str(utt.text or "").strip(),
				)
			)
	else:
		# No diarization; create a single block if timing available
		start_ms = 0
		end_ms = 0
		if getattr(result, "words", None):
			words = [w for w in result.words if getattr(w, "start", None) is not None]
			if words:
				start_ms = int(words[0].start)
				end_ms = int(words[-1].end)
		utterances.append(
			Utterance(speaker=None, start=start_ms, end=end_ms, text=str(result.text or "").strip())
		)

	# Build raw payload: attempt to serialize SDK object minimally
	# The SDK's object isn't directly JSON serializable; construct a safe dict
	raw_dict = {
		"id": getattr(result, "id", None),
		"text": result.text,
		"audio_url": getattr(result, "audio_url", None),
		"status": getattr(result, "status", None),
		"utterances": [
			{
				"speaker": u.speaker,
				"start": u.start,
				"end": u.end,
				"text": u.text,
			}
			for u in utterances
		],
	}

	return TranscriptResult(text=result.text or "", utterances=utterances, raw=raw_dict)


def write_txt(result: TranscriptResult, path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(result.text, encoding="utf-8")


def write_json(result: TranscriptResult, path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	serializable = {
		"text": result.text,
		"utterances": [asdict(u) for u in result.utterances],
		"raw": result.raw,
	}
	path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")


def write_srt(result: TranscriptResult, path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	lines: List[str] = []
	for idx, utt in enumerate(result.utterances, start=1):
		start = _ms_to_srt_time(max(0, utt.start))
		end = _ms_to_srt_time(max(utt.start + 1, utt.end))
		prefix = f"Speaker {utt.speaker}: " if utt.speaker is not None else ""
		lines.append(str(idx))
		lines.append(f"{start} --> {end}")
		lines.append(f"{prefix}{utt.text}")
		lines.append("")
	path.write_text("\n".join(lines), encoding="utf-8")


def write_vtt(result: TranscriptResult, path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	lines: List[str] = ["WEBVTT", ""]
	for utt in result.utterances:
		start = _ms_to_vtt_time(max(0, utt.start))
		end = _ms_to_vtt_time(max(utt.start + 1, utt.end))
		prefix = f"Speaker {utt.speaker}: " if utt.speaker is not None else ""
		lines.append(f"{start} --> {end}")
		lines.append(f"{prefix}{utt.text}")
		lines.append("")
	path.write_text("\n".join(lines), encoding="utf-8")

