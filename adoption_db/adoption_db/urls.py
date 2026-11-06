from django.contrib import admin
from django.conf.urls import include
from django.urls import path

from adoptionapp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('login/', views.login, name='login'),  # normal login
    path('parents/login/', views.parentsLogin, name='parentsLogin'),
    path('about',views.about,name='about'),
    path('contact', views.contact, name='contact'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('reg_amount',views.reg_amount,name='reg_amount'),
    path('forgetpass',views.forgetpass,name='forgetpass'),
    path('otp',views.otp,name='otp'),
    path('pass_db',views.pass_db,name='pass_db'),
    path('reg',views.reg,name='reg'),
    path('reg_amount_view',views.reg_amount_view,name='reg_amount_view'),
    path('reg_view_user/<str:email>',views.reg_view_user,name='reg_view_user'),
    path('changepass',views.changepass,name='changepass'),
    path('make_volunteer/', views.make_volunteer, name='make_volunteer'),
    path('give_reward/', views.give_reward, name='give_reward'),
    path('view_rewards/<int:charity_id>',views.view_rewards,name='view_rewards'),
    path("certificate/<int:reward_id>/", views.reward_certificate, name="reward_certificate"),




    path('babyinfo', views.babyinfo, name='babyinfo'),
    path('parentsinfo', views.parentsinfo, name='parentsinfo'),
    path('reqstatus', views.reqstatus, name='reqstatus'),
    path('homevststatus/<int:pk>', views.homevststatus, name='homevststatus'),
    path('surityinfo', views.surityinfo, name='surityinfo'),
    path('charityinfo', views.charityinfo, name='charityinfo'),
    path('donationinfo', views.donationinfo, name='donationinfo'),
    path('orphanageinfo', views.orphanageinfo, name='orphanageinfo'),
    path('orphnhltsts', views.orphnhltsts, name='orphnhltsts'),
    path('UserRegistration_view', views.UserRegistration_view, name='UserRegistration_view'),

    path('BabyInfo_view', views.BabyInfo_view, name='BabyInfo_view'),
    path('BabyInfo_view_p', views.BabyInfo_view_p, name='BabyInfo_view_p'),
    path('BabyInfo_view_m', views.BabyInfo_view_m, name='BabyInfo_view_m'),
    path('adoption_status_view_p', views.adoption_status_view_p, name='adoption_status_view_p'),

    path('babyinfo_del/<int:pk>',views.babyinfo_del,name='babyinfo_del'),
    path('BabyInfo_update/<int:pk>', views.BabyInfo_update, name='BabyInfo_update'),
    path('babyinfo_db',views.babyinfo_db,name='babyinfo_db'),

    path('ParentsInfo_view/<int:pk>', views.ParentsInfo_view, name='ParentsInfo_view'),
    path('parents_del/<int:pk>',views.parents_del,name='parents_del'),
    path('parents_update/<int:pk>', views.parents_update, name='parents_update'),
    path('parentsinfo_db',views.parentsinfo_db,name='parentsinfo_db'),

    path('Requeststatus_view', views.Requeststatus_view, name='Requeststatus_view'),
    path('req_status_update/<int:pk>', views.req_status_update, name='req_status_update'),
    path('req_status_db',views.req_status_db,name='req_status_db'),
    path('req_status_del/<int:pk>', views.req_status_del, name='req_status_del'),

    path('Homevstngstatus_view', views.Homevstngstatus_view, name='Homevstngstatus_view'),
    path('Homevstngstatus_view_p', views.Homevstngstatus_view_p, name='Homevstngstatus_view_p'),
    path('homevstngstatus_update/<int:pk>', views.homevstngstatus_update, name='homevstngstatus_update'),
    path('homevstngstatus_db',views.homevstngstatus_db,name='homevstngstatus_db'),
    path('homevstngstatus_del/<int:pk>', views.homevstngstatus_del, name='homevstngstatus_del'),

    path('SurityInfo_view', views.SurityInfo_view, name='SurityInfo_view'),
    path('SurityInfo_view_s/<int:id>', views.SurityInfo_view_s, name='SurityInfo_view_s'),
    path('surityInfo_update/<int:pk>', views.surityInfo_update, name='surityInfo_update'),
    path('surityInfo_db',views.surityInfo_db,name='surityInfo_db'),
    path('surityInfo_del/<int:pk>', views.surityInfo_del, name='surityInfo_del'),
    path('upload_court_docs/<int:pk>', views.upload_court_docs, name='upload_court_docs'),
    path('court_doc_view', views.court_doc_view, name='court_doc_view'),

    path('CharityInfo_view', views.CharityInfo_view, name='CharityInfo_view'),
    path('CharityInfo_view_m', views.CharityInfo_view_m, name='CharityInfo_view_m'),

    path('charityInfo_update/<int:pk>', views.charityInfo_update, name='charityInfo_update'),
    path('CharityInfo_db', views.CharityInfo_db, name='CharityInfo_db'),
    path('CharityInfo_del/<int:pk>', views.CharityInfo_del, name='CharityInfo_del'),

    path('DonationInfo_view', views.DonationInfo_view, name='DonationInfo_view'),
    path('DonationInfo_view_m', views.DonationInfo_view_m, name='DonationInfo_view_m'),
    path('donationInfo_update/<int:pk>', views.donationInfo_update, name='donationInfo_update'),
    path('donationInfo_db', views.donationInfo_db, name='donationInfo_db'),
    path('donationInfo_del/<int:pk>', views.donationInfo_del, name='donationInfo_del'),

    path('OrphanageInfo_view', views.OrphanageInfo_view, name='OrphanageInfo_view'),
    path('OrphanageInfo_view_d', views.OrphanageInfo_view_d, name='OrphanageInfo_view_d'),
    path('OrphanageInfo_update/<int:pk>', views.OrphanageInfo_update, name='OrphanageInfo_update'),
    path('OrphanageInfo_db', views.OrphanageInfo_db, name='OrphanageInfo_db'),
    path('OrphanageInfo_del/<int:pk>', views.OrphanageInfo_del, name='OrphanageInfo_del'),

    path('OrphnHltSts_view', views.OrphnHltSts_view, name='OrphnHltSts_view'),
    path('OrphnHltSts_update/<int:pk>', views.OrphnHltSts_update, name='OrphnHltSts_update'),
    path('OrphnHltSts_db', views.OrphnHltSts_db, name='OrphnHltSts_db'),
    path('OrphnHltSts_del/<int:pk>', views.OrphnHltSts_del, name='OrphnHltSts_del'),
    path('parent_home', views.parent_home, name='parent_home'),
    path('admin_home', views.admin_home, name='admin_home'),
    path('donor_home', views.donor_home, name='donor_home'),
    path('manager_home', views.manager_home, name='manager_home'),
    path('adoption_request/<int:pk>', views.adoption_request, name='adoption_request'),
    path('adoption_request_view_m', views.adoption_request_view_m, name='adoption_request_view_m'),
    path('adoption_request_update', views.adoption_request_update, name='adoption_request_update'),
    path('location_view/<str:email>', views.location_view, name='location_view'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('donation_history',views.donation_history,name='donation_history'),

]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
