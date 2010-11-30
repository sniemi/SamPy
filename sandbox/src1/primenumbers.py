
for j in range(2, 200):
    for k in range (2,j):
        if (j % k  == 0):
            print j, "equals", k, "*", j/k
            break
    else:
        print j, "is a prime number"

