'''
Created on Nov 15, 2010

@author: t-bone
'''
import copy
import random

#Defining the basic strategy in Blackjack
FACE_UP = [2,3,4,5,6,7,8,9,10,11]
HARD_STRATEGY = [[1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1],
                [1,2,2,2,2,1,1,1,1,1],
                [2,2,2,2,2,2,2,2,1,1],
                [2,2,2,2,2,2,2,2,2,1],
                [1,1,0,0,0,1,1,1,1,1],
                [0,0,0,0,0,1,1,1,1,1],
                [0,0,0,0,0,1,1,1,1,1],
                [0,0,0,0,0,1,1,1,1,1],
                [0,0,0,0,0,1,1,1,1,1],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0]] 
SOFT_STRATEGY = [[1,1,1,2,2,1,1,1,1,1],
                [1,1,1,2,2,1,1,1,1,1],
                [1,1,2,2,2,1,1,1,1,1],
                [1,1,2,2,2,1,1,1,1,1],
                [1,2,2,2,2,1,1,1,1,1],
                [0,2,2,2,2,0,0,1,1,1],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0]]   
SOFT_STRATEGY_NO_DOUBLING = [[1,1,1,1,1,1,1,1,1,1],
                            [1,1,1,1,1,1,1,1,1,1],
                            [1,1,1,1,1,1,1,1,1,1],
                            [1,1,1,1,1,1,1,1,1,1],
                            [1,1,1,1,1,1,1,1,1,1],
                            [0,0,0,0,0,0,0,1,1,1],
                            [0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0]]
PAIR_STRATEGY= [[3,3,3,3,3,3,1,1,1,1],
               [3,3,3,3,3,3,1,1,1,1],
               [1,1,1,3,3,1,1,1,1,1],
               [2,2,2,2,2,2,2,2,1,1],
               [3,3,3,3,3,1,1,1,1,1],
               [3,3,3,3,3,3,1,1,1,1],
               [3,3,3,3,3,3,3,3,3,3],
               [3,3,3,3,3,0,3,3,0,0],
               [0,0,0,0,0,0,0,0,0,0],
               [3,3,3,3,3,3,3,3,3,3]]

#The table object
class table(object):
    
    def __init__(self,nDeck,nSplit,minBet,maxBet):
        
        #Its attributes
        self.shoe = shoe()
        self.shoe.get(nDeck)
        self.nSplit = nSplit
        self.maxBet = maxBet
        self.minBet = minBet
        self.hands = [[]]
        self.hands[0] = dealer()
        self.hands.append([player()])
    
    #Calculating the cash flows after a hand
    def cashflow(self):
        
        cashflow = 0
        for iHand in range(len(self.hands[1])):
            
            if self.hands[1][iHand].bust:
                #Player's bust
                cashflow = cashflow + -1 * self.hands[1][iHand].bet
            elif self.hands[1][iHand].blackjack and not(self.hands[0].blackjack):
                #Player's Blackjack
                cashflow = cashflow + 1.5 * self.hands[1][iHand].bet
            elif self.hands[0].bust:
                #dealer's bust
                cashflow = cashflow + 1 * self.hands[1][iHand].bet
            elif  self.hands[0].blackjack and not(self.hands[1][iHand].blackjack):
                #Dealer's Blackjack
                cashflow = cashflow - 1 * self.hands[1][iHand].bet
            elif self.hands[1][iHand].total > self.hands[0].total:
                cashflow = cashflow + 1 * self.hands[1][iHand].bet
            elif self.hands[1][iHand].total == self.hands[0].total:
                #Push
                cashflow = cashflow + 0
            else:
                cashflow = cashflow - 1 * self.hands[1][iHand].bet
        
        self.hands[1][0].cashflow = cashflow
    
    #Cleaning the table
    def clean(self):

        self.hands = [[]]
        self.hands[0] = dealer()
        self.hands.append([player()])
        
    #Dealing cards
    def deal(self):
        
        self.hands[1][0].cards[0] = self.shoe.cards.pop()
        self.hands[0].cards.append(self.shoe.cards.pop())
        self.hands[1][0].cards.append(self.shoe.cards.pop())
        self.hands[0].cards.append(self.shoe.cards.pop())

#The player object      
class player(object):
    
    #Its attributes
    def __init__(self,betStrategy = 'Constant'):
        
        self.cards = [[]]
        self.bet = 0
        self.betStrategy = betStrategy
        self.split = 0
        self.nSplit = 0
        self.double = False
        self.blackjack = False
        self.bust = False
        self.total = 0
    
            
    def play(self,table):
        
        self.count(table)
        table.hands[0].count()
        
        if not(table.hands[0].blackjack):
            
            move = self.talk(table)
            
            if  move == 1:
                
                self.cards.append(table.shoe.cards.pop())
                self.play(table)
                
            elif move == 2:
                
                self.bet = self.bet * 2;
                self.cards.append(table.shoe.cards.pop())
                self.double = True
                self.count(table)
                
            elif move == 3:
                
                del self.cards[1:]
                table.hands[1][0].nSplit = table.hands[1][0].nSplit + 1
                self.split = self.split + 1
                newHand = copy.deepcopy(self)
                self.cards.append(table.shoe.cards.pop())
                self.play(table)
                newHand.cards.append(table.shoe.cards.pop())
                newHand.play(table)
                table.hands[1].append(newHand)

    #A player talk according to the basic strategy defined above
    def talk(self,table):
            
        if self.bust:
            #Player bust
            move = 0
            
        elif self.cards[1][0] == self.cards[0][0] and self.nHit() == 2 and table.hands[1][0].nSplit <= table.nSplit:
            #Case when it's a pair
            ixFaceUp = FACE_UP.index(table.hands[0].cards[1][2])
            move = PAIR_STRATEGY[self.cards[0][2]-2][ixFaceUp]
            
        elif self.cards[0][2] == 11 and self.split > 0:
            #A player can't hit the new hands after splitting aces
            move = 0
            
        elif [x[2] for x in self.cards].count(11) > 0 and sum([x[1] for x in self.cards])+10 < 22:
            #Case when there is one or many aces
            ixFaceUp = FACE_UP.index(table.hands[0].cards[1][2])
            if self.nHit()>2:
                move = SOFT_STRATEGY_NO_DOUBLING[sum([x[1] for x in self.cards])-1-2][ixFaceUp]   
            else:
                move = SOFT_STRATEGY[sum([x[1] for x in self.cards])-1-2][ixFaceUp]#-1 for to remove one ace from total
        else:
            #General case
            ixFaceUp = FACE_UP.index(table.hands[0].cards[1][2])
            move = HARD_STRATEGY[sum([x[1] for x in self.cards])-4][ixFaceUp]
            if move == 2 and self.nHit()>2:
                move =1
                
        return move

    #This is where the betting strategy comes into play. The player places his initial bet.
    def placebet(self,table):
    
        if self.betStrategy == 'JP':
            if self.cashflow > 0:
                self.bet = min(self.bet + table.minBet,table.maxBet)
            elif self.cashflow < 0:
                self.bet = table.minBet
        elif self.betStrategy == 'JP2':
            if self.cashflow < 0 or 5 * table.minBet == self.bet:
                self.bet = table.minBet
            elif self.cashflow > 0:
                self.bet = min(self.bet + table.minBet,table.maxBet)
        elif self.betStrategy == 'Doubling':  
            if self.cashflow > 0:
                self.bet = table.minBet
            elif self.cashflow < 0:
                self.bet = min(2 * self.bet,table.maxBet)
        else:
            self.bet = table.minBet
            
        return self.bet

    #Utility function to show how many cards the player has.
    def nHit(self):
        
        return len(self.cards)

    #This is to count the player cards.
    def count(self,table):
        
        count = []
        count.append(sum([x[1] for x in self.cards]))
        count.append(sum([x[2] for x in self.cards]))
        self.total = max([x if x < 22 else 0 for x in count])
        self.blackjack = self.total == 21 and self.nHit() == 2 and not(table.hands[0].blackjack) and self.split == 0
        self.bust = min(count) > 21
        return self.total

#The dealer object
class dealer(object):
    
    #Its attributes
    def __init__(self):
        self.cards = []
        self.blackjack = False
        self.bust = False
        self.total = 0
    
    #The dealer plays according to predefined simple rules.
    def play(self,table):
        
        table.hands[0].count()
       
        if table.hands[0].total >= 17 or table.hands[0].bust:
            pass
        else:
            table.hands[0].cards.append(table.shoe.cards.pop())
            table.hands[0].play(table)
    
    #Utility function that show how many cards the dealer has.        
    def nHit(self):
        
        return len(self.cards)
    
    #Counts the dealer's cards.   
    def count(self):
        
        count = []
        count.append(sum([x[1] for x in self.cards]))
        count.append(sum([x[2] for x in self.cards]))
        self.total = max([x if x < 22 else 0 for x in count]) 
        self.blackjack = self.total == 21 and self.nHit() == 2
        self.bust = min(count) > 21
        return self.total

#The shoe object    
class shoe(object):
    
    def __init__(self):
        
        pass
    
    #Creates a new shuffled shoe.    
    def get(self,nDeck):

        deck = []
        tmpShoe =[[],[],[]]
        #Creating the standard cards of a deck.
        deck.append(range(2,11)*4)
        deck[0].extend(['J','Q','K','A']*4)
        
        #Adding n decks to the shoe 
        shoe = deck[0]*nDeck
        
        #Shuffling the cards
        random.shuffle(shoe)
        tmpShoe[0] = shoe[:]
        shoe = [10 if x in ['J','Q','K'] else x for x in shoe]
        tmpShoe[1] = [1 if x == 'A' else x for x in shoe]
        tmpShoe[2] = [11 if x == 'A' else x for x in shoe]
        del shoe
        shoe = zip(*tmpShoe)
        
        self.cards = shoe
        
    def size(self):
        
        return len(self.cards)
            