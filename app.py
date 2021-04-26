import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas as pd
from geopy.geocoders import Nominatim

import os
import json
import requests


def main():
	st.title("Singapore's Covid-19 Vaccination Centres Finder and Vaccine Types")
	menu = ["About This App", "Vaccination Centres"]

	st.sidebar.subheader('Select display page')

	select_menu = st.sidebar.selectbox("Menu", menu)

	if select_menu == "About This App":
		st.image('PM-Lee-covid-vaccine-cover-1.jpg')
		st.header("Background")
		'''
		On 14 December 2020, Prime Minister Lee Hsien Loong announced that Covid-19 vaccinations will be free for all Singaporeans and long-term residents (Koh, 2020).
		Thereafter, on 13 April 2021, The Straits Times reported that people living in Singapore are allowed to choose which Covid-19 vaccine to take by referring to the Ministry of Health's (MOH) website for the list of vaccination centres and vaccines (Lai, 2021).
		
		The website (Ministry of Health, 2021) allows users to see the lists of vaccination centres in terms of the 5 regions of Singapore as well as which vaccine type belongs to which vaccination centre. Furthermore, the website also has a hyperlink to allow users to access the map to find the vaccination centre near the users.
		
		However, the usability is just showing the users the tables of the vaccination centres and the users still have to click on a link showing a map of Singapore with markers of vaccination centres. What if the users not sure which part of Singapore do they live in by looking at the map? Furthermore, scrolling the webpage to see the lists might make the users feel time-consuming.
		
		Therefore, for this mini-project, I have built an app that allows users to key in their personal address and to pick their favourite vaccine type before selecting the region, based on where they live in or the place they prefer to go to followed by selecting the vaccination centre they would like to go to. Hence, after selecting these choices, a map of the vaccination centre, as well as the path from their own residence, will be shown. The path allows the users to check whether their personal residence is near or far from their chosen vaccination centre. Furthermore, the address of the selected vaccination centre will be shown.
		
		The data shown in this app is accurately based on the MOH's website. Don't worry, the home address data cannot be collected! In addition, please do remember to register your interest in vaccination at __[www.vaccine.gov.sg](www.vaccine.gov.sg)__!
		
		To start using this app, select "Vaccination Centres" in the dropdown menu on the left side of this app.
		
		
		*Top image from the Ministry of Communications and Information*
		'''
		st.header("References")
		'''
		Koh, F. (2020). *7 things to know about phase 3: Dining out in larger groups, free Covid-19 vaccinations.* The Straits Times. December 14. Retrieved from https://www.straitstimes.com/singapore/health/7-things-to-know-about-phase-3-dining-out-in-larger-groups-free-covid-19
		
		Lai, L. (2021). *S’pore residents can now choose which Covid-19 vaccine to take; Moderna jabs given at 11 centres.* The Straits Times. April 13. Retrieved from https://www.straitstimes.com/singapore/people-can-now-choose-which-covid-19-jab-to-take-with-listing-of-vaccination-centres-and
		
		Ministry of Health. (2021). *Vaccination Centres.* April. Retrieved from https://www.vaccine.gov.sg/locations-vcs
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

		st.header("Find the nearest vaccination centre near you")

		df = pd.read_csv('Vaccination_Centres.csv')

		address_text = st.text_input('Type your Address', '')

		if address_text:

			vaccine_brand = st.selectbox("Choose your desired vaccine type",
										 df.loc[:, "Vaccine Type"].unique())  # ["Pfizer", "Moderna"])
			region = st.selectbox("Select a region in Singapore you live in or you plan to go to",
								  df.loc[:, "Region"].unique())  # ["Central", "North", "East", "North East", "West"])

			if vaccine_brand == "Pfizer" and region == "Central":
				central_pfizer_df = df[(df["Vaccine Type"] == "Pfizer") & (df["Region"] == "Central")]
				vc = st.selectbox("Choose the vaccination centre", central_pfizer_df.loc[:, "Name"].unique())

				if vc == "Raffles City Convention Centre":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str("Raffles City") + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][4] # Raffles City Shopping Centre from OneMapAPI in this 4th index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup="RAFFLES CITY CONVENTION CENTRE").add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address", icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine([convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Tanjong Pagar Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # Tanjong Pagar CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Jalan Besar Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # Jalan Besar CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Bishan Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][4] # Bishan CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Queenstown Community Centre":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][3] # Queenstown CC from OneMapAPI in this 3rd index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Toa Payoh West Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # TPY West CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Bukit Timah Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # Bukit Timah CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

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

						m = folium.Map(location=location_coordinates[0], zoom_start=12)
						# add markers
						for point in range(0, maximum):
							folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
							folium.Marker(convert_address(address_text), popup="Your Address",
										  icon=folium.Icon(icon="home")).add_to(m)
							folium.PolyLine(
								[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)
						st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

			elif vaccine_brand == "Pfizer" and region == "North":
				north_pfizer_df = df[(df["Vaccine Type"] == "Pfizer") & (df["Region"] == "North")]
				vc = st.selectbox("Choose the vaccination centre", north_pfizer_df.loc[:, "Name"].unique())

				if vc == "Canberra Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][2] # Canberra CC from OneMapAPI in this 2nd index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Nee Soon East Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # Nee Soon East CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

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

						m = folium.Map(location=location_coordinates[0], zoom_start=12)
						# add markers
						for point in range(0, maximum):
							folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
							folium.Marker(convert_address(address_text), popup="Your Address",
										  icon=folium.Icon(icon="home")).add_to(m)
							folium.PolyLine(
								[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)
						st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

			elif vaccine_brand == "Pfizer" and region == "East":
				east_pfizer_df = df[(df["Vaccine Type"] == "Pfizer") & (df["Region"] == "East")]
				vc = st.selectbox("Choose the vaccination centre", east_pfizer_df.loc[:, "Name"].unique())

				if vc == "Changi Airport Terminal 4":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][6] # T4 from OneMapAPI in this 6th index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Bedok Community Centre":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # Bedok CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Arena@ Our Tampines Hub (Hockey Court)":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str("Our Tampines Hub") + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # Our Tampines Hub from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup="ARENA@ OUR TAMPINES HUB").add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

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

						m = folium.Map(location=location_coordinates[0], zoom_start=12)
						# add markers
						for point in range(0, maximum):
							folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
							folium.Marker(convert_address(address_text), popup="Your Address",
										  icon=folium.Icon(icon="home")).add_to(m)
							folium.PolyLine(
								[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)
						st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

			elif vaccine_brand == "Pfizer" and region == "North East":
				northeast_pfizer_df = df[(df["Vaccine Type"] == "Pfizer") & (df["Region"] == "North East")]
				vc = st.selectbox("Choose the vaccination centre", northeast_pfizer_df.loc[:, "Name"].unique())

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

					m = folium.Map(location=location_coordinates[0], zoom_start=12)
					# add markers
					for point in range(0, maximum):
						folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
						folium.Marker(convert_address(address_text), popup="Your Address",
									  icon=folium.Icon(icon="home")).add_to(m)
						folium.PolyLine(
							[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

			elif vaccine_brand == "Pfizer" and region == "West":
				west_pfizer_df = df[(df["Vaccine Type"] == "Pfizer") & (df["Region"] == "West")]
				vc = st.selectbox("Choose the vaccination centre", west_pfizer_df.loc[:, "Name"].unique())

				if vc == "Former Hong Kah Secondary School":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str('Hong Kah Secondary School') + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][0] # one and only

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup='FORMER HONG KAH SECONDARY SCHOOL').add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Nanyang Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # Nanyang CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Clementi Community Centre":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # Clementi CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Chua Chu Kang Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][2] # CCK CC from OneMapAPI in this 2nd index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

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

						m = folium.Map(location=location_coordinates[0], zoom_start=12)
						# add markers
						for point in range(0, maximum):
							folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
							folium.Marker(convert_address(address_text), popup="Your Address",
										  icon=folium.Icon(icon="home")).add_to(m)
							folium.PolyLine(
								[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)
						st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

			elif vaccine_brand == "Moderna" and region == "Central":
				central_moderna_df = df[(df["Vaccine Type"] == "Moderna") & (df["Region"] == "Central")]
				vc = st.selectbox("Choose the vaccination centre", central_moderna_df.loc[:, "Name"].unique())

				if vc == "Kolam Ayer Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # Kolam Ayer CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

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

						m = folium.Map(location=location_coordinates[0], zoom_start=12)
						# add markers
						for point in range(0, maximum):
							folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
							folium.Marker(convert_address(address_text), popup="Your Address",
										  icon=folium.Icon(icon="home")).add_to(m)
							folium.PolyLine(
								[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)
						st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

			elif vaccine_brand == "Moderna" and region == "North":
				north_moderna_df = df[(df["Vaccine Type"] == "Moderna") & (df["Region"] == "North")]
				vc = st.selectbox("Choose the vaccination centre", north_moderna_df.loc[:, "Name"].unique())

				if vc == "Marsiling Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][4] # Marsiling CC from OneMapAPI in this 4th index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

				elif vc == "Woodlands Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][1] # Woodlands CC from OneMapAPI in this 1st index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

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

						m = folium.Map(location=location_coordinates[0], zoom_start=12)
						# add markers
						for point in range(0, maximum):
							folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
							folium.Marker(convert_address(address_text), popup="Your Address",
										  icon=folium.Icon(icon="home")).add_to(m)
							folium.PolyLine(
								[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)
						st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

			elif vaccine_brand == "Moderna" and region == "East":
				east_moderna_df = df[(df["Vaccine Type"] == "Moderna") & (df["Region"] == "East")]
				vc = st.selectbox("Choose the vaccination centre", east_moderna_df.loc[:, "Name"].unique())

				if vc == "Tampines East Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][2] # Tampines East Community Club from OneMapAPI in this 2nd index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

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

						m = folium.Map(location=location_coordinates[0], zoom_start=12)
						# add markers
						for point in range(0, maximum):
							folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
							folium.Marker(convert_address(address_text), popup="Your Address",
										  icon=folium.Icon(icon="home")).add_to(m)
							folium.PolyLine(
								[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)
						st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

			elif vaccine_brand == "Moderna" and region == "North East":
				northeast_moderna_df = df[(df["Vaccine Type"] == "Moderna") & (df["Region"] == "North East")]
				vc = st.selectbox("Choose the vaccination centre", northeast_moderna_df.loc[:, "Name"].unique())

				if vc == "Kebun Baru Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][3] # Kebun Baru Community CLub from OneMapAPI in this 3rd index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

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

						m = folium.Map(location=location_coordinates[0], zoom_start=12)
						# add markers
						for point in range(0, maximum):
							folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
							folium.Marker(convert_address(address_text), popup="Your Address",
										  icon=folium.Icon(icon="home")).add_to(m)
							folium.PolyLine(
								[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)
						st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

			elif vaccine_brand == "Moderna" and region == "West":
				west_moderna_df = df[(df["Vaccine Type"] == "Moderna") & (df["Region"] == "West")]
				vc = st.selectbox("Choose the vaccination centre", west_moderna_df.loc[:, "Name"].unique())

				if vc == "Hong Kah North Community Club":
					query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(vc) + '&returnGeom=Y&getAddrDetails=Y'
					resp = requests.get(query_string)
					data = json.loads(resp.content)

					results = data['results'][4] # Hong Kah North Community CLub from OneMapAPI in this 4th index

					m = folium.Map(location=[results['LATITUDE'], results['LONGITUDE']], zoom_start=12)
					# add markers
					folium.Marker([results['LATITUDE'], results['LONGITUDE']], popup=results['SEARCHVAL']).add_to(m)
					folium.Marker(convert_address(address_text), popup="Your Address",
								  icon=folium.Icon(icon="home")).add_to(m)
					folium.PolyLine(
						[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
					# call to render Folium map in Streamlit
					folium_static(m)
					st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")

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

						m = folium.Map(location=location_coordinates[0], zoom_start=12)
						# add markers
						for point in range(0, maximum):
							folium.Marker(location_coordinates[point], popup=location_names[point]).add_to(m)
							folium.Marker(convert_address(address_text), popup="Your Address",
										  icon=folium.Icon(icon="home")).add_to(m)
							folium.PolyLine(
								[convert_address(address_text), [results['LATITUDE'], results['LONGITUDE']]]).add_to(m)
						# call to render Folium map in Streamlit
						folium_static(m)
						st.markdown('The address of the selected vaccination centre is ' + "**" + results['ADDRESS'] + "**")


if __name__ == '__main__':
	main()