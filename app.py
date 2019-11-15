# ~ author: Mohamad Al MDFAA
# ~ 19-10-2019

import streamlit as st
import pandas as pd 
import numpy as np 
import plotly.graph_objs as go 
import plotly_express as px 
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

data_url = 'leftsaver_data.csv'
global leftSaverData

def main():
    global leftSaverData

    leftSaverData = load_metadata(data_url)

    run_last_24_hours_service(leftSaverData.loc[leftSaverData.index.date == leftSaverData.index.date.max()])
    range_min = leftSaverData.index.date.max() - timedelta(days=7)
    run_last_7_days_service(leftSaverData[leftSaverData.index.date >= range_min])
    just_4_weeks_ago = leftSaverData.index.date.max() - timedelta(days=28)
    just_8_weeks_ago = leftSaverData.index.date.max() - timedelta(days=54)
    run_last_4_weeks_service(leftSaverData[leftSaverData.index.date >= just_4_weeks_ago], leftSaverData[(leftSaverData.index.date < just_4_weeks_ago) & (leftSaverData.index.date >= just_8_weeks_ago)])
    run_all_time_service(leftSaverData)
    
def run_last_24_hours_service(last_24_hours_data):
    st.title('LeftSaver')
    st.write('## Last 24 hours')
    values = last_24_hours_data.agg('sum')
    costs = calculate_cost(values)
    last_24_hours_data['overall_weight'] = last_24_hours_data.sum(axis=1)
    cost = sum(costs)

    st.write('### Wasted money: ${}'.format(int(cost)))
    stacked_bar_chart(last_24_hours_data, period='time')

    if st.checkbox("Raw data - Today"):    
        st.write(last_24_hours_data)

def run_last_7_days_service(last_7_days_data):
    st.write('## Last 7 days')
    values = last_7_days_data.agg('sum')
    costs = calculate_cost(values)

    last_7_days_data['overall_weight'] = last_7_days_data.sum(axis=1)

    cost = sum(costs)
    
    st.write('### Wasted money: ${}'.format(int(cost)))
    pie_chart(values, costs)

    if st.checkbox("Raw data - last 7 days "):
        st.write(last_7_days_data)


def run_last_4_weeks_service(last_4_weeks_data, previous_4_weeks_data):
    st.write('## Last 4 weeks')
    values = last_4_weeks_data.agg('sum')
    costs = calculate_cost(values)
    last_4_weeks_data['overall_weight'] = last_4_weeks_data.sum(axis=1)
    cost = sum(costs)
    st.write('### Wasted money: ${}'.format(int(cost)))

    line_chart_cost(last_4_weeks_data)
    previous_4_weeks_data['overall_weight'] = previous_4_weeks_data.sum(axis=1)
    line_chart_monthly_comparison(last_4_weeks_data, previous_4_weeks_data)

    if st.checkbox("Raw data - Last 4 weeks"):
        st.write(last_4_weeks_data)



def run_all_time_service(leftsaver_data):
    st.write('## All time')
    yearly_data = leftSaverData.resample('Y', convention='start').agg('sum')

    values = yearly_data.agg('sum')
    costs = calculate_cost(values)
    cost = sum(costs)
    st.write('### Wasted money: ${}'.format(int(cost)))
    yearly_data['overall_weight'] = yearly_data.sum(axis=1)
    line_chart(yearly_data)
    line_chart_cost(yearly_data)
    stacked_bar_chart(yearly_data)
    if st.checkbox("Raw data - All time"):
        st.write(leftSaverData)
    

@st.cache
def load_metadata(url):
    data = pd.read_csv(url)

    data['Date_Time'] = pd.to_datetime(data['Date_Time'])
    data.sort_values('Date_Time', inplace=True)
    data.set_index('Date_Time', inplace=True)

    return data


def stacked_bar_chart(x, period='year'):
    dff = x.Fruit
    trace2 = go.Bar(
        x=eval('dff.index.{}'.format(period)),
        y=dff,
        name='Fruit'
    )

    dff = x.Vegetables
    trace1 = go.Bar(
        x=eval('dff.index.{}'.format(period)),
        y=dff,
        name='Vegetables'
    )

    dff = x.Dessert
    trace4 = go.Bar(
        x=eval('dff.index.{}'.format(period)),
        y=dff,
        name='Dessert'
    )

    dff = x.Protein
    trace3 = go.Bar(
        x=eval('dff.index.{}'.format(period)),
        y=dff,
        name='Protein'
    )

    dff = x.Starch
    trace5 = go.Bar(
        x=eval('dff.index.{}'.format(period)),
        y=dff,
        name='Starch'
    )

    dff = x.Other
    trace6 = go.Bar(
        x=eval('dff.index.{}'.format(period)),
        y=dff,
        name='Other'
    )


    data = [trace1, trace2, trace3, trace4,trace5, trace6]
    layout = go.Layout(xaxis=dict(tickangle=0, showticklabels= True, type= 'category'), title='Category Overview',
        yaxis = dict(title = 'kg'), 
                    barmode='stack')

    fig = go.Figure(data=data, layout=layout)
    st.plotly_chart(fig)

def pie_chart(values, costs):
    labels = ["Vegetable", "Fruit", "Protein", "Dessert", "Strach", "Other"]

    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    fig.add_trace(go.Pie(labels=labels, values=values, name="Weight"),
                1, 1)
    fig.add_trace(go.Pie(labels=labels, values=costs, name="Cost"),
                 1, 2)
    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(
    title_text="Food waste - last 7 days",
    # Add annotations in the center of the donut pies.
    annotations=[dict(text='Weight', x=0.15, y=0.5, font_size=20, showarrow=False),
                 dict(text='Cost', x=0.82, y=0.5, font_size=20, showarrow=False)],
                 paper_bgcolor='rgba(0,0,0,0)',
                 plot_bgcolor = 'rgba(0,0,0,0)')

    st.plotly_chart(fig, filename='transparent-background')


def line_chart(x):
    dff = x.overall_weight
    trace1 = go.Scatter(x=dff.index, y=dff, mode='lines+markers', name='Overall weight (kg)')

    dff = x.Fruit
    trace2 = go.Scatter(x=dff.index, y=dff, mode='lines', name='Fruit waste (kg)')
    dff = x.Vegetables
    trace3 = go.Scatter(x=dff.index, y=dff, line=dict(dash='dot'), mode='lines', name='Vegetables waste (kg)')
    dff = x.Protein
    trace4 = go.Scatter(x=dff.index, y=dff, line=dict(dash='dash'), mode='lines', name='Protein waste (kg)')
    data = [trace1, trace2, trace3, trace4]
    st.plotly_chart(data)

def line_chart_cost(x):
    dff = x.overall_weight
    trace1 = go.Scatter(x=dff.index, y=dff, mode='lines+markers', name='Overall waste ($)')

    dff = x.Fruit
    trace2 = go.Scatter(x=dff.index, y=dff, mode='lines', name='Fruit waste ($)')
    dff = x.Vegetables
    trace3 = go.Scatter(x=dff.index, y=dff, line=dict(dash='dot'), mode='lines', name='Vegetables waste ($)')
    dff = x.Protein
    trace4 = go.Scatter(x=dff.index, y=dff, line=dict(dash='dash'), mode='lines', name='Protein waste ($)')
    data = [trace1, trace2, trace3, trace4]
    st.plotly_chart(data)

def line_chart_monthly_comparison(x, y):
    # TODO: this function just pick each row with index//4=0
    # we need to replace it with finding the mean of each N value came in a row 
    dff = x.overall_weight.iloc[0::4]
    trace1 = go.Scatter(x=dff.index, y=dff, mode='lines+markers', name='Overall weight (kg)')

    dff = y.overall_weight[0::4]
    trace2 = go.Scatter(x=dff.index, y=dff, mode='lines', name='Overall weight "previous month" (kg)')

    data = [trace2, trace1]
    st.plotly_chart(data)

def calculate_cost(values):
    return values*[9,21,30,36, 6, 15 ]



if __name__ == "__main__":
    main()
