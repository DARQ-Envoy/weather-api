import openmeteo_requests
import requests_cache
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from retry_requests import retry
from .serializers import WeatherRequestSerializer

class WeatherView(APIView):
    def get(self, request):
        # Validate request parameters
        serializer = WeatherRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m"
    }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}

        hourly_data["temperature_2m"] = hourly_temperature_2m

        hourly_dataframe = pd.DataFrame(data = hourly_data).to_dict(orient= "records")
        all_days = []
        daily_data = []
        for day in hourly_dataframe:
            if day["date"].day not in all_days:
                daily_data.append(day)
                all_days.append(day["date"].day)
            else:
                continue
        return Response(daily_data, status=status.HTTP_200_OK)


location = {"longitude":52.52, "latitude": 13.41}


# if __name__ == "__main__":
#     get_weather(location)
