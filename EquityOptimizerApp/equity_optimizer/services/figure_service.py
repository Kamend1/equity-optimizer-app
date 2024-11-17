from io import BytesIO
import base64
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import pyplot as plt

from EquityOptimizerApp.equity_optimizer.services import StockDataService
from EquityOptimizerApp.equity_optimizer.utils import generate_color_string


class FigureService:

    @staticmethod
    def generate_simulation_figures(sim_out_df, best_portfolio_data):

        sim_out_df['Sharpe_Ratio_Size'] = sim_out_df['Sharpe_Ratio'].apply(lambda x: max(abs(x), 0.1))

        fig1 = px.scatter(
            sim_out_df,
            x='Volatility',
            y='Portfolio_Return',
            color='Sharpe_Ratio',
            size='Sharpe_Ratio_Size',
            hover_data=['Sharpe_Ratio']
        )
        fig1.add_trace(go.Scatter(
            x=[best_portfolio_data['Volatility']],
            y=[best_portfolio_data['Portfolio_Return']],
            mode='markers+text',
            marker=dict(color='red', size=25, symbol='circle'),
            name='Optimal Portfolio',
            text=['Optimal Portfolio'],
            textposition='top right'
        ))

        fig2 = px.line(sim_out_df, y='Volatility')
        fig3 = px.line(sim_out_df, y='Portfolio_Return')
        fig4 = px.line(sim_out_df, y='Sharpe_Ratio')

        return (fig1.to_html(full_html=False), fig2.to_html(full_html=False),
                fig3.to_html(full_html=False), fig4.to_html(full_html=False))

    @staticmethod
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
                line=dict(color=generate_color_string(255, 0, 0, 0.2))
            ))

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['lower_band'],
                mode='lines',
                name='Bollinger Lower Band',
                line=dict(color=generate_color_string(0, 255, 0, 0.2))  # Alpha included for Bollinger bands
            ))

        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Price',
            template='plotly_white'  # Use a valid Plotly theme here
        )

        return fig.to_html(full_html=False)

    @staticmethod
    def generate_histogram_chart(df, title='Histogram of Daily Returns'):
        """
        Generate a histogram chart of daily returns.

        Args:
            df (pd.DataFrame): DataFrame containing daily returns data.
            title (str): Title for the chart.

        Returns:
            str: HTML representation of the plotly figure.
        """
        fig = px.histogram(df, x='daily_return', title=title)

        fig.update_layout(
            plot_bgcolor='white',
            xaxis_title='Daily Returns',
            yaxis_title='Frequency',
            title_text=title,
            title_x=0.5,
        )

        return fig.to_html(full_html=False)

    @staticmethod
    def plot_financial_data(df, title):
        """
        Generate a line plot for financial data.

        Args:
            df (pd.DataFrame): DataFrame containing financial data with 'date' as index.
            title (str): Title for the plot.

        Returns:
            str: HTML representation of the plotly figure.
        """

        # fig = px.line(df, title=title)
        fig = go.Figure()

        for i in df.columns[0:]:
            fig.add_scatter(x=df.index, y=df[i], name=i)
            fig.update_traces(line_width=5)

        fig.update_layout({
            'plot_bgcolor': 'white',
            'xaxis_title': 'Date',
            'yaxis_title': 'Value',
        })

        return fig.to_html(full_html=False)

    @staticmethod
    def generate_trend_pie_chart(ticker, start_date, end_date):
        """
        Generates a pie chart for trend distribution and returns it as a base64-encoded string.

        Args:
            trend_summary_df (pandas.DataFrame): DataFrame containing trend counts.

        Returns:
            str: Base64-encoded string of the generated pie chart.
        """

        trend_summary_df = StockDataService.get_trend_summary(ticker, start_date, end_date)

        plt.figure(figsize=(8, 8))
        plt.pie(trend_summary_df['count'], labels=trend_summary_df['trend'], autopct='%1.1f%%')
        # plt.title('Trend Distribution')

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_png = buf.getvalue()
        buf.close()

        trend_chart = base64.b64encode(image_png).decode('utf-8')

        return trend_chart
