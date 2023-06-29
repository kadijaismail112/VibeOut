"""
VibeOut: A Python3 script to give a quote that matches the weather and mood of the user.
Given a location, the script will use the OpenWeatherMap API to get the weather and then
prompt the user for their mood. The script will then use the mood and weather to find a
quote that matches the user's mood and the weather.
"""

import random
import requests
import pandas as pd
import sqlalchemy as db

weather_quotes = {
    'sunny': {
        'happy': [
            "The sun shines bright, and so do you. Embrace the radiance within.",
            "Let the sunshine fuel your happiness and brighten your day."
        ],
        'sad': [
            "Even on sunny days, it's okay to feel blue. Reach out and let others in.",
            "Remember that sunshine can warm the coldest of hearts. Seek its embrace."
        ],
        'default': [
            "The sun shines bright, and so do you. Embrace the radiance within.",
            "Let the sunshine fuel your happiness and brighten your day."
        ]
    },
    'clear': {
        'happy': [
            "It's a beautiful day! Embrace the sunshine.",
            "Sunshine is the best medicine for a happy mood."
        ],
        'sad': [
            "Even on clear days, it's okay to feel sad. Take your time.",
            "Remember that clear skies can follow even the stormiest days."
        ],
        'default': [
            "It's a beautiful day! Embrace the sunshine.",
            "Even on clear days, there's always room for improvement."
        ]
    },
    'partly cloudy': {
        'happy': [
            "Even on partly cloudy days, the sky holds endless possibilities.",
            "Don't let the clouds dim your positive vibes."
        ],
        'sad': [
            "Partly cloudy days can match your mood. Hang in there.",
            "Even with clouds around, remember that the sun still shines above."
        ],
        'default': [
            "Even on partly cloudy days, the sky holds endless possibilities.",
            "Don't let the clouds dim your positive vibes."
        ]
    },
    'rain': {
        'happy': [
            "Life isn't about waiting for the storm to pass, it's about dancing in the rain.",
            "Rainy days are perfect for cozying up with a good book."
        ],
        'sad': [
            "Rainy days can make you feel down, but remember the beauty they bring.",
            "Rainy days cleanse the soul. Embrace the rhythm of falling raindrops."
        ],
        'default': [
            "Life isn't about waiting for the storm to pass, it's about dancing in the rain.",
            "Rainy days are perfect for cozying up with a good book."
        ]
    },
    'thunderstorm': {
        'happy': [
            "Find the beauty in thunderstorms. They remind us of nature's power.",
            "Thunderstorms bring a symphony of energy. Embrace the exhilaration."
        ],
        'sad': [
            "Thunderstorms can reflect inner turmoil. Seek comfort and find peace.",
            "Let the rumble of thunder wash away your troubles. Peace awaits."
        ],
        'default': [
            "Find the beauty in thunderstorms. They remind us of nature's power.",
            "Thunderstorms bring a symphony."
        ]
    },
    'snow': {
        'happy': [
            "When life gives you snow, make snow angels.",
            "Embrace the magic of snowy days and find joy in every flake."
        ],
        'sad': [
            "Snowy days can be challenging, but they hold a unique beauty.",
            "Wrap yourself in warmth and find solace in the enchantment of snow."
        ],
        'default': [
            "When life gives you snow, make snow angels.",
            "Embrace the magic of snowy days and find joy in every flake."
        ]
    },
    'fog': {
        'happy': [
            "In the midst of fog, opportunities for mystery and discovery arise.",
            "Fog adds an air of enchantment. Embrace the unknown."
        ],
        'sad': [
            "Fog can mirror a clouded mind. Seek clarity and hold on to hope.",
            "When the world is shrouded in fog, remember that the sun still shines above."
        ],
        'default': [
            "In the midst of fog, opportunities for mystery and discovery arise.",
            "Fog adds an air of enchantment. Embrace the unknown."
        ]
    },
    'windy': {
        'happy': [
            "Let the wind carry away your worries and fill you with renewed energy.",
            "Windy days are perfect for flying kites and feeling alive."
        ],
        'sad': [
            "Windy days can stir restlessness within, but remember the power they hold.",
            "Embrace the gusts of wind and let them guide you towards new beginnings."
        ],
        'default': [
            "Let the wind carry away your worries and fill you with renewed energy.",
            "Windy days are perfect for flying kites and feeling alive."
        ]
    },
    'mist': {
        'happy': [
            "In the mist, secrets of tranquility unravel. Embrace the calm.",
            "Mist adds a touch of magic. Let it guide you to a world of serenity."
        ],
        'sad': [
            "Misty days can mirror a somber mood. Seek solace in gentle moments.",
            "When the mist surrounds you, take a deep breath and find peace within."
        ],
        'default': [
            "In the mist, secrets of tranquility unravel. Embrace the calm.",
            "Mist adds a touch of magic. Let it guide you to a world of serenity."
        ]
    }
}

# Create an engine object
engine = db.create_engine('sqlite:///vibes.db')

# Define the table structure
metadata = db.MetaData()
table = db.Table('weather_data', metadata,
                 db.Column('mood', db.String),
                 db.Column('location', db.String),
                 db.Column('weather_condition', db.String),
                 db.Column('temperature', db.Float),
                 db.Column('quote', db.String)
                 )
metadata.create_all(engine)

# Function to generate a random quote based on weather conditions and mood
def generate_quote(weather_condition, mood, location):
    # Check if any previous records exist with the same location and weather condition
    with engine.connect() as connection:
        query = db.select(table).where(
            (table.c.location == location) &
            (table.c.weather_condition == weather_condition)
        )
        query_result = connection.execute(query)
        rows = query_result.fetchall()

    # If there are previous records with the same location and weather condition,
    # filter the quotes based on the mood
    if rows:
        mood_quotes = [row['quote'] for row in rows if row['mood'] == mood]
        if mood_quotes:
            return random.choice(mood_quotes)

    # If no matching records or no quotes for the mood, generate a random quote
    if weather_condition in weather_quotes:
        quotes = weather_quotes[weather_condition]
        mood_quotes = quotes.get(mood, quotes['default'])
        if mood_quotes:
            return random.choice(mood_quotes)

    return "Enjoy your day!"

# Function to retrieve weather data from the WeatherAPI.com API
def get_weather_data(api_key, location):
    # Make an API request to the WeatherAPI.com API
    url = "http://api.weatherapi.com/v1/current.json"
    query = {"q": location}
    headers = {"key": api_key}

    response = requests.get(url, headers=headers, params=query)
    weather_data = response.json()

    # Extract weather condition and temperature from the API response
    condition = weather_data['current']['condition']['text']
    temperature = weather_data['current']['temp_f']

    return condition, temperature

# Function to handle user input and generate the "vibe of the day"
def generate_vibe_of_the_day():
    mood = input("How are you feeling today? ")
    location = input("Enter your location: ")
    api_key = "aebd444319004748b15155809232706"

    # Retrieve weather data from the WeatherAPI.com API
    weather_condition, temperature = get_weather_data(api_key, location)

    # Generate a quote based on weather conditions, mood, and location
    quote = generate_quote(weather_condition.lower(), mood, location)

    # Display the "vibe of the day" information
    print(f"Weather: {weather_condition}")
    print(f"Temperature: {temperature}°F")
    print(f"Vibe of the day: {quote}")

    # Store the input data in the database
    data = {
        'mood': mood,
        'location': location,
        'weather_condition': weather_condition,
        'temperature': temperature,
        'quote': quote
    }
    with engine.connect() as connection:
        connection.execute(table.insert(), data)

# Run the application
generate_vibe_of_the_day()

# Query and print the stored data if available
with engine.connect() as connection:
    query = db.select(table)
    query_result = connection.execute(query)
    rows = query_result.fetchall()
    
    if rows:
        df = pd.DataFrame(rows, columns=table.columns.keys())
        print(df)
