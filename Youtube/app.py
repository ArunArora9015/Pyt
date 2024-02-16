from flask import Flask, render_template, request, jsonify
import re
import googleapiclient.discovery

app = Flask(__name__)

def get_video_duration(api_key, video_id):
    try:
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        request = youtube.videos().list(part="contentDetails,snippet", id=video_id)
        response = request.execute()

        if "items" in response and response["items"]:
            snippet = response["items"][0]["snippet"]
            is_live = snippet.get("liveBroadcastContent", None) == "live"

            if is_live:
                return "Live"
            else:
                duration_iso = response["items"][0]["contentDetails"]["duration"]
                duration_seconds = duration_iso_to_seconds(duration_iso)
                duration_formatted = (
                    str(int(duration_seconds // 3600)).zfill(2) + ":"
                    + str(int((duration_seconds % 3600) // 60)).zfill(2) + ":"
                    + str(int(duration_seconds % 60)).zfill(2)
                )
                duration_description = get_duration_description(int(duration_seconds))
                return duration_formatted, duration_description
        else:
            return "Error: Video details not available."

    except Exception as e:
        return f"Error: {e}"

def duration_iso_to_seconds(duration_iso):
    match = re.match(r'P(\d+Y)?(\d+M)?(\d+D)?T(\d+H)?(\d+M)?(\d+S)?', duration_iso)
    if match:
        duration = 0
        for group in match.groups():
            if group:
                duration += int(group[:-1]) * 3600 if 'H' in group else 0
                duration += int(group[:-1]) * 60 if 'M' in group else 0
                duration += int(group[:-1]) if 'S' in group else 0
        return duration
    else:
        return 0

def get_duration_description(duration_seconds):
    hours = duration_seconds // 3600
    minutes = (duration_seconds % 3600) // 60
    seconds = duration_seconds % 60

    description = ""
    if hours > 0:
        description += f"{hours} {'hour' if hours == 1 else 'hours'} "
    if minutes > 0:
        description += f"{minutes} {'minute' if minutes == 1 else 'minutes'} "
    if seconds > 0:
        description += f"{seconds} {'second' if seconds == 1 else 'seconds'}"

    return description.strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_duration', methods=['POST'])
def check_duration():
    api_key = "AIzaSyBp4AH48_sbxF_81Zw38dlg6VWiqXyJn7g"  # Replace with your actual YouTube Data API v3 key
    youtube_link = request.form.get('youtube_link')
    video_id = extract_video_id(youtube_link)

    if video_id:
        duration_or_live = get_video_duration(api_key, video_id)
        if isinstance(duration_or_live, tuple):
            duration, duration_description = duration_or_live
            return jsonify({'duration': duration, 'description': duration_description})
        else:
            return jsonify({'live': True})
    else:
        return jsonify({'error': 'Please Check Your Url'})

def extract_video_id(url):
    match = re.search(r'(youtu\.be/|youtube\.com/shorts/|youtube\.com/live/)([^&?/]+)', url)
    return match.group(2) if match else None
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
