# Use an llm which inputs a plain english query and outputs a relevant API call. If information is insufficient, it prompts the user for more information. 

# Imports
#!/usr/bin/env python
# coding: utf-8

import openeo
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
import requests
from dotenv import load_dotenv

import numpy as np  # Make sure to import numpy for np.dstack

# Connect to the OpenEO backend
connection = openeo.connect(url="openeo.dataspace.copernicus.eu")

# Authenticate using OpenID Connect
connection.authenticate_oidc()

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()
google_api_key = os.environ['GOOGLE_API_KEY']

# Initialize the model
model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key)

# Define the fetch_map function
def fetch_map(temp_start, temp_end, west, south, east, north, crs, bands, max_cc):
    """
    Fetch a map based on the input parameters.
    This is a placeholder function; implement the actual logic as needed.
    """
    print(f"Fetching map with parameters: {temp_start}, {temp_end}, {west}, {south}, {east}, {north}, {crs}, {bands}, {max_cc}")
    s2_cube = connection.load_collection(       # Load Sentinel-2 data collection)
        "SENTINEL2_L2A",
        temporal_extent=(temp_start, temp_end),
        spatial_extent={
            "west": west,
            "south": south,
            "east": east,
            "north": north,
            "crs": crs,
        },
        bands=bands,
        max_cloud_cover=max_cc,
    )

    output_file = "sentinel2_image.tif"
    s2_cube.download(output_file)

    with rasterio.open(output_file) as src:
        # Read the bands into arrays
        red = src.read(1)  # Band B04
        green = src.read(2)  # Band B03
        blue = src.read(3)  # Band B02

        # Normalize the bands for better visualization
        red_norm = red / red.max()
        green_norm = green / green.max()
        blue_norm = blue / blue.max()

        # Combine bands into an RGB image
        rgb_image = np.dstack((red_norm, green_norm, blue_norm))

        plt.figure(figsize=(10, 10))
        plt.imshow(rgb_image)
        plt.title("Sentinel-2 RGB Composite")
        plt.axis('off')
        plt.show()
    # Want to mention the exact date and timestamp of the image.

# Define the process_query function
def process_query(query: str):
    user_prompt = (
        "You are an assistant for querying satellite data. "
        "Your task is to extract the following information from the user's request: "
        "1. Official geographic name of the location / place the user is talking about. OR"
        "2. If applicable, any relevant address.\n\n"
        "Only return this relevant information. No other text should be included. Identify the place OR address only."
        "Also, if the name of a place is vague, or you are not sure what exactly it points to, please prompt the user for more information. Only proceed when you are perfectly certain."
        "For example, if the user query is 'Show me a map of Sheraton Hotel, New York in the time-range 2022-12-03 to 2022-12-31', respond with Sheraton New York Times Square Hotel, 811 7th Avenue, W 53rd St, New York, NY 10019"
        f"User query: {query}"
    )

    # Get the response from the model
    llm_response = model.invoke(user_prompt)
    print("LLM Raw Response:", llm_response)  # Debugging step
    
    # Extract the content
    response_content = llm_response.content
    print(response_content)

    return response_content

def get_coordinates(location: str):
    """
    Get the latitude and longitude of a specified location using the Google Geocoding API.

    Args:
        location (str): The location or address to geocode.

    Returns:
        tuple: A tuple containing the latitude and longitude as floats (lat, lng), or None if the request fails.
    """
    from dotenv import load_dotenv
    import os
    import requests

    # Load environment variables
    load_dotenv()
    api_key = os.environ.get('MAPS_API_KEY')  # Ensure the API key is stored in an environment variable
    
    if not api_key:
        raise ValueError("MAPS_API_KEY not found in environment variables.")

    # Build the Geocoding API request URL
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={api_key}"

    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP status codes >= 400

        # Parse the JSON response
        data = response.json()

        if data.get('status') == 'OK':
            # Extract latitude and longitude
            geometry = data['results'][0]['geometry']['location']
            return geometry['lat'], geometry['lng']
        else:
            # Handle specific Geocoding API errors
            print(f"Geocoding failed with status: {data.get('status')}")
            return None

    except requests.exceptions.RequestException as e:
        # Handle request errors
        print(f"Error while making the Geocoding API request: {e}")
        return None
    
# Main function to run the script
if __name__ == "__main__":
    print("Welcome to the Satellite Map Query Assistant!")
    while True:
        user_input = input("\nEnter your query (or type 'exit' to quit): ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # Process the user query and print the result
        response = process_query(user_input)
        print(response)
        north_response = process_query(f"North-most location in {response}")
        south_response = process_query(f"South-most location in {response}")
        east_response = process_query(f"East-most location in {response}")
        west_response = process_query(f"West-most location in {response}")
        print(north_response)
        print(south_response)
        print(east_response)
        print(west_response)
        print(get_coordinates(response))
        print(get_coordinates(north_response))
        print(get_coordinates(south_response))
        print(get_coordinates(east_response))
        print(get_coordinates(west_response))

