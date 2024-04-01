from pytube import YouTube
import os

a=[]
def audio(url):
    url = url
    print()
    global a
    yt = YouTube(url)
    # Filter the available streams to get only audio streams
    audio_streams = yt.streams.filter(only_audio=True)

    # Extract and print the audio qualities
    audio_qualities = [stream.abr for stream in audio_streams if stream.abr]
    print("Available audio qualities:")
    for quality in audio_qualities:
        quality=str(quality)
        if((quality in a) == False):
            a.append(quality)
    print(a)
    for i in a:
        print(i)

        
    desired_audio_quality = input('Enter audio quality')  # Adjust this to the desired audio quality
    desired_audio_quality=desired_audio_quality+'kbps'
    # Filter the available streams to get only audio streams with the desired quality
    audio_stream = yt.streams.filter(only_audio=True, abr=desired_audio_quality).first()

    if audio_stream:
        # Download the selected audio stream
        audio_stream.download(output_path='D:\Youtube-vedio-downlaod\Video-download')
        print("Audio saved successfully!")
    else:
        print(f"No audio stream found with quality '{desired_audio_quality}'.")



def video(url):
    yt = YouTube(url)

    # Filter video streams and display relevant information
    print("Available video streams:")
    for stream in yt.streams.filter(file_extension='mp4'):
        if stream.resolution:
            print(f"Resolution: {stream.resolution}, Audio Bitrate: {stream.abr}, Tag: {stream.itag}")

    resolution = input('Enter resolution required: ')
    resolution+='p'
    output_path='D:\Youtube-vedio-downlaod\Video-download'
    
    # Filter video streams by the specified resolution
    video_stream = yt.streams.filter(res=resolution, progressive=True).first()
    if video_stream:
        video_path = os.path.join(output_path, f"{yt.title}_video.mp4")
        video_stream.download(output_path=output_path, filename=f"{yt.title}_video")
        print(f"Video downloaded successfully with resolution: {resolution}")
    else:
        print(f"No video stream found with resolution '{resolution}'")
        return

    # Get the audio stream with the highest bitrate
    audio_streams = yt.streams.filter(only_audio=True)
    audio_stream = max(audio_streams, key=lambda x: int(x.abr[:-3]))  # Get the stream with highest bitrate
    if audio_stream:
        audio_path = os.path.join(output_path, f"{yt.title}_audio.mp3")
        audio_stream.download(output_path=output_path, filename=f"{yt.title}_audio")
        print(f"Audio downloaded successfully with bitrate: {audio_stream.abr}")
    else:
        print("No audio stream found")
        return

    # Merge video and audio streams using ffmpeg
    final_video_path = os.path.join(output_path, f"{yt.title}_final.mp4")
    os.system(f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -c:a aac -strict experimental {final_video_path}")

    print(f"Final video saved successfully at: {final_video_path}")

    # Clean up temporary files
    os.remove(video_path)
    os.remove(audio_path)   

    



    
url=input('Enter youtube URL:')
print()

yt=YouTube(url)

#Get title of video

video_title=yt.title

print(video_title)
print()
print('1: video download\n2: Audio download')
ch=int(input())
if(ch==2):
    audio(url)

if(ch==1):
    video(url)
