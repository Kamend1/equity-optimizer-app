from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from EquityOptimizerApp.portfolio.models import Portfolio
from EquityOptimizerApp.portfolio.forms import PortfolioForm
from EquityOptimizerApp.portfolio.services import save_portfolio_from_simulation


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

    return render(request, 'tools/../../templates/portfolio/portfolio.html', context)


@login_required
def save_portfolio_view(request):
    if request.method == 'POST':
        portfolio_form = PortfolioForm(request.POST)

        if portfolio_form.is_valid():
            user = request.user
            name = portfolio_form.cleaned_data['name']
            description = portfolio_form.cleaned_data['description']

            # Retrieve best_portfolio_data and initial_investment from the session
            best_portfolio_data = request.session.get('best_portfolio_data')
            initial_investment = request.session.get('initial_investment')

            # Debugging output: log session values
            print(f"Stored in session - best_portfolio_data: {best_portfolio_data}")
            print(f"Stored in session - initial_investment: {initial_investment}")

            if not best_portfolio_data or not initial_investment:
                messages.error(request, "Failed to retrieve simulation data.")
                return redirect('simulation')  # Redirect to 'simulation' on failure

            try:
                save_portfolio_from_simulation(
                    user=user,
                    name=name,
                    description=description,
                    best_portfolio_data=best_portfolio_data,
                    initial_investment=initial_investment
                )

                messages.success(request, "Portfolio saved successfully.")
                return redirect('portfolio')  # Redirect to the list of portfolios
            except Exception as e:
                messages.error(request, f"Failed to save portfolio: {str(e)}")
                print(f"Error during save_portfolio_from_simulation: {e}")
                return redirect('simulation')  # Return a redirect in case of an exception
        else:
            messages.error(request, "Invalid form submission.")
            return render(request, 'tools/../../templates/portfolio/save_portfolio.html', {'portfolio_form': portfolio_form})  # Re-render the form with errors

    else:
        portfolio_form = PortfolioForm()
        return render(request, 'tools/../../templates/portfolio/save_portfolio.html', {'portfolio_form': portfolio_form})


# Create your views here.
@login_required
def portfolio_detail(request, portfolio_id):
    # Fetch the portfolio for the authenticated user
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)

    context = {
        'portfolio': portfolio,
        # 'portfolio_value': portfolio.calculate_value(),
    }

    return render(request, 'tools/../../templates/portfolio/portfolio_detail.html', context)