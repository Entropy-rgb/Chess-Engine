import pygame as pg

pg.init()
screen = pg.display.set_mode((1440,1440))
clock = pg.time.Clock()
running = True
HEIGHT = 180
WIDTH = 180
colour = (234, 181, 99)

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    screen.fill("purple")
    for i in range(0,8):
        for j in range(0,8):
            if (i+j)%2 == 0:
                colour = (234, 181, 99)
            else:
                colour = (84, 42, 0)
            pg.draw.rect(screen, colour,(j*180, i*180, WIDTH, HEIGHT))
    pg.display.flip()
    clock.tick(60)

pg.quit()