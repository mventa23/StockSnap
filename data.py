import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st
from decouple import config
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import base64

# Protect API Key
apikey = config("ALPHA_API_KEY")  # Using Alpha Advantage API for stock data retrieval
news_api_key = config("NEWS_API_KEY")

# Sidebar navigation
menu = st.sidebar.radio(
    "Navigate",
    ("Home", "Market Data", "News", "Market Insights"),
)
with open("logo.png", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")
    st.sidebar.markdown(
        f"""
        <div style="display:table;margin-top:-70%;margin-left:10%;text-align:center;">
            <img src="data:image/jpg;base64,{data}" width="200" height="50">
        </div>
        """,
        unsafe_allow_html=True,
    )
symbol = st.sidebar.text_input("Enter Stock Symbol:")

data = None

# Function to fetch and process stock data
def data_frame(url, time_series_key, button):
    if not symbol:
        st.error("Select a valid stock symbol.")
        return None
    response = requests.get(url)
    if response.status_code == 200:
        st.success("Data successfully retrieved for the selected stock symbol.")
        data = response.json()
        time_series = data.get(time_series_key, {})
        if not time_series:  # Check if time_series is empty
            st.error("No data available for the selected symbol and time frame.")
            return None

        # Create DataFrame from time_series
        df = pd.DataFrame.from_dict(time_series, orient="index")
        if df.empty or len(df.columns) != 5:  # Check if DataFrame has 5 columns
            st.error("Unexpected data structure returned by the API.")
            return None

        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.reset_index(inplace=True)
        df.rename(columns={"index": "Timestamp"}, inplace=True)
        end_date = datetime.now()

        # Apply filters based on the button clicked
        if button == 1:
            return df
        elif button == 2:
            start_date = end_date - relativedelta(days=30)
            return df[df["Timestamp"] >= start_date]
        elif button == 3:
            start_date = end_date - relativedelta(months=6)
            return df[df["Timestamp"] >= start_date]
        elif button == 4:
            start_date = end_date - relativedelta(years=1)
            return df[df["Timestamp"] >= start_date]
        elif button == 5:
            start_date = end_date - relativedelta(years=5)
            if df["Timestamp"].min() > start_date:
                st.error("Time period not available for selected symbol.")
                return None
            return df[df["Timestamp"] >= start_date]
        elif button == 6:
            start_date = end_date - relativedelta(years=10)
            if df["Timestamp"].min() > start_date:
                st.error("Time period not available for selected symbol.")
                return None
            return df[df["Timestamp"] >= start_date]
        elif button == 7:
            return df
    else:
        st.error("Error parsing data from API.")
        return None


# Function to plot stock data
def plot_data(df, symbol, start_date, end_date=None):
    title = f"{symbol} Closing Price {start_date}"
    if end_date:
        title += f" to {end_date}"
    fig = px.line(df, x="Timestamp", y="Close", title=title, labels={"Timestamp": "Timestamp", "Close": "Price"})
    st.plotly_chart(fig, use_container_width=True)
    st.info("Use the scroll bar on the x and y-axes to view all data.")
    st.info("Hover over peaks and dips to see specific prices and timestamps.")

# Home Section
if menu == "Home":
    st.title("📈 Welcome to the Stock Dashboard")
    st.subheader("Empowering You with Smarter Stock Insights")

    st.markdown(
        """
        Unlock the power of stock market insights with our easy-to-use tools:
        - **Market Data**: Dive deep into historical stock trends and visualize them interactively.
        - **News**: Stay informed with the latest financial updates and curated news.
        - **Market Insights**: Analyze sector performance and visualize opportunities.

        Navigate to these features using the sidebar or the buttons below!
        """
    )

    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Explore Market Data"):
            menu = "Market Data"  # Update the menu variable
    with col2:
        if st.button("View News"):
            menu = "News"  # Update the menu variable
    with col3:
        if st.button("Analyze Market Insights"):
            menu = "Market Insights"  # Update the menu variable

    # Footer with a motivational note
    st.markdown(
        """
        ---
        "Stay ahead in the market with smarter insights. Your journey begins here."
        """
    )





# Market Data Section
elif menu == "Market Data":
    st.header("Market Data")
    with st.container():
        b1, b2, b3, b4, b5, b6, b7 = st.columns([1, 1.2, 1.2, 0.9, 1.1, 1.1, 1])
        b1_button = b1.button("Latest")
        b2_button = b2.button("1 Month")
        b3_button = b3.button("6 Months")
        b4_button = b4.button("YTD")
        b5_button = b5.button("5 Years")
        b6_button = b6.button("10 Years")
        b7_button = b7.button("All Time")
    
    if b1_button:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={apikey}'
        time_series_key = "Time Series (5min)"
        data = data_frame(url, time_series_key, 1)
        if data is not None:
            start_date = pd.to_datetime(data["Timestamp"].iloc[0]).strftime("for %A %B %d, %Y")
            plot_data(data, symbol, start_date)
            st.markdown("### Data Table")
            st.dataframe(data)
    elif b2_button:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={apikey}'
        time_series_key = "Time Series (Daily)"
        data = data_frame(url, time_series_key, 2)
        if data is not None:
            end_date = datetime.now()
            start_date = end_date - relativedelta(days=30)
            plot_data(data, symbol, start_date.strftime("from %B %d, %Y"), end_date.strftime("%B %d, %Y"))
            st.markdown("### Data Table")
            st.dataframe(data)
    elif b3_button:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={apikey}'
        time_series_key = "Monthly Time Series"
        data = data_frame(url, time_series_key, 3)
        if data is not None:
            end_date = datetime.now()
            start_date = end_date - relativedelta(months=6)
            plot_data(data, symbol, start_date.strftime("from %B %d, %Y"), end_date.strftime("%B %d, %Y"))
            st.markdown("### Data Table")
            st.dataframe(data)
    elif b4_button:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={apikey}'
        time_series_key = "Monthly Time Series"
        data = data_frame(url, time_series_key, 4)
        if data is not None:
            end_date = datetime.now()
            start_date = end_date - relativedelta(years=1)
            plot_data(data, symbol, start_date.strftime("from %B %d, %Y"), end_date.strftime("%B %d, %Y"))
            st.markdown("### Data Table")
            st.dataframe(data)
    elif b5_button:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={apikey}'
        time_series_key = "Monthly Time Series"
        data = data_frame(url, time_series_key, 5)
        if data is not None:
            end_date = datetime.now()
            start_date = end_date - relativedelta(years=5)
            plot_data(data, symbol, start_date.strftime("from %B %d, %Y"), end_date.strftime("%B %d, %Y"))
            st.markdown("### Data Table")
            st.dataframe(data)
    elif b6_button:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={apikey}'
        time_series_key = "Monthly Time Series"
        data = data_frame(url, time_series_key, 6)
        if data is not None:
            end_date = datetime.now()
            start_date = end_date - relativedelta(years=10)
            plot_data(data, symbol, start_date.strftime("from %B %d, %Y"), end_date.strftime("%B %d, %Y"))
            st.markdown("### Data Table")
            st.dataframe(data)
    elif b7_button:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={apikey}'
        time_series_key = "Monthly Time Series"
        data = data_frame(url, time_series_key, 7)
        if data is not None:
            end_date = datetime.now()
            start_date = data["Timestamp"].min()
            plot_data(data, symbol, start_date.strftime("from %B %d, %Y"), end_date.strftime("%B %d, %Y"))
            st.markdown("### Data Table")
            st.dataframe(data)

# News Section
elif menu == "News":
    st.header("Finance News")
    news_url = f"https://newsapi.org/v2/top-headlines?country=us&category=business&q=finance&apiKey={news_api_key}"
    response = requests.get(news_url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        if articles:
            for article in articles[:5]:
                st.subheader(article.get("title", "No Title"))
                if article.get("urlToImage"):
                    st.image(article.get("urlToImage"), width=700)
                st.write(article.get("description", "No Description"))
                st.markdown(f"[Read More]({article.get('url', '#')})")
                st.markdown("---")
        else:
            st.info("No articles found.")
    else:
        st.warning("Failed to fetch news.")
        
    try:
        location_response = requests.get("https://ipinfo.io")
        if location_response.status_code == 200:
            location_data = location_response.json()
            loc = location_data.get("loc", "0,0").split(",")
            latitude, longitude = map(float, loc)
            st.write(f"Detected location: Latitude {latitude}, Longitude {longitude}")
            location_df = pd.DataFrame([{"latitude": latitude, "longitude": longitude}])
            st.map(location_df)
        else:
            st.warning("Failed to fetch location.")
    except requests.exceptions.RequestException as e:
        
        st.error(f"Error fetching location data: {e}")

# Market Insights Section

elif menu == "Market Insights":
    st.header("Market Insights")

    # Define stock symbols to analyze (update with your preferences)
    stock_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    def fetch_daily_data(symbol):
        """Fetch daily stock data for a given symbol using Alpha Vantage API."""
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={apikey}"
        response = requests.get(url)
        if response.status_code == 200:
            try:
                data = response.json()
                daily_data = data.get("Time Series (Daily)", {})
                if not daily_data:
                    return None
                df = pd.DataFrame.from_dict(daily_data, orient="index")
                df.columns = ["Open", "High", "Low", "Close", "Volume"]
                df = df.astype(float)
                df.index = pd.to_datetime(df.index)
                return df
            except Exception as e:
                st.error(f"Error processing data for {symbol}: {e}")
                return None
        else:
            st.error(f"Failed to fetch data for {symbol}. Status Code: {response.status_code}")
            return None

    # Analyze performance for each stock symbol
    performance_data = []
    for symbol in stock_symbols:
        stock_df = fetch_daily_data(symbol)
        if stock_df is not None:
            # Calculate daily percentage change
            latest_close = stock_df.iloc[0]["Close"]
            prev_close = stock_df.iloc[1]["Close"]
            percent_change = ((latest_close - prev_close) / prev_close) * 100
            performance_data.append({"Symbol": symbol, "Close": latest_close, "Change (%)": percent_change})

    # Create a DataFrame from performance data
    performance_df = pd.DataFrame(performance_data)

    if not performance_df.empty:
        # Sort by percentage change
        performance_df = performance_df.sort_values(by="Change (%)", ascending=False)

        # Display largest daily gainers
        st.write("### Largest Daily Gainers")
        st.table(performance_df.head(5))

        # Plot a bar chart of the top 5 gainers
        fig = px.bar(
            performance_df.head(5),
            x="Symbol",
            y="Change (%)",
            color="Change (%)",
            color_continuous_scale="Blues",
            title="Top 5 Largest Daily Gainers"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No stock performance data available.")