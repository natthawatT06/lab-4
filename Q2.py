s = input().strip()
k = int(input())

grabs = []
passengers = []

for i in range(len(s)):
    if s[i] == 'G':
        grabs.append(i)
    elif s[i] == 'P':
        passengers.append(i)


g = 0
p = 0
count = 0


while g < len(grabs) and p < len(passengers):

    if abs(grabs[g] - passengers[p]) <= k:
        count += 1
        g += 1
        p += 1

    elif grabs[g] < passengers[p]:
        g += 1

    else:
        p += 1


print(count)