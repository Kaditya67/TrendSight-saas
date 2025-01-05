from django.urls import path
from django.shortcuts import resolve_url
from . import views

urlpatterns = [
    # path('',views.index,name="index"),
    # # path('import_data/', views.import_data, name='import_sector_data'),
    path('login/',views.user_login,name="user_login"),
    path('logout/',views.user_logout,name="user_logout"),
    # path('verify/',views.verify,name="verify"),
    # path('verify_password/',views.verify_password,name="verify_password"),
    path('subscription/', views.subscription, name='subscription'),
    # path('leave_page/', views.leave_page, name='leave_page'),
    # path('alerts/', views.alerts, name='alerts'),
    path('signup/',views.signup,name="user_signup"),
    path('forgotpassword/',views.forget_password,name="forgetpassword"),
    # path('send_watchlist_email/',views.send_watchlist_email, name='send_watchlist_email'),
    # # path('home/',views.home,name="home"),
    path('stocks', views.stocks, name='stocks'),
    path('',views.main_page,name='main_page'),
    path('sectors/', views.sectors, name='sectors'),
    # path('add_portfolio/', views.add_portfolio, name='add_portfolio'),
    # path('close_position/', views.close_position, name='close_position'),
    path('portfolio/', views.portfolio, name='portfolio'),
    # path('closed-positions/', views.closed_positions, name='closed_positions'),
    path('settings/', views.settings, name='settings'),
    path('help/', views.help, name='help'),
    path('about/', views.about, name='about'),
    path('main_alerts/', views.main_alerts, name='main_alerts'),
    # path('log/', views.log, name='log'),

    path('graph/<str:type>/<str:symbol>/<int:ema_value>/', views.graph_partial, name='graph'),
    # path('symbols/', views.symbols_and_ema_counts, name='symbols_and_closing_prices'),
    path('dashboard_new/', views.dashboard, name='dashboard'),  # URL for the sectoral dashboard
    # path('dashboard/<int:ema>/', views.dashboard, name='dashboard_with_ema'),
    # # path('home_template/', views.home_temp, name='home_template'),
    # path('stock_template/', views.stock_temp, name='stock_template'),
    path('watchlist/', views.watchlist, name='watchlist'),
    # path('fetch-sector-data/', views.fetch_sector_data, name='fetch_sector_data'),
    # path('fetch_stock_data/', views.fetch_stock_data, name='fetch_stock_data'),
    # path('remove-from-watchlist/', views.remove_from_watchlist, name='remove_from_watchlist'),
    # path('contact/', views.contact, name='contact'),
    ]

    # path('graph/<str:symbol>/<int:ema_value>/', views.graph, name='graph'),

