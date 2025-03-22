# WaveMaker: Audio Waveform Visualizer

WaveMaker is a tool for creating beautiful videos from audio files with animated waveform visualizations overlaid on background images.

## Features

- Create square video files from audio files (WAV) and images
- Multiple waveform visualization styles:
  - `simple`: One-sided waveform
  - `mirror`: Mirrored waveform (symmetric around center)
  - `line`: Line-style waveform
- Customizable resolution: 480p, 720p, or 1080p
- Customizable waveform color

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/wave-maker.git
   cd wave-maker
   ```

2. Set up a Python environment (recommended):
   ```bash
   conda create -n wavemaker python=3.10
   conda activate wavemaker
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Basic usage:
```bash
python movie-maker.py audio_file.wav image_file.png --waveform mirror --resolution 720 --output output.mp4
```

### Parameters

- `audio_file`: Path to the audio file (WAV format)
- `image_file`: Path to the background image file (PNG, JPG, etc.)
- `--waveform`: Waveform visualization style (simple, mirror, line)
- `--resolution`: Video resolution in pixels (480, 720, 1080) - square format
- `--waveform-color`: Color of the waveform in hex format (default: #FF4500)
- `--output`: Output video filename (default: output.mp4)

## Example

```bash
python movie-maker.py voice.wav background.png --waveform mirror --resolution 720 --waveform-color "#00AAFF" --output my_video.mp4
```

## License

MIT License - see LICENSE file for details.