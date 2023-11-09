import backend
import streamlit as st
import pandas as pd
import plotly.express as px


def search(city):
    try:
        lat, lon = backend.lookup_coord(city)
        # st.write(lat)
        data = backend.authenticate(lat,lon)
        # st.write(data)
        extracted_data = backend.sort_data(data)
        # st.write(extracted_data)
        return extracted_data,lat,lon
    except Exception as e:
        print(f"Cannot locate this city. Reason: {e}")

def emoji(emoji):
    weather_emoji = {   
                    'Clouds'   : ':cloud:',
                    'Clear'    : ':sun_behind_cloud:',
                    'Rain'     : ':rain_cloud:',
                    'Snow'     : ':snowflake:'
                    }
    if emoji in weather_emoji:
        return weather_emoji[emoji]
    else:
        return ''

def temp_time_series():
    """Container for temperature time series"""
    temp_time_df = pd.DataFrame({'actual_temp': df['actual_temp'],'feels_like_temp':df['feels_like_temp'],'timestamp':df['timestamp']})
    fig = px.line(temp_time_df, x= 'timestamp',y=['actual_temp','feels_like_temp'],title='Time Series Plot for Temperature')
    new = {'actual_temp':'Actual Temperature', 'feels_like_temp': 'Feels-like Temperature'}
    fig.for_each_trace(lambda t: t.update(name = new[t.name]))
    # fig.update_legends(selector={'actual_temp': 'Air Temperature'})
    # fig = px.scatter(title='Temp')
    # fig.add_scatter(x=df['timestamp'], y=df['actual_temp'],mode='lines',name='Actual Temperature')
    # fig.add_scatter(x=df['timestamp'], y=df['feels_like_temp'],mode='lines',name='Feels-like Temperature') 
    # fig.update_xaxes(title="Date", tickformat="%d-%m-%Y")
    # fig.update_yaxes(title="Temperature (°C)", range=[df['min_temp'].min(), df['max_temp'].max()])
    st.plotly_chart(fig,use_container_width=True)

def weather_pie():
    """Container for pie chart of weather conditions"""
    labels = list(set(df['weather_desc']))
    values = [sum([i==j for i in df['weather_desc']]) for j in labels]
    fig = px.pie(values=values,labels=labels,title="Distribution of Weather Types",hover_name=labels,names=labels)
    st.plotly_chart(fig,use_container_width=True)

def min_max():
    """Container for minimum and maximum temperatures"""
    # min_max_df = pd.DataFrame({'max_temp': df.groupby('date')['max_temp'].max(), 'date': df['date'].unique(), 'min_temp':df.groupby('date')['min_temp'].min()})
    # fig = px.line(min_max_df, x= 'date', y=['max_temp','min_temp'],title='Minimum and Maximum Temperature')
    # new = {'max_temp':'Maximum Temperature', 'min_temp': 'Minimum Temperature'}
    # fig.for_each_trace(lambda t: t.update(name = new[t.name]))
    
    fig = px.scatter(title='Minimum and Maximum Temperature')
    fig.add_scatter(x=df['date'].unique() ,y=df.groupby('date')['max_temp'].max(),name='Maximum Temperature')
    fig.add_scatter(x=df['date'].unique() ,y=df.groupby('date')['min_temp'].min(),name='Minimum Temperature')
    fig.update_yaxes(title="Temperature (°C)")
    st.plotly_chart(fig, use_container_width=True)

def temp_pressure_humidity():
    time_pres_df = pd.DataFrame({'Temperature': df['actual_temp'], 'Pressure': df['pressure'], 'Humidity': df['humidity']})
    fig = px.scatter(time_pres_df, x='Temperature',y= 'Pressure',color='Humidity',title='Temperature and Pressure')
    st.plotly_chart(fig, use_container_width=True)
    

st.set_page_config(page_title='Suleman Weather App',page_icon='	:sunrise_over_mountains:',layout='wide',initial_sidebar_state='expanded')


# Page header
st.title("Weather App :sunrise_over_mountains:")
st.text('Get the forecast for your city, plus a 5-day outlook.')
st.divider()

with st.sidebar.container():
    city= st.sidebar.text_input('**Enter City Name** :city_sunrise:', placeholder='Pune').lower()
    button = st.sidebar.button('Search :microscope:') 
    units = st.sidebar.radio( "##Select temperature units: ",["Celsius", "Fahrenheit","Kelvin"],label_visibility='collapsed')
    st.sidebar.divider()
    show_map = st.sidebar.checkbox('Show map')

if button or city:
    if not city:
        pass
    result,lat,lon = search(city)
    # st.write(result)
    df = pd.DataFrame(result)
    df.rename(columns={0:'city',1:'country',2: 'date', 3:'time',4:'actual_temp',5:'feels_like_temp',6:'min_temp',7: 'max_temp',
                       8:'pressure', 9: 'sea_level', 10: 'grnd_level', 11: 'humidity', 12: 'weather_desc'},inplace=True)
    df['timestamp'] = (df['date'] + ' ' + df['time'])
    if units == 'Celsius':
        df['actual_temp'] = df['actual_temp'] - 273.15
        df['feels_like_temp'] = df['feels_like_temp'] - 273.15
        df['max_temp'] = df['max_temp'] - 273.15
        df['min_temp'] = df['min_temp'] - 273.15
        
    elif units == 'Fahrenheit':
        df['actual_temp'] = df['actual_temp'] * 9/5 - 459.67
        df['feels_like_temp'] = df['feels_like_temp'] * 9/5 - 459.67
        df['max_temp'] = df['max_temp'] * 9/5 - 459.67
        df['min_temp'] = df['min_temp'] * 9/5 - 459.67
        
    else:
        pass
        
    with st.container():

        st.header(f"{city.capitalize()}, {df['country'].iloc[0]} {emoji(df['weather_desc'].iloc[0])}") 
        col1,col2, col3 = st.columns(3)
        with col1:
            col1.metric("Temperature", f"{round(df['actual_temp'].iloc[0],3)}")
            col1.metric("Humidity", f"{df['humidity'].iloc[0]} %")
        with col2:
            col2.metric("Feels Like", f"{round(df['feels_like_temp'].iloc[0],3)}")
            col2.metric("Pressure (mbar)", f"{df['pressure'].iloc[0]}")
        with col3:
            col3.metric("Status", f"{df['weather_desc'].iloc[0]}")
            
        with st.container():
            col1, col2 = st.columns((6,4))
            with col1:
                temp_time_series()     
            with col2:
                weather_pie()
            
            col3, col4 = st.columns((6,4))
            with col3:
                min_max()
            with col4:
                temp_pressure_humidity()

        if show_map and city:
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}),use_container_width=True)


        with st.expander(label="Get the dataset here:"):
            st.table(df)
                
        

