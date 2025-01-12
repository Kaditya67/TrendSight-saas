from django.urls import path

from . import views

urlpatterns = [
    # fetch stock data
    path('fetch/stocks/', views.fetch_stocks, name='fetch_stocks'),
    path('fetch/sectors/', views.fetch_sectors, name='fetch_sectors'),
    path('update/stocks/', views.update_stocks, name='update_stocks'),
    path('update/sectors/', views.update_sectors, name='update_sectors'),
    path('compute/stock_indicators/', views.compute_stock_indicators, name='compute_stock_indicators'),
    path('compute/sector_indicators/', views.compute_sector_indicators, name='compute_sector_indicators'),
    path('update/stock_indicators/', views.update_stock_indicators, name='update_stock_indicators'),
    path('update/sector_indicators/', views.update_sector_indicators, name='update_sector_indicators'),

    path('profile/', views.profile, name='profile'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('watchlist/<int:watchlist_id>/', views.custom_watchlist, name='watchlist'),

    path('custom/portfolio/', views.custom_portfolio, name='custom_portfolio'),

    path('index/',views.index,name="home"),
    path('subscription/', views.subscription, name='subscription'),
    # path('logout/',views.user_logout,name="user_logout"),
    # # path('import_data/', views.import_data, name='import_sector_data'),
    # path('login/',views.user_login,name="user_login"),
    # path('signup/',views.signup,name="user_signup"),
    # path('verify/',views.verify,name="verify"),
    # path('verify_password/',views.verify_password,name="verify_password"),
    path('forgotpassword/',views.forget_password,name="forgetpassword"),
    # path('leave_page/', views.leave_page, name='leave_page'),
    # path('alerts/', views.alerts, name='alerts'),
    # path('send_watchlist_email/',views.send_watchlist_email, name='send_watchlist_email'),
    # # path('home/',views.home,name="home"),
    # path('stocks/', views.stocks, name='stocks'),
    path('sectors/', views.sectors, name='sectors'),
    # path('add_portfolio/', views.add_portfolio, name='add_portfolio'),
    # path('close_position/', views.close_position, name='close_position'),
    # path('closed-positions/', views.closed_positions, name='closed_positions'),
    path('dashboard_new/', views.dashboard, name='dashboard'),  # URL for the sectoral dashboard
    path('graph/<str:type>/<str:symbol>/<int:ema_value>/', views.graph_partial, name='graph'),
    path('portfolio/', views.portfolio, name='portfolio'),
    
    path('settings/', views.settings, name='settings'),
    path('help/', views.help, name='help'),
    path('about/', views.about, name='about'),
    path('main_alerts/', views.main_alerts, name='main_alerts'),
    path('stock/', views.stock, name='stock'),
    path('',views.main_page,name='main_page'),
    path('sidebar',views.sidebar,name='sidebar'),
    path('navbarr',views.navbarr,name='navbarr'),

    
    # path('log/', views.log, name='log'),

    # path('symbols/', views.symbols_and_ema_counts, name='symbols_and_closing_prices'),
    # path('dashboard/<int:ema>/', views.dashboard, name='dashboard_with_ema'),
    # # path('home_template/', views.home_temp, name='home_template'),
    # path('stock_template/', views.stock_temp, name='stock_template'),
    # path('fetch-sector-data/', views.fetch_sector_data, name='fetch_sector_data'),
    # path('fetch_stock_data/', views.fetch_stock_data, name='fetch_stock_data'),
    # path('remove-from-watchlist/', views.remove_from_watchlist, name='remove_from_watchlist'),
    # path('contact/', views.contact, name='contact'),
    ] 