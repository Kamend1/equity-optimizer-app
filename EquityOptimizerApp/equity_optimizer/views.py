import os
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from .models import Stock
from .forms import DateRangeForm, InitialForm, StockSelectionForm
import pandas as pd
import json
from .services import (check_stock_exists, add_stock_to_db, download_and_save_stock_data, get_filtered_stocks,
                       get_stock_by_ticker, plot_financial_data, generate_trend_pie_chart, get_trend_summary,
                       get_stock_data_by_ticker, generate_candlestick_chart, generate_histogram_chart, run_simulation,
                       update_stock_data, fetch_stock_data, generate_portfolio_simulation_figures)
from .. import settings


@login_required
def simulation(request):
    if request.method == 'POST':
        if 'submit_initial' in request.POST:
            # Handle initial form submission
            initial_form = InitialForm(request.POST)

            if initial_form.is_valid():
                num_stocks = int(initial_form.cleaned_data['num_stocks'])

                # Convert date fields to string before storing them in the session
                start_date_str = initial_form.cleaned_data['start_date'].strftime('%Y-%m-%d')
                end_date_str = initial_form.cleaned_data['end_date'].strftime('%Y-%m-%d')

                # Store relevant data in the session
                request.session['num_stocks'] = num_stocks
                request.session['start_date'] = start_date_str
                request.session['end_date'] = end_date_str
                request.session['risk_free_rate'] = float(initial_form.cleaned_data['risk_free_rate'])
                request.session['initial_investment'] = int(initial_form.cleaned_data['initial_investment'])
                request.session['sim_runs'] = int(initial_form.cleaned_data['sim_runs'])

                # Initialize StockSelectionForm with num_stocks
                stock_form = StockSelectionForm(num_stocks=num_stocks)

                return render(request, 'tools/stock_selection.html', {
                    'stock_form': stock_form,
                })
            else:
                # Re-render the initial form with errors
                return render(request, 'tools/simulation.html', {
                    'initial_form': initial_form
                })

        elif 'submit_stocks' in request.POST:
            # Handle stock selection form submission
            num_stocks = request.session.get('num_stocks', 0)

            # Initialize forms with POST data
            stock_form = StockSelectionForm(num_stocks=num_stocks, data=request.POST)

            if stock_form.is_valid():
                # Retrieve stored data from session
                start_date_str = request.session.get('start_date', '')
                end_date_str = request.session.get('end_date', '')
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                risk_free_rate = float(request.session.get('risk_free_rate', 0))
                initial_investment = int(request.session.get('initial_investment', 0))
                sim_runs = int(request.session.get('sim_runs', 0))

                try:
                    # Process valid stock selection
                    selected_stocks = [stock_form.cleaned_data.get(f'stock_{i}') for i in range(num_stocks)]
                    stock_symbols = sorted([stock.ticker for stock in selected_stocks if stock])
                except Exception as e:
                    messages.error(request, f"Invalid Stock Selection: {str(e)}")
                    return render(request, 'tools/stock_selection.html',
                                  {'stock_form': stock_form})

                try:
                    close_price_df = fetch_stock_data(stock_symbols, start_date=start_date, end_date=end_date)
                    print(close_price_df)
                    print(f"Stock price data summary:\n{close_price_df.describe()}")


                except Exception as e:
                    messages.error(request, f"Failed to fetch stock data: {str(e)}")
                    return render(request, 'tools/stock_selection.html',
                                  {'stock_form': stock_form})

                try:
                    sim_out_df, best_portfolio_data = run_simulation(
                        stock_symbols,
                        num_stocks,
                        initial_investment,
                        sim_runs,
                        risk_free_rate,
                        close_price_df
                    )
                except Exception as e:
                    messages.error(request, f"Simulation failed: {str(e)}")
                    return render(request, 'tools/stock_selection.html',
                                  {'stock_form': stock_form})

                try:
                    fig1_html, fig2_html, fig3_html, fig4_html = generate_portfolio_simulation_figures(
                        sim_out_df,
                        best_portfolio_data,
                    )
                except Exception as e:
                    messages.error(request, f"Failed to generate figures: {str(e)}")
                    return render(request, 'tools/stock_selection.html',
                                  {'stock_form': stock_form})

                best_portfolio_data['Weights'] = [round(weight * 100, 2) for weight in best_portfolio_data['Weights']]
                best_portfolio_data['Weights'] = list(zip(best_portfolio_data['Weights'], stock_symbols))
                request.session['best_portfolio_data'] = best_portfolio_data
                request.session['initial_investment'] = initial_investment
                print(f"Stored in session - best_portfolio_data: {request.session.get('best_portfolio_data')}")
                print(f"Stored in session - initial_investment: {request.session.get('initial_investment')}")

                context = {
                    'fig1_html': fig1_html,
                    'fig2_html': fig2_html,
                    'fig3_html': fig3_html,
                    'fig4_html': fig4_html,
                    'best_portfolio_data': best_portfolio_data,
                }
                return render(request, 'tools/simulation_results.html', context)
            else:
                # Re-render the stock selection form with errors
                return render(request, 'tools/stock_selection.html', {
                    'stock_form': stock_form
                })

    else:
        # Handle GET request
        initial_form = InitialForm()
        context = {
            'initial_form': initial_form,
        }
        return render(request, 'tools/simulation.html', context)


@login_required
def add_stock(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')

        if ticker:
            if check_stock_exists(ticker):
                messages.error(request, 'Stock already exists')
                return render(request, 'tools/add.html', {'ticker': ticker})

            try:
                # Add the stock to the database
                stock = add_stock_to_db(ticker)
                # Download and save the historical stock data
                download_and_save_stock_data(stock)
                messages.success(request, f'Stock {ticker} added successfully!')
            except Exception as e:
                # Handle the case where data retrieval fails
                messages.error(request, f'Failed to retrieve data for ticker {ticker}. Error: {str(e)}')
                return render(request, 'tools/add.html', {'ticker': ticker})

            return redirect('stock_list')

    return render(request, 'tools/add.html')


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

    # Fetch stock data
    df = get_stock_data_by_ticker(ticker, start_date, end_date)
    print(df.dtypes)
    print(df)

    # Generate the Plotly line chart
    chart_html = plot_financial_data(df, f'Financial Data for {ticker}')

    # Generate the trend pie chart
    trend_summary = get_trend_summary(ticker, start_date, end_date)
    trend_chart = generate_trend_pie_chart(trend_summary)

    # Generate the Cufflinks candlestick chart with SMA and Bollinger Bands
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

    # Render the template with the chart
    return render(request, 'tools/analyze.html', context)


class StockListView(ListView):
    model = Stock
    template_name = 'tools/stock_list.html'
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
        return render(request, 'tools/stock_detail.html', {'error': 'Stock not found'})

    return render(request, 'tools/stock_detail.html', {'stock': stock})


@user_passes_test(lambda u: u.is_staff)
def update_stocks_view(request):
    if request.method == 'POST':
        try:
            update_stock_data()
            messages.success(request, 'Stock data updated successfully!')
        except Exception as e:
            messages.error(request, f'Failed to update stock data. Error: {str(e)}')

        return redirect('update_stocks')

    return render(request, 'tools/update_stocks.html')


@login_required
def get_progress(request):
    try:
        progress_file = os.path.join(settings.BASE_DIR, 'progress.json')
        with open(progress_file, 'r') as f:
            progress = json.load(f)
    except FileNotFoundError:
        progress = {"progress": 100}  # Assume complete if file is not found

    return JsonResponse(progress)
