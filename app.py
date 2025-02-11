import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Thenpandiyan Transport", page_icon="🚚", layout="wide")

st.title("🚚 Thenpandiyan Transport ")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file", type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_excel(fl)
else:
    os.chdir(r"X:/Projects/transport")
    df = pd.read_excel("March.xls")


date_columns=[col for col in df.columns if 'DATE' in col.upper()]

if len(date_columns)==0:
    st.error("no date columns found")
else:
    selected_date_column = date_columns[0]  # Selecting the first date column by default
    df[selected_date_column] = pd.to_datetime(df[selected_date_column])
    startDate = pd.to_datetime(df[selected_date_column]).min()
    endDate = pd.to_datetime(df[selected_date_column]).max()

    # Sidebar selection boxes
    with st.sidebar:
        st.sidebar.subheader("Filter Selection")
        st.sidebar.markdown("---")
        transporter = st.sidebar.multiselect("Select Transporter", ['--Select--'] + list(df["TRANSPORTER"].unique()))
        loading_location = st.sidebar.multiselect("Select Loading Location", ['--Select--'] + list(df["LOADING LOCATION"].unique()))
        inv_location = st.sidebar.multiselect("Select INV Location", ['--Select--'] + list(df["INV LOCATION"].unique()))
        payment_by = st.sidebar.multiselect("Select Payment By", ['--Select--'] + list(df["PAYMENT BY"].unique()))
    # Main window start and end date inputs
    col1,col2=st.columns(2)
    with col1:
        date1=st.date_input("Start Date",startDate)
    with col2:
        date2=st.date_input("End Date",endDate)
    # Filter the data based on selection
    filtered_df=df[
        (df["TRANSPORTER"].isin(transporter) if transporter and transporter[0] != "--Select--" else True) &
        (df["LOADING LOCATION"].isin(loading_location) if loading_location and loading_location[0] != "--Select--" else True) &
        (df["INV LOCATION"].isin(inv_location) if inv_location and inv_location[0] != "--Select--" else True) &
        (df["PAYMENT BY"].isin(payment_by) if payment_by and payment_by[0] != "--Select--" else True) &
        (df[selected_date_column] >= pd.to_datetime(date1)) &
        (df[selected_date_column] <= pd.to_datetime(date2))
    ]

    # Convert INV-QNT-KG to metric ton
    filtered_df['INV -QNT-MT']=filtered_df['INV-QNT-KG']/1000

    # Calculate total metric ton for each transporter
    transporter_metric_ton=filtered_df.groupby('TRANSPORTER').agg({'INV -QNT-MT': 'sum', 'INV -VALUE': 'sum'}).reset_index()

    # Pie chart for Transporter including metric ton
    st.subheader("Transporter Distribution by Quantity")
    fig_transporter_quantity=px.pie(transporter_metric_ton,names='TRANSPORTER',values='INV -QNT-MT',title='Transporter Distribution by Quantity')
    st.plotly_chart(fig_transporter_quantity,use_container_width=True)

    # Table for Transporter Distribution by Quantity
    transporter_quantity = transporter_metric_ton[['TRANSPORTER', 'INV -QNT-MT']].sort_values(by='INV -QNT-MT', ascending=False)
    st.write(transporter_quantity)

    # Pie chart for Transporter including amount
    st.subheader("Transporter Distribution by Amount")
    fig_transporter_amount = px.pie(transporter_metric_ton, names='TRANSPORTER', values='INV -VALUE', title='Transporter Distribution by Amount')
    st.plotly_chart(fig_transporter_amount, use_container_width=True)

    # Table for Transporter Distribution by Amount
    transporter_amount = transporter_metric_ton[['TRANSPORTER', 'INV -VALUE']].sort_values(by='INV -VALUE', ascending=False)
    st.write(transporter_amount)

    # Pie chart for Loading Location
    st.subheader("Loading Location Distribution")
    fig_loading_location = px.pie(filtered_df, names='LOADING LOCATION', title='Loading Location Distribution')
    st.plotly_chart(fig_loading_location, use_container_width=True)

    # Table for Loading Location Distribution
    loading_location_distribution = filtered_df['LOADING LOCATION'].value_counts().reset_index()
    loading_location_distribution.columns = ['Loading Location', 'Count']
    loading_location_distribution = loading_location_distribution.sort_values(by='Count', ascending=False)
    st.write(loading_location_distribution)

    # Pie chart for Payment By
    st.subheader("Payment By Distribution")
    fig_payment_by = px.pie(filtered_df, names='PAYMENT BY', title='Payment By Distribution')
    st.plotly_chart(fig_payment_by, use_container_width=True)

    # Table for Payment By Distribution
    payment_by_distribution = filtered_df['PAYMENT BY'].value_counts().reset_index()
    payment_by_distribution.columns = ['Payment By', 'Count']
    payment_by_distribution = payment_by_distribution.sort_values(by='Count', ascending=False)
    st.write(payment_by_distribution)

    # Display filtered data
    st.subheader("Filtered Data")
    st.write(filtered_df)

    # Calculate number of days for each trip for each vehicle
    df = df.sort_values(by=['VEHICLE NUMBER', 'INV -DATE'])
    df['Next INV Date'] = df.groupby('VEHICLE NUMBER')[selected_date_column].shift(-1)
    df['Days for Trip'] = (df['Next INV Date'] - df[selected_date_column]).dt.days

    # Table for Number of Days for Each Vehicle Trip
    days_for_trip_table = df[['VEHICLE NUMBER', selected_date_column, 'Next INV Date', 'Days for Trip']].dropna()
    st.subheader("Number of Days for Each Vehicle Trip")
    st.write(days_for_trip_table)

    # Key Metrics Section
    st.subheader("📊 Key Metrics")

    # Calculate key metrics
    total_trips = filtered_df.shape[0]  # Total number of trips
    total_metric_tons = filtered_df['INV -QNT-MT'].sum()  # Total metric tons
    total_invoice_value = filtered_df['INV -VALUE'].sum()  # Total invoice value

    # Display key metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Trips", value=f"{total_trips:,}")
    with col2:
        st.metric(label="Total Metric Tons", value=f"{total_metric_tons:,.2f} MT")
    with col3:
        st.metric(label="Total Invoice Value", value=f"${total_invoice_value:,.2f}")

    # Top 5 Vehicles with Highest Metric Tons Transported
    st.subheader("🏆 Top 5 Vehicles with Highest Metric Tons Transported")

    # Group by vehicle and calculate total metric tons
    top_vehicles = filtered_df.groupby('VEHICLE NUMBER')['INV -QNT-MT'].sum().reset_index()
    top_vehicles = top_vehicles.sort_values(by='INV -QNT-MT', ascending=False).head(5)  # Get top 5

    # Display the top 5 vehicles
    st.write(top_vehicles)

    # Optional: Add a bar chart for visualization
    fig_top_vehicles = px.bar(
        top_vehicles,
        x='VEHICLE NUMBER',
        y='INV -QNT-MT',
        title="Top 5 Vehicles by Metric Tons Transported",
        labels={'INV -QNT-MT': 'Metric Tons', 'VEHICLE NUMBER': 'Vehicle Number'}
    )
    st.plotly_chart(fig_top_vehicles, use_container_width=True)
    # Download filtered data
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Filtered Data', data=csv, file_name="Filtered_Data.csv", mime="text/csv")
