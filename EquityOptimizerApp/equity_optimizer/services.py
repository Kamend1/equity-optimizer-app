import os
import random
from datetime import datetime

import yfinance as yf
import numpy as np
from EquityOptimizerApp.equity_optimizer.models import Stock, StockData
from django.db import transaction
from django.db.models import Q, Count, Max
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
import cufflinks as cf
from plotly.offline import plot
import time
import json
from .utils import percentage_return_classifier
from .. import settings


def check_stock_exists(ticker):
    """
    Checks if a stock with the given ticker already exists in the Stock model.
    """
    return Stock.objects.filter(ticker=ticker).exists()


def add_stock_to_db(ticker):
    """
    Adds a new stock to the Stock model.
    """
    stock_data = yf.Ticker(ticker)
    info = stock_data.info

    if not stock_data:
        raise ValueError("No data returned from yfinance.")

    # Add stock to the Stock model
    stock = Stock.objects.create(
        ticker=ticker,
        name=info.get('shortName', ''),
        sector=info.get('sector', ''),

        # Assigning financial details to the model fields
        market_cap=info.get('marketCap'),
        enterprise_value=info.get('enterpriseValue'),
        trailing_pe=info.get('trailingPE'),
        forward_pe=info.get('forwardPE'),
        peg_ratio=info.get('pegRatio'),
        price_to_book=info.get('priceToBook'),
        profit_margin=info.get('profitMargins'),
        operating_margin=info.get('operatingMargins'),

        revenue=info.get('totalRevenue'),
        gross_profit=info.get('grossProfits'),
        ebitda=info.get('ebitda'),
        net_income=info.get('netIncome'),
        diluted_eps=info.get('dilutedEPSTTM'),

        total_cash=info.get('totalCash'),
        total_debt=info.get('totalDebt'),
        total_assets=info.get('totalAssets'),
        total_liabilities=info.get('totalLiab'),

        dividend_yield=info.get('dividendYield') if info.get('dividendYield') is not None else 0,
        dividend_rate=info.get('dividendRate') if info.get('dividendRate') is not None else 0,
        payout_ratio=info.get('payoutRatio') if info.get('payoutRatio') is not None else 0,

        beta=info.get('beta'),
        fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
        fifty_two_week_low=info.get('fiftyTwoWeekLow'),
        average_daily_volume=info.get('averageVolume')
    )

    return stock


def download_and_save_stock_data(stock, start_date='2010-01-01', end_date=None):
    """
    Downloads historical stock data using yfinance, calculates daily returns and trends,
    cleans up NaN values, and saves it to the StockData model.
    """
    # Download historical data
    data = yf.download(stock.ticker, start=start_date, end=end_date, interval='1d')

    if data.empty:
        raise ValueError("No data returned from yfinance.")

    # Add necessary columns for calculations
    data['daily_return'] = 0.0
    data['trend'] = 'No Data'

    # Calculate daily returns
    data['daily_return'] = data['Adj Close'].pct_change() * 100

    # Calculate trends
    data['trend'] = data['daily_return'].apply(percentage_return_classifier)

    # Remove rows with NaN values in key columns
    data.replace(np.nan, 0, inplace=True)

    # Optional: Fill NaN values in other columns if needed
    # data.fillna({'Open': 0, 'High': 0, 'Low': 0, 'Close': 0, 'Volume': 0}, inplace=True)

    # Reset index to get date as a column
    data.reset_index(inplace=True)

    # Create StockData instances from DataFrame
    stock_data_objects = [
        StockData(
            stock=stock,
            date=row['Date'],
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
            adj_close=row['Adj Close'],
            volume=row['Volume'],
            daily_return=row['daily_return'],
            trend=row['trend']
        )
        for _, row in data.iterrows()
    ]

    # Use transaction.atomic to ensure the bulk insert is done in a single transaction
    with transaction.atomic():
        StockData.objects.bulk_create(stock_data_objects, batch_size=1000)


def get_filtered_stocks(query):
    """Return stocks filtered by the given query."""
    return Stock.objects.filter(
        Q(ticker__icontains=query) |
        Q(name__icontains=query) |
        Q(sector__icontains=query)
    ).order_by('ticker')


def get_stock_by_ticker(ticker):
    """Return a stock instance by its ticker."""
    return Stock.objects.get(ticker=ticker)


def get_stock_data_by_ticker(ticker, start_date, end_date):
    """
    Get stock data for a given ticker within a specified date range.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: A DataFrame containing stock data.
    """
    # Fetch stock data within the specified date range
    stock_data = StockData.objects.filter(
        stock__ticker=ticker,
        date__range=[start_date, end_date]
    ).values('date', 'open', 'high', 'low', 'close', 'adj_close', 'volume', 'daily_return').order_by('date')

    # Convert QuerySet to DataFrame
    df = pd.DataFrame(list(stock_data))

    # Check if DataFrame is empty
    if df.empty:
        raise ValueError("No data available for the given ticker and date range.")

    # Ensure 'date' column is converted to datetime and set as index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    return df


def plot_financial_data(df, title):
    """
    Generate a line plot for financial data.

    Args:
        df (pd.DataFrame): DataFrame containing financial data with 'date' as index.
        title (str): Title for the plot.

    Returns:
        str: HTML representation of the plotly figure.
    """

    # Create the figure with the title
    # fig = px.line(df, title=title)
    fig = go.Figure()

    # Loop over all columns to plot them
    for i in df.columns[0:]:
        fig.add_scatter(x=df.index, y=df[i], name=i)
        fig.update_traces(line_width=5)

    # Customize layout
    fig.update_layout({
        'plot_bgcolor': 'white',
        'xaxis_title': 'Date',
        'yaxis_title': 'Value',
    })

    # Return the figure's HTML representation
    return fig.to_html(full_html=False)


def get_trend_summary(ticker, start_date, end_date):
    """
    Get a summary of trends for a given stock within a specified date range.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: A DataFrame summarizing the trend counts.
    """
    stock = Stock.objects.filter(ticker=ticker).first()

    # Filter the StockData by stock and the date range
    trend_summary = StockData.objects.filter(
        stock=stock,
        date__range=[start_date, end_date]
    ).values('trend').annotate(count=Count('trend'))

    # Convert QuerySet to DataFrame
    trend_summary_df = pd.DataFrame(list(trend_summary))

    return trend_summary_df


def generate_trend_pie_chart(trend_summary_df):
    """
    Generates a pie chart for trend distribution and returns it as a base64-encoded string.

    Args:
        trend_summary_df (pandas.DataFrame): DataFrame containing trend counts.

    Returns:
        str: Base64-encoded string of the generated pie chart.
    """
    # Generate the trend pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(trend_summary_df['count'], labels=trend_summary_df['trend'], autopct='%1.1f%%')
    # plt.title('Trend Distribution')

    # Save the plot to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_png = buf.getvalue()
    buf.close()

    # Convert the image to base64
    trend_chart = base64.b64encode(image_png).decode('utf-8')

    return trend_chart


def generate_color_string(r, g, b, a=1.0):
    """
    Generate a valid RGBA color string from given values.

    Args:
        r (int): Red component (0-255).
        g (int): Green component (0-255).
        b (int): Blue component (0-255).
        a (float): Alpha (opacity) component (0.0 - 1.0).

    Returns:
        str: RGBA color string.
    """
    # Construct the RGBA color string
    return f'rgba({r}, {g}, {b}, {a})'

# def generate_candlestick_chart(df, title, sma_periods=[30, 100], add_bollinger_bands=True):
#     """
#     Generate a candlestick chart with optional moving averages and Bollinger bands.
#     """
#     # Initialize the QuantFig object with the stock data
#     figure = cf.QuantFig(df, title=title, name='Candlestick')
#
#     # Add moving averages without specifying colors
#     sma_colors = [generate_color_string(255, 0, 0), generate_color_string(0, 255, 0)]
#     figure.add_sma(periods=sma_periods, column='close', colors=sma_colors)
#
#     # Add Bollinger bands if specified
#     if add_bollinger_bands:
#         figure.add_bollinger_bands(periods=20, boll_std=2, column='close')
#
#     # Generate the figure with specified up and down colors
#     candlestick_fig = figure.iplot(asFigure=True, up_color=generate_color_string(0, 255, 0), down_color=generate_color_string(255, 0, 0))
#
#     # Return the HTML representation of the figure
#     return candlestick_fig.to_html(full_html=False)
#


def generate_candlestick_chart(df, title, sma_periods=[30, 100], add_bollinger_bands=True):
    """
    Generate a candlestick chart with optional moving averages and Bollinger bands.
    """
    fig = go.Figure()

    # Add candlestick trace
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlestick',
    ))

    # Add moving averages
    for period in sma_periods:
        df[f'SMA_{period}'] = df['close'].rolling(window=period).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[f'SMA_{period}'],
            mode='lines',
            name=f'SMA {period}',
            line=dict(width=2, color=generate_color_string(255, 153, 51))  # Color without alpha for SMA lines
        ))

    # Add Bollinger bands if specified
    if add_bollinger_bands:
        df['mean'] = df['close'].rolling(window=20).mean()
        df['std'] = df['close'].rolling(window=20).std()
        df['upper_band'] = df['mean'] + (df['std'] * 2)
        df['lower_band'] = df['mean'] - (df['std'] * 2)

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['upper_band'],
            mode='lines',
            name='Bollinger Upper Band',
            line=dict(color=generate_color_string(255, 0, 0, 0.2))  # Alpha included for Bollinger bands
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['lower_band'],
            mode='lines',
            name='Bollinger Lower Band',
            line=dict(color=generate_color_string(0, 255, 0, 0.2))  # Alpha included for Bollinger bands
        ))

    # Customize layout
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_white'  # Use a valid Plotly theme here
    )

    # Return the HTML representation of the figure
    return fig.to_html(full_html=False)


def generate_histogram_chart(df, title='Histogram of Daily Returns'):
    """
    Generate a histogram chart of daily returns.

    Args:
        df (pd.DataFrame): DataFrame containing daily returns data.
        title (str): Title for the chart.

    Returns:
        str: HTML representation of the plotly figure.
    """
    # Create the histogram
    fig = px.histogram(df, x='daily_return', title=title)

    # Update the layout
    fig.update_layout(
        plot_bgcolor='white',  # Set the plot background color to white
        xaxis_title='Daily Returns',
        yaxis_title='Frequency',
        title_text=title,
        title_x=0.5  # Center the title
    )

    # Return the HTML representation of the figure
    return fig.to_html(full_html=False)


def generate_portfolio_weights(n):
    # Generate a list of random weights
    weights = [random.random() for _ in range(n)]

    # Convert the list to a NumPy array for vectorized operations
    weights = np.array(weights)

    # Normalize weights to ensure they sum up to 1
    weights /= np.sum(weights)

    return weights


def price_scaling(raw_prices_df):
    # Ensure the DataFrame is working with floating-point numbers
    scaled_prices_df = raw_prices_df.copy()  # Create a copy to avoid modifying the original DataFrame

    # Convert all columns to float (except 'Date' if it's present)
    for column in raw_prices_df.columns[1:]:
        raw_prices_df[column] = raw_prices_df[column].astype(float)

    # Scale prices
    for column in raw_prices_df.columns[1:]:
        scaled_prices_df[column] = raw_prices_df[column]/raw_prices_df[column][0]

    return scaled_prices_df


def asset_allocation(df, weights, initial_investment):
    portfolio_df = df.copy()

    # Scale stock prices using the "price_scaling" function that we defined earlier (Make them all start at 1)
    scaled_df = price_scaling(df)


    for i, stock in enumerate(scaled_df.columns[1:]):
        portfolio_df[stock] = scaled_df[stock] * weights[i] * initial_investment

    # Sum up all values and place the result in a new column titled "portfolio value [$]"
    # Note that we excluded the date column from this calculation

    portfolio_df['Portfolio Value [$]'] = portfolio_df[portfolio_df != 'date'].sum(axis=1, numeric_only=True)
    # Calculate the portfolio percentage daily return and replace NaNs with zeros
    portfolio_df['Portfolio Daily Return [%]'] = portfolio_df['Portfolio Value [$]'].pct_change(1) * 100
    portfolio_df.replace(np.nan, 0, inplace=True)

    return portfolio_df


def simulation_engine(close_price_df, weights, initial_investment, risk_free_rate):
    # Perform asset allocation using the random weights (sent as arguments to the function)
    try:
        portfolio_df = asset_allocation(close_price_df, weights, initial_investment)
    except Exception as e:
        print(f"Error during asset allocation calculation: {e}")
        raise  # Re-raise to ensure error propagation

    # Calculate the return on the investment
    # Return on investment is calculated using the last final value of the portfolio compared to its initial value

    try:
        return_on_investment = ((portfolio_df['Portfolio Value [$]'][-1:] -
                             portfolio_df['Portfolio Value [$]'][0]) /
                            portfolio_df['Portfolio Value [$]'][0]) * 100
    except Exception as e:
        print(f"Error during return on investment: {e}")
        raise  # Re-raise to ensure error propagation

    try:
    # Daily change of every stock in the portfolio after we drop the date, portfolio daily worth and daily % returns
        portfolio_daily_return_df = portfolio_df.drop(columns=['date', 'Portfolio Value [$]', 'Portfolio Daily Return [%]'])
        portfolio_daily_return_df = portfolio_daily_return_df.pct_change(1).dropna()

    # Portfolio Expected Return formula
        expected_portfolio_return = np.sum(weights * portfolio_daily_return_df.mean()) * 252
    except Exception as e:
        print(f"Error during expected_portfolio_return: {e}")
        raise  # Re-raise to ensure error propagation

    # Portfolio volatility (risk) formula
    # The risk of an asset is measured using the standard deviation which indicates the dispertion away from the mean
    # The risk of a portfolio is not a simple sum of the risks of the individual assets within the portfolio
    # Portfolio risk must consider correlations between assets within the portfolio which is indicated by the covariance
    # The covariance determines the relationship between the movements of two random variables
    # When two stocks move together, they have a positive covariance when they move inversely, the have a negative covariance

    covariance = portfolio_daily_return_df.cov() * 252
    expected_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance, weights)))

    # Check out the chart for the 10-years U.S. treasury at https://ycharts.com/indicators/10_year_treasury_rate
    rf = risk_free_rate  # Try to set the risk free rate of return to 1% (assumption)

    # Calculate Sharpe ratio
    sharpe_ratio = (expected_portfolio_return - rf) / expected_volatility
    return expected_portfolio_return, expected_volatility, sharpe_ratio, \
    portfolio_df['Portfolio Value [$]'][-1:].values[0], return_on_investment.values[0]


def run_simulation(stock_symbols, n, initial_investment, sim_runs, risk_free_rate, close_price_df):
    global progress
    progress_file_path = os.path.join(settings.BASE_DIR, 'progress.json')
    progress = {"current": 0, "total": sim_runs}

    with open(progress_file_path, 'w') as file:
        json.dump(progress, file)

    # Placeholder to store all weights
    weights_runs = np.zeros((sim_runs, n))

    # Placeholder to store all Sharpe ratios
    sharpe_ratio_runs = np.zeros(sim_runs)

    # Placeholder to store all expected returns
    expected_portfolio_returns_runs = np.zeros(sim_runs)

    # Placeholder to store all volatility values
    volatility_runs = np.zeros(sim_runs)

    # Placeholder to store all returns on investment
    return_on_investment_runs = np.zeros(sim_runs)

    # Placeholder to store all final portfolio values
    final_value_runs = np.zeros(sim_runs)

    for i in range(sim_runs):

        try:
            # Generate random weights
            weights = generate_portfolio_weights(n)

            # Store the weights
            weights_runs[i, :] = weights

            # Call "simulation_engine" function and store results
            expected_portfolio_returns_runs[i], volatility_runs[i], sharpe_ratio_runs[i], \
                final_value_runs[i], return_on_investment_runs[i] = simulation_engine(
                close_price_df,
                weights,
                initial_investment,
                risk_free_rate)

            # Print progress to console/logs
            progress["current"] = i + 1
            with open('progress.json', 'w') as file:
                json.dump(progress, file)
            print(f"Simulation {i + 1}/{sim_runs} completed.")
            print(f"Weights: {weights.round(3)}")
            print(f"Final Value: ${final_value_runs[i]:.2f}")
            print(f"Sharpe Ratio: {sharpe_ratio_runs[i]:.2f}\n")
        except Exception as e:
            print(f"Error during simulation run {i + 1}: {e}")

        progress["current"] = i + 1
        with open(progress_file_path, 'w') as file:
            json.dump(progress, file)

    progress["current"] = sim_runs
    with open(progress_file_path, 'w') as file:
        json.dump(progress, file)

    # Prepare DataFrame for visualization
    sim_out_df = pd.DataFrame(
        {
            'Volatility': volatility_runs.tolist(),
            'Portfolio_Return': expected_portfolio_returns_runs.tolist(),
            'Sharpe_Ratio': sharpe_ratio_runs.tolist(),
            'Final_Value': final_value_runs.tolist(),
            'Return_on_Investment': return_on_investment_runs.tolist(),
            'Weights': [weights_runs[i, :] for i in range(sim_runs)]
        }
    )

    # Find the index of the portfolio with the highest Sharpe ratio
    max_sharpe_idx = sim_out_df['Sharpe_Ratio'].idxmax()
    print(max_sharpe_idx)
    # Extract the data for the portfolio with the highest Sharpe ratio
    best_portfolio_data = {
        'Volatility': sim_out_df.at[max_sharpe_idx, 'Volatility'],
        'Portfolio_Return': sim_out_df.at[max_sharpe_idx, 'Portfolio_Return'],
        'Sharpe_Ratio': sim_out_df.at[max_sharpe_idx, 'Sharpe_Ratio'],
        'Final_Value': sim_out_df.at[max_sharpe_idx, 'Final_Value'],
        'Return_on_Investment': sim_out_df.at[max_sharpe_idx, 'Return_on_Investment'],
        'Weights': sim_out_df.at[max_sharpe_idx, 'Weights']
    }

    return sim_out_df, best_portfolio_data


def generate_portfolio_simulation_figures(sim_out_df, best_portfolio_data):
    # Plot interactive scatter plot for volatility vs. return
    fig1 = px.scatter(
        sim_out_df,
        x='Volatility',
        y='Portfolio_Return',
        color='Sharpe_Ratio',
        size='Sharpe_Ratio',
        hover_data=['Sharpe_Ratio']
    )

    # Highlight the best portfolio
    fig1.add_trace(
        go.Scatter(
            x=[best_portfolio_data['Volatility']],
            y=[best_portfolio_data['Portfolio_Return']],
            mode='markers+text',
            marker=dict(color='red', size=25, symbol='circle'),
            name='Optimal Portfolio',
            text=['Optimal Portfolio'],
            textposition='top right',
            textfont=dict(color='black', size=14),  # Customize the text font
            showlegend=False
        )
    )
    fig1.update_layout({'plot_bgcolor': "white"})

    # Plot interactive line plot for volatility
    fig2 = px.line(sim_out_df, y='Volatility')

    # Plot interactive line plot for Portfolio Return
    fig3 = px.line(sim_out_df, y='Portfolio_Return')
    fig3.update_traces(line_color='red')

    # Plot interactive line plot for Sharpe Ratio
    fig4 = px.line(sim_out_df, y='Sharpe_Ratio')
    fig4.update_traces(line_color='purple')

    return fig1.to_html(full_html=False), fig2.to_html(full_html=False), fig3.to_html(full_html=False), fig4.to_html(full_html=False)


def update_stock_data_trend_daily_return(date):

    queryset = StockData.objects.filter(date__gt=date)
    stock_data_objects = []
    for stock_data in queryset:
        # current_stock = Stock.objects.filter(pk=stock_data.stock).first()

        daily_return = StockData.objects.calculate_daily_return(
            stock=stock_data.stock,
            date=stock_data.date,
            adj_close=stock_data.adj_close,
        )

        stock_data.daily_return = daily_return
        stock_data.trend = StockData.objects.calculate_trend(daily_return)
        stock_data_objects.append(stock_data)
    StockData.objects.bulk_update(stock_data_objects, fields=['daily_return', 'trend'])


def update_stock_data():
    """
    Updates stock data for all stocks in the database by fetching the latest data from yfinance.
    """
    stocks = Stock.objects.all()
    # stock_tickers = [stock.ticker for stock in stocks]

    # Fetch historical data for all tickers in a single request
    try:
        # Initialize lists for bulk updates
        stock_data_objects = []
        stock_objects = []
        min_date = datetime(2100, 1, 1).date()

        for stock in stocks:
            # Determine the last update date for the current stock
            last_update = StockData.objects.filter(stock=stock).aggregate(
                last_update=Max('updated_at')
            )['last_update']

            # If no data exists, set start date to a default past date
            if not last_update:
                start_date = '2010-01-01'
            else:
                start_date = last_update.date()
                if start_date < min_date:
                    min_date = start_date

            # Fetch historical data for the stock
            data = yf.download(stock.ticker, start=start_date, interval='1d')
            if not data.empty:
                data['daily_return'] = data['Adj Close'].pct_change() * 100
                data['trend'] = data['daily_return'].apply(percentage_return_classifier)
                data.reset_index(inplace=True)
                data.fillna(0, inplace=True)

                # Create or update StockData instances
                stock_data_objects.extend([
                    StockData(
                        stock=stock,
                        date=row['Date'],
                        open=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        adj_close=row['Adj Close'],
                        volume=row['Volume'],
                        daily_return=row['daily_return'],
                        trend=row['trend']
                    )
                    for _, row in data.iterrows()
                ])

            # Fetch and update stock details
            stock_data = yf.Ticker(stock.ticker)
            info = stock_data.info

            stock_objects.append(
                Stock(
                    id=stock.id,
                    name=info.get('shortName', stock.name),
                    sector=info.get('sector', stock.sector),
                    market_cap=info.get('marketCap', stock.market_cap),
                    enterprise_value=info.get('enterpriseValue', stock.enterprise_value),
                    trailing_pe=info.get('trailingPE', stock.trailing_pe),
                    forward_pe=info.get('forwardPE', stock.forward_pe),
                    peg_ratio=info.get('pegRatio', stock.peg_ratio),
                    price_to_book=info.get('priceToBook', stock.price_to_book),
                    profit_margin=info.get('profitMargins', stock.profit_margin),
                    operating_margin=info.get('operatingMargins', stock.operating_margin),
                    revenue=info.get('totalRevenue', stock.revenue),
                    gross_profit=info.get('grossProfits', stock.gross_profit),
                    ebitda=info.get('ebitda', stock.ebitda),
                    net_income=info.get('netIncome', stock.net_income),
                    diluted_eps=info.get('dilutedEPSTTM', stock.diluted_eps),
                    total_cash=info.get('totalCash', stock.total_cash),
                    total_debt=info.get('totalDebt', stock.total_debt),
                    total_assets=info.get('totalAssets', stock.total_assets),
                    total_liabilities=info.get('totalLiab', stock.total_liabilities),
                    dividend_yield=info.get('dividendYield', stock.dividend_yield) if info.get(
                        'dividendYield') is not None else 0,
                    dividend_rate=info.get('dividendRate', stock.dividend_rate) if info.get(
                        'dividendRate') is not None else 0,
                    payout_ratio=info.get('payoutRatio', stock.payout_ratio) if info.get(
                        'payoutRatio') is not None else 0,
                    beta=info.get('beta', stock.beta),
                    fifty_two_week_high=info.get('fiftyTwoWeekHigh', stock.fifty_two_week_high),
                    fifty_two_week_low=info.get('fiftyTwoWeekLow', stock.fifty_two_week_low),
                    average_daily_volume=info.get('averageVolume', stock.average_daily_volume)
                )
            )

        # Bulk create or update StockData model
        with transaction.atomic():
            StockData.objects.bulk_create(
                stock_data_objects,
                ignore_conflicts=True
            )

            # Bulk update Stock model
            Stock.objects.bulk_update(
                stock_objects,
                [
                    'name', 'sector', 'market_cap', 'enterprise_value', 'trailing_pe', 'forward_pe',
                    'peg_ratio', 'price_to_book', 'profit_margin', 'operating_margin', 'revenue',
                    'gross_profit', 'ebitda', 'net_income', 'diluted_eps', 'total_cash', 'total_debt',
                    'total_assets', 'total_liabilities', 'dividend_yield', 'dividend_rate',
                    'payout_ratio', 'beta', 'fifty_two_week_high', 'fifty_two_week_low', 'average_daily_volume'
                ]
            )

        update_stock_data_trend_daily_return(min_date)

    except Exception as e:
        print(f"Failed to update stock data: {e}")


def fetch_stock_data(stock_symbols, start_date='2010-01-01', end_date=None):
    """
    Fetch historical stock data for given stock symbols from the database and return as a DataFrame.
    """
    try:
        # Validate stock_symbols list and dates are not None
        if not stock_symbols:
            raise ValueError("No stock symbols provided.")

        if start_date is None:
            start_date = '2010-01-01'  # Set default start date if None

        if end_date is None:
            end_date = pd.Timestamp.now().strftime('%Y-%m-%d')  # Set default end date if None

        # Filter StockData objects by stock symbols and date range
        stock_data = StockData.objects.filter(
            stock__ticker__in=stock_symbols,
            date__gte=start_date,
            date__lte=end_date
        ).select_related('stock')

        # Raise error if no data found
        if not stock_data.exists():
            raise ValueError("No historical data found for the provided stock symbols and date range.")

        # Convert to DataFrame
        data_list = list(stock_data.values('stock__ticker', 'date', 'adj_close'))
        for data in data_list:
            data['adj_close'] = float(data['adj_close'])  # Cast to float

        df = pd.DataFrame(data_list)

        if df.empty:
            raise ValueError("Converted DataFrame is empty.")

        # Pivot the DataFrame to have stocks as columns and dates as rows
        close_price_df = df.pivot(index='date', columns='stock__ticker', values='adj_close')

        # Fill missing values with 0
        close_price_df.fillna(0, inplace=True)

        close_price_df.reset_index(inplace=True)

        numeric_cols = close_price_df.columns.difference(['date'])
        close_price_df[numeric_cols] = close_price_df[numeric_cols].astype(float)

        return close_price_df

    except Exception as e:
        print(f"Error fetching stock data: {str(e)}")
        raise
