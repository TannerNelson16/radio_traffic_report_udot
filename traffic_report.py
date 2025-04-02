#!/usr/bin/python3
import requests
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
import os
from google.cloud import texttospeech
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1

local_time = datetime.now()
print("Local time:", local_time)

# Set the path to your Google service account JSON key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/radio_weather_report/service_account_key.json"

# API Endpoints and Parameters
API_KEY = "YOUR API KEY"
BASE_PARAMS = {"key": API_KEY, "format": "json"}
road_conditions_url = "https://www.udottraffic.utah.gov/api/v2/get/roadconditions"
mountain_passes_url = "https://www.udottraffic.utah.gov/api/v2/get/mountainpasses"
advisories_url = "https://www.udottraffic.utah.gov/api/v2/get/alerts"
snow_plows_url = "https://www.udottraffic.utah.gov/api/v2/get/servicevehicles"

# Interest Parameters
roadways_of_interest = ["SEARCH API INFO ON UDOT's WEBSITE FOR ROADWAYS OF INTEREST"]
passes_of_interest = {"SEARCH API INFO ON UDOT's WEBSITE FOR PASSES OF INTEREST"}
regions_of_interest = {"SEARCH API INFO ON UDOT's WEBSITE FOR REGIONS OF INTEREST"}
REF_LATITUDE = YOUR LATITUDE
REF_LONGITUDE = YOUR LONGITUDE
MAX_DISTANCE = 15  # miles
ONE_HOUR_AGO = datetime.now() - timedelta(hours=1)

# Helper Functions
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Radius of Earth in miles
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def bearing_to_cardinal(bearing):
    directions = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]
    return directions[round(bearing / 45) % 8]

def get_address_from_coords(latitude, longitude):
    url = "https://nominatim.openstreetmap.org/reverse"
    headers = {"User-Agent": "Traffic_Update (tannernelson16@gmail.com)"}
    response = requests.get(url, params={"lat": latitude, "lon": longitude, "format": "json", "addressdetails": 1}, headers=headers)
    if response.ok:
        address = response.json().get("address", {})
        return address.get("road", "Street not found"), address.get("city", address.get("town", address.get("village", "City not found"))), address.get("county", "County not found")
    return " ", " ", " "

def generate_traffic_report():
    report = ["Here is your Radio traffic report! With the help of U-DOT, we provide you the most up to date information."]

    # Road Conditions
    response = requests.get(road_conditions_url, params=BASE_PARAMS)
    road_conditions = response.json() if response.ok else []
    dry_fair = True
    for condition in road_conditions:
        if condition.get("RoadwayName") in roadways_of_interest:
            road_condition = condition.get("RoadCondition", "Unknown")
            weather_condition = condition.get("WeatherCondition", "Unknown")
            if road_condition != "Dry" or weather_condition != "Fair":
                report.append(f"{condition['RoadwayName']} is {road_condition} with {weather_condition} weather.")
                dry_fair = False
    if dry_fair:
        report.append("All roadways are clear in the area.")

    # Mountain Passes
    response = requests.get(mountain_passes_url, params=BASE_PARAMS)
    mountain_passes = response.json() if response.ok else []
    good_visibility = True
    for pass_info in mountain_passes:
        name, roadway = pass_info.get("Name"), pass_info.get("Roadway")
        visibility = pass_info.get("Visibility", "None")
        if name in passes_of_interest and roadway == passes_of_interest[name]:
            # Convert visibility to a float if it's a valid number
            if visibility is not None and visibility != "None" and visibility != "":
                try:
                    visibility_value = float(visibility)
                    if visibility_value <= 4:
                        report.append(f"{roadway} has low visibility due to the current weather conditions.")
                        good_visibility = False
                    elif visibility_value <=8:
                        report.append(f"{roadway} has lowered visibility due to the current weather conditions.")
                except ValueError:
                    # Skip if visibility is not a valid float
                    pass
    if good_visibility:
        report.append("All mountain passes are clear with good visibility.")

    # Advisories
    response = requests.get(advisories_url, params=BASE_PARAMS)
    advisories = response.json() if response.ok else []
    
    for advisory in advisories:
        if "Seasonal Road Closures" not in advisory.get("Message", "") and regions_of_interest.intersection(set(advisory.get("Regions", []))):
            message = advisory.get("Message","")
            start_time = advisory.get("StartTime", 0)
            end_time = advisory.get("EndTime",0)
            start_time_dt = datetime.fromtimestamp(start_time).strftime('%B %d at %-I:%M %p')
            end_time_dt = datetime.fromtimestamp(end_time).strftime('%B %d at %-I:%M %p')
            report.append(f"According to U-Dot, as of {start_time_dt}, {message}, This advisory is in place until {end_time_dt}.")

    # Snow Plows
    response = requests.get(snow_plows_url, params=BASE_PARAMS)
    vehicles = response.json() if response.ok else []
    for vehicle in vehicles:
        bearing = vehicle.get("Bearing")
        latitude, longitude = vehicle.get("Latitude"), vehicle.get("Longitude")
        last_updated = datetime.fromtimestamp(vehicle.get("LastUpdated", 0))
        street, city, _ = get_address_from_coords(latitude, longitude)
        if city != "City not found" and street != "Street not found": 
            distance = haversine(REF_LATITUDE, REF_LONGITUDE, latitude, longitude) if latitude and longitude else None
            if distance and distance <= MAX_DISTANCE and last_updated >= ONE_HOUR_AGO:
                report.append(f"There is a snowplow on {street} in {city} heading {bearing_to_cardinal(float(bearing))}.")
    
    #report.append("Drive Cautiously.")
    report.append("We hope you found this traffic report helpful. Drive safely out there.")
    return " ".join(report)

def text_to_speech_traffic(report):
    """Convert the traffic report to realistic speech and save as MP3."""
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=report)
    voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-I",
    ssml_gender=texttospeech.SsmlVoiceGender.MALE
)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Generate the speech
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Save the audio as an MP3 file
    #timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"traffic_report.mp3"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
        print(f"Traffic report saved as {filename}")
    return filename

def add_background_music_with_fade(voice_file, music_file, output_file,name,music_volume=-8, fade_in_duration=1000, fade_out_duration=1500):
    """
    Adds background music to a voice audio file with fade-in and fade-out effects.

    Parameters:
    - voice_file: str - Path to the synthesized voice audio file.
    - music_file: str - Path to the background music audio file.
    - output_file: str - Path to the output file.
    - music_volume: int - Volume adjustment for the music in dB.
    - fade_in_duration: int - Duration of the fade-in effect in milliseconds.
    - fade_out_duration: int - Duration of the fade-out effect in milliseconds.
    """
    # Load the voice audio and background music
    voice = AudioSegment.from_file(voice_file)
    music = AudioSegment.from_file(music_file)

    # Adjust music volume
    music = music - abs(music_volume)

    # Loop or trim the background music to match the length of the voice
    if len(music) < len(voice):
        music = music * (len(voice) // len(music) + 1)
    music = music[:len(voice)]

    # Apply fade-in and fade-out effects to the music
    music = music.fade_in(fade_in_duration).fade_out(fade_out_duration)

    # Overlay voice onto music
    combined = music.overlay(voice)

    # Export the combined audio
    combined.export(output_file, format="mp3")
    audio_file = MP3(output_file, ID3=ID3)

    # Add metadata tags
    audio_file["TPE1"] = TPE1(encoding=3, text="Morgan Valley Radio")  # Artist tag
    audio_file["TIT2"] = TIT2(encoding=3, text=name)   # Title tag

    # Save the metadata changes
    audio_file.save()
    print(f"Saved report with background music and fades as '{output_file}'.")

def main():
    traffic_report = generate_traffic_report()
    #print(traffic_report)
    add_background_music_with_fade(text_to_speech_traffic(traffic_report),"/etc/radio_weather_report/music.mp3",output_file="/media/plexmediaserver/Personal/Music/Traffic/traffic_update.mp3",name="Traffic Update")

if __name__ == "__main__":
    main()
