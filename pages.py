import numpy as np
import h5py
from plotly.tools import make_subplots
import streamlit as st
import plotly.graph_objects as go

def PVBESSDG(filename):
    f = h5py.File(filename,'r')
    start = f['input'].attrs['pv_start']
    end = f['input'].attrs['pv_end']
    delta = f['input'].attrs['pv_delta']
    g = f['output']

    BESS_charge =  np.zeros(shape=len(g))
    BESS_discharge = np.zeros(shape=len(g))
    DG_supply = np.zeros(shape=len(g))
    available_solar = np.zeros(shape=len(g))
    available_solar_for_BESS = np.zeros(shape=len(g))
    solar_to_load = np.zeros(shape=len(g))
    solar_pv_capacity = np.zeros(shape=len(g))
    solar_pv_curtailed = np.zeros(shape=len(g))
    installed_pv = np.zeros(shape=len(g))

    #Finance Parameters
    total_annual_cost = np.zeros(shape=len(g))
    energy_rate_over_crp = np.zeros(shape=len(g))
    effective_cost = np.zeros(shape=len(g))
    savings = np.zeros(shape=len(g))
    savings_pct = np.zeros(shape=len(g))

    # Constants
    total_energy = 24*50*365.0

    for i in range(len(g)):
        thisfolder = str(start + (i*delta))
        installed_pv[i] = start + (i*delta)
        BESS_charge[i] = g[thisfolder].attrs['BESS_charge']
        BESS_discharge[i] = g[thisfolder].attrs['BESS_discharge']
        DG_supply[i] = g[thisfolder].attrs['DG_supply']
        available_solar[i] = g[thisfolder].attrs['available_solar']
        available_solar_for_BESS[i] = g[thisfolder].attrs['available_solar_for_BESS']
        solar_to_load[i] = g[thisfolder].attrs['solar_to_load']
        solar_pv_capacity[i] = g[thisfolder].attrs['solar_pv_capacity']
        solar_pv_curtailed[i] = g[thisfolder].attrs['solar_pv_curtailed']
        financestring = 'output/'+thisfolder+'/finance'
        total_annual_cost[i] = f[financestring].attrs['total_annual_cost']
        energy_rate_over_crp[i] = f[financestring].attrs['energy_rate_over_crp']
        effective_cost[i] = f[financestring].attrs['effective_cost']
        savings[i] = f[financestring].attrs['savings']
        savings_pct[i]= f[financestring].attrs['savings_pct']
    def mainPlot():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=installed_pv, y=available_solar, name="Available Solar"))
        fig.add_trace(go.Scatter(x=installed_pv, y=available_solar_for_BESS, name="Available Solar for BESS"))
        fig.add_trace(go.Scatter(x=installed_pv, y=BESS_charge, name="BESS Charge"))
        fig.add_trace(go.Scatter(x=installed_pv, y=BESS_discharge, name="BESS Discharge"))
        fig.add_trace(go.Scatter(x=installed_pv, y=DG_supply, name="Diesel Generator Supplied"))
        fig.add_trace(go.Scatter(x=installed_pv, y=solar_pv_curtailed, name="Curtailed Energy from Solar PV"))
        fig.update_layout(
        xaxis_title='Installed PV Capacity (kW)',
        yaxis_title= 'Power (kW)',
        title = 'Chart 1. Configuration Performance',
        title_x = 0.5
        )
        return fig
    def pctPlot():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=installed_pv, y=(available_solar/available_solar)*100, name="Available Solar"))
        fig.add_trace(go.Scatter(x=installed_pv, y=(solar_to_load/available_solar)*100, name="Solar PV deployed to Load"))
        fig.add_trace(go.Scatter(x=installed_pv, y=(available_solar_for_BESS/available_solar)*100, name="Available Solar for BESS"))
        fig.add_trace(go.Scatter(x=installed_pv, y=(BESS_charge/available_solar)*100, name="BESS Charge"))
        fig.add_trace(go.Scatter(x=installed_pv, y=(BESS_discharge/available_solar)*100, name="BESS Discharge"))
        fig.add_trace(go.Scatter(x=installed_pv, y=(solar_pv_curtailed/available_solar)*100, name="Curtailed Energy from Solar PV"))
        fig.update_layout(
        xaxis_title='Installed PV Capacity (kW)',
        yaxis_title= 'Percentage (%)',
        title = 'Chart 2. Solar Energy Harvested',
        title_x = 0.5
        )
        return fig
    
    def pctBarPlot():
        fig = go.Figure()
        fig.add_trace(go.Bar(x=installed_pv, y=(solar_to_load/available_solar)*100, name="Solar PV deployed to Load"))
        fig.add_trace(go.Bar(x=installed_pv, y=(BESS_charge/available_solar)*100, name="BESS Charge"))
        fig.add_trace(go.Bar(x=installed_pv, y=(solar_pv_curtailed/available_solar)*100, name="Curtailed Energy from Solar PV"))
        fig.add_trace(go.Bar(x=installed_pv,y=(1-((solar_to_load/available_solar)+(BESS_charge/available_solar)+(solar_pv_curtailed/available_solar)))*100,name="Losses"))
        fig.update_layout(
        xaxis_title='Installed PV Capacity (kW)',
        yaxis_title= 'Percentage (%)',
        title = 'Chart 3. Solar Energy Harvested',
        title_x = 0.5,
        barmode='stack'
        )
        return fig
    
    def plotPls(y_data,y_label,title_label):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=installed_pv,y=y_data,mode='lines'))
        fig.update_layout(
            xaxis_title='Installed PV Capacity (kW)',
            yaxis_title=y_label,
            title = title_label,
            title_x = 0.5
        )
        return fig

    def supplyPlot():
        fig = go.Figure()
        fig.add_trace(go.Bar(x=installed_pv, y=solar_to_load/total_energy, name="Solar PV"))
        fig.add_trace(go.Bar(x=installed_pv, y=BESS_discharge/total_energy, name = "BESS"))
        fig.add_trace(go.Bar(x=installed_pv, y=DG_supply/total_energy, name="Diesel Generator"))
        fig.update_layout(
            xaxis_title='Installed PV Capacity (kW)',
            yaxis_title= "% Share",
            title = "Chart 4. Power supply by Source",
            title_x = 0.5,
            barmode='stack',
            height = 400,
        )
        return fig

    def financePlots():
        fig = make_subplots(rows=5,cols=1,shared_xaxes=True, subplot_titles=("Total Annual Cost", "Energy Rate of CAPEX Recovery Period","Effective Cost","Savings","% Savings"))
        fig.add_trace(go.Scatter(x=installed_pv, y=total_annual_cost,name="Total Annual Cost"),row=1,col=1)
        fig.add_trace(go.Scatter(x=installed_pv, y=energy_rate_over_crp),row=2,col=1)
        fig.add_trace(go.Scatter(x=installed_pv, y=effective_cost, name="Effective Cost"),row=3,col=1)
        fig.add_trace(go.Scatter(x=installed_pv, y=savings, name="Savings"),row=4,col=1)
        fig.add_trace(go.Scatter(x=installed_pv,y=savings_pct),row=5,col=1)

        fig.update_layout(
            xaxis5_title='Installed PV Capacity (kW)',
            yaxis_title= "Amount <br> (PhP)",
            yaxis2_title='Rate <br>(PhP/kWh)',
            yaxis3_title='Rate <br>(PhP/kWh)',
            yaxis4_title='Rate <br>(PhP/kWh)',
            yaxis5_title='Percentage<br>(%)',
            title = 'Chart 5. Financial Data',
            title_x = 0.5,
            showlegend = False,
            height=700,
        )
        return fig
    # Main Report body

    def reportBody():
        st.title('Case Study for Microgrid using Solar PV, BESS and Diesel Generator')
        st.header('Summary')
        st.markdown('This study aims to explore the performance of a microgrid setup consisting of Solar PV Installation (SPV), Battery Energy Storage System (BESS) and Diesel Generator (DG) for a customer with fixed energy demand. The SPV capacity was varied from 100-300kWp while maintaining constant BESS capacity (238kWh/100kW) and DG Capacity (50kW/h).<br><br> It was observed that the best utilization of the added SPV and BESS was at an installed capacity of 200 kWp. This configuration offered a 50% reduction in the usage of DG while offering the lowest Total Annual Cost and highest Savings for the customer.',unsafe_allow_html=True)
        # st.header('Simulation Parameters')
        # col1, col2 = st.beta_columns(2)
        # col1.subheader('Battery')
        # col1.markdown('Capacity: 238kWh/100kW')
        # col1.markdown('Round Trip Efficiency: 80%')
        # col1.markdown('Trial')
        # col2.subheader('Diesel Generator')
        # col2.markdown('Trial')
        # col2.markdown('Trial')
        
        st.header('Results')
        st.plotly_chart(mainPlot())
        st.plotly_chart(pctBarPlot())
        st.plotly_chart(pctPlot())
        st.plotly_chart(supplyPlot())
        st.plotly_chart(financePlots())

    reportBody()