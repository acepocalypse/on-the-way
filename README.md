# 🚗 On The Way – AI-Powered Road Trip Planner

**On The Way** is an intelligent road trip planning tool that leverages Google Maps and Gemini AI to recommend ideal trip durations, generate tailored stop suggestions based on your interests, and optimize the driving route between your starting point and destination.

### 🌟 Features

- 🔮 **AI-Powered Trip Duration Estimates**  
  Get a recommended number of days for a relaxing road trip with leisure stops, powered by Gemini AI.

- 📍 **Custom Stop Recommendations**  
  Generate personalized stop suggestions based on your interests and desired number of stops.

- 🗺️ **Optimized Routing**  
  Visualize and analyze the most efficient route using Google Maps Directions API.

- ✅ **User-Selected Stops**  
  Interactively select preferred stops from AI suggestions before optimizing your route.

---

### 🏗️ Technologies Used

- [Streamlit](https://streamlit.io/) – for building the interactive web UI  
- [Google Maps API](https://developers.google.com/maps/documentation) – for place lookups and route optimization  
- [Google Gemini AI (Generative AI)](https://ai.google.dev/) – for intelligent content generation  
- [Python](https://www.python.org/) – core programming language  
- [Pandas](https://pandas.pydata.org/) – for structured data formatting

---

### 🚀 How to Run the App

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/ontheway-app.git
   cd ontheway-app
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**
   Create a `.streamlit/secrets.toml` file and add your API keys:
   ```toml
   [api_keys]
   google_api_key = "YOUR_GOOGLE_MAPS_API_KEY"
   genai_api_key = "YOUR_GEMINI_API_KEY"
   ```

4. **Run the App**
   ```bash
   streamlit run streamlit_app.py
   ```

---

### 🔧 App Structure

- `trip_length_recommendation(start, end)`  
  Uses Gemini AI to estimate an ideal trip length in days.

- `stops_recommendation(start, end, interests, wanted_stops, trip_days)`  
  Recommends relevant stops using AI based on user preferences.

- `route_optimization(start, end, stops)`  
  Uses Google Maps to compute the most efficient route including stops.

- `main()`  
  Orchestrates the Streamlit UI, user inputs, session management, and displays.

---

### 📝 Future Enhancements

- Add map visualization for optimized routes  
- Include lodging/dining recommendations  
- Save/share itineraries  
- Multiday trip breakdowns with pacing suggestions

---

### 🤝 Contributing

Contributions are welcome! Please open issues or submit pull requests with improvements, bug fixes, or new features.

---

### 📄 License

This project is licensed under the MIT License. See `LICENSE` for more details.
