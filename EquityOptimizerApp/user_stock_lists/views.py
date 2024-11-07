from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.http import JsonResponse
from .models import FavoriteStockList
from EquityOptimizerApp.equity_optimizer.models import Stock
from .forms import FavoriteStockListForm


# Create your views here.
class UserStockListCreateView(LoginRequiredMixin, CreateView):
    model = FavoriteStockList
    form_class = FavoriteStockListForm
    template_name = 'user_stock_lists/user_stock_list_create.html'
    success_url = reverse_lazy('stock_lists')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        stock_ids = self.request.POST.getlist('stocks')
        if stock_ids:
            form.instance.stocks.set(stock_ids)

        return response


@login_required
def stock_search(request):
    query = request.GET.get('q', '')
    if query:
        stocks = Stock.objects.filter(name__icontains=query)[:50]  # Limit to 50 results
        results = [{'id': stock.id, 'text': f"{stock.ticker} - {stock.name}"} for stock in stocks]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})


class UserListsMain(ListView, LoginRequiredMixin):
    model = FavoriteStockList
    template_name = 'user_stock_lists/user_stock_lists.html'
    context_object_name = 'lists'


class UserListsDeleteView(DeleteView, LoginRequiredMixin):
    model = FavoriteStockList
    success_url = reverse_lazy('stock_lists')
    template_name = 'user_stock_lists/user_stock_list_delete.html'
