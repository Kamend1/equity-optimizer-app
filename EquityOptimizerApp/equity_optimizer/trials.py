from .models import StockData
import pandas as pd
import plotly.express as px

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
    ).values('date', 'open', 'high', 'low', 'close', 'adj_close', 'volume')

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
    # Convert columns to numeric, forcing errors to NaN
    df = df.apply(pd.to_numeric, errors='coerce')

    # Create the figure with the title
    fig = px.line(df, title=title)

    # Loop over all columns to plot them
    for i in df.columns[1:]:
        fig.add_scatter(x=df['date'], y=df[i], name=i)
        fig.update_traces(line_width=5)


    # Customize layout
    fig.update_layout({
        'plot_bgcolor': 'white',
        'xaxis_title': 'Date',
        'yaxis_title': 'Value',
    })

    # Return the figure's HTML representation
    return fig.to_html(full_html=False)


ticker = 'AAPL'
start_date = '2010-01-01'
end_date = pd.to_datetime('today').strftime('%Y-%m-%d')

df = get_stock_data_by_ticker(ticker, start_date, end_date)
print(df)
