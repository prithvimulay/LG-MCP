# Audio Podcast Integration with Nari Labs Dia TTS

This document describes the integration of Nari Labs Dia TTS for generating audio podcasts from PDF content.

## Overview

The audio integration adds the capability to generate realistic dialogue audio from podcast scripts using the [Nari Labs Dia TTS model](https://github.com/nari-labs/dia). Dia is a 1.6B parameter text-to-speech model that can generate ultra-realistic dialogue in one pass.

## Features

- **Text-to-Audio Conversion**: Convert podcast scripts to high-quality audio
- **Speaker Differentiation**: Uses S1 (Host) and S2 (Expert) speaker tags
- **Lazy Loading**: TTS model is only loaded when audio generation is requested
- **Error Handling**: Graceful fallback if audio dependencies are not available
- **Configurable Parameters**: Adjust temperature, guidance scale, and other generation parameters

## Installation

### Quick Install
```bash
python install_audio_deps.py
```

### Manual Install
```bash
pip install torch>=2.0.0 torchaudio>=2.0.0 transformers>=4.40.0
pip install descript-audio-codec>=1.0.0 soundfile>=0.13.1
pip install huggingface-hub>=0.30.2 safetensors>=0.5.3

# Platform specific (Windows)
pip install triton-windows==3.2.0.post18

# Platform specific (Linux)
pip install triton==3.2.0
```

## Hardware Requirements

- **GPU Recommended**: CUDA-compatible GPU for faster generation (RTX 4090: ~2x realtime)
- **CPU Fallback**: Works on CPU but significantly slower
- **Memory**: ~4.4GB VRAM (GPU) or ~7.9GB RAM (CPU)
- **Storage**: ~3GB for initial model download

## Usage

### MCP Tools

The integration provides two MCP tools:

1. **`generate_podcast_tool`** - Text-only podcast generation (existing)
2. **`generate_audio_podcast_tool`** - Text + Audio podcast generation (new)

### Example Usage

```python
# Text only podcast
result = generate_podcast("machine learning", "ml_paper.pdf", generate_audio=False)

# Audio podcast  
result = generate_podcast("machine learning", "ml_paper.pdf", generate_audio=True)
```

### MCP Tool Response Format

```json
{
  "success": true,
  "script": "S1: Today we're discussing...",
  "audio_path": "/path/to/audio.mp3",
  "audio_generated": true,
  "audio_duration_estimate": 45,
  "generation_params": {
    "temperature": 1.8,
    "guidance_scale": 3.0,
    "top_p": 0.90,
    "top_k": 45
  },
  "speaker_format": "S1 (Host), S2 (Expert)",
  "source_pdf": "document.pdf",
  "generated_at": "2024-01-01T12:00:00"
}
```

## Speaker Format

The integration uses the Dia TTS speaker format:

- **S1**: Host/Interviewer role
- **S2**: Expert/Content provider role

This format is optimized for the Dia model and ensures proper speaker differentiation in the generated audio.

## Configuration

### Audio Storage
Audio files are saved to the path specified in settings:
```python
# In settings.py
audio_storage_path: Path = Field(default_factory=lambda: Path("src/data/audio"))
```

### Generation Parameters
Default parameters can be adjusted in the `DiaTTS.generate_audio()` method:

- **max_new_tokens**: 3072 (maximum audio length)
- **guidance_scale**: 3.0 (CFG guidance strength)  
- **temperature**: 1.8 (sampling randomness)
- **top_p**: 0.90 (nucleus sampling threshold)
- **top_k**: 45 (top-k sampling limit)

## Architecture

### Components

1. **`pdf_mcp/audio/dia_tts.py`** - Core TTS integration
2. **`pdf_mcp/tools/podcast.py`** - Enhanced podcast generation
3. **`pdf_mcp/mcp/tools_impl.py`** - MCP tool registration
4. **`pdf_mcp/config/settings.py`** - Configuration management

### Flow

1. PDF content extraction
2. Dialogue script generation (S1/S2 format)
3. Optional audio generation via Dia TTS
4. File storage and response formatting

## Error Handling

The integration includes comprehensive error handling:

- **Missing Dependencies**: Graceful fallback to text-only mode
- **Model Loading Failures**: Detailed error messages
- **Generation Errors**: Error reporting with script preservation
- **Hardware Issues**: CPU/GPU detection and appropriate configuration

## Performance

### Benchmarks (RTX 4090)
- **bfloat16**: 2.1x realtime factor with compile, 1.5x without
- **float16**: 2.2x realtime factor with compile, 1.3x without  
- **float32**: 1.0x realtime factor with compile, 0.9x without

### Memory Usage
- **bfloat16/float16**: ~4.4GB VRAM
- **float32**: ~7.9GB VRAM

## Troubleshooting

### Common Issues

1. **"CUDA out of memory"**
   - Reduce batch size or use CPU
   - Close other GPU applications

2. **"Transformers not found"**  
   - Run `pip install transformers>=4.40.0`

3. **Slow generation on CPU**
   - Expected behavior, consider GPU upgrade
   - Reduce max_new_tokens for shorter audio

4. **Model download fails**
   - Check internet connection
   - Verify Hugging Face access

### Debug Mode
Enable detailed logging:
```python
import logging
logging.getLogger("pdf_mcp.audio").setLevel(logging.DEBUG)
```

## Future Enhancements

- **Voice Cloning**: Support for custom voice samples
- **Batch Processing**: Multiple podcast generation
- **Quality Settings**: Configurable audio quality/speed trade-offs
- **Caching**: Model caching for faster subsequent generations
- **Quantization**: Memory-efficient model variants

## References

- [Nari Labs Dia GitHub](https://github.com/nari-labs/dia)
- [Dia Model on Hugging Face](https://huggingface.co/nari-labs/Dia-1.6B-0626)
- [Dia Demo Space](https://huggingface.co/spaces/nari-labs/Dia-1.6B)
