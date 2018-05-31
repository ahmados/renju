def checkGameHorizontal(image, a, b):
    color = image[a][b]
    t = b
    counter = 0
    while ((t >= 0) and (image[a][t] == color)):
        t -= 1
        counter += 1
    t = b
    while ((t <= 14) and (image[a][t] == color)):
        t += 1
        counter += 1
    if (counter >= 6):
        print("HORIZONTAL WIN")
        return 1
    return 0

def checkGameVertical(image, a, b):
    color = image[a][b]
    t = a
    counter = 0
    while ((t >= 0) and (image[t][b] == color)):
        t -= 1
        counter += 1
    t = a
    while ((t <= 14) and (image[t][b] == color)):
        t += 1
        counter += 1
    if (counter >= 6):
        print("VERTICAL WIN")
        return 1
    return 0

def checkGameMainDiagonal(image, a, b):
    color = image[a][b]
    p = a
    t = b
    counter = 0
    while ((min(t, p) >= 0) and (image[p][t] == color)):
        t -= 1
        p -= 1
        counter += 1
    p = a
    t = b
    while ((max(t, p) <= 14) and (image[p][t] == color)):
        t += 1
        p += 1
        counter += 1
    if (counter >= 6):
        print("MAIN DIAGONAL WIN")
        return 1
    return 0

def checkGameLDiagonal(image, a, b):
    color = image[a][b]
    p = a
    t = b
    counter = 0
    while ((min(14 - t, p) >= 0) and (image[p][t] == color)):
        t += 1
        p -= 1
        counter += 1
    p = a
    t = b
    while ((max(14 - t, p) <= 14) and (image[p][t] == color)):
        t -= 1
        p += 1
        counter += 1
    if (counter >= 6):
        print("LDIAGONAL WIN")
        return 1
    return 0

def checkGame(image, a, b):
    if ((checkGameHorizontal(image, a, b) or (checkGameVertical(image, a, b))) or (checkGameMainDiagonal(image, a, b) or checkGameLDiagonal(image, a, b))):
        return 1
    return 0

def callbackButton():
    global pos
    global winflag
    pos[0][:][:][0] = 0
    winflag = 0
    v.set("RENJU")
    for a in range(15):
        for b in range(15):
            if (image[a][b] != 0):
                clean(a, b)
                image[a][b] = 0
    for i in range(15):
        w.create_rectangle(40 + 40 * i, 0, 41 + 40 * i, 600, fill='red')
        w.create_rectangle(0, 40 + 40 * i, 600, 41 + 40 * i, fill='red')

from tkinter import *
from keras.models import load_model
import numpy as np

model_2 = load_model('comp.h5')
model = load_model('colab.h5')

pos = np.zeros((1, 15, 15, 1))
image = np.zeros((15, 15), dtype=np.uint8)
a = 0
b = 0
winflag = 0

master = Tk()
w = Canvas(master, width=700, height=700)
v = StringVar()
Label(master, textvariable=v, font=("Helvetica", 32)).pack()
v.set("RENJU")
button = Button(master, text="RESET", command=callbackButton)
button.pack()

counter = 0


# def play_against_human(model, master):
#     master.update_idletasks() 
#     master.update()
#     pos = np.zeros((1, 15, 15, 1))
#     image = np.zeros((15, 15), dtype=np.uint8)
#     a = 0
#     b = 0
#     i = 0
#     vec = model.predict(pos)
#     maxmove = 0
#     move = 0
#     xy = 0
#     for m in vec[0]:
#         if ((m > maxmove) and (pos[0][xy // 15][xy % 15][0] == 0)):
#             move = xy
#             maxmove = m
#         xy += 1
#     image[move // 15][move % 15] = 127
#     pos[0][move // 15][move % 15][0] = (127 / 256)
#     i += 1
#     print(str(i) , " MOVE : ", str(move // 15), " ", str(move % 15))
#     # plt.imshow(image, cmap='Greys', vmin=0, vmax=255)
#     # plt.show()
#     draw_first(move // 15, move % 15)
#     waitflag = 1
#     while (a != -1):
#         while (1):
#             if (waitflag):
#                 waitflag = 0
#                 break;
#         if (a == -1):
#             print("GAME STOPPED BY PLAYER")
#             return 0
#         if (image[a][b] != 0):
#             print("ALREADY OCCUPIED")
#             continue
#         draw_second(a, b)
#         pos[0][a][b][0] = 1
#         image[a][b] = 255
#         if (checkGame(image, a, b)):
#             print("PLAYER WON")
#             break
#         vec = model.predict(pos)
#         maxmove = 0
#         move = 0
#         xy = 0
#         for m in vec[0]:
#             if ((m > maxmove) and (pos[0][xy // 15][xy % 15][0] == 0)):
#                 move = xy
#                 maxmove = m
#             xy += 1
#         draw_first(move // 15, move % 15)
#         image[move // 15][move % 15] = 127
#         pos[0][move // 15][move % 15][0] = 0.5

#         print(str(i) , " MOVE : ", str(move // 15), " ", str(move % 15))
#         if (checkGame(image, move // 15, move % 15)):
#             print("COMPUTER WON")
#             break
#         # plt.imshow(image, cmap='Greys', vmin=0, vmax=255)
#         # plt.show()
#     # plt.imshow(image)

def clean(a, b):
    w.create_rectangle(40 * a, 40 * b, 40 * a + 40, 40 * b + 40, outline='black', fill='white')

def draw_first(x, y):
    w.create_rectangle(40 * x, 40 * y, 40 * x + 40, 40 * y + 40, fill='black')

def draw_second(x, y):
    w.create_line(40 * x, 40 * y, 40 * x + 40, 40 * y + 40)
    w.create_line(40 * x + 40, 40 * y, 40 * x, 40 * y + 40)

def callback(event):
    global winflag
    print("CLICKED")
    if (winflag):
        return 0
    v.set("RENJU")
    print("clicked at", event.x // 40, event.y // 40)
    a = event.x // 40
    b = event.y // 40
    if (image[a][b] != 0):
            v.set("OCCUPIED!!!")
            return 0
    draw_second(a, b)
    pos[0][a][b][0] = 1
    image[a][b] = 255
    if (checkGame(image, a, b)):
        v.set("PLAYER WON")
        winflag = 1
        return 0
    vec_1 = model.predict(pos)
    vec_2 = model_2.predict(pos)
    vec = vec_1 + vec_2
    maxmove = 0
    move = 0
    xy = 0
    for m in vec[0]:
        if ((m >= maxmove) and (pos[0][xy // 15][xy % 15][0] == 0)):
            move = xy
            maxmove = m
        xy += 1
    draw_first(move // 15, move % 15)
    image[move // 15][move % 15] = 127
    pos[0][move // 15][move % 15][0] = 0.5
    # print(str(i) , " MOVE : ", str(move // 15), " ", str(move % 15))
    if (checkGame(image, move // 15, move % 15)):
        winflag = 1
        v.set("COMPUTER WON")
        return 0
    # counter += 1
    # if not (counter % 2):
    #     w.create_line(40 * (event.x // 40), 40 * (event.y // 40), 40 * (event.x // 40) + 40, 40 * (event.y // 40) + 40)
    #     w.create_line(40 * (event.x // 40) + 40, 40 * (event.y // 40), 40 * (event.x // 40), 40 * (event.y // 40) + 40)
    # else:
    #     w.create_rectangle(40 * (event.x // 40), 40 * (event.y // 40), 40 * (event.x // 40) + 40, 40 * (event.y // 40) + 40, fill='black')



w.pack()
for i in range(1, 15):
    w.create_rectangle(40 + 40 * i, 40, 41 + 40 * i, 600, fill='red')
    w.create_rectangle(40, 40 + 40 * i, 600, 41 + 40 * i, fill='red')
# for i in range(100):
#   for j in range(100):
#       w.create_rectangle(16 * i, 16 * j, 15 + 20 * i, 15 + 20 * j, fill='black')
vec = model.predict(pos)
maxmove = 0
move = 0
xy = 0
for m in vec[0]:
    if ((m > maxmove) and (pos[0][xy // 15][xy % 15][0] == 0)):
        move = xy
        maxmove = m
    xy += 1
draw_first(move // 15, move % 15)
image[move // 15][move % 15] = 127
pos[0][move // 15][move % 15][0] = 0.5

button = Button(master, text="RESET", command=callbackButton)
button.pack()
w.bind("<Button-1>", callback)
w.pack()

mainloop()
