import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas as pd
from geopy.geocoders import Nominatim
import math

import os
import json
import requests


def main():
	st.title("Singapore's Covid-19 Vaccination Centres and Vaccine Types Finder")
	menu = ["About This App", "Vaccination Centres"]

	st.sidebar.subheader('Select display page')

	select_menu = st.sidebar.selectbox("Menu", menu)

	if select_menu == "About This App":
		st.markdown("")
		st.markdown("")
		st.image('PM-Lee-covid-vaccine-cover-1.jpg')
		st.header("Background")
		'''
		On 14 December 2020, Prime Minister Lee Hsien Loong announced that Covid-19 vaccinations will be free for all Singaporeans and long-term residents (Koh, 2020).
		Thereafter, on 13 April 2021, The Straits Times reported that people living in Singapore are allowed to choose which Covid-19 vaccine to take by referring to the Ministry of Health's (MOH) website for the list of vaccination centres and vaccines (Lai, 2021).
		
		The website (Ministry of Health, 2021) allows users to see the lists of vaccination centres in terms of the 5 regions of Singapore as well as which vaccine type belongs to which vaccination centre. Furthermore, the website also has a hyperlink to allow users to access the map to find the vaccination centre near the users.
		
		However, the usability is just showing the users the tables of the vaccination centres and the users still have to click on a link showing a map of Singapore with markers of vaccination centres. While assessing the map, the user could have difficulty finding the search bar to input his/her home address. Furthermore, scrolling the webpage to see the lists might make the users feel time-consuming.
		
		Therefore, for this mini-project, I have built an app that allows users to key in their personal address and to pick their favourite vaccine type before selecting the region, based on where they live in or the place they prefer to go to followed by selecting the vaccination centre they would like to go to. Hence, after selecting these choices, a map of the vaccination centre will be shown. From the map, the users can click the path to show the distance between their personal residence and their chosen vaccination centre. This allows the users to check how near or far is from their residence to the chosen vaccination centre. Furthermore, the distance and the address of the selected vaccination centre will be shown.
		
		The data shown in this app is accurately based on the MOH's website. Don't worry, the home address data cannot be collected! In addition, please do remember to register your interest in vaccination at __[www.vaccine.gov.sg](www.vaccine.gov.sg)__!
		
		To start using this app, select "Vaccination Centres" in the dropdown menu on the left side of this app.
		'''
		st.header("Limitation")
		'''
		The distance between the user's residence and the chosen vaccination centre did not take into account the roads on the map but it is merely based on one point to one point, hence, the straight line.
		'''
		st.header("Future Work")
		'''
		If there's the availability of data that allows the users to know which date is the earliest slot that the users can book for the vaccination appointment for that chosen vaccination centre, this feature will be implemented in this app where the earliest date of appointment will be shown on the vaccination centre's marker on the map.
		'''
		st.markdown("")
		'''
		*Top image from the Ministry of Communications and Information*
		'''
		st.header("References")
		'''
		Koh, F. (2020). *7 things to know about phase 3: Dining out in larger groups, free Covid-19 vaccinations.* The Straits Times. December 14. Retrieved from [https://www.straitstimes.com/singapore/health/7-things-to-know-about-phase-3-dining-out-in-larger-groups-free-covid-19](https://www.straitstimes.com/singapore/health/7-things-to-know-about-phase-3-dining-out-in-larger-groups-free-covid-19)
		
		Lai, L. (2021). *S’pore residents can now choose which Covid-19 vaccine to take; Moderna jabs given at 11 centres.* The Straits Times. April 13. Retrieved from [https://www.straitstimes.com/singapore/people-can-now-choose-which-covid-19-jab-to-take-with-listing-of-vaccination-centres-and](https://www.straitstimes.com/singapore/people-can-now-choose-which-covid-19-jab-to-take-with-listing-of-vaccination-centres-and)
		
		Ministry of Health. (2021). *Vaccination Centres.* April. Retrieved from [https://www.vaccine.gov.sg/locations-vcs](https://www.vaccine.gov.sg/locations-vcs)
		'''
	elif select_menu == "Vaccination Centres":

		def convert_address(address):
			# using Nominatin from Geopy to convert address to latitude and longitude coordinates
			geolocator = Nominatim(user_agent="my_app")  # using open street map API
			Geo_Coordinate = geolocator.geocode(address)
			lat = Geo_Coordinate.latitude
			lon = Geo_Coordinate.longitude
			# Convert the lat long into a list and store is as points
			point = [lat, lon]
			return point

		def distance(origin, lat2, lon2):
			lat1 = float(origin[0])
			lon1 = float(origin[1])
			lat2 = float(lat2)
			lon2 = float(lon2)
			radius = 6371  # km

			dlat = math.radians(lat2 - lat1)
			dlon = math.radians(lon2 - lon1)
			a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
				* math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
			c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
			d = radius * c
			d = round(d,2)
			return d

		st.markdown("")
		st.header("Find a vaccination centre near you")

		df = pd.read_csv('Vaccination_Centres.csv')

		address_text = st.text_input('Type your Address (For example, 108 Punggol Field):', '')

		if address_text:

			try:

				vaccine_brand = st.selectbox("Choose your desired vaccine type",
											 df.loc[:, "Vaccine Type"].unique())  # ["Pfizer", "Moderna"])
				region = st.selectbox("Select a region in Singapore you live in or you plan to go to",
									  df.loc[:, "Region"].unique())  # ["Central", "North", "East", "North East", "West"])

				if vaccine_brand == "Pfizer" and region == "Central":
					central_pfizer_df = df[(df["Vaccine Type"] == "Pfizer") & (df["Region"] == "Central")]
					vc = st.radio("Choose the vaccination centre", central_pfizer_df.loc[:, "Name"].unique())

					if vc == "Raffles City Convention Centre":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str("Raffles City") + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][4] # Raffles City Shopping Centre from OneMapAPI in this 4th index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup="RAFFLES CITY CONVENTION CENTRE").add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address", icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Tanjong Pagar Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # Tanjong Pagar CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Jalan Besar Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # Jalan Besar CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Bishan Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][4] # Bishan CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Queenstown Community Centre":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][3] # Queenstown CC from OneMapAPI in this 3rd index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Toa Payoh West Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # TPY West CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Bukit Timah Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # Bukit Timah CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					else:
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						location_names = []
						location_coordinates = []
						length = data['found']

						maximum = 1
						if length == 1:
							maximum = length
						if length > 0:
							for i in range(maximum):
								results = data['results'][i]
								location_coordinates.append([results['LATITUDE'], results['LONGITUDE']])
								location_names.append(results['SEARCHVAL'])

							st.markdown('The address of the selected vaccination centre is ' + "**" + results[
								'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
								distance(convert_address(address_text), results['LATITUDE'],
										 results['LONGITUDE'])) + "km**.")

							m = folium.Map(location=location_coordinates[0], zoom_start=12)
							# add markers
							for point in range(0, maximum):
								folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
								folium.Marker(convert_address(address_text), popup="Your Address",
											  icon=folium.Icon(icon="home")).add_to(m)
								folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
							# call to render Folium map in Streamlit
							folium_static(m)

				elif vaccine_brand == "Pfizer" and region == "North":
					north_pfizer_df = df[(df["Vaccine Type"] == "Pfizer") & (df["Region"] == "North")]
					vc = st.radio("Choose the vaccination centre", north_pfizer_df.loc[:, "Name"].unique())

					if vc == "Canberra Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][2] # Canberra CC from OneMapAPI in this 2nd index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Nee Soon East Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # Nee Soon East CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					else:

						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						location_names = []
						location_coordinates = []
						length = data['found']

						maximum = 1
						if length == 1:
							maximum = length
						if length > 0:
							for i in range(maximum):
								results = data['results'][i]
								location_coordinates.append([results['LATITUDE'], results['LONGITUDE']])
								location_names.append(results['SEARCHVAL'])

							st.markdown('The address of the selected vaccination centre is ' + "**" + results[
								'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
								distance(convert_address(address_text), results['LATITUDE'],
										 results['LONGITUDE'])) + "km**.")

							m = folium.Map(location=location_coordinates[0], zoom_start=12)
							# add markers
							for point in range(0, maximum):
								folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
								folium.Marker(convert_address(address_text), popup="Your Address",
											  icon=folium.Icon(icon="home")).add_to(m)
								folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
							# call to render Folium map in Streamlit
							folium_static(m)

				elif vaccine_brand == "Pfizer" and region == "East":
					east_pfizer_df = df[(df["Vaccine Type"] == "Pfizer") & (df["Region"] == "East")]
					vc = st.radio("Choose the vaccination centre", east_pfizer_df.loc[:, "Name"].unique())

					if vc == "Changi Airport Terminal 4":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][6] # T4 from OneMapAPI in this 6th index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Bedok Community Centre":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # Bedok CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Arena@ Our Tampines Hub (Hockey Court)":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str("Our Tampines Hub") + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # Our Tampines Hub from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup="ARENA@ OUR TAMPINES HUB").add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					else:
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						location_names = []
						location_coordinates = []
						length = data['found']

						maximum = 1
						if length == 1:
							maximum = length
						if length > 0:
							for i in range(maximum):
								results = data['results'][i]
								location_coordinates.append([results['LATITUDE'], results['LONGITUDE']])
								location_names.append(results['SEARCHVAL'])

							st.markdown('The address of the selected vaccination centre is ' + "**" + results[
								'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
								distance(convert_address(address_text), results['LATITUDE'],
										 results['LONGITUDE'])) + "km**.")

							m = folium.Map(location=location_coordinates[0], zoom_start=12)
							# add markers
							for point in range(0, maximum):
								folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
								folium.Marker(convert_address(address_text), popup="Your Address",
											  icon=folium.Icon(icon="home")).add_to(m)
								folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
							# call to render Folium map in Streamlit
							folium_static(m)

				elif vaccine_brand == "Pfizer" and region == "North East":
					northeast_pfizer_df = df[(df["Vaccine Type"] == "Pfizer") & (df["Region"] == "North East")]
					vc = st.radio("Choose the vaccination centre", northeast_pfizer_df.loc[:, "Name"].unique())

					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					location_names = []
					location_coordinates = []
					length = data['found']

					maximum = 1
					if length == 1:
						maximum = length
					if length > 0:
						for i in range(maximum):
							results = data['results'][i]
							location_coordinates.append([results['LATITUDE'], results['LONGITUDE']])
							location_names.append(results['SEARCHVAL'])

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=location_coordinates[0], zoom_start=12)
						# add markers
						for point in range(0, maximum):
							folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
							folium.Marker(convert_address(address_text), popup="Your Address",
										  icon=folium.Icon(icon="home")).add_to(m)
							folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

				elif vaccine_brand == "Pfizer" and region == "West":
					west_pfizer_df = df[(df["Vaccine Type"] == "Pfizer") & (df["Region"] == "West")]
					vc = st.radio("Choose the vaccination centre", west_pfizer_df.loc[:, "Name"].unique())

					if vc == "Former Hong Kah Secondary School":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str('Hong Kah Secondary School') + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][0] # one and only

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup='FORMER HONG KAH SECONDARY SCHOOL').add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Nanyang Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # Nanyang CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Clementi Community Centre":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # Clementi CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Chua Chu Kang Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][2] # CCK CC from OneMapAPI in this 2nd index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					else:
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						location_names = []
						location_coordinates = []
						length = data['found']

						maximum = 1
						if length == 1:
							maximum = length
						if length > 0:
							for i in range(maximum):
								results = data['results'][i]
								location_coordinates.append([results['LATITUDE'], results['LONGITUDE']])
								location_names.append(results['SEARCHVAL'])

							st.markdown('The address of the selected vaccination centre is ' + "**" + results[
								'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
								distance(convert_address(address_text), results['LATITUDE'],
										 results['LONGITUDE'])) + "km**.")

							m = folium.Map(location=location_coordinates[0], zoom_start=12)
							# add markers
							for point in range(0, maximum):
								folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
								folium.Marker(convert_address(address_text), popup="Your Address",
											  icon=folium.Icon(icon="home")).add_to(m)
								folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
							# call to render Folium map in Streamlit
							folium_static(m)

				elif vaccine_brand == "Moderna" and region == "Central":
					central_moderna_df = df[(df["Vaccine Type"] == "Moderna") & (df["Region"] == "Central")]
					vc = st.radio("Choose the vaccination centre", central_moderna_df.loc[:, "Name"].unique())

					if vc == "Kolam Ayer Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # Kolam Ayer CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					else:
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(
							vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						location_names = []
						location_coordinates = []
						length = data['found']

						maximum = 1
						if length == 1:
							maximum = length
						if length > 0:
							for i in range(maximum):
								results = data['results'][i]
								location_coordinates.append([results['LATITUDE'], results['LONGITUDE']])
								location_names.append(results['SEARCHVAL'])

							st.markdown('The address of the selected vaccination centre is ' + "**" + results[
								'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
								distance(convert_address(address_text), results['LATITUDE'],
										 results['LONGITUDE'])) + "km**.")

							m = folium.Map(location=location_coordinates[0], zoom_start=12)
							# add markers
							for point in range(0, maximum):
								folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
								folium.Marker(convert_address(address_text), popup="Your Address",
											  icon=folium.Icon(icon="home")).add_to(m)
								folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
							# call to render Folium map in Streamlit
							folium_static(m)

				elif vaccine_brand == "Moderna" and region == "North":
					north_moderna_df = df[(df["Vaccine Type"] == "Moderna") & (df["Region"] == "North")]
					vc = st.radio("Choose the vaccination centre", north_moderna_df.loc[:, "Name"].unique())

					if vc == "Marsiling Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][4] # Marsiling CC from OneMapAPI in this 4th index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					elif vc == "Woodlands Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][1] # Woodlands CC from OneMapAPI in this 1st index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					else:

						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(
							vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						location_names = []
						location_coordinates = []
						length = data['found']

						maximum = 1
						if length == 1:
							maximum = length
						if length > 0:
							for i in range(maximum):
								results = data['results'][i]
								location_coordinates.append([results['LATITUDE'], results['LONGITUDE']])
								location_names.append(results['SEARCHVAL'])

							st.markdown('The address of the selected vaccination centre is ' + "**" + results[
								'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
								distance(convert_address(address_text), results['LATITUDE'],
										 results['LONGITUDE'])) + "km**.")

							m = folium.Map(location=location_coordinates[0], zoom_start=12)
							# add markers
							for point in range(0, maximum):
								folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
								folium.Marker(convert_address(address_text), popup="Your Address",
											  icon=folium.Icon(icon="home")).add_to(m)
								folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
							# call to render Folium map in Streamlit
							folium_static(m)

				elif vaccine_brand == "Moderna" and region == "East":
					east_moderna_df = df[(df["Vaccine Type"] == "Moderna") & (df["Region"] == "East")]
					vc = st.radio("Choose the vaccination centre", east_moderna_df.loc[:, "Name"].unique())

					if vc == "Tampines East Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][2] # Tampines East Community Club from OneMapAPI in this 2nd index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					else:
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						location_names = []
						location_coordinates = []
						length = data['found']

						maximum = 1
						if length == 1:
							maximum = length
						if length > 0:
							for i in range(maximum):
								results = data['results'][i]
								location_coordinates.append([results['LATITUDE'], results['LONGITUDE']])
								location_names.append(results['SEARCHVAL'])

							st.markdown('The address of the selected vaccination centre is ' + "**" + results[
								'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
								distance(convert_address(address_text), results['LATITUDE'],
										 results['LONGITUDE'])) + "km**.")

							m = folium.Map(location=location_coordinates[0], zoom_start=12)
							# add markers
							for point in range(0, maximum):
								folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
								folium.Marker(convert_address(address_text), popup="Your Address",
											  icon=folium.Icon(icon="home")).add_to(m)
								folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
							# call to render Folium map in Streamlit
							folium_static(m)

				elif vaccine_brand == "Moderna" and region == "North East":
					northeast_moderna_df = df[(df["Vaccine Type"] == "Moderna") & (df["Region"] == "North East")]
					vc = st.radio("Choose the vaccination centre", northeast_moderna_df.loc[:, "Name"].unique())

					if vc == "Kebun Baru Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][3] # Kebun Baru Community CLub from OneMapAPI in this 3rd index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					else:
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						location_names = []
						location_coordinates = []
						length = data['found']

						maximum = 1
						if length == 1:
							maximum = length
						if length > 0:
							for i in range(maximum):
								results = data['results'][i]
								location_coordinates.append([results['LATITUDE'], results['LONGITUDE']])
								location_names.append(results['SEARCHVAL'])

							st.markdown('The address of the selected vaccination centre is ' + "**" + results[
								'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
								distance(convert_address(address_text), results['LATITUDE'],
										 results['LONGITUDE'])) + "km**.")

							m = folium.Map(location=location_coordinates[0], zoom_start=12)
							# add markers
							for point in range(0, maximum):
								folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
								folium.Marker(convert_address(address_text), popup="Your Address",
											  icon=folium.Icon(icon="home")).add_to(m)
								folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
							# call to render Folium map in Streamlit
							folium_static(m)

				elif vaccine_brand == "Moderna" and region == "West":
					west_moderna_df = df[(df["Vaccine Type"] == "Moderna") & (df["Region"] == "West")]
					vc = st.radio("Choose the vaccination centre", west_moderna_df.loc[:, "Name"].unique())

					if vc == "Hong Kah North Community Club":
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						results = data['results'][4] # Hong Kah North Community CLub from OneMapAPI in this 4th index

						st.markdown('The address of the selected vaccination centre is ' + "**" + results[
							'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
							distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km**.")

						m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
						# add markers
						folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)

					else:
						query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(
							vc) + '&returnGeom=Y&getAddrDetails=Y'
						resp = requests.get(query_string)
						data = json.loads(resp.content)

						location_names = []
						location_coordinates = []
						length = data['found']

						maximum = 1
						if length == 1:
							maximum = length
						if length > 0:
							for i in range(maximum):
								results = data['results'][i]
								location_coordinates.append([results['LATITUDE'], results['LONGITUDE']])
								location_names.append(results['SEARCHVAL'])

							st.markdown('The address of the selected vaccination centre is ' + "**" + results[
								'ADDRESS'] + "**" + ' and the straight line distance from your house to your selected vaccination centre is ' + "**" + str(
								distance(convert_address(address_text), results['LATITUDE'],
										 results['LONGITUDE'])) + "km**.")

							m = folium.Map(location=location_coordinates[0], zoom_start=12)
							# add markers
							for point in range(0, maximum):
								folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
								folium.Marker(convert_address(address_text), popup="Your Address",
											  icon=folium.Icon(icon="home")).add_to(m)
								folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]], popup=str(distance(convert_address(address_text), results['LATITUDE'], results['LONGITUDE'])) + "km").add_to(m)
							# call to render Folium map in Streamlit
							folium_static(m)
			except:
				st.header("Please type a valid address")

	st.sidebar.markdown("")
	st.sidebar.markdown("")
	st.sidebar.markdown("")
	st.sidebar.markdown("")
	st.sidebar.markdown("")
	st.sidebar.markdown("")
	st.sidebar.markdown("")
	st.sidebar.markdown("")
	st.sidebar.markdown("")
	st.sidebar.subheader("Jim Meng Kok")
	st.sidebar.markdown('Please feel free to connect with me on LinkedIn: [www.linkedin.com/in/jimmengkok](www.linkedin.com/in/jimmengkok)')
	st.sidebar.markdown('Medium: [https://medium.com/@jimintheworld](https://medium.com/@jimintheworld)')


if __name__ == '__main__':
	main()