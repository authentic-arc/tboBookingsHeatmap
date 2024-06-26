#make 70+
#print country with max-min bookings, city with max-min bookings

import streamlit as st
import math
import pandas as pd
from streamlit_folium import st_folium
import folium
from branca.colormap import ColorMap, LinearColormap
from branca.element import MacroElement
from branca.element import Figure, JavascriptLink
from branca.utilities import legend_scaler
import branca.colormap as cm

# this wasnt at top
st.set_page_config(page_title='Day-wise  bookings')

colormap = cm.LinearColormap(colors=['red','yellow','green'], 
                             index=[1, 2, 6], 
                             vmin=1, vmax=6,
                            caption='legend',
                             tick_labels=[])
                             

try:
    data = pd.read_csv(r'C:\Users\Sujat\Downloads\joined_df.csv') #r works for some reason
    data['booking_date'] = pd.to_datetime(data['booking_date'], format='%Y-%m-%d').dt.date


except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

date_list = sorted(data['booking_date'].dropna().unique()) #to delete the nans thingy

def display_time_filters():
    # day = st.sidebar.selectbox('select the day', date_list, index=len(date_list)-1 if date_list else 0)
    day = st.sidebar.slider('select the day', min_value=date_list[0], max_value=date_list[-1])
    return day

def mapDate(date_str):
    d = data[data['booking_date'] == date_str]


    max_bookings = d['total_bookings'].max()
    min_bookings = d['total_bookings'].min()
    max_booking_country = data['country_name'][d['total_bookings'].max()]
    min_booking_country = data['country_name'][d['total_bookings'].min()]
    max_booking_city = data['city_name'][d['total_bookings'].max()]
    min_booking_city = data['city_name'][d['total_bookings'].min()]

    col1, col2 = st.columns(2)
    with col1:
        st.text(f'Maximum bookings created: {max_bookings}')
        st.text(f'City: {max_booking_city}, Country: {max_booking_country}')
    with col2:
        st.text(f'Minimum bookings created: {min_bookings}')
        st.text(f'City: {min_booking_city}, Country: {min_booking_country}')




    d = d.dropna(subset=['Longitude', 'Latitude'])  #prenvet NaNs thingy
    folium_map = folium.Map()
  

    for index, row in d.iterrows():
        city = row['city_name']
        total_bookings = row['total_bookings']
        country = row['country_name']

        radius = 1e5 * 3
        popup_message = f"City: {city}, Country: {country} <br>Total Bookings: {total_bookings}"

    #make a function for colour, that determins colour using the weight - done
    #keep radius constant - done

        def colour_weight(booking_value):
            colour = colormap(math.log(booking_value, 2))
            return colour
            #take a gradient like thing and the position of the pixel from which we choose the colour is determined by the booking weight - done
        
        folium.Circle(location=[row['Longitude'], row['Latitude']], #brackets were wrong here
            radius=radius,
            fill_opacity=0.5,
            fill=True,
            fill_color=colour_weight(row['total_bookings']),
            color = colour_weight(row['total_bookings']),
            opacity = 0.3,
            popup=folium.Popup(popup_message)
        ).add_to(folium_map)
        folium_map.add_child(colormap)
    
    return folium_map

APP_TITLE = 'Day-wise bookings'


def save_map_to_state(map):
    st.session_state['folium_map_html'] = map._repr_html_()  

def load_map_from_state():
    return st.session_state.get('folium_map_html')

def main():
    st.sidebar.title(APP_TITLE)
    #st.caption(APP_SUB_TITLE)

    day = display_time_filters()
    st.header(f'Selected Day: {day}')
    folium_map = mapDate(day)
    save_map_to_state(folium_map)
    
    
    if 'folium_map_html' in st.session_state:
        folium_map_html = load_map_from_state()
        st.components.v1.html(folium_map_html, height=600)


if __name__ == "__main__":
    
    main()