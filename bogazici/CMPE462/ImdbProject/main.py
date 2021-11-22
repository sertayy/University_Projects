import os


files = os.listdir("/Users/apple/Desktop/S/")

file_content = []
for file in files:

    with open("/Users/apple/Desktop/S/" + file, "r") as infile:
        a = infile.read()
        file_content.append(a)

print()
