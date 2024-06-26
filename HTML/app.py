from flask import Flask, render_template, request, send_file,jsonify
from pytube import YouTube
#import subprocess

import os
import socket
from datetime import datetime
import requests
from PIL import Image
from pytube.innertube import _default_clients

_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]


app = Flask(__name__)


filepa=''
img=''
n=''
jk=''
city=''
country=''
Latitude=''
Longitude=''
def fetch_random_joke():
    global jk
    api_url = 'https://api.api-ninjas.com/v1/jokes?limit=1'
    headers = {'X-Api-Key': 'Your api'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data and len(data) > 0:
            joke = data[0].get('joke')
            return joke
    jk=joke
    return None


def get_tumb(url):
    global img
    global n
    yt=YouTube(url)
    img= yt.thumbnail_url
    
    n=yt.streams[0].title

def get_location():
    global city
    global country
    global longitude
    global latitude
    # Get user's IP address from the request headers
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    print(user_ip,)

    # Query IP geolocation service to get user's location
    response = requests.get(f'https://ipinfo.io/{user_ip}?token=Your api')
    print(response)
    
    if response.status_code == 200:
        # Parse the JSON response
        location_data = response.json()
        
        # Extract relevant location information
        city = location_data.get('city')
        country = location_data.get('country')
        
        # Check if loc attribute exists before splitting it
        loc = location_data.get('loc')
        if loc:
            latitude, longitude = loc.split(',')
        else:
            latitude, longitude = None, None
        
        # Print location information in the terminal
        print(f"User's Location - City: {city}, Country: {country}, Latitude: {latitude}, Longitude: {longitude}")
        
        return jsonify({
            'city': city,
            'country': country,
            'latitude': latitude,
            'longitude': longitude
        })
    else:
        return jsonify({'error': 'Failed to retrieve location information'}), 500
def logs(url, user_ip, device_name, choice, quality, syt):
    global city
    global country
    global longitude
    global latitude
    global jk
    # parameters to retrieve from API
    params = ['query', 'status', 'country', 'countryCode', 'city', 'timezone', 'mobile']
    resp = requests.get('http://ip-api.com/json/' + user_ip, params={'fields': ','.join(params)})
    info = resp.json()

    # Extract relevant information from the API response

    is_mobile = info.get('mobile', 'Unknown')
    get_location()
    


    # Get current time
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

    # Create log entry with all the information
    log_entry = f"{current_datetime};{user_ip};{device_name};{url};{choice};{quality};{syt};{country};{city};{latitude};{longitude};{is_mobile},{jk}\n"

    # Print log entry
    print(log_entry)

    # Write log entry to file for persistent logging
    log_file_path = 'd:/Youtube-vedio-downlaod/HTML/logs/logs.txt'
    with open(log_file_path, 'a') as file:
        file.write(log_entry)

    webhook_url = "https://webhook.site/7583aa57-5c30-4727-81ef-514e7baaacc7"

    # Define the data to be sent (as a string)
    data_to_send = log_entry

    # Send a POST request with the data to the webhook URL
    response = requests.post(webhook_url, data=data_to_send)

    # Check the response status
    if response.status_code == 200:
        print("Data sent successfully to the webhook!")
    else:
        print(f"Failed to send data to the webhook. Status code: {response.status_code}")


def sanitize_title(title):
    
    #Remove special characters from the title string.
    
    special_characters = ['/', '\\', '|', '?', '*', ':', '"', '<', '>', '.']
    for char in special_characters:
        title = title.replace(char, '_')
    return title

def audiodownload(url, qua):
    desired_audio_quality = qua
    yt = YouTube(url)
    title = sanitize_title(yt.title)
    audio_stream = yt.streams.filter(only_audio=True, abr=desired_audio_quality).first()

    if audio_stream:
        audio_path = os.path.join('D:/Youtube-vedio-downlaod/Video-download/', f"{title}_{desired_audio_quality}.mp3")
        audio_stream.download(output_path='D:/Youtube-vedio-downlaod/Video-download/', filename=f"{title}_{desired_audio_quality}.mp3")
        print("Audio saved successfully!")
        return audio_path
    else:
        print(f"No audio stream found with quality '{desired_audio_quality}'.")

def videodownload(url, resolution):
    yt = YouTube(url)
    title = sanitize_title(yt.title)
    video_stream = yt.streams.filter(res=resolution, progressive=True).first()
    output_path = r'D:\Youtube-vedio-downlaod\Video-download'

    if video_stream:
        temp_filename = f"{title}_final.mp4"
        video_path = os.path.join(output_path, temp_filename)
        video_stream.download(output_path=output_path, filename=temp_filename)
        print(f"Video downloaded successfully with resolution: {resolution}")
    else:
        print(f"No video stream found with resolution '{resolution}'")
        return

    audio_streams = yt.streams.filter(only_audio=True)
    audio_stream = None
    for stream in audio_streams:
        try:
            bitrate = int(stream.abr[:-3])
            if audio_stream is None or bitrate > int(audio_stream.abr[:-3]):
                audio_stream = stream
        except ValueError:
            print(f"Skipping stream with bitrate '{stream.abr}' as it cannot be converted to an integer")

    if audio_stream:
        audio_path = os.path.join(output_path, f"{title}_audio.mp3")
        audio_stream.download(output_path=output_path, filename=f"{title}_audio")
        print(f"Audio downloaded successfully with bitrate: {audio_stream.abr}")
    else:
        print("No audio stream found")
        return

    final_video_path = os.path.join(output_path, f"{title}_temp_video.mp4")
    os.system(f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -c:a aac -strict experimental -movflags +faststart {final_video_path}")
    print(f"Final video saved successfully at: {final_video_path}")
    os.remove(video_path)
    os.remove(audio_path)
    os.rename(final_video_path, os.path.join(output_path, f"{title}_final.mp4"))

@app.route('/')
def index():
    user_ip = request.remote_addr
    device_name = socket.gethostname()
    return render_template('index.html', user_ip=user_ip, device_name=device_name)

def videoquality(url):
    yt = YouTube(url)
    streams_info = []
    for stream in yt.streams.filter(file_extension='mp4'):
        if stream.resolution:
            streams_info.append({
                'resolution': stream.resolution,
                'audio_bitrate': stream.abr,
                'itag': stream.itag
            })
    return streams_info

def audioquality(url):
    yt = YouTube(url)
    audio_streams_info = []
    audio_streams = yt.streams.filter(only_audio=True)
    for stream in audio_streams:
        audio_streams_info.append({
            'audio_bitrate': stream.abr,
            'itag': stream.itag
        })
    return audio_streams_info

@app.route('/video_quality', methods=['POST'])
def video_quality():
    global img
    global n
    url = request.form['url']
    get_tumb(url)
    option = request.form['option']
    if option == 'video':
        streams_info = videoquality(url)
        return render_template('video_quality.html', streams_info=streams_info, url=url, option=option,image=img,nam=n)
    elif option == 'audio':
        audio_streams_info = audioquality(url)
        return render_template('audio_quality.html', audio_streams_info=audio_streams_info, url=url, option=option,image=img,nam=n)

@app.route('/audio_quality', methods=['POST'])
def audio_quality():
    global img
    global n
    url = request.form['url']
    option = request.form['option']
    audio_streams_info = audioquality(url)
    return render_template('audio_quality.html', audio_streams_info=audio_streams_info, url=url, option=option,image=img,nam=n)


@app.route('/thankuu')
def thank():
    return send_file(filepa,as_attachment=True)



@app.route('/download', methods=['POST'])
def download():
    global filepa
    url = request.form['url']
    option = request.form['option']
    chosen_quality = request.form['chosen_quality']
    

    if option == 'video':
        if chosen_quality == '160':
            chosen_quality = '144p'
        elif chosen_quality == '133':
            chosen_quality = '240p'
        elif (chosen_quality == '134') or (chosen_quality == '18'):
            chosen_quality = '360p'
        elif chosen_quality == '135':
            chosen_quality = '480p'
        elif (chosen_quality == '136') or (chosen_quality == '22'):
            chosen_quality = '720p'
        elif chosen_quality == '137':
            chosen_quality = '1080p'

        
        title = sanitize_title(YouTube(url).title)  # Sanitize the title
        file_name = f"{title}_final.mp4"
        chek=os.path.join('D:/Youtube-vedio-downlaod/Video-download/', file_name)
        if(os.path.exists(chek)==False):
            print('video not found downloading')
            file_path = os.path.join('D:/Youtube-vedio-downlaod/Video-download/', file_name)
            videodownload(url, chosen_quality)
        else:
            print('Video found presenting it')
            file_path=chek
            
    elif option == 'audio':
        if chosen_quality == '251':
            chosen_quality = '160kbps'
        elif chosen_quality == '250':
            chosen_quality = '70kbps'
        elif chosen_quality == '249':
            chosen_quality = '50kbps'
        elif chosen_quality == '140':
            chosen_quality = '128kbps'
        elif chosen_quality == '139':
            chosen_quality = '48kbps'
        yt = YouTube(url)
        title = sanitize_title(yt.title)
        chek = os.path.join('D:/Youtube-vedio-downlaod/Video-download/', f"{title}_{chosen_quality}.mp3")
        print(chek+'a')
        if(os.path.exists(chek)==False):
            print('Not found downloading')
            file_path = audiodownload(url, chosen_quality)
        else:
            print('Sucessfully found existing audio')
            file_path=chek
    user_agent = request.headers.get('User-Agent')

    logs(url, request.remote_addr, socket.gethostname(), option, chosen_quality, user_agent)
    
    filepa=file_path
    #Get quote
        # Fetching quote and author from the API
    joke = fetch_random_joke()
    # Render the "thankyou.html" template
    return render_template('thankyou.html',joke=joke)



    


if __name__ == '__main__':
    #cert_path = r'd:\Youtube-vedio-downlaod\HTML\cert.pem'  
    #key_path = r'd:\Youtube-vedio-downlaod\HTML\key.pem'   
    app.run( debug=True, host='0.0.0.0', port=80)

