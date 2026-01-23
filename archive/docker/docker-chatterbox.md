# Chatterbox TTS Docker Container (GPU/CUDA)

This Docker container runs Chatterbox-Turbo TTS with full NVIDIA GPU support via CUDA 12.1.

## Prerequisites

1. **Docker Desktop for Windows** with WSL 2 backend
2. **NVIDIA GPU Driver** (version 525.60.13 or later recommended)
3. **NVIDIA Container Toolkit** - Follow the [NVIDIA Container Toolkit Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

### Verify GPU Support in Docker

```powershell
# Check NVIDIA driver is working
nvidia-smi

# Test Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```powershell
# Build and start the container
docker-compose up -d --build

# View logs
docker-compose logs -f chatterbox-tts

# Stop the container
docker-compose down
```

### Option 2: Manual Docker Commands

```powershell
# Build the image
docker build -f Dockerfile.turbo -t chatterbox-turbo .

# Run with GPU support
docker run -d --gpus all -p 3000:3000 --name chatterbox-turbo chatterbox-turbo

# View logs
docker logs -f chatterbox-turbo

# Stop and remove
docker stop chatterbox-turbo && docker rm chatterbox-turbo
```

## API Endpoints

### Health Check

```powershell
curl http://localhost:3000/health
```

Response:
```json
{"status": "ok", "model_loaded": true}
```

### Synthesize Speech

**`POST /speech`** - Docker-compatible endpoint

```powershell
$body = @{text="Hello, this is a test!"; exaggeration=0.5; cfg=0.5; temperature=0.8} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:3000/speech" -Method POST -Body $body -ContentType "application/json" -OutFile "output.wav"
```

**`POST /synthesize`** - Legacy endpoint with voice reference support

```powershell
$body = @{text="Hello world"; voice_reference="/app/voice_references/my_voice.wav"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:3000/synthesize" -Method POST -Body $body -ContentType "application/json" -OutFile "output.wav"
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | Server port |
| `CUDA_VISIBLE_DEVICES` | `0` | GPU device ID |
| `HF_TOKEN` | - | HuggingFace token for gated models |

### Using Custom Voice References

Uncomment the volume mount in `docker-compose.yml`:

```yaml
volumes:
  - ./assets/voice_references:/app/voice_references:ro
```

Then reference voices in your API calls:
```json
{"text": "Hello!", "voice_reference": "/app/voice_references/my_voice.wav"}
```

## Performance Notes

- **First startup** takes 2-3 minutes as the model downloads (~2GB)
- Model cache is persisted in a Docker volume to avoid re-downloading
- Inference runs on GPU (RTX 3060 Laptop = ~2-3s per sentence)
- Requires ~4GB GPU VRAM during inference

## Troubleshooting

### Container exits immediately

Check logs for errors:
```powershell
docker logs chatterbox-turbo
```

### Out of GPU Memory

Reduce batch size or ensure no other GPU processes are running:
```powershell
nvidia-smi
```

### Docker can't find GPU

Ensure NVIDIA Container Toolkit is installed:
```powershell
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

If this fails, reinstall the NVIDIA Container Toolkit.

### Model download fails

Set HuggingFace token in docker-compose.yml:
```yaml
environment:
  - HF_TOKEN=your_token_here
```

## System Requirements

- **GPU**: NVIDIA GPU with Compute Capability 7.0+ (RTX 20/30/40 series, or equivalent)
- **VRAM**: 4GB+ recommended
- **RAM**: 8GB+ system memory
- **Disk**: 10GB+ for Docker image and model cache
