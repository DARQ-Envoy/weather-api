from django.test import TestCase
# Create your tests here.
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status




class WeatherApiTest(APITestCase):
    
    def test_weather_api_valid_request(self):
        url = reverse('weather')
        params = {'latitude': 40.7128, 'longitude': -74.0060}
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertIn('temperature_2m', item)

        
    def test_weather_api_missing_parameters(self):
        url = reverse('weather')
        
        response = self.client.get(url)  # Missing parameters
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)