from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DetailView, ListView

from EquityOptimizerApp.equity_optimizer.forms import DateRangeForm
from EquityOptimizerApp.mixins import ObjectOwnershipRequiredMixin
from EquityOptimizerApp.portfolio.models import Portfolio, PortfolioStock, PortfolioValueHistory, PortfolioUpvote
from EquityOptimizerApp.portfolio.forms import PortfolioForm
from EquityOptimizerApp.portfolio.services import PortfolioCreationService, PortfolioValueService

portfolio_creation_service = PortfolioCreationService()
portfolio_value_service = PortfolioValueService()

user_model = get_user_model()


class PersonalPortfolioListView(LoginRequiredMixin, ListView):
    model = Portfolio
    template_name = 'portfolio/personal_portfolio_list.html'
    context_object_name = 'user_portfolios'
    paginate_by = 9

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user).order_by('-created_at')


class PublicPortfolioListView(LoginRequiredMixin, ListView):
    model = Portfolio
    template_name = 'portfolio/public_portfolio_list.html'
    context_object_name = 'public_portfolios'
    paginate_by = 9

    def get_queryset(self):

        queryset = Portfolio.objects.filter(public=True).annotate(total_upvotes=Count('upvotes')).order_by('-total_upvotes')
        user_id = self.request.GET.get('user_id')

        if user_id:
            user = get_object_or_404(user_model, id=user_id)
            queryset = queryset.filter(user=user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.GET.get('user_id')
        if user_id:
            user = get_object_or_404(user_model, id=user_id)
            context['filtered_user'] = user
        return context


@login_required
def upvote_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)

    if portfolio.public and portfolio.user != request.user:
        portfolio.upvotes += 1
        portfolio.save()
        messages.success(request, 'You upvoted this portfolio!')

    return HttpResponseRedirect(reverse('personal-portfolios'))


@login_required
def toggle_upvote(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)

    upvote, created = PortfolioUpvote.objects.get_or_create(user=request.user, portfolio=portfolio)

    if not created:
        upvote.delete()
        messages.info(request, 'You removed your upvote from this portfolio.')
    else:
        messages.success(request, 'You upvoted this portfolio!')

    return HttpResponseRedirect(reverse('personal-portfolios'))

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
                portfolio_creation_service.create_from_simulation(
                    user=user,
                    name=name,
                    description=description,
                    best_portfolio_data=best_portfolio_data,
                    initial_investment=initial_investment
                )

                messages.success(request, "Portfolio saved successfully.")
                return redirect('personal-portfolios')
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


class PortfolioDetailView(LoginRequiredMixin, DetailView):
    model = Portfolio
    template_name = 'portfolio/portfolio_detail.html'
    context_object_name = 'portfolio'

    def get_object(self, queryset=None):

        portfolio = get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'])

        if portfolio.user == self.request.user or portfolio.public:
            return portfolio
        else:
            raise PermissionDenied("You do not have permission to view this portfolio.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio = context['portfolio']

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


class PortfolioEditView(ObjectOwnershipRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'portfolio/portfolio_edit.html'
    success_url = reverse_lazy('personal-portfolios')

    def get_object(self, queryset=None):
        return get_object_or_404(Portfolio, id=self.kwargs.get('portfolio_id'))


@user_passes_test(lambda u: u.is_staff)
def update_portfolios_view(request):
    if request.method == 'POST':
        try:
            portfolio_value_service.update_all_portfolios()
            messages.success(request, 'Portfolio values updated successfully!')
        except Exception as e:
            messages.error(request, f'Failed to update portfolio values. Error: {str(e)}')

        return redirect('update_portfolios')  # Ensure 'update_portfolios' is defined in your URL configurations

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
