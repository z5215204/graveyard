from flask import Flask, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_migrate import Migrate
from time import sleep
import os
import random
import string

#TOADD
# - Facedown Cards
# - 7 is higher/lower
# - 3 is a mirror
# - Swapping faceup and hand cards

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/gamedb'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Gameid(db.Model):
    __tablename__ = 'gameid'
    code = db.Column(db.String(4), primary_key=True)
    createTime = db.Column(db.DateTime, default=db.func.now())
    turn = db.Column(db.Integer, default=0)
    started = db.Column(db.BOOLEAN, default=False)
    lplayed = db.Column(db.Integer, default=-1)
    nlPlayed = db.Column(db.Integer, default=-1)
    playerRef = db.relationship('Players', cascade='all, delete-orphan', backref='gameid')
    deckRef = db.relationship('Decks', cascade='all, delete-orphan', backref='gameid')
    handRef = db.relationship('Hands', cascade='all, delete-orphan', backref='gameid')
# lPlayed is modulo 13

class Decks(db.Model):
    __tablename__ = 'decks'
    code = db.Column(db.String(4), db.ForeignKey('gameid.code'), primary_key=True)
    card = db.Column(db.Integer, primary_key=True)
    deckType = db.Column(db.String(10), primary_key=True)
# deckType = 'draw' or 'discard'

class Hands(db.Model):
    __tablename__ = 'hands'
    card = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), db.ForeignKey('gameid.code'), primary_key=True)
    cardType = db.Column(db.String(10), primary_key=True) 
    player = db.Column(db.String(15), primary_key=True)
#cardType = 'faceup' or 'facedown' or 'hand'


class Players(db.Model):
    __tablename__ = 'players'
    name = db.Column(db.String(15), primary_key=True)
    code = db.Column(db.String(4), db.ForeignKey('gameid.code'), primary_key=True)
    turn = db.Column(db.Integer)

# Card 0-12 is diamonds
# Card 13-25 is clubs
# Card 26-38 is hearts
# Card 39-51 is spades
# Card order is 2,3,4,5,6,7,8,9,10,J,Q,K,A

#@app.route('/')
#def index():
#    return send_from_directory(basedir, 'index.html')

@app.route('/api/create', methods=['POST', 'GET'])
def Create():
    if request.method == 'POST':
        game = makeGame()
        newGame = Gameid(code=game)
        db.session.add(newGame)
        db.session.commit()
        return ({
            'game': game
        })
    elif request.method == 'GET':
        game = makeGame()
        newGame = Gameid(code=game)
        db.session.add(newGame)
        db.session.commit()
        return ({
            'game': game
        })

def makeGame():
    while True:
        code = ''.join(random.choices(string.ascii_lowercase, k=4))
        exists = db.session.query(Gameid).filter_by(code=code).first()
        if exists is None:
            return code
        return code

def cleanDB():
    db.session.query(Players).delete()
    db.session.query(Decks).delete()
    db.session.query(Hands).delete()
    games = db.session.query(Gameid).all()
    for i in games:
        db.session.delete(i)
    db.session.commit()
    print('Cleaning')
    #while True:
     #   lh = datetime.now() - timedelta(hours=1)
      #  db.session.query(Gameid).filter(Gameid.creatime < lh).delete()
       # db.session.commit()
        #sleep(3600)

def findValidPlays(code, player):
    game = db.session.query(Gameid).filter_by(code=code).first()
    prev = game.lplayed
    hand = db.session.query(Hands).filter_by(code=code, player=player, cardType='hand').all()
    # If hand isn't empty, pick from hand
    if len(hand) > 0:
        cards = [x.card for x in hand] # list(map(lambda x: x.card, hand))
    # Else, return the list of facedown cards
    else:
        fd = db.session.query(Hands).filter_by(code=code, player=player, cardType='facedown').all()
        cards = [x.card for x in fd]

    valid = []
    for i in cards:
        mod = i % 13
        if prev == -1 or mod >= prev or mod == 0 or mod == 8:
            valid.append(i)
    return valid

def playCard(player, code, played):
    # Play card assumes the play is valid, so only handles the moving of cards, unless its facedown
    # If the card is a facedown card, then check if its valid first
    game = db.session.query(Gameid).filter_by(code=code).first()
    if db.session.query(Hands).filter_by(code=code, card=played[0], cardType='facedown').first():
        mod = played[0] % 13
        if not (game.lplayed == -1 or mod >= game.lplayed or mod == 0 or mod == 8):
            pickupCards(player, code)
            return

    if (played[0] % 13 == 8) or ((played[0] % 13 == game.lplayed) and (len(played) + game.nlPlayed >= 4)):
        # Burn cards
        db.session.query(Decks).filter_by(code=code, deckType='discard').delete()
        for i in played:
            db.session.query(Hands).filter_by(code=code, player=player, card=i).delete()
        game.lplayed = -1
        game.nlPlayed = -1
    else:
        # Play cards normally
        # Move cards to discard pile
        for i in played:
            card = db.session.query(Hands).filter_by(code=code, player=player, card=i).first()
            mC = Decks(code=code, card=card.card, deckType='discard')
            db.session.add(mC)
            db.session.delete(card)
        # If cards are same but not burned only chnage nlPlayed
        if (played[0] % 13) == game.lplayed:
            game.nlnPlayed = game.nlPlayed + len(played)
        else:
            game.lplayed = played[0] % 13
            game.nlPlayed = len(played)
    
    # Pickup till hand has 3 cards if there are cards in the deck
    if db.session.query(Decks).filter_by(code=code, deckType='draw').count() > 0:
        pickup = db.session.query(Decks).filter_by(code=code, deckType='draw').limit(len(played))
        for i in pickup:
            nH = Hands(card=i.card, code=code, cardType='hand', player=player)
            db.session.add(nH)
            db.session.delete(i)
    # if there are no cards in the deck or in your hand then faceup becomes hand
    elif db.session.query(Hands).filter_by(code=code, player=player, cardType='hand').count() == 0:
        if db.session.query(Hands).filter_by(code=code, player=player, cardType='faceup').count() > 0:
            faceup = db.session.query(Hands).filter_by(code=code, player=player, cardType='faceup').all()
            for c in faceup:
                c.cardType = 'hand'
    db.session.commit()



    

def pickupCards(player, code):
    # Move the cards from the discard pile to the players hand
    game = db.session.query(Gameid).filter_by(code=code).first()
    discard = db.session.query(Decks).filter_by(code=code, deckType='discard').all()
    for i in discard:
        nC = Hands(card=i.card code=code cardType='hand', player=player)
        db.session.add(nC)
        db.session.delete(i)
    db.session.commit()






@socketio.on('leave')
def Leave(data):
    code = data['code']
    leave_room(code)

@socketio.on('join')
def Join(data):
    code = data['code']
    name = data['name']
    # Add player if its allowed
    exists = db.session.query(Gameid).filter_by(code=code).first()
    if exists is None:
        emit('isJoinSuccess', {'isJoined': False, 'msg': "It appears the game doesn't exist. Try making one yourself!", 'state': []})
        return
    nPlayers = db.session.query(Players).filter_by(code=code).count()
    if nPlayers >= 4:
        emit('isJoinSuccess', {'isJoined': False, 'msg': "It appears the game is full. Try snaking one of your friends or creating your own game!", 'state': []})
        return
    if exists.started:
        emit('isJoinSuccess', {'isJoined': False, 'msg': "It appears the game has already started. Try Joining a different game!", 'state': []})
        return
    newName = name
    nameCount = 0
    while True:
        nameCopies = 0
        nameCopies = db.session.query(Players).filter_by(code=code, name=newName).count()
        if (nameCopies != 0):
            nameCount += 1
            newName = name + ' (' + str(nameCount) + ')'
        else:
            break
    name = newName
    emit('setUser', {'name': name})
    newPlayer = Players(code=code, name=name, turn=nPlayers)
    db.session.add(newPlayer)
    db.session.commit()

    #add game state
    state = []
    players = db.session.query(Players).filter_by(code=room).order_by(Players.turn).all()
    for i in players:
        state.append({'name': i.name, 'turn': i.turn, 'faceup': [], 'handlen': 0})

    join_room(code)
    emit('myTurn', {'myTurn': nPlayers})
    emit('isJoinSuccess', {'isJoined': True, 'msg': "", 'state': state}, room=code)
    return

@socketio.on('startGame')
def Start(data):
    code = data['code']
    game = db.session.query(Gameid).filter_by(code=code).first()
    if (game.started):
        return
    else:
        game.started = True

    print("creating deck")
    
    deck = [i for i in range(0,52)]
    random.shuffle(deck)
    players = db.session.query(Players).filter_by(code=code).order_by(Players.turn).all()
    state = []
    fu = []
    for i in players:
        for j in range(3):
            nC = deck.pop(0)
            nH = Hands(card=nC, code=code, cardType='hand', player=i.name)
            db.session.add(nH)
            nC = deck.pop(0)
            nH = Hands(card=nC, code=code, cardType='faceup', player=i.name)
            db.session.add(nH)
            fu.append(nC)
            nC = deck.pop(0)
            nH = Hands(card=nC, code=code, cardType='facedown', player=i.name)
            db.session.add(nH)
        state.append({'name': i.name, 'turn': i.turn, 'faceup': fu, 'handlen': 3})
    for i in deck:
        nD = Decks(code=code, card=i, deckType='draw')
        db.session.add(nD)
    db.session.commit()
    print('Decks dealt')
    emit('start', {'started': True, 'turn': 0, 'state': state}, room=code)
    print('Started')

@socketio.on('getHand')
def GetHand(data):
    player = data['player']
    code = data['code']
    fu = db.session.query(Hands).filter_by(code=code, player=player, cardType='faceup').all()
    fd = db.session.query(Hands).filter_by(code=code, player=player, cardType='facedown').all()
    h = db.session.query(Hands).filter_by(code=code, player=player, cardType='hand').all()
    faceup = [x.card for x in fu] # list(map(lambda x: x.card, fu)) 
    facedown = [x.card for x in fd] # list(map(lambda x: x.card, fd))
    hand = [x.card for x in h] # list(map(lambda x: x.card, h))
    plays = findValidPlays(code, player)
    emit('giveHand', {'faceup': faceup, 'facedown': facedown, 'hand': hand, 'validPlays': plays})
                    

@socketio.on('play')
def Play(data):
    emit('updating', {'updating': True})
    player = data['player']
    code = data['code']
    played = data['played']
    if len(played) > 0:
        playCard(player,code,played)
    else:
        pickupCards(player, code)
    game = db.session.query(Gameid).filter_by(code=code).first()

    # End the game if player runs out of cards (wins)
    if db.session.query(Hands).filter_by(player=player, code=code).count() == 0:
        #TODO
        return
    # Update the game state
    state = []
    players = db.session.query(Players).filter_by(code=room).order_by(Players.turn).all()
    for i in players:
        fu = db.session.query(Hands).filter_by(code=code, player=i.name, cardType='faceup').all()
        faceup = [x.card for x in fu]
        handlen = db.session.query(Hands).filter_by(code=code, player=i.name, cardType='hand').count()
        state.append({'name': i.name, 'turn': i.turn, 'faceup': faceup, 'handlen': handlen})
    
    # If pile wasn't burnt, go to next player
    if game.lplayed > 0:
        game.turn = (game.turn + 1) % db.session.query(Players).filter_by(code=code).count()
        db.session.commit()
        return

    # Else, go to next player
    emit('updating', {'updating': False})
    emit('update', {'turn': game.turn, 'state': state}, room=code)


#@socketio.on('draw')

#@socketio.on('')

    



if __name__ == '__main__':
    socketio.run(app)