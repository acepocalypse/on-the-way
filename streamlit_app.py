import streamlit as st
import requests
import googlemaps
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
google_api_key="AIzaSyA63OBpKtps7DCapnYEdQ7kaIQhNeVNBeM"
genai_api_key="AIzaSyBzhJig2EgnHA_yrOX0pW_pdkKlFdqjGfY"

# Set up Google Maps client
gmaps = googlemaps.Client(key=google_api_key)

# Set up Generative AI model
genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")


def stops_recommendation(start, end, interests, wanted_stops, trip_days):
    prompt = f"Help me pick destinations that I should spend time at during my {trip_days} long road trip from {start} to {end}. I am interested in {', '.join(interests)}. I want to make {wanted_stops} stops along the way. Please provide a list of recommended stops that align with these interests, ensuring they are spaced out appropriately for the trip duration. Join any stops that are within 30 miles of each other and do not include the end point. List the stops in a table with the name and state in one column, and the description in the other column"

    ai_response = model.generate_content(prompt)
    stops = [stop.strip() for stop in ai_response.text.split(";") if stop.strip()]
    return stops


def route_optimization(start, end, stops):
    try:
        directions_result = gmaps.directions(
            start,
            end,
            waypoints=stops,
            mode="driving",
            optimize_waypoints=True,
        )

        if directions_result and len(directions_result) > 0:
            optimized_route = directions_result[0]
            optimized_waypoints = optimized_route.get("waypoint_order")
            optimized_stops = [stops[i] for i in optimized_waypoints]

            total_distance = sum(
                leg["distance"]["value"] for leg in optimized_route["legs"]
            )
            total_duration = sum(
                leg["duration"]["value"] for leg in optimized_route["legs"]
            )

            return optimized_stops, total_distance, total_duration
        else:
            return None, None, None

    except googlemaps.exceptions.ApiError as e:
        st.error(f"Error: {e}")
        return None, None, None


# Streamlit App
st.title("Road Trip Planner")

# Inputs
start_location = st.text_input("Start Location (City, State)")
end_location = st.text_input("End Location (City, State)")
interests = st.text_area(
    "What are your interests?", "e.g., nature, history, food"
).split(",")
wanted_stops = st.slider("How many stops would you like?", 1, 10, 5)
trip_days = st.slider("Duration of the trip (in days):", 1, 30, 7)

# Generate Recommendations
if st.button("Get Stops Recommendation"):
    if start_location and end_location:
        recommended_stops = stops_recommendation(
            start_location, end_location, interests, wanted_stops, trip_days
        )
        if recommended_stops:
            st.subheader("Recommended Stops")
            st.write(recommended_stops)

            # Route Optimization
            if st.button("Optimize Route"):
                optimized_stops, total_distance, total_duration = route_optimization(
                    start_location, end_location, recommended_stops
                )
                if optimized_stops:
                    st.subheader("Optimized Route")
                    st.write(optimized_stops)
                    st.write(f"Total Distance: {total_distance/1000:.2f} km")
                    st.write(f"Total Duration: {total_duration/60:.2f} minutes")
                else:
                    st.error("Could not optimize route.")
    else:
        st.error("Please provide both start and end locations.")