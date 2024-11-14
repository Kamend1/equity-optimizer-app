from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404
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
        stocks = Stock.objects.filter(
            Q(delisted=False) & (Q(ticker__icontains=query) | Q(name__icontains=query))
        )[:50]
        results = [{'id': stock.id, 'text': f"{stock.ticker} - {stock.name}"} for stock in stocks]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})


class UserListsMain(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = FavoriteStockList
    template_name = 'user_stock_lists/user_stock_lists.html'
    context_object_name = 'lists'
    paginate_by = 9

    def test_func(self):
        list_id = self.kwargs.get('pk')
        if list_id is None:
            return True  # General view access check
        # Verify that the requested list belongs to the authenticated user
        return FavoriteStockList.objects.filter(id=list_id, user=self.request.user).exists()

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).order_by('pk')


class UserListsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = FavoriteStockList
    success_url = reverse_lazy('stock_lists')
    template_name = 'user_stock_lists/user_stock_list_delete.html'

    def test_func(self):
        favorite_list = get_object_or_404(FavoriteStockList, id=self.kwargs.get('pk'))
        return favorite_list.user == self.request.user

    def handle_no_permission(self):
        raise PermissionDenied("You do not have permission to delete this list.")


class UserStockListUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = FavoriteStockList
    form_class = FavoriteStockListForm
    template_name = 'user_stock_lists/user_stock_list_edit.html'
    success_url = reverse_lazy('stock_lists')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        stock_ids = self.request.POST.getlist('stocks')
        if stock_ids:
            form.instance.stocks.set(stock_ids)
        else:
            form.instance.stocks.clear()

        return response

    def test_func(self):
        favorite_list = get_object_or_404(FavoriteStockList, id=self.kwargs.get('pk'))
        return favorite_list.user == self.request.user

    def handle_no_permission(self):
        raise PermissionDenied("You do not have permission to edit this list.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'].initial['name'] = self.object.name
        context['form'].initial['description'] = self.object.description
        context['selected_stocks'] = [
            {
                'id': stock.id,
                'text': f"{stock.ticker} - {stock.name}"
            }
            for stock in self.object.stocks.all()
        ]

        return context
