# Equity Optimizer App

![Logo](static/images/logo.png)

## Overview

The **Equity Optimizer App** is a comprehensive tool designed for investors and financial analysts. It helps users analyze stocks, perform portfolio simulations, and optimize their investment strategies using historical financial data. The application supports a wide range of features, including stock performance analysis, Monte Carlo simulations, currency exchange rates, and portfolio management. This is my capstone project for the Python Database and Python Web Modules at SOFTUNI, part of the Web Development track.

## Features

- **User Authentication**: Secure registration and login for users to access personalized features.
- **Stock Analysis**: In-depth analysis of various stocks, including financial metrics, trends, and visualizations.
- **Currency Support**: The app maintains exchange rates for global currencies, converting them to a base currency (USD). This allows users to analyze stocks traded on international markets.
- **Yahoo Finance API Integration**: Stock and currency data are sourced from the free Yahoo Finance API, allowing users to browse up-to-date information.
- **Favorite Stock Lists**: Users can create multiple lists of favorite stocks, organizing them into collections for easier analysis.
- **Monte Carlo Simulation**: Users can select between 5 and 50 stocks from their favorite lists to perform a Monte Carlo simulation. The simulation analyzes historical data for a specified time interval and attempts up to 20,000 runs to identify the most efficient risk/return portfolio.
- **Portfolio Management**: Users can save, track, and maintain multiple portfolios based on the results of the simulations. Detailed value histories and performance analytics are provided.
- **Search and Filter**: Powerful search and filter options for finding specific stocks quickly.
- **Sorting Options**: Users can sort stock data based on various financial metrics in ascending or descending order.
- **Pagination**: Smooth navigation through large lists of stocks using pagination.

## Technologies Used

- **Django**: Web framework for building the application backend.
- **Bootstrap**: Responsive design and UI components for a polished user interface.
- **Python**: The primary programming language for backend logic and data processing.
- **HTML/CSS**: Markup and styling for the frontend presentation.
- **PostgreSQL**: Database used to store stock and currency data (can be replaced with another DB setup).
- **Yahoo Finance API**: Provides real-time and historical stock and currency data, which are integrated into the app.

## Usage

Once the app is running, you can:

1. **Register or Log In**: Create a new user account or log in to access personalized features.
2. **Browse Stocks and Currencies**: Use the search and filter options to explore various stocks and view currency exchange rates.
3. **Create Favorite Stock Lists**: Organize your chosen stocks into multiple favorite lists for easier tracking and analysis.
4. **Perform Monte Carlo Simulations**: Select a list of favorite stocks, specify a time interval and the number of simulation runs, and let the app identify the most efficient portfolio using the Harry Markowitz Efficient Frontier model.
5. **Manage Portfolios**: Save and monitor your portfolios, review historical performance, and track the value changes over time.

## Currency and Exchange Rate Support

The app supports analysis of stocks from markets outside the US by maintaining exchange rates for global currencies. The exchange rates are converted to a base currency (USD), ensuring accurate and consistent analysis. This feature is integrated with the Yahoo Finance API, providing users with real-time and historical currency data.

## Contributing

Contributions are welcome! If you have suggestions, new features, or improvements, please fork the repository, make your changes, and submit a pull request. We appreciate community involvement.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

## Contact

For inquiries, please reach out to me at **kamendd@hotmail.com**.

---

<em>Disclaimer: This app is intended for educational and testing purposes only. It does not provide investment advice and should not be used as a sole source for making investment decisions. Always consult with a qualified financial advisor before making any financial decisions.</em>
