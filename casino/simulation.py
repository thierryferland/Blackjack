'''
Created on Nov 14, 2010

@author: t-bone
'''
import math
from graph import googlechart
from table import table as greenTable

class simulation(object):

    def __init__(self,betType = 'JP',nDeck = 2,nSim = 100,minBet = 10,maxBet = 1000,audit = False):
        
        self.audit = audit
        self.nDeck = nDeck
        self.initialBet = minBet
        self.betType = betType
        self.nSplit = 3
        self.auditCards = [[]]
        self.nSim = nSim;
        self.finalMoney = []
        self.houseAdvantage = []
        self.hist = histogram()
        self.maxBet = maxBet
        
        #Hardcoded parameters
        self.initialMoney = 200
        self.nShoe = 1
        self.cutoff = .20
        self.nPlayer = 1

    def letsGamble(self):
       
        bet = self.initialBet
        nDeck = self.nDeck
        nSplit = self.nSplit
        nPlayer = self.nPlayer
        initialBet = self.initialBet
        initialMoney = self.initialMoney
        nShoe = self.nShoe
        cutoff = self.cutoff
        betStrategy = self.betType
        maxBet = self.maxBet
        cashflow = []
        cumCashflow = []
        auditSplit = []
        houseAdvantage = []
        
        #Simulating a blackjack table
        for iShoe in range(nShoe):
            
            #Initiating the table
            table = greenTable(nDeck,nSplit,initialBet,maxBet)
            
            cutoffFlag = 0
            while not(cutoffFlag):
                
                #Actual play
                table.clean()
                table.deal()
                table.hands[1][0].bet = bet
                table.hands[1][0].betStrategy = betStrategy
                table.hands[1][0].play(table)
                table.hands[0].play(table)
                
                #Calculating cash flows
                table.cashflow()
                cashflow.append(table.hands[1][0].cashflow)
                cumCashflow.append(sum(cashflow))
                houseAdvantage.append(table.hands[1][0].cashflow/bet)
                
                #This section is for audit purposes and it's not used in the production environment
                if self.audit:
                    for iSplit in range(len(table.hands[1])):
                        self.auditCards[-1].append([[x[0] for x in table.hands[1][iSplit].cards],
                                                    [x[0] for x in table.hands[0].cards],
                                                    table.hands[1][iSplit].split,
                                                    table.hands[1][iSplit].double,
                                                    table.hands[1][0].cashflow])
                        if [x[0] for x in table.hands[1][iSplit].cards].count('A') > 0 and  len(table.hands[1]) > 1:
                            print [[x[0] for x in table.hands[1][iSplit].cards],
                                                    [x[0] for x in table.hands[0].cards],
                                                    table.hands[1][iSplit].double,
                                                    table.hands[1][iSplit].split,
                                                    table.hands[1][0].cashflow,
                                                    bet]
                            
                        auditSplit.append([table.hands[0].total,table.hands[1][iSplit].total,table.hands[1][iSplit].split,table.hands[1][iSplit].double])
                 
                #We have to create a new shoe when we are close to the end of it.           
                cutoffFlag = table.shoe.size() < min(cutoff * nDeck * 52,75);
                
                #the bet is reset to what it was before any doubling up
                table.hands[1][0].bet = bet
                bet = table.hands[1][0].placebet(table)

            del table
        
        #Saving results.    
        self.auditCards.append([])    
        self.finalMoney.append(float(cumCashflow[-1]))
        self.houseAdvantage.append(-float(sum(houseAdvantage))/len(houseAdvantage))
    
    def run(self):
    
        #Repeating the game n times
        for iGame in range(self.nSim):
            self.letsGamble()
        
        #Aggregating results
        houseAdvantage = round(sum(self.houseAdvantage)/self.nSim,4)
        expectedGain = round(sum(self.finalMoney)/self.nSim,2)
        standardDev = int(round(math.sqrt(sum([(x - expectedGain)**2 for x in self.finalMoney])/self.nSim),0))
        maximumGain = int(round(max(self.finalMoney),0))
        minGain = int(round(min(self.finalMoney),0))
        
        #Building stats dictionary
        self.stats = [{'name' : 'House Advantage','value': houseAdvantage},
                      {'name' : 'Expected Loss (or Gain)','value': expectedGain},
                      {'name' : 'Standard Deviation', 'value' : standardDev},
                      {'name' : 'Maximum Gain','value': maximumGain}
                      ,{'name' : 'Maximum Loss' , 'value' : minGain}]

class histogram(object):

    def __init__(self):
        
        self.data = []
        self.bucket = []
        self.nBucket = 20
        self.url = ''
        
    def build(self,sim):
        
        #Creates an histogram using the Google chart API
        minData = min(sim.finalMoney)
        maxData = max(sim.finalMoney)
        inc = int((maxData - minData)/self.nBucket)/10*10
        self.bucket = range(0-inc,int(minData)-inc,-inc)
        self.bucket.extend(range(0,int(maxData)+inc,inc))
        self.bucket.sort()
        data = [int(y/inc) for y in sim.finalMoney]
        self.data = [int(float(data.count(y))/len(data)*100) for y in range(min(data),max(data)+1)]
        chart = googlechart.StackedVerticalBarChart(1000, 200,
                                        y_range=(0, max(self.data)))
        chart.set_bar_width(25)
        chart.set_colours(['3072F3'])
        chart.add_data(self.data)
        chart.set_axis_range('y', 0, max(self.data))
        chart.set_title('Distribution of the final gains or losses')
        chart.set_axis_labels('x', self.bucket)
        chart.fill_solid('bg','FFFFFF00')
        self.url = chart.get_url()
