#!/usr/bin/env python
import os
import click
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, VideoClip, CompositeVideoClip
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import matplotlib
import time
import librosa
matplotlib.use('Agg')

# Ensure compatibility with newer Pillow versions
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

def get_audio_data(audio_file):
    """Load audio data using librosa instead of MoviePy."""
    print("Loading audio with librosa...")
    y, sr = librosa.load(audio_file, sr=None)
    print(f"Audio loaded: {len(y)} samples, {sr}Hz sample rate")
    return y, sr

def create_waveform_animation(audio_data, sample_rate, duration, waveform_type, resolution, waveform_color="#FF4500"):
    """
    Create a waveform animation video clip.
    
    Args:
        audio_data: Audio samples from librosa
        sample_rate: Audio sample rate
        duration: Duration of the video
        waveform_type: Type of waveform ('simple', 'mirror', or 'line')
        resolution: Video resolution (square)
        waveform_color: Color of the waveform (default: orange-red)
        
    Returns:
        VideoClip with waveform animation
    """
    fps = 30
    
    # Function to create a frame at time t
    def make_frame(t):
        try:
            # Calculate which audio segment to display based on time
            center_idx = int(t * sample_rate)
            
            # Use larger window for better visibility
            window_size = int(sample_rate * 0.5)  # 500ms window
            start_idx = max(0, center_idx - window_size//2)
            end_idx = min(len(audio_data), start_idx + window_size)
            
            # Extract audio segment
            if end_idx <= start_idx:
                audio_segment = np.array([0, 0])
            else:
                audio_segment = audio_data[start_idx:end_idx]
            
            # Ensure enough samples
            if len(audio_segment) < 2:
                audio_segment = np.array([0, 0])
                
            # Create figure with transparent background
            fig = plt.figure(figsize=(8, 8), dpi=resolution//8)
            plt.axis('off')
            
            # Set completely transparent figure
            fig.patch.set_alpha(0)
            
            # X-axis values
            x = np.linspace(0, 1, len(audio_segment))
            
            # Create different waveform visualizations
            if waveform_type == "simple":
                # Simple one-sided waveform
                plt.fill_between(x, audio_segment, 0, color=waveform_color)
                plt.ylim(-0.8, 0.8)
                
            elif waveform_type == "mirror":
                # Mirrored waveform (symmetric around center)
                plt.fill_between(x, audio_segment, -audio_segment, color=waveform_color)
                plt.ylim(-0.8, 0.8)
                
            elif waveform_type == "line":
                # Line waveform with higher resolution
                plt.plot(x, audio_segment, color=waveform_color, linewidth=4)
                plt.ylim(-0.8, 0.8)
                
            # Save the figure to an RGB array (moviepy works best with RGB)
            # First save to a PNG with transparent background
            buf = BytesIO()
            plt.savefig(buf, format='png', transparent=True, 
                      bbox_inches='tight', pad_inches=0)
            buf.seek(0)
            
            # Open with PIL
            pil_img = Image.open(buf)
            
            # Resize to match resolution
            pil_img = pil_img.resize((resolution, resolution), Image.LANCZOS)
            
            # Convert to RGB (moviepy expects RGB)
            rgb_img = np.array(pil_img.convert('RGB'))
            
            plt.close(fig)
            return rgb_img
            
        except Exception as e:
            print(f"Error in make_frame at t={t}: {e}")
            # Return a blank frame in case of error
            return np.zeros((resolution, resolution, 3), dtype=np.uint8)
    
    # Create and return video clip
    return VideoClip(make_frame, duration=duration).set_fps(fps)

@click.command()
@click.argument("audio_file", type=click.Path(exists=True))
@click.argument("image_file", type=click.Path(exists=True))
@click.option("--waveform", type=click.Choice(['simple', 'mirror', 'line']), 
              default='mirror', prompt=True,
              help="Choose waveform style: simple, mirror, or line")
@click.option("--resolution", type=click.Choice(['480', '720', '1080']), 
              default='720', prompt=True,
              help="Video resolution (square): 480, 720, or 1080")
@click.option("--waveform-color", default="#FF4500", help="Waveform color in hex format (e.g. #FF4500 for orange)")
@click.option("--output", "-o", default="output.mp4", help="Output video filename")
def create_waveform_video(audio_file, image_file, waveform, resolution, waveform_color="#FF4500", output="output.mp4"):
    """Create a video with waveform animation overlay on a background image."""
    
    print(f"Processing audio: {audio_file}")
    print(f"Processing image: {image_file}")
    print(f"Waveform type: {waveform}")
    print(f"Waveform color: {waveform_color}")
    print(f"Resolution: {resolution}x{resolution}")
    print(f"Output will be saved to: {output}")
    
    start_time = time.time()
    try:
        resolution = int(resolution)
        
        # Load the audio file with librosa
        audio_data, sample_rate = get_audio_data(audio_file)
        
        # Also load with MoviePy for playback
        audio_clip = AudioFileClip(audio_file)
        duration = audio_clip.duration
        print(f"Audio duration: {duration:.2f} seconds")
        
        # Load and resize the background image to be square
        image_clip = (ImageClip(image_file)
                     .set_duration(duration)
                     .resize(width=resolution, height=resolution))
        
        print("Image prepared")
        
        # Generate waveform animation
        print("Generating waveform animation...")
        waveform_clip = create_waveform_animation(
            audio_data, sample_rate, duration, waveform, resolution, waveform_color
        )
        print("Waveform animation created")
        
        # Set opacity for waveform over image
        waveform_clip = waveform_clip.set_opacity(0.8)
        
        # Combine image and waveform (waveform on top)
        final_clip = CompositeVideoClip(
            [image_clip, waveform_clip.set_position('center')],
            size=(resolution, resolution)
        )
        
        # Add audio to the final clip
        final_clip = final_clip.set_audio(audio_clip)
        print("Video composition complete")
        
        # Export the video
        print(f"Writing output to {output}...")
        final_clip.write_videofile(
            output,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=4
        )
        print(f"Video successfully created at {output}")
        
        elapsed_time = time.time() - start_time
        print(f"Total processing time: {elapsed_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error creating video: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    create_waveform_video()