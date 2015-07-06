'''
Created on Nov 20, 2010

@author: t-bone
'''
from django.shortcuts import render_to_response
from django import newforms as forms
from casino import simulation
from google.appengine.api import taskqueue
#from google.appengine.ext import db
from django.http import HttpResponseRedirect, HttpResponse
from google.appengine.api import memcache
import math

#Defines the betting strategies and the some rules of the blackjack table.
BETTYPE_CHOICES = [
                   ('Constant','Constant'),
                   ('JP', 'Increase after win'),
                   ('Doubling','Doubling'),
]

NDECK_CHOICES = [(x,x) for x in range(2,9)]
NSIM_CHOICES = [(10**x,10**x) for x in range(2,7)]
#SOFT17 = [('Stand', 'Stand')]
#DOUBLE_AFTER_SPLIT = [('Yes','Yes')]
#SURRENDER = [('No','No')]
#YES_NO =[('Yes','Yes'),('No','No')]
MINIMUM = [(10,10)]
MAXIMUM = [(1000,1000),(10000,10000)]

#This the main view. It gets the input from the form and starts adding jobs to the queue.
def simulation_main(request):
    
    ispost = request.method == 'POST'
    if ispost:
        
        #Getting the input from the form
        betType = request.POST.get('betType', '')
        initialBet = request.POST.get('minimumBet', '')
        maximumBet = request.POST.get('maximumBet', '')
        nDeck = int(request.POST.get('nDeck', ''))
        nSim = int(request.POST.get('nSim', ''))
        soft17 = request.POST.get('soft17', '')
        surrender = request.POST.get('surrender', '')
        das = request.POST.get('das', '')
        ras = request.POST.get('rsa', '')
        
        #Splitting the simulation into part for parallel computation
        NRun = 1
        if nSim > 1000:
            NRun = nSim / 1000
            nSim = 1000
            
        memcache.set("NRun", NRun)
        memcache.set("counter", 0)
        #Adding jobs to the queue
        for iRun in range(NRun):
            q = taskqueue.Queue()
            t = taskqueue.Task(url='/Simulation/Queue/', params={'betType': betType,
                                                                 'nDeck': nDeck,
                                                                 'iRun':iRun,
                                                                 'NRun':NRun,
                                                                 'maxBet':maximumBet})
            q.add(t)
        form = inputForm(request.POST)
        
    else:
        form = inputForm()
    
    
    return render_to_response("Sim.html",{'form' : form,'method' : ispost })

#Each job simulates 1000 games.
def simulation_queue(request):
    
    #Getting the parameters
    betType = request.POST.get('betType', 'JP')
    nDeck = int(request.POST.get('nDeck', '2'))    
    maxBet = int(request.POST.get('maxBet','0'))
    iRun = int(request.POST.get('iRun','0'))
    NRun = int(request.POST.get('NRun','0'))
    
    #Simulating
    sim = simulation.simulation(betType,nDeck,1000,maxBet = maxBet)
    sim.run()
    
    #Saving results to cache
    memcache.incr("counter")
    count = memcache.get("counter")
    memcache.set("run" + str(iRun), sim)
    memcache.set("progress", count*100/NRun)
    
    return HttpResponse()

#Form to set the betting strategy and the tables parameters    
class inputForm(forms.Form):
    
    betType = forms.ChoiceField(choices=BETTYPE_CHOICES,label = 'Betting Strategy')
    nDeck = forms.ChoiceField(choices=NDECK_CHOICES,label = 'Number of Decks')
    nSim = forms.ChoiceField(choices=NSIM_CHOICES,label = 'Number of Simulation')
    minimumBet = forms.ChoiceField(choices=MINIMUM,label = 'Minimum Bet')
    maximumBet = forms.ChoiceField(choices=MAXIMUM,label = 'Maximum Bet')
    #soft17 = forms.ChoiceField(widget = forms.CheckboxInput , label = 'Dealer stands on soft 17',initial = True)
    #das = forms.ChoiceField(widget = forms.CheckboxInput , label = 'Doubling after splitting permitted',initial = True)
    #rsa = forms.ChoiceField(widget = forms.CheckboxInput , label = 'Re-splitting of aces permitted',initial = True)
    #surrender = forms.ChoiceField(widget = forms.CheckboxInput , label = 'Possible to surrender',initial = False)


#This is an iframe that shows the results or the progress of the simulation if not completed.
def bar(request):
    
    #Getting the progress info from the cache
    progress = memcache.get("progress")
    refresh = ''
    simulating = 0 <= progress < 100
    done = progress == 100
    
    if  done:
        #Showing results if we are done
        progress = 100
        iRun = 0
        sim = simulation.simulation()
        NRun = memcache.get("NRun")
        
        #Aggregating all jobs
        while iRun < NRun:
            simTemp = memcache.get("run" + str(iRun))
            sim.houseAdvantage.extend(simTemp.houseAdvantage)
            sim.finalMoney.extend(simTemp.finalMoney)
            iRun = iRun + 1
            
        #Aggregating stats
        sim.hist.build(sim)    
        houseAdvantage = round(sum(sim.houseAdvantage)/len(sim.houseAdvantage),4)
        expectedGain = round(sum(sim.finalMoney)/len(sim.finalMoney),2)
        standardDev = int(round(math.sqrt(sum([(x - expectedGain)**2 for x in sim.finalMoney])/len(sim.finalMoney)),0))
        maximumGain = int(round(max(sim.finalMoney),0))
        minGain = int(round(min(sim.finalMoney),0))
        
        #Building stats dictionary
        sim.stats = [{'name' : 'House Advantage','value': houseAdvantage},
                     {'name' : 'Expected Loss (or Gain)','value': expectedGain},
                     {'name' : 'Standard Deviation', 'value' : standardDev},
                     {'name' : 'Maximum Gain','value': maximumGain}
                     ,{'name' : 'Maximum Loss' , 'value' : minGain}]
        
        return render_to_response("Bar.html",{'sim' : sim,
                                              'progress' : str(progress) + '%',
                                              'refresh' :  refresh,
                                              'simulating' : simulating,
                                              'done' : done})

    elif simulating:
        #We are refreshing every 5 seconds while simulating
        refresh = '<meta http-equiv="refresh" content="5" >'
        return render_to_response("Bar.html",{'progress' : str(progress) + '%',
                                              'refresh' :  refresh,
                                              'simulating' : simulating})
    else:
        #When the simulation hasn't started yet.
        return render_to_response("Bar.html",{'progress' : str(progress) + '%',
                                              'refresh' :  refresh,
                                              'simulating' : simulating,
                                              'done' : done})