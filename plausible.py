import secrets
import toyspider

fake = False
outerDeck=toyspider.create()
n=len(outerDeck)
innerDeck=[n-i-1 for i in range(n)]
if not fake:
    outerDeck=toyspider.shuffle(outerDeck)
    innerDeck=toyspider.shuffle(innerDeck)    

innerMessage="42"
innerDecimal = toyspider.decimal(innerMessage)
outerMessage="TOY SPIDER"
outerDecimal = toyspider.decimal(outerMessage)

innerPlain=toyspider.plainFromMessage(innerDeck,innerMessage,fake)

(innerCipher,rngDeck)=toyspider.encrypt(innerDeck,innerPlain)
print("innerCipher=" + str(innerCipher))

outerPrefix=innerCipher[0:toyspider.PREFIX_LEN]
innerCipher=innerCipher[toyspider.PREFIX_LEN:]
outerPadded=toyspider.pad(outerDeck,toyspider.encode(outerDeck,outerMessage))

if len(outerPadded) < len(innerCipher):
    print("outer message is too short: " + str(len(outerPlain)) + " < " + len(innerCipher))
else:
    outerPlain=outerPrefix.copy()
    for i in range(len(outerPadded)):
        outerRandom = 0
        if (i < len(innerCipher)):
            outerRandom = innerCipher[i]
        else:
            innerSecret = 0 if i % 2 == 1 else (9-i) % n if fake else secrets.randbelow(n)
            (rngVal,rngDeck)=toyspider.encrypt(rngDeck,[innerSecret])
            outerRandom = rngVal[0]
        outerPlain.append(outerRandom)
        outerPlain.append(outerPadded[i])
    (outerCipher,outerDeckAfter)=toyspider.encrypt(outerDeck,outerPlain)

    print ("cipher=" + str(outerCipher))

    # ... decode

    outerPlain2 = toyspider.decrypt(outerDeck,outerCipher)[0]
    print ("outerPlain2=" + str(outerPlain2))        
    outerMessage2 = toyspider.messageFromPlain(outerDeck,outerPlain2,outerDecimal)
    print ("outerMessage2=" + str(outerMessage2))
    innerCipher2 = outerPlain2[0:toyspider.PREFIX_LEN]
    innerCipher2.extend(outerPlain2[toyspider.PREFIX_LEN::2])
    print("innerCipher2=" + str(innerCipher2))
    innerPlain2 = toyspider.decrypt(innerDeck,innerCipher2)[0]
    print("innerPlain2=" + str(innerPlain2))
    while len(innerPlain2)>toyspider.PREFIX_LEN and ((len(innerPlain2) % 2) == 1 or innerPlain2[len(innerPlain2)-1] == 0):
        innerPlain2.pop()
    print("innerPlain2=" + str(innerPlain2))
    innerMessage2 = toyspider.messageFromPlain(innerDeck,innerPlain2,innerDecimal)
    
    print ("inner message " + str(innerMessage2))
