from datetime import datetime
import random
import numpy as np


def percentage_return_classifier(percentage_return):
    if percentage_return > -0.3 and percentage_return <= 0.3:
        return 'Insignificant Change'
    elif percentage_return > 0.3 and percentage_return <= 3:
        return 'Positive Change'
    elif percentage_return > -3 and percentage_return <= -0.3:
        return 'Negative Change'
    elif percentage_return > 3 and percentage_return <= 7:
        return 'Large Positive Change'
    elif percentage_return > -7 and percentage_return <= -3:
        return 'Large Negative Change'
    elif percentage_return > 7:
        return 'Bull Run'
    elif percentage_return <= -7:
        return 'Bear Sell Off'


def parse_date(date_value):

    if isinstance(date_value, str):
        try:
            return datetime.fromisoformat(date_value).date()
        except ValueError:
            return None
    elif isinstance(date_value, (int, float)):
        return datetime.fromtimestamp(date_value).date()
    return None


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
    return f'rgba({r}, {g}, {b}, {a})'

