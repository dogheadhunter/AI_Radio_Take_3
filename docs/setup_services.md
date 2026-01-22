# Setting up Ollama & Chatterbox (TTS)

This document explains how to make the generation integration tests runnable locally.

Ollama
------
- You mentioned Ollama is already installed. Verify it is running and the `/api/generate` endpoint is available:
  - curl -I http://localhost:11434/api/generate
  - python -c "from src.ai_radio.generation.llm_client import check_ollama_available; print(check_ollama_available())"
- If not running, start Ollama per its installation docs.

Chatterbox or Mock TTS
----------------------
- For true Chatterbox, follow https://github.com/resemble-ai/chatterbox to run the service (Docker is typical).
- Alternatively, a lightweight mock TTS is provided to exercise the pipeline and generate sample audio without external services.
- **Local Chatterbox (non-Docker)**: If you have Chatterbox cloned locally (e.g., `C:\Users\doghe\chatterbox`), you can start it directly:
  - PowerShell: `scripts\start_chatterbox.ps1`
  - Bash: `scripts/start_chatterbox.sh`
  - This will stop the mock TTS (port 3000), run `npm install` if needed, and start Chatterbox with `npm run dev`.

Using the mock TTS (recommended for development)
1. Ensure Docker and docker-compose are installed.
2. Start the mock service:
   - bash: `scripts/start_services.sh`
   - powershell: `scripts\start_services.ps1`
3. The mock TTS listens at `http://localhost:3000` by default and responds to `POST /synthesize` with a tiny WAV.
4. **Alternatively, run without Docker**: `python scripts/run_mock_tts.py` (requires Flask).

Offline Docker Usage
--------------------
- If you plan to work offline or your Internet may go down, pre-pull and save Docker images while online:
  - PowerShell: `scripts\save_docker_images.ps1`
  - Bash: `scripts/save_docker_images.sh`
- Later, load them offline:
  - PowerShell: `scripts\load_docker_images.ps1`
  - Bash: `scripts/load_docker_images.sh`
- Once images are saved, you can build and run containers without Internet access.

Configuration
-------------
- Point the LLM/TTS clients to custom endpoints using environment variables:
  - `AI_RADIO_LLM_URL` - e.g. `http://localhost:11434`
  - `AI_RADIO_TTS_URL` - e.g. `http://localhost:3000`

Quick test
----------
- Start the mock TTS and run:
  - `python scripts/generate_content.py --intros --dj julie --limit 3 --resume`
- You should find generated WAVs in `data/generated/intros/`.

Notes
-----
- Integration tests are still guarded and will skip if the required endpoints are missing or return 404.
- If you want me to add an optional `docker-compose` entry for a real Chatterbox image, provide the image name or I can try to detect it from the Chatterbox repo.
