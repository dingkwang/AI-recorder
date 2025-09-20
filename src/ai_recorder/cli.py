from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import get_assemblyai_api_key
from .transcriber import (
	TranscriptResult,
	transcribe,
	write_json,
	write_srt,
	write_txt,
	write_vtt,
)


app = typer.Typer(help="AI Recorder - AssemblyAI transcription CLI")
console = Console()


@app.command()
def transcribe_cmd(
	audio: str = typer.Argument(..., help="Path or URL to audio (mp3/wav/etc)"),
	out_dir: Path = typer.Option(Path("outputs"), help="Directory to save outputs"),
	format: List[str] = typer.Option(
		["txt", "json"], "--format", "-f", help="Output formats: txt/json/srt/vtt"
	),
	diarization: bool = typer.Option(True, help="Enable speaker diarization"),
	speakers_expected: Optional[int] = typer.Option(
		None, help="Expected number of speakers (optional)"
	),
	universal: bool = typer.Option(
		True, help="Use AssemblyAI 'universal' model for robust transcription"
	),
):
	"""Transcribe an audio file or URL and save outputs."""
	api_key = get_assemblyai_api_key()
	console.rule("Transcribing")
	console.print(
		f"[bold]Audio[/]: {audio}\n[bold]Diarization[/]: {diarization}  [bold]Universal[/]: {universal}"
	)
	if speakers_expected:
		console.print(f"[bold]Speakers expected[/]: {speakers_expected}")

	result: TranscriptResult = transcribe(
		audio_path_or_url=audio,
		api_key=api_key,
		use_universal=universal,
		use_speaker_labels=diarization,
		speakers_expected=speakers_expected,
	)

	# Basename for outputs
	name = Path(audio).stem if "://" not in audio else "remote_audio"
	out_dir.mkdir(parents=True, exist_ok=True)

	for fmt in format:
		fmt_lower = fmt.lower()
		path = out_dir / f"{name}.{fmt_lower}"
		if fmt_lower == "txt":
			write_txt(result, path)
		elif fmt_lower == "json":
			write_json(result, path)
		elif fmt_lower == "srt":
			write_srt(result, path)
		elif fmt_lower == "vtt":
			write_vtt(result, path)
		else:
			typer.echo(f"Unknown format: {fmt}")

	# Print a summary table
	table = Table(title="Transcript Summary")
	table.add_column("Field")
	table.add_column("Value")
	table.add_row("Text length", str(len(result.text)))
	table.add_row("Utterances", str(len(result.utterances)))
	table.add_row("Output dir", str(out_dir))
	console.print(table)
	console.print("[green]Done.[/]")


if __name__ == "__main__":
	app()

