text = ''
with open("write.txt", "w", encoding="utf-8") as f:
    for i in range(4):
        text += input() + '\n'
    f.write(text)