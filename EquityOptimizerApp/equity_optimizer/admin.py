from django.contrib import admin
from .models import Stock, StockData


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name', 'sector', 'industry', 'market_cap', 'beta', 'trailing_pe', 'forward_pe')
    search_fields = ('ticker', 'name', 'sector', 'industry', 'market_cap', 'city', 'country')
    list_filter = ('sector', 'industry', 'country', 'delisted')
    ordering = ('ticker',)
    list_per_page = 50

    fieldsets = (
        ('Basic Information', {
            'fields': ('ticker', 'name', 'sector', 'industry', 'website', 'logo_url', 'delisted')
        }),
        ('Market Data', {
            'fields': ('market_cap', 'enterprise_value', 'trailing_pe', 'forward_pe', 'peg_ratio', 'price_to_book', 'beta')
        }),
        ('Valuation Metrics', {
            'fields': ('trailing_eps', 'forward_eps', 'book_value', 'fifty_two_week_high', 'fifty_two_week_low', 'fifty_day_average')
        }),
        ('Financial Data', {
            'fields': ('revenue', 'gross_profit', 'ebitda', 'net_income', 'diluted_eps', 'profit_margin', 'operating_margin')
        }),
        ('Balance Sheet Data', {
            'fields': ('total_cash', 'total_debt', 'total_assets', 'total_liabilities')
        }),
        ('Dividend Data', {
            'fields': ('dividend_yield', 'dividend_rate', 'payout_ratio', 'ex_dividend_date', 'last_dividend_date')
        }),
        ('Company Profile', {
            'fields': ('address1', 'city', 'state', 'country', 'phone', 'full_time_employees', 'long_business_summary')
        }),
        ('Sustainability & Recommendations', {
            'fields': ('esg_scores', 'recommendations')
        }),
    )

    # Custom actions
    actions = ['mark_as_delisted']

    def mark_as_delisted(self, request, queryset):
        queryset.update(delisted=True)
        self.message_user(request, f"{queryset.count()} stocks marked as delisted.")
    mark_as_delisted.short_description = "Mark selected stocks as delisted"


@admin.register(StockData)
class StockDataAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'adj_close_to_usd',
                    'volume', 'daily_return', 'trend')
    search_fields = ('stock__ticker', 'stock__name', 'date', 'trend')
    list_filter = ('stock__sector', 'stock__industry', 'date', 'trend')
    ordering = ('-date',)
    date_hierarchy = 'date'
    list_per_page = 50

    fieldsets = (
        ('Stock Information', {
            'fields': ('stock', 'date')
        }),
        ('Price Data', {
            'fields': ('open', 'high', 'low', 'close', 'adj_close', 'adj_close_to_usd')
        }),
        ('Volume & Performance', {
            'fields': ('volume', 'daily_return', 'trend')
        }),
    )

    # Custom action for recalculating daily return and trend
    actions = ['recalculate_daily_return_and_trend']

    def recalculate_daily_return_and_trend(self, request, queryset):
        for stock_data in queryset:
            stock_data.daily_return = StockData.objects.calculate_daily_return(stock_data.stock, stock_data.date, stock_data.adj_close)
            stock_data.trend = StockData.objects.calculate_trend(stock_data.daily_return)
            stock_data.save()
        self.message_user(request, f"Recalculated daily return and trend for {queryset.count()} entries.")
    recalculate_daily_return_and_trend.short_description = "Recalculate daily return and trend"

