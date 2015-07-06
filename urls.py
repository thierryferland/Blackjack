from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^Simulation/Queue/', simulation_queue),
    (r'^.*Bar/', bar),
    (r'^Simulation/', simulation_main),
    (r'', simulation_main),
)
