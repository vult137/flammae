from django.conf.urls import url
from function import views


app_name = 'function'
urlpatterns = [
    url(r'^add_switch/', views.add_switch, name='add_switch'),
    url(r'^all_switch/', views.switch_view_all, name='all_switch'),
    url(r'^modify_switch/(?P<pk>[0-9]+)/$', views.switch_modify, name='modify_switch'),
    url(r'^apic_login', views.apic_login, name='apic_login'),
    url(r'^apic_query/', views.apic_query, name='apic_query'),
    url(r'^apic_query_detail/(?P<pk>[0-9]+)/$', views.apic_query_detail, name='apic_query_detail'),
    url(r'^apic_query_vlan/(?P<pk>[0-9]+)/$', views.apic_query_vlan, name='apic_query_vlan'),
    url(r'^apic_query_vlan_deliver/(?P<pk>[0-9]+)/$', views.deliver_apic_vlan_config, name='vlan_deliver'),

]
