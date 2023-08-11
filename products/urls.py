from django.urls import path
from .views import view_admin, add_product, del_all_products, \
                    import_products, show_invalid_rows, export_products, \
                    product_details, edit_product, delete_product, add_tips, \
                    show_all_tips, tip_details, del_all_tips, edit_tip, \
                    delete_tip, login, logout, change_password, change_username

urlpatterns = [
    # -----------Product section--------------#
    path('admin', view_admin, name='admin'),
    path('add_product', add_product, name='add_product'),
    path('delete_all_products', del_all_products, name='del_all_products'),
    path('import_products', import_products, name='import_products'),
    path('invalid_rows', show_invalid_rows, name='invalid_rows'),
    path('export_products', export_products, name='export_products'),
    path('product_details/<pk>', product_details, name='product_details'),
    path('edit_product/<pk>', edit_product, name='edit_product'),
    path('delete_product/<pk>', delete_product, name='delete_product'),
    # -----------Health Tips section--------------#
    path('add_Tips', add_tips, name='add_tips'),
    path('health_tips', show_all_tips, name='show_tips'),
    path('tip_details/<pk>', tip_details, name='tip_details'),
    path('delete_all_tips', del_all_tips, name='del_all_tips'),
    path('edit_tip/<pk>', edit_tip, name='edit_tip'),
    path('delete_tip/<pk>', delete_tip, name='delete_tip'),
    # -----------user section-----------------#
    path('user/login', login, name='login'),
    path('user/logout', logout, name='logout'),
    path('user/change_password', change_password, name='change_password'),
    path('user/change_username', change_username, name='change_username'),

]
