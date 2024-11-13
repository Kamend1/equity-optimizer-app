from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404
from .models import Currency, ExchangeRate
from .forms import CurrencyCreateForm, CurrencyEditForm
from ..equity_optimizer.forms import DateRangeForm


class CurrencyListView(ListView):
    model = Currency
    template_name = 'currencies/currency_list.html'
    context_object_name = 'currencies'
    paginate_by = 10


class CurrencyDetailView(DetailView):
    model = Currency
    template_name = 'currencies/currency_detail.html'
    context_object_name = 'currency'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = self.object

        if currency.code != 'USD':
            latest_rate = (
                ExchangeRate.objects.filter(base_currency__code='USD', target_currency=currency)
                .order_by('-date')
                .first()
            )

            context['latest_exchange_rate'] = latest_rate.rate if latest_rate else 'N/A'
        else:
            context['latest_exchange_rate'] = None

        return context


class CurrencyCreateView(CreateView):
    model = Currency
    form_class = CurrencyCreateForm
    template_name = 'currencies/currency_form.html'
    success_url = reverse_lazy('currency-list')


class CurrencyEditView(UpdateView):
    model = Currency
    form_class = CurrencyEditForm
    template_name = 'currencies/currency_form.html'
    success_url = reverse_lazy('currency-list')

    def get_object(self, queryset=None):
        return get_object_or_404(Currency, pk=self.kwargs['pk'])


class ExchangeRateListView(ListView):
    model = ExchangeRate
    template_name = 'currencies/exchange_rate_list.html'
    context_object_name = 'exchange_rates'
    paginate_by = 50

    def get_queryset(self):
        base_currency = get_object_or_404(Currency, code=self.kwargs['base_code'])
        target_currency = get_object_or_404(Currency, code=self.kwargs['target_code'])
        queryset = ExchangeRate.objects.filter(base_currency=base_currency, target_currency=target_currency).order_by('-date')

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
        context['base_currency'] = get_object_or_404(Currency, code=self.kwargs['base_code'])
        context['target_currency'] = get_object_or_404(Currency, code=self.kwargs['target_code'])
        return context
