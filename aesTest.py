from AESCipher import *
password = "'=o>-1RB"
obj = AESCipher('')
msg = 'RZfPjTFvac1yPrAZQquJY9NHC3fHVfw6vuH7wnqtujk='
dMsg = obj.toDecryption(msg)
print(dMsg)