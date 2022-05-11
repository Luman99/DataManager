import matplotlib.pyplot as plt

text = []
with open('in.tsv', encoding='utf-8') as data:
    for row in data:
       text.append(row[53:])

spaces_in_all = []
new_line_in_all = []
for i, str in enumerate(text):
    spaces = 0
    new_line = 0
    for char in str:
        if char == ' ':
            spaces += 1
    spaces_in_all.append(spaces)
    print(str.count('\\n'))
    new_line_in_all.append(str.count('\\n'))

average_number_of_spaces = sum(spaces_in_all)/len(spaces_in_all)
print(average_number_of_spaces)

plt.hist(spaces_in_all, bins=50)
plt.show()

plt.hist(new_line_in_all, bins=50)
plt.show()
