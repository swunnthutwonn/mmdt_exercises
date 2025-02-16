# exercise
def exe1():
    days = 365
    hours = 24
    minutes = 60
    hrs_in_year = days * hours
    mins_in_decade = hrs_in_year * 100

    age = 25
    days = age * 365
    hrs = days * 24
    mins = hrs * 60
    secs_in_age = mins * 60

    print(f"{hrs_in_year} hours are in a year.\n{mins_in_decade} minutes in a decade.\nYour are {secs_in_age} seconds old.")

exe1()



def exe2():
    secs = 1406 * 1000000
    mins = secs / 60
    hrs = mins / 60
    days = hrs / 24
    years = days / 365
    print(f"you are {years} old!")

exe2()


# Exercise 2
def exe3(a, b):
    alice_scores = 0
    bob_scores = 0

    for i in range(3):
        if a[i] > b[i]:
            alice_scores += 1
        elif a[i] < b[i]:
            bob_scores += 1
    return (f"Alices scores is {alice_scores} and Bob scores is {bob_scores}!") 

a = [7,3,1]
b = [3,9,4]
print(exe3(a, b))
    



def exe4(rows):
    for i in range(rows, 0, -1):  
        for j in range(i):
            print("*", end="")
        print()

exe4(7)


def triangle_area(b, h):
    return b * h

print(triangle_area(2.28,3.5))