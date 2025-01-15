from django.shortcuts import redirect, render
from .calculateView import (compute_sector_indicators,
                            compute_stock_indicators, fetch_sectors,
                            fetch_stocks, update_sector_indicators,
                            update_sectors, update_stock_indicators,
                            update_stocks)
from .featureViews import (custom_watchlist, watchlist, stock, sectors, custom_portfolio)
from .forms import UserProfileForm

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        logged=True
    else:
        logged=False
    context = {
        'logged': logged
    }
    return render(request, 'stocks/index.html',context)

def user_login(request):
    return render(request, 'stocks/user_login.html')

def nuser_logout(request):
    return render(request, 'stocks/logout.html')

def subscription(request):
    return render(request, 'stocks/subscription.html')

def forget_password(request):
    return render(request, 'stocks/forgetpassword.html')

def signup(request):
    return render(request, 'stocks/signup.html')

def dashboard(request):
    return render(request, 'stocks/dashboard_new.html')

def graph_partial(request):
    return render(request, 'stocks/graph_partial.html')



def main_alerts(request):
    return render(request, 'stocks/main_alerts.html')

def portfolio(request):
    return render(request, 'stocks/portfolio.html')


def settings(request):
    return render(request, 'stocks/settings.html')

def help(request):  
    return render(request, 'stocks/help.html')

def add_watchlist(request):
    return render(request,'stocks/watchlist/watchlist.html')

def about(request):
    return render(request, 'stocks/about.html')

def profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Optionally redirect to profile page after successful save
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'stocks/stock_users/profile.html', {'form': form})

def main_page(request):
    return render(request,'stocks/main_page.html')

def sidebar(request):
    return render(request,'stocks/sidebar.html')
def navbarr(request):
    return render(request,'stocks/navbarr.html')