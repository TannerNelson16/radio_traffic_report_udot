# Radio Traffic Report

This Python script generates a traffic report using data from the Utah Department of Transportation (UDOT) API and converts the report into an audio file. The script provides road conditions, mountain pass visibility, advisories, and snowplow locations, with the audio report enhanced with background music.

## Sample

https://github.com/user-attachments/assets/bb5d332a-0eff-4599-ac0c-52b2df829afa

## Features

- **Traffic Report Generation:** Fetches real-time traffic information for surrounding regions, including:
  - Road conditions for key roadways of interest
  - Mountain pass visibility and conditions
  - Active traffic advisories
  - Snowplow locations and routes
- **Text-to-Speech Conversion:** The report is converted into speech using Google Cloud's Text-to-Speech API.
- **Background Music:** Background music is added to the generated audio report with a fade-in and fade-out effect.
- **Metadata:** The generated MP3 includes metadata tags for artist and title.

## Requirements

- Python 3.x
- Google Cloud Text-to-Speech API (ensure you have set up your Google Cloud service account and the associated credentials)
- Required Python packages:
  - `requests`
  - `google-cloud-texttospeech`
  - `pydub`
  - `mutagen`

You can install the required packages using pip:

pip install requests google-cloud-texttospeech pydub mutagen

## Setup

1. **Google Cloud API Key:**  
   Set up your Google Cloud project and enable the Text-to-Speech API. Download the service account key in JSON format and save it to `/etc/radio_weather_report/service_account_key.json`. 

2. **API Keys and URLs:**  
   Replace the placeholders in the script with the necessary API keys and parameters:
   - `API_KEY`: Set your UDOT API key for traffic data.
   - `BASE_PARAMS`: Set your API parameters as needed.

3. **Background Music:**  
   Ensure that you have a background music file (`music.mp3`) located at `/etc/radio_weather_report/music.mp3`. The music file will be used as the background track in the final report.

## Usage

1. Clone the repository to your local machine:

2. Run the script to generate the traffic report and audio file:

python3 traffic_report.py

This will generate an MP3 file (`traffic_update.mp3`) with the traffic report, which will be saved to the specified output directory.

## File Structure

radio-traffic-report/  
├── traffic_report.py         # Main Python script  
├── README.md                 # This README file  
└── /etc/radio_weather_report/  # Folder for service account key and background music  
    ├── music.mp3             # Background music for the report  
    └── service_account_key.json  # Google Cloud service account key  

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- UDOT Traffic API for providing real-time traffic data.
- Google Cloud Text-to-Speech API for converting the text into speech.
- Pydub and Mutagen libraries for audio processing and metadata management.
