#/usr/bin/env python3

import secrets

FACES=['Q','A','2','3','4','5','6','7','8','9']
SUITES=[ '♣' ]
CIPHER={ 'zth' : 5 , 'offset' : len(FACES)*len(SUITES)-5 }
CUT={ 'zth' : 1 , 'offset' : len(FACES)*len(SUITES)-2 }
PREFIX_LEN = 4

def create():
    n = len(FACES)*len(SUITES)
    return [i for i in range(n)]

def shuffle(deck):
    shuffled=deck.copy()
    n = len(deck)
    for i in range(n):
        j=i+secrets.randbelow(n-i)
        (shuffled[i],shuffled[j])=(shuffled[j],shuffled[i])
    return shuffled

def deckOutput(deck,cfg):
    n=len(deck)
    mark=(deck[cfg['zth']]+cfg['offset']) % n
    markLoc=deck.index(mark)
    padLoc=(markLoc+1) % n
    return deck[padLoc]

def cutPad(deck):
    return deckOutput(deck,CUT)

def cipherPad(deck):
    return deckOutput(deck,CIPHER)

def cut(deck,loc):
    n = len(deck)
    return [deck[(i+loc) % n] for i in range(n)]

def backFrontShuffle(deck):
    n=len(deck)
    shuffled=[]
    for i in range(n):
        if i % 2 == 0:
            shuffled.append(deck[i])
        else:
            shuffled.insert(0,deck[i])
    return shuffled

def mix(deck,deciphered):
    n = len(deck)
    cutCard = (cutPad(deck) + deciphered) % n
    cutLoc = deck.index(cutCard)
    deck = cut(deck,cutLoc)
    deck = backFrontShuffle(deck)
    return deck
    
def prefix(deck,fake=False):
    n = len(deck)
    return [ i+1 if fake else secrets.randbelow(n) for i in range(PREFIX_LEN) ]

def encode(deck,letters):
    n = len(deck)
    encoded=[]
    for letter in str(letters):
        if '0' <= letter and letter <= '9':
            encoded.append(ord(letter)-ord('0'))
        else:
            code = None
            if 'A' <= letter and letter <= 'Z':
                code = ord(letter)-ord('A') + 1
            elif 'a' <= letter and letter <= 'z':
                code = ord(letter)-ord('a') + 1
            elif letter == ' ':
                code = 0
            if code != None:
                encoded.append(code // n)
                encoded.append(code %  n)
    return encoded

def pad(deck,codes):
    n = len(deck)
    padded = codes.copy()
    padLen = PREFIX_LEN // 2
    while (len(codes)+padLen) % PREFIX_LEN != 0:
        padLen += 1
    padded.extend([padLen for i in range(padLen)])
    return padded

def injectRandomness(deck,padded,fake=False):
    n = len(deck)
    injected=[]
    for i in range(len(padded)):
        injected.append(((9-i) % n if fake else secrets.randbelow(n)))
        injected.append(padded[i])
    return injected

def plainFromMessage(deck,message,fake=False):
    plain=prefix(deck,fake)
    encoded=encode(deck,message)
    padded=pad(deck,encoded)
    randomized=injectRandomness(deck,padded,fake)
    plain.extend(randomized)
    return plain

def messageFromPlain(deck,plain,decimal=False):
    if len(plain) < 3*PREFIX_LEN:
        return None
    # remove prefix and injected randomness
    padded=plain[PREFIX_LEN+1:len(plain):2]
    padLen = padded[len(padded)-1]
    if padLen < PREFIX_LEN//2 or padLen > len(padded):
        return None
    codes=padded[0:len(padded)-padLen]
    pad=padded[len(padded)-padLen:]
    if pad != [padLen]*padLen:
        return None
    message=[]
    if decimal:
        message=['0']*len(codes)
        for i in range(len(codes)):
            message[i]=str(codes[i])
    else:
        n = len(deck)
        message=['A']*(len(codes)//2)
        for i in range(len(codes)//2):
            decode=codes[2*i]*n+codes[2*i+1]
            message[i]=' ' if decode == 0 else chr(ord('A')+decode-1)
    return "".join(message)
    
def encrypt(deck,plain):
    cipher=[]
    n = len(deck)
    for deciphered in plain:
        enciphered=(deciphered + cipherPad(deck)) % n
        cipher.append(enciphered)
        deck = mix(deck,deciphered)
    return (cipher,deck)

def decrypt(deck,cipher):
    plain=[]
    n = len(deck)
    for encipher in cipher:
        deciphered = (encipher+(n-cipherPad(deck))) % n
        plain.append(deciphered)
        deck = mix(deck,deciphered)
    return (plain,deck)

def prettyCard(card):
    return FACES[card % 10] # + SUITES[card // 10]

def prettyCards(cards):
    return "".join([prettyCard(card) for card in cards])

def encryptSteps(deck,message,fake=False):
    n = len(deck)
    pfx=prefix(deck,fake)
    codes=encode(deck,message)
    padded=pad(deck,codes)
    randomized=injectRandomness(deck,padded,fake)
    plain=pfx.copy()
    plain.extend(randomized)
    step=0
    print('prefix=' + prettyCards(pfx))
    print('message=' + message)
    print('codes=' + prettyCards(codes))
    print('pad=' + prettyCards(padded[len(codes):]))
    print('plain=' + prettyCards(plain))
    cipher=[]
    print ("step,deck,plain,cipher_mark,cipher_pad,cipher,cut_mark,cut_pad,cut")
    for deciphered in plain:
        cipherMarkCard = (deck[CIPHER['zth']]+CIPHER['offset']) % n
        cipherPadCard = deck[(deck.index(cipherMarkCard)+1) % n]
        if cipherPad(deck) != cipherPadCard:
            print ("cipherPad mismatch.")
        cutMarkCard = (deck[CUT['zth']]+CUT['offset']) % n
        cutPadCard = deck[(deck.index(cutMarkCard)+1) % n]
        if cutPad(deck) != cutPadCard:
            print ("cutPad mismatch.")
        enciphered = (cipherPadCard + deciphered) % n
        cutCard = (cutPadCard + deciphered) % n
        cutDeck=cut(deck,deck.index(cutCard))
        mixed = backFrontShuffle(cutDeck)
        if encrypt(deck,[deciphered]) != ([enciphered],mixed):
            print ("mix mismatch")
        print (str(step) + "," + (prettyCards(deck)) + "," + prettyCard(deciphered) + "," + prettyCard(cipherMarkCard) + "," + prettyCard(cipherPadCard) + "," + prettyCard(enciphered) + "," + prettyCard(cutMarkCard) + "," + prettyCard(cutPadCard) + "," + prettyCard(cutCard))
        cipher.append(enciphered)
        deck = mixed
        step += 1
    print("cipher=" + prettyCards(cipher))
    return (cipher,deck)

deck=create()
fake=True
message42="42"
plain42=plainFromMessage(deck,"42",fake)
messageToySpider="TOY SPIDER"
plainToySpider=plainFromMessage(deck,"TOY SPIDER",fake)
(cipher42,deck42)=encrypt(deck,plain42)
(cipherToySpider,deckToySpider)=encrypt(deck,plainToySpider)
if messageFromPlain(deck,decrypt(deck,cipher42)[0],True) != message42:
    print("decrypt decimal failed.")
if messageFromPlain(deck,decrypt(deck,cipherToySpider)[0],False) != messageToySpider:
    print("decrypt letters failed.")
    
encryptSteps(deck,message42)
encryptSteps(deck,messageToySpider)



    


