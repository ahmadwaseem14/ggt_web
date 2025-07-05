from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('laptops/', views.laptops_list, name='laptops_list'),
    path('laptop/<int:pk>/', views.laptop_detail, name='laptop_detail'),  # We'll create this view later
    path('comparison/', views.comparison_view, name='comparison_view'),
    path('comparison/add/<str:product_sku>/', views.add_to_comparison, name='add_to_comparison'),
    path('comparison/remove/<int:item_id>/', views.remove_from_comparison, name='remove_from_comparison'),
    path('comparison/clear/<int:comparison_id>/', views.clear_comparison, name='clear_comparison'),
    path('comparison/debug/', views.debug_comparison, name='debug_comparison'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<str:product_sku>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('quick-view/<str:product_sku>/', views.quick_view, name='quick_view'),
    path('product/<str:product_sku>/', views.product_detail, name='product_detail'),
    path('products/<str:product_type>/', views.product_list, name='product_list'),
    path('all-products/', views.all_products, name='all_products'),
    path('categories/', views.all_categories, name='all_categories'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
     path('support/', views.customer_support_view, name='customer_support'),
     path('order-return-policy/', views.order_return_policy_view, name='order_return_policy'), # Add this line
       path('why-choose-ggt/', views.why_ggt_view, name='why_ggt'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
handler404 = 'store.views.handler404'