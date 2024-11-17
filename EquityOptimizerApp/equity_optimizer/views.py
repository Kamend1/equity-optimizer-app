import os
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from .models import Stock, StockData
from .forms import DateRangeForm, InitialForm
import pandas as pd
import json
import logging
from .services import StockService, StockDataService, FigureService, SimulationService, YFinanceFetcher, DataFetcher, \
    StockUpdateService
from .. import settings

fetcher: DataFetcher = YFinanceFetcher()
stock_service = StockService(fetcher)
stock_data_service = StockDataService(fetcher)


@login_required
def simulation(request):
    if request.method == 'POST':
        initial_form = InitialForm(request.POST, user=request.user)

        if initial_form.is_valid():
            print("Form is valid. Proceeding with simulation...")

            start_date = initial_form.cleaned_data['start_date']
            end_date = initial_form.cleaned_data['end_date']
            risk_free_rate = float(initial_form.cleaned_data['risk_free_rate'])
            initial_investment = float(initial_form.cleaned_data['initial_investment'])
            sim_runs = initial_form.cleaned_data['sim_runs']
            favorite_list = initial_form.cleaned_data['favorite_list']

            selected_stocks = favorite_list.stocks.all().order_by('ticker')
            stock_symbols = sorted([stock.ticker for stock in selected_stocks])

            if not stock_symbols:
                messages.error(request, "The selected stock list is empty. Please choose a list with stocks.")
                return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})

            try:
                close_price_df = stock_data_service.fetch_stock_data(stock_symbols, start_date, end_date)
                print("Data fetched successfully. Shape:", close_price_df.shape)
            except Exception as e:
                print(f"Error fetching stock data: {str(e)}")
                context = {'error_message': str(e)}
                return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form, 'error_message': str(e)})

            try:
                sim_out_df, best_portfolio_data = SimulationService.run_simulation(
                    stock_symbols,
                    len(stock_symbols),
                    initial_investment,
                    sim_runs,
                    risk_free_rate,
                    close_price_df
                )
                print("Simulation completed successfully.")
            except Exception as e:
                print(f"Simulation failed: {str(e)}")
                messages.error(request, f"Simulation failed: {str(e)}")
                return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})

            try:
                fig1_html, fig2_html, fig3_html, fig4_html = FigureService.generate_simulation_figures(
                    sim_out_df,
                    best_portfolio_data
                )
                print("Figures generated successfully.")
            except Exception as e:
                print(f"Failed to generate figures: {str(e)}")
                messages.error(request, f"Failed to generate figures: {str(e)}")
                return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})

            try:
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

                print("Rendering simulation results page...")
                return render(request, 'equity_optimizer/simulation_results.html', context)

            except Exception as e:
                print(f"Error during final rendering: {str(e)}")
                messages.error(request, f"Error during final rendering: {str(e)}")
                return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})

        else:
            print("Form validation failed. Errors:", initial_form.errors)
            messages.error(request, "Form validation failed. Please check your input.")
            return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})

    else:
        initial_form = InitialForm(user=request.user)
        return render(request, 'equity_optimizer/simulation.html', {'initial_form': initial_form})


@login_required
def add_stock(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        if ticker:
            if stock_service.check_stock_exists(ticker):
                messages.error(request, 'Stock already exists.')
                return render(request, 'equity_optimizer/add.html', {'ticker': ticker})

            try:
                stock = stock_service.add_stock_to_db(ticker)
                stock_list = [stock,]
                stock_data_service.download_and_save_stock_data(stock_list)
                messages.success(request, f'Stock {ticker} added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding stock: {str(e)}')
                return render(request, 'equity_optimizer/add.html', {'ticker': ticker})

            return redirect('stock_list')

    return render(request, 'equity_optimizer/add.html')


def analyze_stock(request, ticker):

    default_start_date = '2012-01-01'
    default_end_date = pd.to_datetime('today').strftime('%Y-%m-%d')

    form = DateRangeForm(request.GET or None)

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date') or default_start_date
        end_date = form.cleaned_data.get('end_date') or default_end_date
    else:
        start_date = default_start_date
        end_date = default_end_date

    df = stock_data_service.get_stock_data_by_ticker(ticker, start_date, end_date)
    print(df.dtypes)
    print(df)

    chart_html = FigureService.plot_financial_data(df, f'Financial Data for {ticker}')

    trend_chart = FigureService.generate_trend_pie_chart(ticker, start_date, end_date)

    candlestick_chart_html = FigureService.generate_candlestick_chart(df, f'{ticker} Candlestick Chart')

    histogram_chart = FigureService.generate_histogram_chart(df, f'{ticker} Histogram of Daily Returns')

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
        queryset = super().get_queryset().filter(delisted=False).order_by('ticker')
        queryset = Stock.objects.annotate_with_latest_adj_close(queryset)

        query = self.request.GET.get('q', '')
        sort = self.request.GET.get('sort', 'ticker')
        direction = self.request.GET.get('direction', 'asc')

        if query:
            queryset = stock_service.get_filtered_stocks(query).filter(delisted=False)

        if sort:
            if direction == 'desc':
                sort = f'-{sort}'
            queryset = queryset.order_by(sort)

        return queryset


class StockListTemplateView(TemplateView):
    template_name = 'equity_optimizer/api_stock_list_template.html'


class StockDetailView(DetailView):
    model = Stock
    template_name = 'equity_optimizer/stock_detail.html'
    context_object_name = 'stock'
    pk_url_kwarg = 'ticker'
    slug_field = 'ticker'
    slug_url_kwarg = 'ticker'

    def get_object(self, queryset=None):
        return get_object_or_404(Stock, ticker=self.kwargs.get('ticker'))


@user_passes_test(lambda u: u.is_staff)
def update_stocks_view(request):
    if request.method == 'POST':
        try:
            StockUpdateService.update_stock_data()
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


class StockDataListView(ListView):
    model = StockData
    template_name = 'equity_optimizer/stock_data_list.html'
    context_object_name = 'stock_data'
    paginate_by = 50

    def get_queryset(self):
        stock = get_object_or_404(Stock, ticker=self.kwargs['ticker'])
        queryset = StockData.objects.filter(stock=stock).order_by('-date')

        form = DateRangeForm(self.request.GET)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            if end_date:
                queryset = queryset.filter(date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DateRangeForm(self.request.GET)
        context['stock'] = get_object_or_404(Stock, ticker=self.kwargs['ticker'])
        return context
