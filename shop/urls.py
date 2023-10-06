from django.urls import path
from .import views


urlpatterns = [
    path("",views.index,name="shophome"),
    path("about/",views.about,name="AboutUs"),
    path("contact/",views.contact,name="Contactus"),
    path("tracker/",views.tracker,name="TrackUs"),
    path("search/",views.search,name="Search"),
    path("productview/<int:myid>",views.productview,name="ProductView"),
    path("checkout/",views.checkout,name="Checkout"),
    path("handlerequest/",views.handlerequest,name="HandleRequest"),




    
]