def generate_google_maps_link(lat, lon):
    try:
        link = f"https://www.google.com/maps?q={lat},{lon}"
        return link
    except Exception as e:
        print(f"Error generating Google Maps link: {e}")
        return "N/A"
