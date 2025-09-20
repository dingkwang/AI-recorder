import os
from dotenv import load_dotenv


def get_assemblyai_api_key() -> str:
	"""Return the AssemblyAI API key from env or .env; raise if missing."""
	load_dotenv()
	api_key = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
	if not api_key:
		raise RuntimeError(
			"Missing ASSEMBLYAI_API_KEY. Set it in your environment or .env file."
		)
	return api_key

