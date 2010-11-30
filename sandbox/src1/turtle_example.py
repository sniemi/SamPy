# the turtle module provides turtle graphics primitives, it uses a Tkinter canvas
# turtle is part of the Tkinter library (lib-tk)
# tested with Python24  vegaseat  30jun2005

from turtle import *
import time

# pen/turtle starts at the center (x=0, y=0) of the turtle display area

color("green")
# pen up, don't draw
up()
# centers the circle
goto(0,-50)
# pen down, draw
down()
# radius=50  center is 50 radius units above the turtle
circle(50)
up()
goto(-100,100)
down()
circle(100)
up()
# center the turtle again
goto(0,0)
down()

# draw blue 100x100 squares
color("blue")
for deg in range(0, 61, 6):
    right(90 + deg)
    forward(123)
    right(90)
    forward(123)
    right(90)
    forward(123)
    right(90)
    forward(123)
    
up()
goto(-150,-120)
color("red")
write("Done!")

time.sleep(10)  # wait 5 seconds

