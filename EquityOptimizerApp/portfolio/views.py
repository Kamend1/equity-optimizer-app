from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DetailView, ListView

from EquityOptimizerApp.equity_optimizer.forms import DateRangeForm
from EquityOptimizerApp.portfolio.models import Portfolio, PortfolioStock, PortfolioValueHistory
from EquityOptimizerApp.portfolio.forms import PortfolioForm
from EquityOptimizerApp.portfolio.services import save_portfolio_from_simulation, update_all_portfolios_daily_values


@login_required
def portfolio(request):
    # Fetch the authenticated user's portfolios
    user_portfolios = Portfolio.objects.filter(user=request.user)

    # Check if the user has portfolios
    has_portfolios = user_portfolios.exists()

    context = {
        'user_portfolios': user_portfolios,
        'has_portfolios': has_portfolios,
    }

    return render(request, 'equity_optimizer/../../templates/portfolio/portfolio.html', context)


@login_required
def save_portfolio_view(request):
    if request.method == 'POST':
        portfolio_form = PortfolioForm(request.POST)

        if portfolio_form.is_valid():
            user = request.user
            name = portfolio_form.cleaned_data['name']
            description = portfolio_form.cleaned_data['description']

            best_portfolio_data = request.session.get('best_portfolio_data')
            initial_investment = request.session.get('initial_investment')

            print(f"Stored in session - best_portfolio_data: {best_portfolio_data}")
            print(f"Stored in session - initial_investment: {initial_investment}")

            if not best_portfolio_data or not initial_investment:
                messages.error(request, "Failed to retrieve simulation data.")
                return redirect('simulation')

            try:
                save_portfolio_from_simulation(
                    user=user,
                    name=name,
                    description=description,
                    best_portfolio_data=best_portfolio_data,
                    initial_investment=initial_investment
                )

                messages.success(request, "Portfolio saved successfully.")
                return redirect('portfolio')
            except Exception as e:
                messages.error(request, f"Failed to save portfolio: {str(e)}")
                print(f"Error during save_portfolio_from_simulation: {e}")
                return redirect('simulation')
        else:
            messages.error(request, "Invalid form submission.")
            return render(
                request,
                'equity_optimizer/../../templates/portfolio/save_portfolio.html',
                {'portfolio_form': portfolio_form},
            )

    else:
        portfolio_form = PortfolioForm()
        return render(
            request,
            'equity_optimizer/../../templates/portfolio/save_portfolio.html',
            {'portfolio_form': portfolio_form},
        )


class PortfolioDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Portfolio
    template_name = 'portfolio/portfolio_detail.html'
    context_object_name = 'portfolio'

    def get_object(self, queryset=None):
        return get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'], user=self.request.user)

    def test_func(self):
        portfolio = self.get_object()
        return portfolio.user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        portfolio = context['portfolio']

        # Retrieve related stocks and their details
        portfolio_stocks = PortfolioStock.objects.filter(portfolio=portfolio).select_related('stock')
        stock_details = [
            {
                'name': ps.stock.name,
                'ticker': ps.stock.ticker,
                'quantity': ps.quantity,
                'last_close': ps.stock.last_adj_close(),
            }
            for ps in portfolio_stocks
        ]

        latest_value_entry = PortfolioValueHistory.objects.filter(portfolio=portfolio).order_by('-date').first()
        latest_value_date = latest_value_entry.date if latest_value_entry else None
        latest_value = latest_value_entry.value if latest_value_entry else None

        context.update({
            'stock_details': stock_details,
            'latest_value_date': latest_value_date,
            'latest_value': latest_value,
            'user_profile_link': reverse('profile_details', kwargs={'pk': portfolio.user.pk}),
        })

        return context


class PortfolioEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'portfolio/portfolio_edit.html'
    success_url = reverse_lazy('portfolio')

    def get_object(self, queryset=None):
        return get_object_or_404(Portfolio, id=self.kwargs.get('portfolio_id'), user=self.request.user)

    def test_func(self):
        portfolio = self.get_object()
        return portfolio.user == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit this portfolio.")
        return redirect('portfolio_list')


@user_passes_test(lambda u: u.is_staff)
def update_portfolios_view(request):
    if request.method == 'POST':
        try:
            # Call the function to update daily portfolio values for all portfolios
            update_all_portfolios_daily_values()
            messages.success(request, 'Portfolio values updated successfully!')
        except Exception as e:
            messages.error(request, f'Failed to update portfolio values. Error: {str(e)}')

        return redirect('update_portfolios')  # Ensure 'update_portfolios' is defined in your URL configurations

    # Render the update page if the request method is GET
    return render(request, 'portfolio/update_portfolios.html')


class PortfolioValueHistoryListView(LoginRequiredMixin, ListView):
    model = PortfolioValueHistory
    template_name = 'portfolio/portfolio_value_history_list.html'
    context_object_name = 'value_history'
    paginate_by = 50

    def get_queryset(self):
        portfolio = get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'], user=self.request.user)
        queryset = PortfolioValueHistory.objects.filter(portfolio=portfolio).order_by('-date')

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
        context['portfolio'] = get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'], user=self.request.user)
        return context