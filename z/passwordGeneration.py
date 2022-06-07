import random
import string
import os

# get random password pf length 8 with letters, digits, and symbols
characters = string.ascii_letters + string.digits + string.punctuation
password = ''.join(random.choice(characters) for i in range(8))
print(password)

save_path_1 = "/Volumes/USB-1"
save_path_2 = "/Volumes/USB-2"
file_name = "key.txt"

completeName_1 = os.path.join(save_path_1, file_name)
completeName_2 = os.path.join(save_path_2, file_name)
print(completeName_1)
print(completeName_2)

file1 = open(completeName_1, "w")
file2 = open(completeName_2, "w")
file1.write(password)
file2.write(password)
file1.close()
file2.close()