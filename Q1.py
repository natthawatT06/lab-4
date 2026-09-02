s = input().strip()
k = int(input())

grabs = []
passengers = []

for i in range(len(s)):
    if s[i] == 'G':
        grabs.append(i)
    elif s[i] == 'P':
        passengers.append(i)


used = set()

max_passengers = 0
num_solutions = 0


def search(index, count):

    global max_passengers
    global num_solutions

    # ถ้าพิจารณา Grab ครบทุกคันแล้ว
    if index == len(grabs):

        # เจอคำตอบที่ดีกว่าเดิม
        if count > max_passengers:
            max_passengers = count
            num_solutions = 1

        # เจอคำตอบที่ดีที่สุดเท่ากับเดิม
        elif count == max_passengers:
            num_solutions += 1

        return


    # กรณีที่ 1
    # Grab คันนี้ไม่รับ Passenger
    search(index + 1, count)


    # กรณีที่ 2
    # Grab คันนี้ลองรับ Passenger
    for p in passengers:

        if p not in used and abs(grabs[index] - p) <= k:

            # ใช้ Passenger คนนี้
            used.add(p)

            # ไป Grab คันต่อไป
            search(index + 1, count + 1)

            # ย้อนกลับเพื่อทดลองทางเลือกอื่น
            used.remove(p)


search(0, 0)


print(num_solutions)
print(max_passengers)