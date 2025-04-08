import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Must be the first Streamlit command
st.set_page_config(page_title="Chinook Analysis", layout="wide")

def get_connection():
    return sqlite3.connect('Chinook_Sqlite.sqlite')

def load_data(query):
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)

# App title and description
st.title('Chinook Music Store Analysis Dashboard')

# Initialize analysis variable
analysis = None

# Create pages with radio buttons
if 'page' not in st.session_state:
    st.session_state.page = "Home"

page = st.session_state.page
page = st.sidebar.radio("Navigation", ["Home", "Analysis Dashboard"])

if page == "Home":
    # Home page content
    st.write("## Welcome to the Chinook Music Store Analysis Dashboard")
    
    st.markdown("""
    ### Project Objective
    This dashboard provides comprehensive analysis of the Chinook digital music store database, 
    answering key business questions to help optimize operations and increase revenue.
    
    ### About the Chinook Database
    The Chinook database represents a digital media store, including tables for artists, albums, 
    tracks, invoices, and customers. It's a real-world database that captures the business processes 
    of a digital media store.
    
    ### Key Analysis Areas
    - **Customer Analysis**: Understand customer demographics and purchasing patterns
    - **Sales Analysis**: Track revenue by country, time period, and sales agents
    - **Music Analysis**: Identify popular tracks, genres, and artists
    - **Employee Performance**: Evaluate sales support agent effectiveness
    
    ### How to Use This Dashboard
    1. Select "Analysis Dashboard" from the navigation menu
    2. Choose an analysis category from the dropdown
    3. Select a specific analysis to view visualizations and data tables
    
    ### Business Questions Addressed
    This dashboard answers 26 key business questions, including:
    - Which countries have the most customers?
    - What are the sales trends over time?
    - Who are the top-performing sales agents?
    - Which music genres and artists are most popular?
    """)
    
    # Display a sample of the database structure
    st.subheader("Database Schema Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Main Tables**")
        st.markdown("""
        - Customer
        - Employee
        - Invoice
        - InvoiceLine
        - Track
        - Album
        - Artist
        - Genre
        - MediaType
        - Playlist
        """)
    
    with col2:
        # Show a sample query result
        try:
            sample_query = """
            SELECT 
                (SELECT COUNT(*) FROM Customer) AS Customers,
                (SELECT COUNT(*) FROM Invoice) AS Invoices,
                (SELECT COUNT(*) FROM Track) AS Tracks,
                (SELECT COUNT(*) FROM Artist) AS Artists,
                (SELECT COUNT(*) FROM Album) AS Albums,
                (SELECT COUNT(*) FROM Genre) AS Genres
            """
            sample_data = load_data(sample_query)
            st.write("Database Statistics:")
            st.dataframe(sample_data)
        except Exception as e:
            st.error(f"Could not load sample data: {str(e)}")

else:  # Analysis Dashboard page
    st.write('Analysis of sales, customers, and music data from the Chinook database')
    
    # Sidebar with categories
    category = st.sidebar.selectbox(
        'Select Analysis Category',
        ['Customer Analysis', 'Sales Analysis', 'Music Analysis', 'Employee Performance']
    )
    
    # Rest of your existing code for the analysis dashboard
    if category == 'Customer Analysis':
        analysis = st.selectbox(
            'Select Analysis',
            ['Non-US Customers', 'Brazilian Customers', 'Brazilian Customer Invoices', 
             'Customer Distribution by Country']
        )
        
        if analysis == 'Non-US Customers':
            query = """
            SELECT FirstName || ' ' || LastName AS FullName, CustomerId, Country
            FROM Customer
            WHERE Country <> 'USA'
            """
        elif analysis == 'Brazilian Customers':
            query = """
            SELECT FirstName || ' ' || LastName AS FullName, CustomerId, Country
            FROM Customer
            WHERE Country = 'Brazil'
            """
        elif analysis == 'Brazilian Customer Invoices':
            query = """
            SELECT
                c.FirstName || ' ' || c.LastName AS FullName, 
                i.InvoiceId,
                i.InvoiceDate,
                i.BillingCountry
            FROM
                Customer c 
            JOIN
                Invoice i ON c.CustomerId = i.CustomerId
            WHERE
                c.Country = 'Brazil'
            """
        elif analysis == 'Customer Distribution by Country':
            query = """
            SELECT Country, COUNT(*) as CustomerCount
            FROM Customer
            GROUP BY Country
            ORDER BY CustomerCount DESC
            """
    
    elif category == 'Sales Analysis':
        analysis = st.selectbox(
            'Select Analysis',
            ['Sales by Country', 'Sales by Year', 'Invoice Details', 
             'Items per Invoice', 'Sales by Agent 2009', 'Sales by Agent 2010',
             'Best Global Sales Agent']
        )
        
        if analysis == 'Sales by Country':
            query = """
            SELECT i.BillingCountry AS Country,
                SUM(i.Total) AS TotalSales 
            FROM Invoice i 
            GROUP BY i.BillingCountry
            ORDER BY TotalSales DESC
            """
        elif analysis == 'Items per Invoice':
            query = """
            SELECT i.InvoiceId, COUNT(il.InvoiceLineId) AS NumberOfItems 
            FROM Invoice i 
            JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId 
            GROUP BY i.InvoiceId
            ORDER BY i.InvoiceId
            """
        elif analysis == 'Sales by Agent 2010':
            query = """
            SELECT 
                e.FirstName || ' ' || e.LastName AS SalesAgent,
                SUM(i.Total) AS TotalSales
            FROM Employee e
            JOIN Customer c ON e.EmployeeId = c.SupportRepId
            JOIN Invoice i ON c.CustomerId = i.CustomerId
            WHERE strftime('%Y', i.InvoiceDate) = '2010'
            GROUP BY SalesAgent
            ORDER BY TotalSales DESC
            """
        elif analysis == 'Best Global Sales Agent':
            query = """
            SELECT e.FirstName || ' ' || e.LastName AS SalesAgent,
                SUM(i.Total) AS TotalSales
            FROM Employee e
            JOIN Customer c ON e.EmployeeId = c.SupportRepId
            JOIN Invoice i ON c.CustomerId = i.CustomerId
            GROUP BY SalesAgent
            ORDER BY TotalSales DESC
            LIMIT 1
            """
        elif analysis == 'Sales by Year':
            query = """
            SELECT
                strftime('%Y', InvoiceDate) AS InvoiceYear,
                COUNT(InvoiceID) AS TotalInvoices,
                ROUND(SUM(Total), 2) AS TotalSale
            FROM Invoice
            GROUP BY InvoiceYear
            ORDER BY InvoiceYear
            """
        elif analysis == 'Invoice Details':
            query = """
            SELECT
                i.InvoiceId,
                c.FirstName || ' ' || c.LastName AS CustomerName,
                i.BillingCountry,
                e.FirstName || ' ' || e.LastName AS SalesAgent,
                ROUND(SUM(il.Quantity * il.UnitPrice), 2) AS TotalAmount
            FROM Invoice i 
            JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
            JOIN Customer c ON i.CustomerId = c.CustomerId
            JOIN Employee e ON c.SupportRepId = e.EmployeeId
            GROUP BY i.InvoiceId
            """
        elif analysis == 'Sales by Agent 2009':
            query = """
            SELECT 
                e.FirstName || ' ' || e.LastName AS SalesAgent,
                ROUND(SUM(i.Total), 2) AS TotalSales
            FROM Employee e
            JOIN Customer c ON e.EmployeeId = c.SupportRepId
            JOIN Invoice i ON c.CustomerId = i.CustomerId
            WHERE strftime('%Y', i.InvoiceDate) = '2009'
            GROUP BY SalesAgent
            ORDER BY TotalSales DESC
            """
    
    elif category == 'Music Analysis':
        analysis = st.selectbox(
            'Select Analysis',
            ['Top Tracks', 'Tracks by Genre', 'Most Popular Artists',
             'Tracks per Playlist', 'Media Types', 'Most Purchased Track 2013',
             'Top 5 Tracks All Time']
        )
        
        if analysis == 'Top Tracks':
            query = """
            SELECT t.Name as TrackName, 
                COUNT(il.TrackId) as PurchaseCount,
                ROUND(SUM(il.UnitPrice * il.Quantity), 2) as TotalRevenue
            FROM InvoiceLine il
            JOIN Track t ON il.TrackId = t.TrackId
            GROUP BY t.TrackId
            ORDER BY PurchaseCount DESC
            LIMIT 10
            """
        elif analysis == 'Tracks per Playlist':
            query = """
            SELECT p.Name AS PlaylistName, COUNT(pt.TrackId) AS NumberOfTracks
            FROM Playlist p
            JOIN PlaylistTrack pt ON p.PlaylistId = pt.PlaylistId
            GROUP BY p.PlaylistId, p.Name
            ORDER BY NumberOfTracks DESC
            """
        elif analysis == 'Media Types':
            query = """
            SELECT mt.Name AS MediaType, COUNT(t.TrackId) AS TrackCount
            FROM Track t
            JOIN MediaType mt ON t.MediaTypeId = mt.MediaTypeId
            GROUP BY mt.MediaTypeId
            ORDER BY TrackCount DESC
            """
        elif analysis == 'Top 5 Tracks All Time':
            query = """
            SELECT t.Name AS TrackName, COUNT(il.TrackId) AS PurchaseCount
            FROM InvoiceLine il
            JOIN Track t ON il.TrackId = t.TrackId
            GROUP BY t.TrackId, t.Name
            ORDER BY PurchaseCount DESC
            LIMIT 5
            """
        elif analysis == 'Most Popular Artists':
            query = """
            SELECT ar.Name AS Artist, COUNT(il.TrackId) AS TracksSold
            FROM InvoiceLine il
            JOIN Track t ON il.TrackId = t.TrackId
            JOIN Album al ON t.AlbumId = al.AlbumId
            JOIN Artist ar ON al.ArtistId = ar.ArtistId
            GROUP BY ar.ArtistId
            ORDER BY TracksSold DESC
            LIMIT 10
            """
        elif analysis == 'Tracks by Genre':
            query = """
            SELECT g.Name as Genre, COUNT(*) as TrackCount
            FROM Track t
            JOIN Genre g ON t.GenreId = g.GenreId
            GROUP BY g.GenreId
            ORDER BY TrackCount DESC
            """
        elif analysis == 'Most Purchased Track 2013':
            query = """
            SELECT 
                t.Name AS TrackName, 
                COUNT(il.TrackId) AS PurchaseCount
            FROM InvoiceLine il
            JOIN Track t ON il.TrackId = t.TrackId
            JOIN Invoice i ON il.InvoiceId = i.InvoiceId
            WHERE strftime('%Y', i.InvoiceDate) = '2013'
            GROUP BY t.TrackId, t.Name
            ORDER BY PurchaseCount DESC
            LIMIT 1
            """
    
    elif category == 'Employee Performance':
        analysis = st.selectbox(
            'Select Analysis',
            ['Sales Support Agents', 'Best Performing Agents', 
             'Sales by Agent', 'Customers per Agent']
        )
        
        if analysis == 'Sales by Agent':
            query = """
            SELECT e.FirstName || ' ' || e.LastName AS SalesAgent,
                SUM(i.Total) AS TotalSales
            FROM Employee e 
            JOIN Customer c ON e.EmployeeId = c.SupportRepId
            JOIN Invoice i ON c.CustomerId = i.CustomerId
            GROUP BY SalesAgent
            ORDER BY TotalSales DESC
            """
        elif analysis == 'Customers per Agent':
            query = """
            SELECT e.FirstName || ' ' || e.LastName AS SalesAgent,
                COUNT(c.CustomerId) AS NumberOfClients
            FROM Employee e
            JOIN Customer c ON e.EmployeeId = c.SupportRepId
            GROUP BY SalesAgent
            ORDER BY NumberOfClients DESC
            """
        elif analysis == 'Best Performing Agents':
            query = """
            SELECT e.FirstName || ' ' || e.LastName AS SalesAgent,
                COUNT(DISTINCT c.CustomerId) AS ClientCount,
                COUNT(i.InvoiceId) AS InvoiceCount,
                ROUND(SUM(i.Total), 2) AS TotalSales
            FROM Employee e
            JOIN Customer c ON e.EmployeeId = c.SupportRepId
            JOIN Invoice i ON c.CustomerId = i.CustomerId
            WHERE e.Title = 'Sales Support Agent'
            GROUP BY e.EmployeeId
            ORDER BY TotalSales DESC
            """
        elif analysis == 'Sales Support Agents':
            query = """
            SELECT FirstName || ' ' || LastName AS FullName,
                   Title
            FROM Employee
            WHERE Title = 'Sales Support Agent'
            """

# Execute query and display results
try:
    data = load_data(query)
    st.write(f"## {analysis}")
    
    # Display visualization based on analysis type
    if len(data) == 0:
        st.warning("No data found for this query.")
    else:
        # Customer Analysis visualizations
        if analysis == 'Customer Distribution by Country':
            fig = px.pie(data, values='CustomerCount', names='Country', 
                         title='Customer Distribution by Country',
                         hole=0.4)
            st.plotly_chart(fig)
            
            # Also show a bar chart for comparison
            fig2 = px.bar(data.head(10), x='Country', y='CustomerCount',
                         title='Top 10 Countries by Customer Count')
            st.plotly_chart(fig2)
            
        # Sales Analysis visualizations
        elif analysis == 'Sales by Country':
            fig = px.choropleth(data, locations='Country', 
                               locationmode='country names',
                               color='TotalSales', 
                               hover_name='Country',
                               title='Global Sales Distribution',
                               color_continuous_scale='Viridis')
            st.plotly_chart(fig)
            
            # Add a bar chart for top countries
            fig2 = px.bar(data.head(10), x='Country', y='TotalSales',
                         title='Top 10 Countries by Sales')
            st.plotly_chart(fig2)
            
        elif analysis == 'Sales by Year':
            fig = px.line(data, x='InvoiceYear', y='TotalSale', 
                         markers=True, 
                         title='Sales Trend by Year')
            fig.update_layout(xaxis_title='Year', yaxis_title='Total Sales ($)')
            st.plotly_chart(fig)
            
            # Add a bar chart showing invoice counts
            fig2 = px.bar(data, x='InvoiceYear', y='TotalInvoices',
                         title='Number of Invoices by Year')
            st.plotly_chart(fig2)
            
        elif analysis == 'Items per Invoice':
            fig = px.histogram(data, x='NumberOfItems',
                              title='Distribution of Items per Invoice',
                              nbins=20)
            st.plotly_chart(fig)
            
        # Music Analysis visualizations
        elif analysis == 'Top Tracks':
            fig = px.bar(data.head(10), x='TrackName', y='PurchaseCount',
                        title='Top 10 Tracks by Purchase Count')
            fig.update_layout(xaxis_title='Track', yaxis_title='Purchase Count')
            st.plotly_chart(fig)
            
        elif analysis == 'Tracks by Genre':
            fig = px.pie(data, values='TrackCount', names='Genre',
                        title='Track Distribution by Genre')
            st.plotly_chart(fig)
            
        elif analysis == 'Most Popular Artists':
            fig = px.bar(data.head(10), x='Artist', y='TracksSold',
                        title='Top 10 Artists by Tracks Sold')
            fig.update_layout(xaxis_title='Artist', yaxis_title='Tracks Sold')
            st.plotly_chart(fig)
            
        elif analysis == 'Media Types':
            fig = px.pie(data, values='TrackCount', names='MediaType',
                        title='Track Distribution by Media Type')
            st.plotly_chart(fig)
            
        # Employee Performance visualizations
        elif analysis == 'Sales by Agent':
            fig = px.bar(data, x='SalesAgent', y='TotalSales',
                        title='Sales Performance by Agent')
            fig.update_layout(xaxis_title='Sales Agent', yaxis_title='Total Sales ($)')
            st.plotly_chart(fig)
            
        elif analysis == 'Customers per Agent':
            fig = px.bar(data, x='SalesAgent', y='NumberOfClients',
                        title='Number of Clients per Sales Agent')
            st.plotly_chart(fig)
            
        elif analysis == 'Best Performing Agents':
            # Create a multi-metric visualization
            fig = px.bar(data, x='SalesAgent', y=['ClientCount', 'InvoiceCount'],
                        title='Agent Performance Metrics',
                        barmode='group')
            st.plotly_chart(fig)
            
            # Add a separate chart for sales
            fig2 = px.bar(data, x='SalesAgent', y='TotalSales',
                         title='Total Sales by Agent')
            st.plotly_chart(fig2)
            
        # Default visualization for other analyses
        elif 'Revenue' in data.columns or 'TotalRevenue' in data.columns or 'TotalSales' in data.columns:
            # Determine which column to use
            if 'TotalRevenue' in data.columns:
                value_col = 'TotalRevenue'
            elif 'Revenue' in data.columns:
                value_col = 'Revenue'
            else:
                value_col = 'TotalSales'
                
            fig = px.bar(data, x=data.columns[0], y=value_col,
                        title=f'{analysis} - Revenue Analysis')
            st.plotly_chart(fig)
            
        elif any(col in data.columns for col in ['Count', 'NumberOfSales', 'PurchaseCount', 'TrackCount']):
            # Find the count column
            count_cols = [col for col in data.columns if col in ['Count', 'NumberOfSales', 'PurchaseCount', 'TrackCount']]
            if count_cols:
                count_col = count_cols[0]
                fig = px.bar(data, x=data.columns[0], y=count_col,
                            title=f'{analysis} - Count Analysis')
                st.plotly_chart(fig)
        
        # Add insights section for key analyses
        if analysis in ['Sales by Country', 'Customer Distribution by Country', 'Top Tracks', 'Sales by Agent']:
            st.subheader("Key Insights")
            
            if analysis == 'Sales by Country':
                top_country = data.iloc[0]['Country']
                top_sales = data.iloc[0]['TotalSales']
                st.info(f"📊 The highest revenue comes from {top_country} with ${top_sales:.2f} in sales.")
                st.info(f"🌍 The top 3 countries represent {data.head(3)['TotalSales'].sum() / data['TotalSales'].sum():.1%} of total sales.")
                
            elif analysis == 'Customer Distribution by Country':
                top_country = data.iloc[0]['Country']
                top_count = data.iloc[0]['CustomerCount']
                total = data['CustomerCount'].sum()
                st.info(f"👥 Most customers are from {top_country} ({top_count} customers, {top_count/total:.1%} of total).")
                
            elif analysis == 'Top Tracks':
                top_track = data.iloc[0]['TrackName']
                top_count = data.iloc[0]['PurchaseCount']
                st.info(f"🎵 The most purchased track is '{top_track}' with {top_count} purchases.")
                
            elif analysis == 'Sales by Agent':
                top_agent = data.iloc[0]['SalesAgent']
                top_sales = data.iloc[0]['TotalSales']
                st.info(f"🏆 The top performing sales agent is {top_agent} with ${top_sales:.2f} in sales.")
        
        # Always display the data table
        st.subheader("Data Table")
        st.dataframe(data)
        
        # Add download button for data
        csv = data.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'{analysis.lower().replace(" ", "_")}.csv',
            mime='text/csv',
        )
    
except Exception as e:
    st.error(f"Error executing query for {analysis}: {str(e)}")
    st.write("Please check the database connection and query syntax.")