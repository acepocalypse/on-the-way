import streamlit as st
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import os
import pandas as pd
import googlemaps
from googlemaps.exceptions import ApiError

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
genai_api_key = os.getenv("GENAI_API_KEY")

# Validate API keys
if not google_api_key or not genai_api_key:
    st.error("Missing API keys in environment variables")
    st.stop()

# Set up clients
gmaps = googlemaps.Client(key=google_api_key)
genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def trip_length_recommendation(start, end):
    prompt = (
        f"Only answer with a range of numbers (e.g. 1-2, 4-6). "
        f"What is the ideal number of days for a relaxing road trip from {start} to {end}, "
        f"including leisure stops along the way for sightseeing and unwinding?"
    )
    try:
        ai_response = model.generate_content(prompt)
        range_str = ai_response.text.strip()
        if '-' not in range_str:
            raise ValueError("Invalid response format")
        start_num, end_num = map(int, range_str.split('-'))
        return list(range(start_num, end_num + 1))
    except Exception as e:
        st.error(f"Error generating trip length recommendation: {str(e)}")
        return []

def validate_stops(stops, end_location):
    """Filter out empty stops and exclude end location"""
    return [stop.strip() for stop in stops 
            if stop.strip() and stop.strip().lower() != end_location.lower()]

def stops_recommendation(start, end, interests, wanted_stops, trip_days):
    prompt = (
        f"Help me pick destinations for my {trip_days}-day road trip from {start} to {end}. "
        f"I'm interested in {', '.join(interests)} and want {wanted_stops} stops. "
        "List stops concisely, separated by semicolons. Exclude the end point. "
        "Merge stops within 30 miles of each other. Only output the name of the place without additional descriptions. Note that when listing national parks you need to include 'National Park' in the name and the state abbreviation."
    )
    try:
        ai_response = model.generate_content(prompt)
        stops = ai_response.text.split(";")
        return validate_stops(stops, end)
    except Exception as e:
        st.error(f"Error generating stops recommendation: {str(e)}")
        return []

def get_route_polyline(optimized_route):
    return [{"lat": step['end_location']['lat'], "lng": step['end_location']['lng']} 
            for leg in optimized_route['legs'] for step in leg['steps']]

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def get_place_id(location):
    """Convert location string to Google Place ID"""
    try:
        places_result = gmaps.find_place(
            location,
            'textquery',
            fields=['place_id']
        )
        if places_result['candidates']:
            return places_result['candidates'][0]['place_id']
        return None
    except Exception as e:
        st.error(f"Error getting place ID for {location}: {str(e)}")
        return None

def route_optimization(start, end, stops):
    try:
        if not stops:
            st.warning("No stops to optimize")
            return None

        # Convert locations to Place IDs
        start_id = get_place_id(start)
        end_id = get_place_id(end)
        stop_ids = [get_place_id(stop) for stop in stops]

        # Validate Place IDs
        if not all([start_id, end_id] + stop_ids):
            st.error("Could not convert all locations to Place IDs")
            return None

        # Get optimized directions using Place IDs
        directions_result = gmaps.directions(
            origin=f'place_id:{start_id}',
            destination=f'place_id:{end_id}',
            waypoints=[f'place_id:{stop_id}' for stop_id in stop_ids],
            optimize_waypoints=True,
            mode="driving"
        )

        if not directions_result:
            st.error("No directions found")
            return None

        optimized_route = directions_result[0]
        waypoint_order = optimized_route.get('waypoint_order', [])
        ordered_stops = [stops[i] for i in waypoint_order]

        # Route data
        route_data = []
        total_distance_miles = 0
        total_duration_seconds = 0

        for i, leg in enumerate(optimized_route['legs']):
            dist_miles = leg['distance']['value'] * 0.000621371
            dur_seconds = leg['duration']['value']
            total_distance_miles += dist_miles
            total_duration_seconds += dur_seconds

            route_data.append({
                'Segment': i + 1,
                'Start': leg['start_address'],
                'End': leg['end_address'],
                'Distance (miles)': f"{round(dist_miles, 0):.2f}",
                'Duration': format_time(dur_seconds)
            })

        return {
            "optimized_order": ordered_stops,
            "route_data": route_data,
            "total_distance": total_distance_miles,
            "total_duration": format_time(total_duration_seconds),
            "visualization_data": get_route_polyline(optimized_route)
        }

    except googlemaps.exceptions.ApiError as e:
        st.error(f"Google Maps API Error: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
    return None

def main():
    st.title("On The Way")

    # Input section
    start_location = st.text_input("Enter start location:", key="start")
    end_location = st.text_input("Enter end location:", key="end")

    # Reset session state if locations change
    if 'start' in st.session_state or 'end' in st.session_state:
        if (st.session_state.get('prev_start') != start_location or
            st.session_state.get('prev_end') != end_location):
            st.session_state.clear()
            st.session_state.update({
                'prev_start': start_location,
                'prev_end': end_location
            })

    # Trip duration recommendation
    if st.button("Get Recommended Days"):
        if start_location and end_location:
            with st.spinner("Calculating ideal trip duration..."):
                recommended_days = trip_length_recommendation(start_location, end_location)
                if recommended_days:
                    st.session_state["recommended_days"] = recommended_days
        else:
            st.warning("Both start and end locations are required")

    # Days selection
    if "recommended_days" in st.session_state:
        days_options = st.session_state["recommended_days"]
        chosen_days = st.selectbox(
            "Choose trip duration:",
            options=days_options,
            index=len(days_options)-1 if days_options else 0
        )
        
        # Stops recommendation inputs
        interests = st.text_input("Enter interests (comma-separated):", 
                                placeholder="nature, history, food")
        wanted_stops = st.number_input(
            "Number of desired stops:",
            min_value=1,
            max_value=20,
            value=5,
            step=1
        )

        if st.button("Generate Stops"):
            if interests:
                interest_list = [i.strip() for i in interests.split(",") if i.strip()]
                with st.spinner("Planning your perfect stops..."):
                    stops = stops_recommendation(
                        start_location, 
                        end_location,
                        interest_list,
                        wanted_stops,
                        chosen_days
                    )
                    if stops:
                        st.session_state["stops"] = stops
                        st.success("Suggested stops:")
                        for i, s in enumerate(stops, 1):
                            st.write(f"{i}. {s}")
                    else:
                        st.warning("Could not generate stops recommendations")
            else:
                st.warning("Please enter your interests")

    # Route optimization
    if "stops" in st.session_state and st.button("Optimize Route"):
        with st.spinner("Optimizing your route..."):
            directions_result = route_optimization(
                start_location,
                end_location,
                st.session_state["stops"]
            )
            if directions_result:
                st.subheader("Optimized Route")
                st.write(", ".join(directions_result["optimized_order"]))

                st.subheader("Route Summary")
                st.write(f"**Total Distance:** {directions_result['total_distance']:.2f} miles")
                st.write(f"**Total Duration:** {directions_result['total_duration']}")

                st.subheader("Route Details")
                st.table(directions_result["route_data"])

                # st.subheader("Route Visualization Data")
                # st.json(directions_result["visualization_data"])
            else:
                st.error("Failed to optimize route")

if __name__ == "__main__":
    main()