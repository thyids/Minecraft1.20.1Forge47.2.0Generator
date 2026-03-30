ins = {"test1": "tes1", "test2": "tes2", "test3": "tes3"}

strings = ""
for key in ins.keys():
    strings += key + "/"
strings = strings[:-1]
print(strings)