import os
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from .models import Stock
from .forms import DateRangeForm, InitialForm
import pandas as pd
import json
import logging
from .services import (check_stock_exists, add_stock_to_db, download_and_save_stock_data, get_filtered_stocks,
                       get_stock_by_ticker, plot_financial_data, generate_trend_pie_chart, get_trend_summary,
                       get_stock_data_by_ticker, generate_candlestick_chart, generate_histogram_chart, run_simulation,
                       update_stock_data, fetch_stock_data, generate_portfolio_simulation_figures)
from .. import settings


@login_required
def simulation(request):
    if request.method == 'POST':
        initial_form = InitialForm(request.POST, user=request.user)

        if initial_form.is_valid():
            start_date = initial_form.cleaned_data['start_date']
            end_date = initial_form.cleaned_data['end_date']
            risk_free_rate = float(initial_form.cleaned_data['risk_free_rate'])
            initial_investment = float(initial_form.cleaned_data['initial_investment'])
            sim_runs = initial_form.cleaned_data['sim_runs']
            favorite_list = initial_form.cleaned_data['favorite_list']

            # Fetch selected stock list's stock tickers
            selected_stocks = favorite_list.stocks.all()
            stock_symbols = sorted([stock.ticker for stock in selected_stocks])

            if not stock_symbols:
                messages.error(request, "The selected stock list is empty. Please choose a list with stocks.")
                return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})

            try:
                # Fetch stock data
                close_price_df = fetch_stock_data(stock_symbols, start_date=start_date, end_date=end_date)
                print(close_price_df)
                print(f"Stock price data summary:\n{close_price_df.describe()}")
            except Exception as e:
                messages.error(request, f"Failed to fetch stock data: {str(e)}")
                return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})

            try:
                # Run the simulation
                sim_out_df, best_portfolio_data = run_simulation(
                    stock_symbols,
                    len(stock_symbols),
                    initial_investment,
                    sim_runs,
                    risk_free_rate,
                    close_price_df
                )
            except Exception as e:
                messages.error(request, f"Simulation failed: {str(e)}")
                return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})

            try:
                # Generate portfolio simulation figures
                fig1_html, fig2_html, fig3_html, fig4_html = generate_portfolio_simulation_figures(
                    sim_out_df,
                    best_portfolio_data,
                )
            except Exception as e:
                messages.error(request, f"Failed to generate figures: {str(e)}")
                return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})

            best_portfolio_data['Weights'] = [
                (float(round(weight * 100, 2)), ticker) for weight, ticker in zip(
                    best_portfolio_data['Weights'], stock_symbols
                )
            ]
            request.session['best_portfolio_data'] = best_portfolio_data
            request.session['initial_investment'] = float(initial_investment)

            context = {
                'fig1_html': fig1_html,
                'fig2_html': fig2_html,
                'fig3_html': fig3_html,
                'fig4_html': fig4_html,
                'best_portfolio_data': best_portfolio_data,
            }
            return render(request, 'equity_optimizer/simulation_results.html', context)
        else:
            return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})

    else:
        initial_form = InitialForm(user=request.user)
        return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})


@login_required
def add_stock(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')

        if ticker:
            if check_stock_exists(ticker):
                messages.error(request, 'Stock already exists')
                return render(request, 'equity_optimizer/add.html', {'ticker': ticker})

            try:
                # Add the stock to the database
                stock = add_stock_to_db(ticker)
                # Download and save the historical stock data
                download_and_save_stock_data(stock)
                messages.success(request, f'Stock {ticker} added successfully!')
            except Exception as e:
                # Handle the case where data retrieval fails
                messages.error(request, f'Failed to retrieve data for ticker {ticker}. Error: {str(e)}')
                return render(request, 'equity_optimizer/add.html', {'ticker': ticker})

            return redirect('stock_list')

    return render(request, 'equity_optimizer/add.html')


@login_required
def analyze_stock(request, ticker):

    default_start_date = '2012-01-01'
    default_end_date = pd.to_datetime('today').strftime('%Y-%m-%d')

    form = DateRangeForm(request.GET or None)

    # Validate and parse the dates from the form
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date') or default_start_date
        end_date = form.cleaned_data.get('end_date') or default_end_date
    else:
        start_date = default_start_date
        end_date = default_end_date

    df = get_stock_data_by_ticker(ticker, start_date, end_date)
    print(df.dtypes)
    print(df)

    chart_html = plot_financial_data(df, f'Financial Data for {ticker}')

    trend_summary = get_trend_summary(ticker, start_date, end_date)
    trend_chart = generate_trend_pie_chart(trend_summary)

    candlestick_chart_html = generate_candlestick_chart(df, f'{ticker} Candlestick Chart')

    histogram_chart = generate_histogram_chart(df, f'{ticker} Histogram of Daily Returns')

    context = {
        'chart_html': chart_html,
        'ticker': ticker,
        'trend_chart': trend_chart,
        'candlestick_chart_html': candlestick_chart_html,  # Add the candlestick chart to the context
        'histogram_chart': histogram_chart,
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'equity_optimizer/analyze.html', context)


class StockListView(ListView):
    model = Stock
    template_name = 'equity_optimizer/stock_list.html'
    context_object_name = 'stocks'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['sort'] = self.request.GET.get('sort', '')
        context['direction'] = self.request.GET.get('direction', 'asc')

        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by('ticker')
        query = self.request.GET.get('q', '')
        sort = self.request.GET.get('sort', '')
        direction = self.request.GET.get('direction', 'asc')

        if query:
            queryset = get_filtered_stocks(query)

        if sort:
            if direction == 'desc':
                sort = f'-{sort}'
            queryset = queryset.order_by(sort)

        return queryset.prefetch_related('historical_data')


def stock_detail(request, ticker):
    try:
        stock = get_stock_by_ticker(ticker)
    except Stock.DoesNotExist:
        return render(request, 'equity_optimizer/stock_detail.html', {'error': 'Stock not found'})

    return render(request, 'equity_optimizer/stock_detail.html', {'stock': stock})


@user_passes_test(lambda u: u.is_staff)
def update_stocks_view(request):
    if request.method == 'POST':
        try:
            update_stock_data()
            messages.success(request, 'Stock data updated successfully!')
        except Exception as e:
            messages.error(request, f'Failed to update stock data. Error: {str(e)}')

        return redirect('update_stocks')

    return render(request, 'equity_optimizer/update_stocks.html')


logger = logging.getLogger(__name__)


@login_required
def get_progress(request):
    progress_file_path = os.path.join(settings.BASE_DIR, 'progress.json')
    try:
        with open(progress_file_path, 'r') as f:
            progress = json.load(f)
            logger.info(f"Progress data: {progress}")
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        logger.error(f"Error reading progress file: {e}")
        progress = {"current": 0, "total": 1}

    return JsonResponse(progress)
