import toyspider

deck=toyspider.create()
fake=True
message42="42"
plain42=toyspider.plainFromMessage(deck,"42",fake)
messageToySpider="TOY SPIDER"
plainToySpider=toyspider.plainFromMessage(deck,"TOY SPIDER",fake)
(cipher42,deck42)=toyspider.encrypt(deck,plain42)
(cipherToySpider,deckToySpider)=toyspider.encrypt(deck,plainToySpider)
if toyspider.messageFromPlain(deck,toyspider.decrypt(deck,cipher42)[0],True) != message42:
    print("decrypt decimal failed.")
if toyspider.messageFromPlain(deck,toyspider.decrypt(deck,cipherToySpider)[0],False) != messageToySpider:
    print("decrypt letters failed.")
    
toyspider.encryptSteps(deck,message42,fake)
toyspider.encryptSteps(deck,messageToySpider,fake)



    


