import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import requests as rs
import json
import random
import webbrowser
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from sys_var import api_list,indicator_symbol_list,graph_type_list



class MyError(Exception) :

    # Constructor or Initializer
    def __init__(self, value) :
        self.value = value

    # __str__ is to print() the value
    def __str__(self) :
        return (repr(self.value))




st.set_page_config(layout='wide')
st.sidebar.title('FINANCIAL PREDICTION AND ANALYSIS APPLICATION')
radio_select = st.sidebar.radio('Select from below options', [ 'Indian Stocks','Crypto', 'US Stocks', 'Forex',
                                                              "Global stocks and more(Alpha Vantage)",
                                                              "Global stocks and more(Yahoo Finance)",'Prediction'])

if radio_select == 'Crypto' :
    st.title("CRYPTOCURRENCIES")
    col1, col2 = st.columns(2)
    with col1 :
        digital_data = pd.read_csv("digital_currency_list.csv")
        dictio = digital_data.set_index('currency name').T.to_dict('list')
        digital_list = digital_data['currency name'].dropna().unique().tolist()
        crypto_select1 = st.selectbox("Select a Cryptocurrency", digital_list)
        input_value = dictio[crypto_select1][0]
    with col2 :
        currency_data = pd.read_csv("physical_currency_list.csv")
        dictio2 = currency_data.set_index('currency name').T.to_dict('list')
        currency_list = currency_data['currency name'].dropna().unique().tolist()
        currency_select = st.selectbox("Select Currency Pair", currency_list)
        currency_select = dictio2[currency_select][0]


    with st.expander('Show Options'):
        col3, col4 = st.columns(2)
        col5, col6 = st.columns(2)

    with col3 :
        interval_list = ["1 Minute", "5 Minutes", "15 Minutes", "30 Minutes", "60 Minutes", "1 Day", "1 Week",
                         "1 Month"]
        interval_list1 = ["1 Minute", "5 Minutes", "15 Minutes", "30 Minutes", "60 Minutes"]
        interval_list2 = ["1 Day", "1 Week", "1 Month"]
        interval_list1_dict = {"1 Minute" : "1min", "5 Minutes" : "5min", "15 Minutes" : "15min",
                               "30 Minutes" : "30min",
                               "60 Minutes" : "60min"}
        interval_list2_dict = {"1 Day" : "DAILY", "1 Week" : "WEEKLY", "1 Month" : "MONTHLY"}
        interval_list21_dict = {"1 Day" : "Daily", "1 Week" : "Weekly", "1 Month" : "Monthly"}
        indicator_dict = {"1 Minute" : "1min", "5 Minutes" : "5min", "15 Minutes" : "15min", "30 Minutes" : "30min",
                          "60 Minutes" : "60min", "1 Day" : "daily", "1 Week" : "weekly", "1 Month" : "monthly"}
        interval_select = st.selectbox("Select Interval", interval_list)

    with col4 :
        graph_type = st.selectbox('Select Graph type', graph_type_list)

    flag = 0
    if interval_select in interval_list1 :
        flag = 1

    try :
        y_arr = ['Rate']
        data = None
        if flag == 1 :
            data = rs.get("https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol=" + str(
                input_value) + "&market=" + str(currency_select) + "&interval=" + interval_list1_dict[
                              interval_select] + "&apikey=" + random.choice(api_list))
            print("jello")
            data = data.json()
            data = json.dumps(data["Time Series Crypto (" + str(interval_list1_dict[interval_select]) + ")"])
            data = pd.read_json(data)
            data = data.T.reset_index()
            data.rename(columns={'1. open' : 'Open'}, inplace=True)
            data.rename(columns={'2. high' : 'High'}, inplace=True)
            data.rename(columns={'3. low' : 'Low'}, inplace=True)
            data.rename(columns={'4. close' : 'Rate'}, inplace=True)

            st.markdown(
                "<h1 style='text-align: center; color: red;'>Chart of " + crypto_select1 + "&nbsp;&nbsp;<sub style='font-size: 25px;'>" + input_value + "/" + currency_select + "</sub></h1>",
                unsafe_allow_html=True)

            if graph_type == 'Line' :
                # fig = px.line(data, x="index", y=y_arr, template="ggplot2", labels={"index" : "Date"})

                fig = make_subplots(specs=[[{"secondary_y" : True}]])

                fig.add_trace(go.Scatter(x=data['index'], y=data['Rate'], name='Rate'),
                              secondary_y=True)

                fig.add_trace(go.Bar(x=data['index'], y=data['5. volume'], name='Volume', opacity=0.5),
                              secondary_y=False)

                fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators", font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="RebeccaPurple"
                ))
                fig.layout.yaxis2.showgrid = False
                st.plotly_chart(fig)
            if graph_type == 'Candlesticks' or graph_type == 'OHLC' :
                data.rename(columns={'Rate' : 'Close'}, inplace=True)
                fig = make_subplots(specs=[[{"secondary_y" : True}]])

                # include candlestick with rangeselector
                if graph_type == 'Candlesticks':
                    fig.add_trace(go.Candlestick(x=data['index'],
                                                 open=data['Open'], high=data['High'],
                                                 low=data['Low'], close=data['Close'], name='Rate'),
                                  secondary_y=True)
                if graph_type == 'OHLC':

                    fig.add_trace(go.Ohlc(x=data['index'],
                                    open=data['Open'], high=data['High'],
                                    low=data['Low'], close=data['Close'], name='Rate'),
                                    secondary_y=True)


                # include a go.Bar trace for volumes
                fig.add_trace(go.Bar(x=data['index'], y=data['5. volume'], name='Volume', opacity=0.5),
                              secondary_y=False)
                fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators", font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="RebeccaPurple"
                ))

                fig.layout.yaxis2.showgrid = False
                st.plotly_chart(fig)
            if graph_type == 'Filled Area' :
                fig = px.area(data, x='index', y='Rate', template="ggplot2", labels={"index" : "Date"})
                fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators", font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="RebeccaPurple"
                ))
                st.plotly_chart(fig)

        if flag == 0 :
            data = rs.get("https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_" + interval_list2_dict[
                interval_select] + "&symbol=" + str(
                input_value) + "&market=" + str(currency_select) + "&apikey=" + random.choice(api_list))

            data = data.json()
            data = json.dumps(data["Time Series (Digital Currency " + str(interval_list21_dict[interval_select]) + ")"])
            data = pd.read_json(data)
            data = data.T.reset_index()
            data.rename(columns={'4a. close (' + str(currency_select) + ')' : 'Rate'}, inplace=True)
            data.rename(columns={'1a. open (' + str(currency_select) + ')' : 'Open'}, inplace=True)
            data.rename(columns={'2a. high (' + str(currency_select) + ')' : 'High'}, inplace=True)
            data.rename(columns={'3a. low (' + str(currency_select) + ')' : 'Low'}, inplace=True)

            if graph_type != 'Filled Area' :
                with col5 :
                    indicate_select = st.multiselect('Add Indicators', indicator_symbol_list)

                    interval_sel = indicate_select
                with col6 :
                    time_select = st.number_input('Select indicator time period', max_value=30, min_value=5, step=1)
                for i in range(len(interval_sel)) :
                    data2 = rs.get("https://www.alphavantage.co/query?function=" + interval_sel[i] + "&symbol=" + str(
                        input_value) + str(currency_select) + "&interval=" + indicator_dict[
                                       interval_select] + "&time_period=" + str(
                        time_select) + "&series_type=open&apikey=" + random.choice(api_list))

                    data2 = data2.json()

                    data2 = json.dumps(data2["Technical Analysis: " + interval_sel[i]])

                    data2 = pd.read_json(data2)
                    data2 = data2.T.reset_index()
                    data = pd.merge(data, data2, on="index", how="left")
                y_arr = y_arr + interval_sel
            st.markdown(
                "<h1 style='text-align: center; color: red;'>Chart of " + crypto_select1 + "&nbsp;&nbsp;<sub style='font-size: 25px;'>" + input_value + "/" + currency_select + "</sub></h1>",
                unsafe_allow_html=True)

            # fig = px.line(data, x="index", y=y_arr, template="ggplot2", labels={"index" : "Date"})
            if graph_type == 'Line' :
                fig = make_subplots(specs=[[{"secondary_y" : True}]])

                fig.add_trace(go.Scatter(x=data['index'], y=data['Rate'], name='Rate'),
                              secondary_y=True)
                for i in range(len(interval_sel)) :
                    fig.add_trace(go.Scatter(x=data['index'], y=data[interval_sel[i]], name=interval_sel[i]),
                                  secondary_y=True)

                fig.add_trace(go.Bar(x=data['index'], y=data['5. volume'], name='Volume', opacity=0.5),
                              secondary_y=False)

                fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators", font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="RebeccaPurple"
                ))
                fig.layout.yaxis2.showgrid = False
                st.plotly_chart(fig)
            if graph_type == 'Candlesticks' or graph_type == 'OHLC' :
                data.rename(columns={'Rate' : 'Close'}, inplace=True)
                fig = make_subplots(specs=[[{"secondary_y" : True}]])

                # include candlestick with rangeselector
                if graph_type == 'Candlesticks' :
                    fig.add_trace(go.Candlestick(x=data['index'],
                                                 open=data['Open'], high=data['High'],
                                                 low=data['Low'], close=data['Close'], name='Rate'),
                                  secondary_y=True)
                if graph_type == 'OHLC' :
                    fig.add_trace(go.Ohlc(x=data['index'],
                                          open=data['Open'], high=data['High'],
                                          low=data['Low'], close=data['Close'], name='Rate'),
                                  secondary_y=True)

                # include a go.Bar trace for volumes
                fig.add_trace(go.Bar(x=data['index'], y=data['5. volume'], name='Volume', opacity=0.5),
                              secondary_y=False)
                fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators", font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="RebeccaPurple"
                ))

                fig.layout.yaxis2.showgrid = False
                st.plotly_chart(fig)

            if graph_type == 'Filled Area' :
                fig = px.area(data, x='index', y='Rate', template="ggplot2", labels={"index" : "Date"})
                fig.update_layout(autosize=False, width=1600, height=500, legend_title="Indicators", font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="RebeccaPurple"
                ))
                st.plotly_chart(fig)
    except Exception as e :
        st.info(
            "The selected cryptocurrency data is currently unavailable please check your connection or choose any other cryptocurrency(like Bitcoin)")

if radio_select == 'Forex' :

    st.title("FOREX")
    size_select = st.sidebar.radio('Select output size', ['compact', 'full(uses more data)'])
    size_select = size_select.split('(')[0]
    col1, col2 = st.columns(2)
    with col1 :
        digital_data = pd.read_csv("physical_currency_list1.csv")
        dictio = digital_data.set_index('currency name').T.to_dict('list')
        digital_list = digital_data['currency name'].dropna().unique().tolist()
        crypto_select1 = st.selectbox("Select the Currency", digital_list)
        input_value = dictio[crypto_select1][0]
    with col2 :
        currency_data = pd.read_csv("physical_currency_list.csv")
        dictio2 = currency_data.set_index('currency name').T.to_dict('list')
        currency_list = currency_data['currency name'].dropna().unique().tolist()
        currency_select = st.selectbox("Select currency pair", currency_list)
        currency_select = dictio2[currency_select][0]

    with st.expander('Show Options') :
        col3, col4 = st.columns(2)
        col5, col6 = st.columns(2)

    with col3 :
        interval_list = ["1 Day", "1 Week", "1 Month"]



        interval_list2_dict = {"1 Day" : "DAILY", "1 Week" : "WEEKLY", "1 Month" : "MONTHLY"}
        interval_list21_dict = {"1 Day" : "Daily", "1 Week" : "Weekly", "1 Month" : "Monthly"}
        indicator_dict = {"1 Minute" : "1min", "5 Minutes" : "5min", "15 Minutes" : "15min", "30 Minutes" : "30min",
                          "60 Minutes" : "60min", "1 Day" : "daily", "1 Week" : "weekly", "1 Month" : "monthly"}
        interval_select = st.selectbox("Select Interval", interval_list)

    with col4 :
        graph_type = st.selectbox('Select Graph type', graph_type_list)

    flag = 0


    try :
        y_arr = ['Rate']
        data = None

        if flag == 0 :
            print("https://www.alphavantage.co/query?function=FX_" + interval_list2_dict[
                interval_select] + "&from_symbol=" + str(
                input_value) + "&to_symbol=" + str(currency_select) + "&apikey=" + random.choice(api_list))
            data = rs.get("https://www.alphavantage.co/query?function=FX_" + interval_list2_dict[
                interval_select] + "&from_symbol=" + str(
                input_value) + "&to_symbol=" + str(
                currency_select) + "&outputsize=" + size_select + "&apikey=" + random.choice(api_list))

            data = data.json()
            print(data)
            data = json.dumps(data["Time Series FX (" + str(interval_list21_dict[interval_select]) + ")"])
            data = pd.read_json(data)
            data = data.T.reset_index()
            data.rename(columns={'4. close' : 'Rate'}, inplace=True)
            data.rename(columns={'1. open' : 'Open'}, inplace=True)
            data.rename(columns={'2. high' : 'High'}, inplace=True)
            data.rename(columns={'3. low' : 'Low'}, inplace=True)

            if graph_type != 'Filled Area' :
                with col5 :
                    indicate_select = st.multiselect('Add Indicators', indicator_symbol_list)

                    interval_sel = indicate_select
                with col6 :
                    time_select = st.number_input('Select indicator time period', max_value=30, min_value=5, step=1)
                for i in range(len(interval_sel)) :
                    data2 = rs.get("https://www.alphavantage.co/query?function=" + interval_sel[i] + "&symbol=" + str(
                        input_value) + str(currency_select) + "&interval=" + indicator_dict[
                                       interval_select] + "&time_period=" + str(
                        time_select) + "&series_type=open&outputsize=" + size_select + "&apikey=" + random.choice(
                        api_list))

                    data2 = data2.json()

                    data2 = json.dumps(data2["Technical Analysis: " + interval_sel[i]])

                    data2 = pd.read_json(data2)
                    data2 = data2.T.reset_index()
                    data = pd.merge(data, data2, on="index", how="left")
                y_arr = y_arr + interval_sel
            st.markdown(
                "<h1 style='text-align: center; color: red;'>Chart of " + crypto_select1 + "&nbsp;&nbsp;<sub style='font-size: 25px;'>" + input_value + "/" + currency_select + "</sub></h1>",
                unsafe_allow_html=True)

            # fig = px.line(data, x="index", y=y_arr, template="ggplot2", labels={"index" : "Date"})
            if graph_type == 'Line' :
                fig = make_subplots(specs=[[{"secondary_y" : True}]])

                fig.add_trace(go.Scatter(x=data['index'], y=data['Rate'], name='Rate'),
                              secondary_y=True)
                for i in range(len(interval_sel)) :
                    fig.add_trace(go.Scatter(x=data['index'], y=data[interval_sel[i]], name=interval_sel[i]),
                                  secondary_y=True)

                fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators", font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="RebeccaPurple"
                ))
                fig.layout.yaxis2.showgrid = False
                st.plotly_chart(fig)
            if graph_type == 'Candlesticks' or graph_type == 'OHLC' :
                data.rename(columns={'Rate' : 'Close'}, inplace=True)
                fig = make_subplots(specs=[[{"secondary_y" : True}]])

                # include candlestick with rangeselector
                if graph_type == 'Candlesticks' :
                    fig.add_trace(go.Candlestick(x=data['index'],
                                                 open=data['Open'], high=data['High'],
                                                 low=data['Low'], close=data['Close'], name='Rate'),
                                  secondary_y=True)
                if graph_type == 'OHLC' :
                    fig.add_trace(go.Ohlc(x=data['index'],
                                          open=data['Open'], high=data['High'],
                                          low=data['Low'], close=data['Close'], name='Rate'),
                                  secondary_y=True)
                for i in range(len(interval_sel)) :
                    fig.add_trace(go.Scatter(x=data['index'], y=data[interval_sel[i]], name=interval_sel[i]),
                                  secondary_y=True)

                # include a go.Bar trace for volumes

                fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators", font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="RebeccaPurple"
                ))

                fig.layout.yaxis2.showgrid = False
                st.plotly_chart(fig)

            if graph_type == 'Filled Area' :
                fig = px.area(data, x='index', y='Rate', template="ggplot2", labels={"index" : "Date"})
                fig.update_layout(autosize=False, width=1600, height=500, legend_title="Indicators", font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="RebeccaPurple"
                ))
                st.plotly_chart(fig)
    except Exception as e :
        st.info(
            "The selected forex pair data is currently unavailable please check your connection or choose any other pair")


if radio_select == "Global stocks and more(Alpha Vantage)" :

    st.title(radio_select)
    size_select = st.sidebar.radio('Select output size', ['compact', 'full(uses more data)'])
    size_select = size_select.split('(')[0]
    keyword = st.text_input("Search by symbol,name or keyword")

    if keyword != '' :
        print(keyword)
        print('https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=' + str(
            keyword) + '&apikey=' + random.choice(api_list))
        data = rs.get('https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=' + str(
            keyword) + '&apikey=' + random.choice(api_list))
        data = data.json()
        # data = pd.read_json(data)
        try :
            if data["bestMatches"] == [] :
                raise (MyError('No financial entity with this name found in our system'))
            data = json.dumps(data["bestMatches"])
            data = pd.read_json(data)
            data.rename(columns={'1. symbol' : 'Symbol'}, inplace=True)
            data.rename(columns={'2. name' : 'Name'}, inplace=True)
            data.rename(columns={'3. type' : 'Type'}, inplace=True)
            data.rename(columns={'4. region' : 'Region'}, inplace=True)
            data.rename(columns={'5. marketOpen' : 'Market Open'}, inplace=True)
            data.rename(columns={'6. marketClose' : 'Market Close'}, inplace=True)
            data.rename(columns={'7. timezone' : 'Timezone'}, inplace=True)
            data.rename(columns={'8. currency' : 'Currency'}, inplace=True)

            data_ticker = data['Symbol'].tolist()
            data_name = data['Name'].tolist()
            data_type = data['Type'].tolist()
            data_region = data['Region'].tolist()

            new_list = []
            for i in range(len(data_ticker)) :
                s = data_name[i] + "----" + data_ticker[i] + "----" + data_type[i] + "----" + data_region[i]
                new_list.append(s)
            new_list.insert(0, '--Select from options--')

            col1, col2 = st.columns(2)
            with col1 :
                new_box = st.selectbox("Select from below options", new_list)
            if (new_box != '--Select from options--') :

                input_value = new_box.split("----")[1]
                crypto_select1 = new_box.split("----")[0]
                currency_select = data[data['Symbol'] == input_value]['Currency'].tolist()
                currency_select1 = currency_select[0]
                print(currency_select)
                currency_data = pd.read_csv("physical_currency_list.csv")
                currency_select = currency_data[currency_data['currency code'] == currency_select[0]]['currency name']
                print(currency_select)
                with col2 :
                    st.selectbox("Select Currency pair", currency_select, disabled=True)
                st.table(data[data['Symbol'] == input_value].drop(['9. matchScore'], axis=1))
                with st.expander('Show Options'):
                    col3, col4 = st.columns(2)
                    col5, col6 = st.columns(2)

                with col3 :
                    interval_list = ["1 Day", "1 Week", "1 Month"]

                    interval_list2_dict = {"1 Day" : "DAILY", "1 Week" : "WEEKLY", "1 Month" : "MONTHLY"}
                    interval_list21_dict = {"1 Day" : "Daily", "1 Week" : "Weekly", "1 Month" : "Monthly"}
                    indicator_dict = {"1 Minute" : "1min", "5 Minutes" : "5min", "15 Minutes" : "15min",
                                      "30 Minutes" : "30min",
                                      "60 Minutes" : "60min", "1 Day" : "daily", "1 Week" : "weekly",
                                      "1 Month" : "monthly"}
                    interval_select = st.selectbox("Select Interval", interval_list)

                with col4 :
                    graph_type = st.selectbox('Select Graph type', graph_type_list)

                flag = 0


                try :
                    y_arr = ['Rate']
                    data = None

                    if flag == 0 :

                        data = rs.get("https://www.alphavantage.co/query?function=TIME_SERIES_" + interval_list2_dict[
                            interval_select] + "&symbol=" + str(
                            input_value) + "&outputsize=" + size_select + "&apikey=" + random.choice(api_list))
                        # data=rs.get('https://www.alphavantage.co/query?function=DAILY&symbol=RELIANCE.BSE&outputsize=full&apikey=demo')

                        data = data.json()
                        data = json.dumps(data["Time Series (" + str(interval_list21_dict[interval_select]) + ")"])
                        data = pd.read_json(data)
                        data = data.T.reset_index()
                        data.rename(columns={'4. close' : 'Rate'}, inplace=True)
                        data.rename(columns={'1. open' : 'Open'}, inplace=True)
                        data.rename(columns={'2. high' : 'High'}, inplace=True)
                        data.rename(columns={'3. low' : 'Low'}, inplace=True)

                        if graph_type != 'Filled Area' :
                            with col5 :
                                indicate_select = st.multiselect('Add Indicators', indicator_symbol_list)

                                interval_sel = indicate_select
                            with col6 :
                                time_select = st.number_input('Select indicator time period', max_value=30, min_value=5,
                                                              step=1)
                            for i in range(len(interval_sel)) :
                                data2 = rs.get(
                                    "https://www.alphavantage.co/query?function=" + interval_sel[i] + "&symbol=" + str(
                                        input_value) + "&interval=" + indicator_dict[
                                        interval_select] + "&time_period=" + str(
                                        time_select) + "&series_type=open&outputsize=" + size_select + "&apikey=" + random.choice(
                                        api_list))

                                data2 = data2.json()

                                data2 = json.dumps(data2["Technical Analysis: " + interval_sel[i]])

                                data2 = pd.read_json(data2)
                                data2 = data2.T.reset_index()
                                data = pd.merge(data, data2, on="index", how="left")
                            y_arr = y_arr + interval_sel
                        st.markdown(
                            "<h1 style='text-align: center; color: red;'>Chart of " + crypto_select1 + "&nbsp;&nbsp;<sub style='font-size: 25px;'>" + input_value + "/" + currency_select1 + "</sub></h1>",
                            unsafe_allow_html=True)

                        # fig = px.line(data, x="index", y=y_arr, template="ggplot2", labels={"index" : "Date"})
                        if graph_type == 'Line' :
                            fig = make_subplots(specs=[[{"secondary_y" : True}]])

                            fig.add_trace(go.Scatter(x=data['index'], y=data['Rate'], name='Rate'),
                                          secondary_y=True)
                            for i in range(len(interval_sel)) :
                                fig.add_trace(
                                    go.Scatter(x=data['index'], y=data[interval_sel[i]], name=interval_sel[i]),
                                    secondary_y=True)

                            fig.add_trace(go.Bar(x=data['index'], y=data['5. volume'], name='Volume', opacity=0.5),
                                          secondary_y=False)

                            fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators",
                                              font=dict(
                                                  family="Courier New, monospace",
                                                  size=18,
                                                  color="RebeccaPurple"
                                              ))
                            fig.layout.yaxis2.showgrid = False
                            st.plotly_chart(fig)
                        if graph_type == 'Candlesticks' or graph_type == 'OHLC' :
                            data.rename(columns={'Rate' : 'Close'}, inplace=True)
                            fig = make_subplots(specs=[[{"secondary_y" : True}]])

                            # include candlestick with rangeselector
                            if graph_type == 'Candlesticks' :
                                fig.add_trace(go.Candlestick(x=data['index'],
                                                             open=data['Open'], high=data['High'],
                                                             low=data['Low'], close=data['Close'], name='Rate'),
                                              secondary_y=True)
                            if graph_type == 'OHLC' :
                                fig.add_trace(go.Ohlc(x=data['index'],
                                                      open=data['Open'], high=data['High'],
                                                      low=data['Low'], close=data['Close'], name='Rate'),
                                              secondary_y=True)
                            for i in range(len(interval_sel)) :
                                fig.add_trace(
                                    go.Scatter(x=data['index'], y=data[interval_sel[i]], name=interval_sel[i]),
                                    secondary_y=True)

                            # include a go.Bar trace for volumes
                            fig.add_trace(go.Bar(x=data['index'], y=data['5. volume'], name='Volume', opacity=0.5),
                                          secondary_y=False)
                            fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators",
                                              font=dict(
                                                  family="Courier New, monospace",
                                                  size=18,
                                                  color="RebeccaPurple"
                                              ))

                            fig.layout.yaxis2.showgrid = False
                            st.plotly_chart(fig)

                        if graph_type == 'Filled Area' :
                            fig = px.area(data, x='index', y='Rate', template="ggplot2", labels={"index" : "Date"})
                            fig.update_layout(autosize=False, width=1600, height=500, legend_title="Indicators",
                                              font=dict(
                                                  family="Courier New, monospace",
                                                  size=18,
                                                  color="RebeccaPurple"
                                              ))
                            st.plotly_chart(fig)

                except Exception as e :
                    st.info(
                        "The selected financial entity data is currently unavailable please check your connection or choose another name")

        except MyError as err :
            st.info(err.value)

if radio_select == "US Stocks" :

    st.title(radio_select)
    keyword = st.text_input("Search by symbol,name or keyword")
    size_select = st.sidebar.radio('Select output size', ['compact', 'full(uses more data)'])
    size_select = size_select.split('(')[0]

    if keyword != '' :
        print(keyword)
        print('https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=' + str(
            keyword) + '&apikey=' + random.choice(api_list))
        data = rs.get('https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=' + str(
            keyword) + '&apikey=' + random.choice(api_list))
        data = data.json()
        # data = pd.read_json(data)
        try :
            if data["bestMatches"] == [] :
                raise (MyError('No financial entity with this name found in our system'))
            data = json.dumps(data["bestMatches"])
            data = pd.read_json(data)
            data.rename(columns={'1. symbol' : 'Symbol'}, inplace=True)
            data.rename(columns={'2. name' : 'Name'}, inplace=True)
            data.rename(columns={'3. type' : 'Type'}, inplace=True)
            data.rename(columns={'4. region' : 'Region'}, inplace=True)
            data.rename(columns={'5. marketOpen' : 'Market Open'}, inplace=True)
            data.rename(columns={'6. marketClose' : 'Market Close'}, inplace=True)
            data.rename(columns={'7. timezone' : 'Timezone'}, inplace=True)
            data.rename(columns={'8. currency' : 'Currency'}, inplace=True)

            data = data[data['Region'] == 'United States']

            if data.count(axis=0)['Symbol'] == 0 :
                raise (MyError('No US Stocks with this name found in our system'))
            data_ticker = data['Symbol'].tolist()
            data_name = data['Name'].tolist()
            data_type = data['Type'].tolist()
            data_region = data['Region'].tolist()

            new_list = []
            for i in range(len(data_ticker)) :
                s = data_name[i] + "----" + data_ticker[i] + "----" + data_type[i]
                new_list.append(s)
            new_list.insert(0, '--Select from options--')

            col1, col2 = st.columns(2)
            with col1 :
                new_box = st.selectbox("Select from below options", new_list)
            if (new_box != '--Select from options--') :

                input_value = new_box.split("----")[1]
                crypto_select1 = new_box.split("----")[0]
                currency_select = data[data['Symbol'] == input_value]['Currency'].tolist()
                currency_select1 = currency_select[0]
                currency_data = pd.read_csv("physical_currency_list.csv")
                currency_select = currency_data[currency_data['currency code'] == currency_select[0]]['currency name']

                with col2 :
                    st.selectbox("Select Currency pair", currency_select, disabled=True)
                st.table(data[data['Symbol'] == input_value].drop(['9. matchScore'], axis=1))
                over_data = rs.get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=' + str(
                    input_value) + '&apikey=' + random.choice(api_list))
                if over_data.json() != {} :
                    milind = st.button('Get more info')
                    if milind :
                        a = over_data.json()
                        c = pd.DataFrame(a, index=[0])
                        d = c.T.reset_index()
                        d.index = np.arange(1, len(d) + 1)
                        d.rename(columns={'index' : 'Info Term'}, inplace=True)
                        d.rename(columns={0 : 'Info Description'}, inplace=True)
                        st.table(d)
                with st.expander('Show Options'):
                    col3, col4 = st.columns(2)
                    col5, col6 = st.columns(2)

                with col3 :
                    interval_list = ["1 Day", "1 Week", "1 Month"]

                    interval_list2_dict = {"1 Day" : "DAILY", "1 Week" : "WEEKLY", "1 Month" : "MONTHLY"}
                    interval_list21_dict = {"1 Day" : "Daily", "1 Week" : "Weekly", "1 Month" : "Monthly"}
                    indicator_dict = {"1 Minute" : "1min", "5 Minutes" : "5min", "15 Minutes" : "15min",
                                      "30 Minutes" : "30min",
                                      "60 Minutes" : "60min", "1 Day" : "daily", "1 Week" : "weekly",
                                      "1 Month" : "monthly"}
                    interval_select = st.selectbox("Select Interval", interval_list)

                with col4 :
                    graph_type = st.selectbox('Select Graph type', graph_type_list)

                flag = 0


                try :
                    y_arr = ['Rate']
                    data = None

                    if flag == 0 :

                        data = rs.get("https://www.alphavantage.co/query?function=TIME_SERIES_" + interval_list2_dict[
                            interval_select] + "&symbol=" + str(
                            input_value) + "&outputsize=" + size_select + "&apikey=" + random.choice(api_list))
                        # data=rs.get('https://www.alphavantage.co/query?function=DAILY&symbol=RELIANCE.BSE&outputsize=full&apikey=demo')

                        data = data.json()
                        data = json.dumps(data["Time Series (" + str(interval_list21_dict[interval_select]) + ")"])
                        data = pd.read_json(data)
                        data = data.T.reset_index()
                        data.rename(columns={'4. close' : 'Rate'}, inplace=True)
                        data.rename(columns={'1. open' : 'Open'}, inplace=True)
                        data.rename(columns={'2. high' : 'High'}, inplace=True)
                        data.rename(columns={'3. low' : 'Low'}, inplace=True)

                        if graph_type != 'Filled Area' :
                            with col5 :
                                indicate_select = st.multiselect('Add Indicators', indicator_symbol_list)

                                interval_sel = indicate_select
                            with col6 :
                                time_select = st.number_input('Select indicator time period', max_value=30, min_value=5,
                                                              step=1)
                            for i in range(len(interval_sel)) :
                                data2 = rs.get(
                                    "https://www.alphavantage.co/query?function=" + interval_sel[i] + "&symbol=" + str(
                                        input_value) + "&interval=" + indicator_dict[
                                        interval_select] + "&time_period=" + str(
                                        time_select) + "&series_type=open&outputsize=" + size_select + "&apikey=" + random.choice(
                                        api_list))

                                data2 = data2.json()

                                data2 = json.dumps(data2["Technical Analysis: " + interval_sel[i]])

                                data2 = pd.read_json(data2)
                                data2 = data2.T.reset_index()
                                data = pd.merge(data, data2, on="index", how="left")
                            y_arr = y_arr + interval_sel
                        st.markdown(
                            "<h1 style='text-align: center; color: red;'>Chart of " + crypto_select1 + "&nbsp;&nbsp;<sub style='font-size: 25px;'>" + input_value + "/" + currency_select1 + "</sub></h1>",
                            unsafe_allow_html=True)

                        # fig = px.line(data, x="index", y=y_arr, template="ggplot2", labels={"index" : "Date"})
                        if graph_type == 'Line' :
                            fig = make_subplots(specs=[[{"secondary_y" : True}]])

                            fig.add_trace(go.Scatter(x=data['index'], y=data['Rate'], name='Rate'),
                                          secondary_y=True)
                            for i in range(len(interval_sel)) :
                                fig.add_trace(
                                    go.Scatter(x=data['index'], y=data[interval_sel[i]], name=interval_sel[i]),
                                    secondary_y=True)

                            fig.add_trace(go.Bar(x=data['index'], y=data['5. volume'], name='Volume', opacity=0.5),
                                          secondary_y=False)

                            fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators",
                                              font=dict(
                                                  family="Courier New, monospace",
                                                  size=18,
                                                  color="RebeccaPurple"
                                              ))
                            fig.layout.yaxis2.showgrid = False
                            st.plotly_chart(fig)
                        if graph_type == 'Candlesticks' or graph_type == 'OHLC' :
                            data.rename(columns={'Rate' : 'Close'}, inplace=True)
                            fig = make_subplots(specs=[[{"secondary_y" : True}]])

                            # include candlestick with rangeselector
                            if graph_type == 'Candlesticks' :
                                fig.add_trace(go.Candlestick(x=data['index'],
                                                             open=data['Open'], high=data['High'],
                                                             low=data['Low'], close=data['Close'], name='Rate'),
                                              secondary_y=True)
                            if graph_type == 'OHLC' :
                                fig.add_trace(go.Ohlc(x=data['index'],
                                                      open=data['Open'], high=data['High'],
                                                      low=data['Low'], close=data['Close'], name='Rate'),
                                              secondary_y=True)

                            # include a go.Bar trace for volumes
                            fig.add_trace(go.Bar(x=data['index'], y=data['5. volume'], name='Volume', opacity=0.5),
                                          secondary_y=False)
                            fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators",
                                              font=dict(
                                                  family="Courier New, monospace",
                                                  size=18,
                                                  color="RebeccaPurple"
                                              ))

                            fig.layout.yaxis2.showgrid = False
                            st.plotly_chart(fig)

                        if graph_type == 'Filled Area' :
                            fig = px.area(data, x='index', y='Rate', template="ggplot2", labels={"index" : "Date"})
                            fig.update_layout(autosize=False, width=1600, height=500, legend_title="Indicators",
                                              font=dict(
                                                  family="Courier New, monospace",
                                                  size=18,
                                                  color="RebeccaPurple"
                                              ))
                            st.plotly_chart(fig)






                except Exception as e :
                    st.info(
                        "The selected financial entity data is currently unavailable please check your connection or choose another name")


        except MyError as err :
            st.info(err.value)

if radio_select == 'Indian Stocks' :

    st.title(radio_select)
    keyword = st.text_input("Search by symbol,name or keyword")
    size_select = st.sidebar.radio('Select output size', ['compact', 'full(uses more data)'])
    size_select = size_select.split('(')[0]

    if keyword != '' :
        print(keyword)
        print('https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=' + str(
            keyword) + '&apikey=' + random.choice(api_list))
        data = rs.get('https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=' + str(
            keyword) + '&apikey=' + random.choice(api_list))
        data = data.json()
        # data = pd.read_json(data)
        try :
            if data["bestMatches"] == [] :
                raise (MyError('No financial entity with this name found in our system'))
            data = json.dumps(data["bestMatches"])
            data = pd.read_json(data)
            data.rename(columns={'1. symbol' : 'Symbol'}, inplace=True)
            data.rename(columns={'2. name' : 'Name'}, inplace=True)
            data.rename(columns={'3. type' : 'Type'}, inplace=True)
            data.rename(columns={'4. region' : 'Region'}, inplace=True)
            data.rename(columns={'5. marketOpen' : 'Market Open'}, inplace=True)
            data.rename(columns={'6. marketClose' : 'Market Close'}, inplace=True)
            data.rename(columns={'7. timezone' : 'Timezone'}, inplace=True)
            data.rename(columns={'8. currency' : 'Currency'}, inplace=True)

            data = data[data['Region'] == 'India/Bombay']

            if data.count(axis=0)['Symbol'] == 0 :
                raise (MyError('No Indian Stocks with this name found in our system'))
            data_ticker = data['Symbol'].tolist()
            data_name = data['Name'].tolist()
            data_type = data['Type'].tolist()
            data_region = data['Region'].tolist()

            new_list = []
            for i in range(len(data_ticker)) :
                s = data_name[i] + "----" + data_ticker[i].split('.')[0] + "----" + data_type[i]
                new_list.append(s)
            new_list.insert(0, '--Select from options--')

            col1, col2 = st.columns(2)
            with col1 :
                new_box = st.selectbox("Select from below options", new_list)
            if (new_box != '--Select from options--') :
                temp_select = new_box.split("----")[1]
                input_value = new_box.split("----")[1] + '.BSE'
                crypto_select1 = new_box.split("----")[0]
                currency_select = data[data['Symbol'] == input_value]['Currency'].tolist()
                currency_select1 = currency_select[0]
                currency_data = pd.read_csv("physical_currency_list.csv")
                currency_select = currency_data[currency_data['currency code'] == currency_select[0]]['currency name']

                with col2 :
                    st.selectbox("Select Currency pair", currency_select, disabled=True)
                data = data[data['Symbol'] == input_value].drop(['9. matchScore'], axis=1)
                data['Symbol'][0] = temp_select
                st.table(data)

                with st.expander('Show Options'):
                    col3, col4 = st.columns(2)
                    col5, col6 = st.columns(2)

                with col3 :
                    interval_list = ["1 Day", "1 Week", "1 Month"]

                    interval_list2_dict = {"1 Day" : "DAILY", "1 Week" : "WEEKLY", "1 Month" : "MONTHLY"}
                    interval_list21_dict = {"1 Day" : "Daily", "1 Week" : "Weekly", "1 Month" : "Monthly"}
                    indicator_dict = {"1 Minute" : "1min", "5 Minutes" : "5min", "15 Minutes" : "15min",
                                      "30 Minutes" : "30min",
                                      "60 Minutes" : "60min", "1 Day" : "daily", "1 Week" : "weekly",
                                      "1 Month" : "monthly"}
                    interval_select = st.selectbox("Select Interval", interval_list)

                with col4 :
                    graph_type = st.selectbox('Select Graph type', graph_type_list)

                flag = 0


                try :
                    y_arr = ['Rate']
                    data = None

                    if flag == 0 :

                        data = rs.get("https://www.alphavantage.co/query?function=TIME_SERIES_" + interval_list2_dict[
                            interval_select] + "&symbol=" + str(
                            input_value) + "&outputsize=" + size_select + "&apikey=" + random.choice(api_list))
                        # data=rs.get('https://www.alphavantage.co/query?function=DAILY&symbol=RELIANCE.BSE&outputsize=full&apikey=demo')

                        data = data.json()
                        data = json.dumps(data["Time Series (" + str(interval_list21_dict[interval_select]) + ")"])
                        data = pd.read_json(data)
                        data = data.T.reset_index()
                        data.rename(columns={'4. close' : 'Rate'}, inplace=True)
                        data.rename(columns={'1. open' : 'Open'}, inplace=True)
                        data.rename(columns={'2. high' : 'High'}, inplace=True)
                        data.rename(columns={'3. low' : 'Low'}, inplace=True)

                        if graph_type != 'Filled Area' :
                            with col5 :
                                indicate_select = st.multiselect('Add Indicators', indicator_symbol_list)

                                interval_sel = indicate_select
                            with col6 :
                                time_select = st.number_input('Select indicator time period', max_value=30, min_value=5,
                                                              step=1)
                            for i in range(len(interval_sel)) :
                                data2 = rs.get(
                                    "https://www.alphavantage.co/query?function=" + interval_sel[i] + "&symbol=" + str(
                                        input_value) + "&interval=" + indicator_dict[
                                        interval_select] + "&time_period=" + str(
                                        time_select) + "&series_type=open&outputsize=" + size_select + "&apikey=" + random.choice(
                                        api_list))

                                data2 = data2.json()

                                data2 = json.dumps(data2["Technical Analysis: " + interval_sel[i]])

                                data2 = pd.read_json(data2)
                                data2 = data2.T.reset_index()
                                data = pd.merge(data, data2, on="index", how="left")
                            y_arr = y_arr + interval_sel
                        st.markdown(
                            "<h1 style='text-align: center; color: red;'>Chart of " + crypto_select1 + "&nbsp;&nbsp;<sub style='font-size: 25px;'>" + temp_select + "/" + currency_select1 + "</sub></h1>",
                            unsafe_allow_html=True)

                        # fig = px.line(data, x="index", y=y_arr, template="ggplot2", labels={"index" : "Date"})
                        if graph_type == 'Line' :
                            fig = make_subplots(specs=[[{"secondary_y" : True}]])

                            fig.add_trace(go.Scatter(x=data['index'], y=data['Rate'], name='Rate'),
                                          secondary_y=True)
                            for i in range(len(interval_sel)) :
                                fig.add_trace(
                                    go.Scatter(x=data['index'], y=data[interval_sel[i]], name=interval_sel[i]),
                                    secondary_y=True)

                            fig.add_trace(go.Bar(x=data['index'], y=data['5. volume'], name='Volume', opacity=0.5),
                                          secondary_y=False)

                            fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators",
                                              font=dict(
                                                  family="Courier New, monospace",
                                                  size=18,
                                                  color="RebeccaPurple"
                                              ))
                            fig.layout.yaxis2.showgrid = False
                            st.plotly_chart(fig)
                        if graph_type == 'Candlesticks' or graph_type == 'OHLC' :
                            data.rename(columns={'Rate' : 'Close'}, inplace=True)
                            fig = make_subplots(specs=[[{"secondary_y" : True}]])

                            # include candlestick with rangeselector
                            if graph_type == 'Candlesticks' :
                                fig.add_trace(go.Candlestick(x=data['index'],
                                                             open=data['Open'], high=data['High'],
                                                             low=data['Low'], close=data['Close'], name='Rate'),
                                              secondary_y=True)
                            if graph_type == 'OHLC' :
                                fig.add_trace(go.Ohlc(x=data['index'],
                                                      open=data['Open'], high=data['High'],
                                                      low=data['Low'], close=data['Close'], name='Rate'),
                                              secondary_y=True)
                            for i in range(len(interval_sel)) :
                                fig.add_trace(
                                    go.Scatter(x=data['index'], y=data[interval_sel[i]], name=interval_sel[i]),
                                    secondary_y=True)

                            # include a go.Bar trace for volumes
                            fig.add_trace(go.Bar(x=data['index'], y=data['5. volume'], name='Volume', opacity=0.5),
                                          secondary_y=False)
                            fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators",
                                              font=dict(
                                                  family="Courier New, monospace",
                                                  size=18,
                                                  color="RebeccaPurple"
                                              ))

                            fig.layout.yaxis2.showgrid = False
                            st.plotly_chart(fig)

                        if graph_type == 'Filled Area' :
                            fig = px.area(data, x='index', y='Rate', template="ggplot2", labels={"index" : "Date"})
                            fig.update_layout(autosize=False, width=1600, height=500, legend_title="Indicators",
                                              font=dict(
                                                  family="Courier New, monospace",
                                                  size=18,
                                                  color="RebeccaPurple"
                                              ))
                            st.plotly_chart(fig)






                except Exception as e :
                    st.info(
                        "The selected financial entity data is currently unavailable please check your connection or choose another name")


        except MyError as err :
            st.info(err.value)
    else:
        st.info('Here only Bombay Stock Exchange(BSE/BS) is supported for National Stock Exchange(NSE/NS) select "Global stocks and more(Yahoo Finance)" option from sidebar ')

if radio_select == "Global stocks and more(Yahoo Finance)" :

    st.title(radio_select)

    keyword = st.text_input("Search by Symbol/Ticker")

    sym_but = st.button('Click here to search for supported symbols')
    if sym_but :
        webbrowser.open('https://finance.yahoo.com/screener/new')

    if keyword != '' :
        ticker = yf.Ticker(keyword)
        try :
            if ticker.info['sector'] :



                function_list = ['Information', 'Chart', 'Dividend and Stock Splits', 'Financials', 'Major Holders',
                                 'Institutional Holders', 'Balance sheet', 'Recommendations', 'Cashflow', 'Earnings']

                function_select = st.selectbox('Select the function', function_list)
                st.write(" ")
                if function_select == 'Chart' :
                    with st.expander('Show Options'):
                        col3, col4 = st.columns(2)
                        col5, col6 = st.columns(2)

                        with col3 :
                            interval_list = ["1 Day", "1 Week",
                                             "1 Month"]
                            interval_list2_dict = {"1 Day" : "1d", "1 Week" : "1wk", "1 Month" : "1mo"}

                            interval_select = st.selectbox("Select Interval", interval_list)

                        with col4 :
                            graph_type = st.selectbox('Select Graph type', graph_type_list)

                        with col5 :
                            start_date = st.date_input("Start date", datetime.date(2021, 1, 10))
                        with col6 :
                            end_date = st.date_input("End date", datetime.date(2022, 2, 10))

                    st.markdown(
                        "<h1 style='text-align: center; color: red;'>Chart of " + str(
                            ticker.info['longName']) + "&nbsp;&nbsp;<sub style='font-size: 25px;'>" +
                        str(ticker.info['symbol']) + "/" + str(ticker.info['financialCurrency']) + "</sub></h1>",
                        unsafe_allow_html=True)

                    data = yf.download(keyword, start=start_date, end=end_date,
                                       interval=interval_list2_dict[interval_select])

                    data = data.reset_index()
                    if graph_type == 'Candlesticks' or graph_type == 'OHLC':
                        fig = make_subplots(specs=[[{"secondary_y" : True}]])

                        # include candlestick with rangeselector
                        if graph_type=='Candlesticks':
                            fig.add_trace(go.Candlestick(x=data['Date'],
                                                         open=data['Open'], high=data['High'],
                                                         low=data['Low'], close=data['Close'], name='Rate'),
                                          secondary_y=True)
                        if graph_type=='OHLC':
                            fig.add_trace(go.Ohlc(x=data['Date'],
                                                         open=data['Open'], high=data['High'],
                                                         low=data['Low'], close=data['Close'], name='Rate'),
                                          secondary_y=True)

                        # include a go.Bar trace for volumes

                        fig.add_trace(go.Bar(x=data['Date'], y=data['Volume'], name='Volume', opacity=0.5),
                                      secondary_y=False)
                        fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators", font=dict(
                            family="Courier New, monospace",
                            size=18,
                            color="RebeccaPurple"
                        ))

                        fig.layout.yaxis2.showgrid = False
                        st.plotly_chart(fig)

                    if graph_type == 'Filled Area' :
                        data.rename(columns={'Close' : 'Rate'}, inplace=True)
                        fig = px.area(data, x='Date', y='Rate', template="ggplot2", )
                        fig.update_layout(autosize=False, width=1600, height=500, legend_title="Indicators", font=dict(
                            family="Courier New, monospace",
                            size=18,
                            color="RebeccaPurple"
                        ))
                        st.plotly_chart(fig)

                    if graph_type == 'Line' :
                        data.rename(columns={'Close' : 'Rate'}, inplace=True)
                        fig = make_subplots(specs=[[{"secondary_y" : True}]])

                        fig.add_trace(go.Scatter(x=data['Date'], y=data['Rate'], name='Rate'),
                                      secondary_y=True)

                        fig.add_trace(go.Bar(x=data['Date'], y=data['Volume'], name='Volume', opacity=0.5),
                                      secondary_y=False)

                        fig.update_layout(autosize=False, width=1600, height=800, legend_title="Indicators", font=dict(
                            family="Courier New, monospace",
                            size=18,
                            color="RebeccaPurple"
                        ))
                        fig.layout.yaxis2.showgrid = False
                        st.plotly_chart(fig)

                if function_select == 'Information' :
                    info = ticker.info

                    if info['logo_url'] != '' :
                        string_logo = '<img src=%s>' % info['logo_url']
                        st.markdown(string_logo, unsafe_allow_html=True)

                    string_name = info['longName']
                    st.title('**%s**' % string_name)

                    try :
                        st.info(info["longBusinessSummary"])
                    except :
                        pass
                    st.title('Basic Details ')
                    try :
                        st.markdown('<div style="color:green"><b >ZIP : </b>' + info['zip'] + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass

                    try :
                        st.markdown(
                            '<div style="color:green"><b >Full Time Employees : </b>' + str(
                                info['fullTimeEmployees']) + '</div>',
                            unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Sector : </b>' + info['sector'] + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Industry : </b>' + info['industry'] + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Address : </b>' + info['address1'] + ',' + info[
                            'address2'] + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        try :
                            st.markdown('<div style="color:green"><b >Address : </b>' + info['address1'] + '</div>',
                                        unsafe_allow_html=True)
                        except :
                            pass
                    try :
                        st.markdown('<div style="color:green"><b >City : </b>' + info['city'] + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    st.markdown('<div style="color:green"><b >Country : </b>' + info['country'] + '</div>',
                                unsafe_allow_html=True)

                    try :
                        st.markdown('<div style="color:green"><b >Phone : </b>' + str(info['phone']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try:
                        st.markdown('<div style="color:green"><b >Website : </b><a href="' + str(info['website']) + '">' + str(info['website']) + '</a></div>',
                                    unsafe_allow_html=True)

                    except:
                        pass

                    st.title('Share Details')
                    try :
                        st.markdown('<div style="color:green"><b >Exchange : </b>' + info['exchange'] + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Symbol : </b>' + info['symbol'] + '</div>',
                                    unsafe_allow_html=True)

                    except :
                        pass
                    try :
                        st.markdown(
                            '<div style="color:green"><b >Currency : </b>' + info['financialCurrency'] + '</div>',
                            unsafe_allow_html=True)

                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Type : </b>' + info['quoteType'] + '</div>',
                                    unsafe_allow_html=True)

                    except :
                        pass
                    try :
                        st.markdown(
                            '<div style="color:green"><b >Total Cash : </b>' + str(info['totalCash']) + '</div>',
                            unsafe_allow_html=True)

                    except :
                        pass
                    try :
                        st.markdown(
                            '<div style="color:green"><b >Total Debt : </b>' + str(info['totalDebt']) + '</div>',
                            unsafe_allow_html=True)

                    except :
                        pass
                    try :
                        st.markdown(
                            '<div style="color:green"><b >Total Revenue : </b>' + str(info['totalRevenue']) + '</div>',
                            unsafe_allow_html=True)

                    except :
                        pass
                    try :
                        st.markdown(
                            '<div style="color:green"><b >Market Cap : </b>' + str(info['marketCap']) + '</div>',
                            unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Total Cash Per Share : </b>' + str(
                            info['totalCashPerShare']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Revenue Per Share : </b>' + str(
                            info['revenuePerShare']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass

                    try :
                        st.markdown('<div style="color:green"><b >Shares Outstanding : </b>' + str(
                            info['sharesOutstanding']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Target Low : </b>' + str(
                            info['targetLowPrice']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Target High : </b>' + str(
                            info['targetHighPrice']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Recommendation : </b>' + str(
                            info['recommendationKey']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    st.title('Advance Details')

                    try :
                        st.markdown('<div style="color:green"><b >Operating Margins : </b>' + str(
                            info['operatingMargins']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Profit Margins : </b>' + str(
                            info['profitMargins']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Shares Outstanding : </b>' + str(
                            info['grossMargins']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Gross Profits : </b>' + str(
                            info['grossProfits']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Revenue Growth : </b>' + str(
                            info['revenueGrowth']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass
                    try :
                        st.markdown('<div style="color:green"><b >Earnings Growth : </b>' + str(
                            info['earningsGrowth']) + '</div>',
                                    unsafe_allow_html=True)
                    except :
                        pass




                if function_select == 'Dividend and Stock Splits' :
                    try:
                        st.table(ticker.actions.reset_index())
                    except:
                        st.info("This function information is not available for selected Symbol")

                if function_select == 'Financials' :
                    try:
                        st.table(ticker.financials.reset_index())
                    except:
                        st.info("This function information is not available for selected Symbol")

                if function_select == 'Major Holders' :
                    try:
                        st.table(ticker.major_holders)
                    except:
                        st.info("This function information is not available for selected Symbol")

                if function_select == 'Institutional Holders' :
                    try:
                        st.table(ticker.institutional_holders)
                    except:
                        st.info("This function information is not available for selected Symbol")

                if function_select == 'Balance sheet' :
                    try:
                        st.table(ticker.balance_sheet.reset_index())
                    except:
                        st.info("This function information is not available for selected Symbol")

                if function_select == 'Recommendations' :
                    try:
                        st.table(ticker.recommendations.reset_index())
                    except:
                        st.info("This function information is not available for selected Symbol")
                if function_select == 'Cashflow' :
                    try:
                        st.table(ticker.cashflow.reset_index())
                    except:
                        st.info("This function information is not available for selected Symbol")

                if function_select == 'Earnings' :
                    try:
                        st.table(ticker.earnings.reset_index())
                    except:
                        st.info("This function information is not available for selected Symbol")



        except Exception as e :
            st.warning('Either there is connection error or symbol/ticker is not found in our system')
            st.write(e)
    else:
        st.info('For Indian stocks only National Stock Exchange(NSE/NS) is supported for Bombay Stock Exchange(BSE/BS) select "Indian Stocks" option from sidebar ')

if radio_select == 'Prediction':
    st.title('Stock Forecast App')
    START = "2015-01-01"
    TODAY = datetime.date.today().strftime("%Y-%m-%d")

    st.title(radio_select)

    selected_stock = st.text_input("Search by Symbol/Ticker","AAPL")


    n_years = st.slider('Years of prediction:', 1, 4)
    period = n_years * 365


    @st.cache
    def load_data(ticker) :
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data


    data_load_state = st.text('Loading data...')
    data = load_data(selected_stock)
    data_load_state.text('Loading data... done!')

    namer=yf.Ticker(selected_stock).info['longName']




    # Predict forecast with Prophet.
    df_train = data[['Date', 'Close']]
    df_train = df_train.rename(columns={"Date" : "ds", "Close" : "y"})

    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)

    # Show and plot forecast


    st.write(f'Forecast plot for {n_years} years')
    st.title("Price prediction "+namer+"(" + selected_stock + ")")
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1)



st.write('')
st.warning('In case of any error try clicking rerun button on top left after 1 minute')
