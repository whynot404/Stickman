# StickMan Animation
import random
from tkinter import *
import time


class Sprite:
    # Parent Class
    def __init__(self, game):
        self.game = game
        self.endgame = False
        self.coordinates = None

    def move(self):  # Method to be Override.
        pass

    def coords(self):
        return self.coordinates


class ExitDoor(Sprite):
    def __init__(self, game, x, y, width, height):
        Sprite.__init__(self, game)
        self.door_photo = [PhotoImage(file='./sprite/Door_close.gif'),
                           PhotoImage(file='./sprite/Door_open.gif')]
        self.door_canvas = game.game_canvas.create_image(x, y, image=self.door_photo[0], anchor='nw')
        self.coordinates = Coordinates(x, y, x + (width / 2), y + height)
        print(f'door_x2:{self.coordinates.x2}')
        self.endgame = False

    def move(self):  # Override from Parent class
        if self.endgame:
            self.game.game_canvas.itemconfig(self.door_canvas, image=self.door_photo[1])


class Platforms(Sprite):
    # Platforms
    def __init__(self, game, photo, x, y, width, height):
        Sprite.__init__(self, game)  # <-I still don't understand this part.
        self.photo = photo
        self.img = game.game_canvas.create_image(x, y, image=self.photo, anchor='nw')
        self.coordinates = Coordinates(x, y, x + width, y + height)


class MrStick(Sprite):

    def __init__(self, game):
        Sprite.__init__(self, game)  # <-I still don't understand this part.
        # List of sprites for Left and Right orientation
        self.img_left = [
            PhotoImage(file='./sprite/stickman4.gif'),
            PhotoImage(file='./sprite/stickman5.gif'),
            PhotoImage(file='./sprite/stickman6.gif')
        ]
        self.img_right = [
            PhotoImage(file='./sprite/stickman1.gif'),
            PhotoImage(file='./sprite/stickman2.gif'),
            PhotoImage(file='./sprite/stickman3.gif')
        ]
        print('stickman')
        self.image = game.game_canvas.create_image(50, 400, image=self.img_left[0], anchor='nw')
        self.x = 0
        self.y = 0
        self.cur_img = 0
        self.cur_img_add = 1
        self.jump_count = 0  # Jump to count counter so that the object will not jump forever
        self.last_time = time.time()  # make a counter for time to jump again
        self.coordinates = Coordinates()  # x , y = 0
        self.left = self.right = self.top = self.bottom = self.falling = None

        # Key Bindings
        game.game_canvas.bind_all('<KeyPress-4>', self.turn_left)
        game.game_canvas.bind_all('<KeyPress-6>', self.turn_right)
        game.game_canvas.bind_all('<space>', self.jump)  # set to 1 if keypress space

    # Key Bindings call function
    def turn_left(self, evt):
        if self.y == 0:
            self.x = -2

    def turn_right(self, evt):
        if self.y == 0:
            self.x = 2

    def jump(self, evt):
        if self.y == 0:
            self.y = -4
            self.jump_count = 0

    def animate(self):  # check for movement and image.
        if self.x != 0 and self.y == 0:  # check the object if not yet move left right/ or jump
            if time.time() - self.last_time > 0.1:  # Limit the transition of animation of each image.
                self.last_time = time.time()  # Reset the stopwatch.
                self.cur_img += self.cur_img_add  # Store the index position for the next image to load.
                if self.cur_img_add >= 2:
                    self.cur_img_add = -1
                if self.cur_img_add <= 0:
                    self.cur_img_add = 1
                if self.cur_img > 2:
                    self.cur_img = 1

        if self.x < 0:  # Going to  the left action <-
            if self.y != 0:  # Not yet Jumping?
                # show jumping sprite
                self.game.game_canvas.itemconfig(self.image, image=self.img_left[2])
            else:
                # If not yet jumping use what index of sprite is currently next
                self.game.game_canvas.itemconfig(self.image, image=self.img_left[self.cur_img])
        elif self.x > 0:  # Going to the right action ->
            if self.y != 0:  # Not yet Jumping?
                self.game.game_canvas.itemconfig(self.image, image=self.img_right[2])
            else:
                self.game.game_canvas.itemconfig(self.image, image=self.img_right[self.cur_img])

    def stick_coord(self):
        xy = self.game.game_canvas.coords(self.image)  # Check were is our stickman at the board
        self.coordinates.x1 = xy[0]
        self.coordinates.y1 = xy[1]
        self.coordinates.x2 = xy[0] + 27
        self.coordinates.y2 = xy[1] + 30

        return self.coordinates

    def move(self):  # Override from Parent Class.
        self.animate()

        if self.y < 0:
            self.jump_count += 1
            if self.jump_count > 20:
                self.y = 4
        if self.y > 0:
            self.jump_count -= 1

        cur_coord = self.stick_coord()

        self.left = self.right = self.top = self.bottom = self.falling = True

        # Check if stickman is colliding with the canvas sides (left,right,top,bottom)
        if self.y > 0 and cur_coord.y2 >= self.game.canvas_height:
            self.y = 0
            self.bottom = False
            self.endgame = True
        elif self.y < 0 and cur_coord.y1 <= 0:
            self.y = 0
            self.top = False
        if self.x > 0 and cur_coord.x2 >= self.game.canvas_width:
            self.x = 0
            self.right = False
        elif self.x < 0 and cur_coord.x1 <= 0:
            self.x = 0
            self.left = False

        # Collide with other sprites in the board
        for sprites in self.game.sprite:

            if sprites == self:  # check if the current sprite in the list of sprite is the  object itself.
                continue
            sprite_co = sprites.coords()
            class_name = str(sprites.__class__.__name__)
            # print(f'stickman-{cur_coord.x1}-{cur_coord.x2}_{cur_coord.y1}{cur_coord.y2}')
            if self.top and self.y < 0 and collide_top(cur_coord, sprite_co):
                self.y = -self.y
                self.top = False
            if self.bottom and self.y > 0 and collide_bottom(cur_coord, sprite_co, self.y):
                self.y = sprite_co.y1 - cur_coord.y2
                if self.y < 0:
                    self.y = 0
                self.bottom = self.top = False
                # checking at the Edge of the Platform
            if self.bottom and self.falling and self.y == 0 \
                    and cur_coord.y2 < self.game.canvas_height \
                    and collide_bottom(cur_coord, sprite_co, 1):
                # set falling condition to False
                self.falling = False

            if self.left and self.x < 0 and collide_left(cur_coord, sprite_co):
                self.x = 0
                self.left = False

                if class_name == 'ExitDoor':  # Check if the object is the door
                    sprites.endgame = True

                    self.game.is_running = False
                    print('Exit Door Left')

            if self.right and self.x > 0 and collide_right(cur_coord, sprite_co):
                self.x = 0
                self.right = False
                if class_name == 'ExitDoor':
                    sprites.endgame = True

                    self.game.is_running = False
                    print('Exit Door Right')

        if self.falling and self.bottom and self.y == 0 \
                and cur_coord.y2 < self.game.canvas_height:
            print(f'Falling')
            self.y = 4

        self.game.game_canvas.move(self.image, self.x, self.y)  # The current movement of stickman


class Game:
    # Game board interface
    def __init__(self):

        self.tk = Tk()
        self.tk.title("Mr Stickman")
        self.tk.resizable(0, 0)
        self.tk.wm_attributes("-topmost", 1)
        self.game_canvas = Canvas(self.tk, width=500, height=500, bd=0, highlightthickness=0)
        self.game_canvas.pack()
        self.canvas_height = 500
        self.canvas_width = 500
        self.game_bg = PhotoImage(file='./sprite/bg2.gif')  # assists images location
        bg_w = self.game_bg.width()
        bg_h = self.game_bg.height()
        self.sprite = []
        self.is_running = True

        # BACKGROUND TILES
        for x in range(0, 5):
            for y in range(0, 5):
                if (x + y) % 2 == 1:  # Checkerboard

                    self.game_canvas.create_image(x * bg_w, y * bg_h, image=self.game_bg, anchor='nw')
            # print(f'{x*bg_w}-{y*bg_h}')

        self.tk.update()

    def main(self):
        while True:
            if self.is_running:
                for sprite in self.sprite:
                    sprite.move()  # Function from Parent Class -> Sprite

            self.tk.update_idletasks()
            self.tk.update()
            time.sleep(0.03)  # Delay Load 0.03 seconds


class Coordinates:
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        # if default parameter is set, all parameter should follow also.
        # Coordinate class will handle  the coordinates of each objects
        # All coordinates initialized to 0
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2


def within_x(cor1, cor2):
    # Good programming practice #
    # less the redundancy of if elif else statement

    if (cor2.x1 < cor1.x1 < cor2.x2) \
            or (cor2.x1 < cor1.x2 < cor2.x2) \
            or (cor1.x1 < cor2.x1 < cor1.x2) \
            or (cor1.x1 < cor2.x2 < cor1.x2):
        return True
    else:
        return False


def within_y(cor1, cor2):
    if (cor2.y2 < cor1.y1 < cor2.y2) \
            or (cor2.y2 < cor1.y2 < cor2.y2) \
            or (cor1.y1 < cor2.y1 < cor1.y2) \
            or (cor1.y1 < cor2.y2 < cor1.y1):
        return True
    else:
        return False


# Collide check Functions

def collide_left(coor1, coor2):
    if within_y(coor1, coor2):
        # if coor1.x1 <= coor2.x2 and coor1.x1 >= coor2.x1: [Unsimplified check]
        if coor2.x2 >= coor1.x1 >= coor2.x1:
            return True
    else:
        return False


def collide_right(coor1, coor2):
    if within_y(coor1, coor2):
        # if coor1.x2 >= coor2.x1 and coor1.x2 < coor2.x2: [Unsimplified check]
        if coor2.x1 <= coor1.x2 < coor2.x2:
            return True
    else:
        return False


def collide_top(coor1, coor2):
    if within_x(coor1, coor2):
        if coor2.y2 >= coor1.y1 >= coor2.y1:
            return True
    else:
        return False


def collide_bottom(coor1, coor2, add):
    if within_x(coor1, coor2):
        y_add = coor1.y2 + add
        if coor2.y1 <= y_add <= coor2.y2:
            return True
    else:
        return False


if __name__ == '__main__':
    game = Game()

    # For Dynamic floor and loading
    # Check sprite folder & randomly choose from the platforms
    # For each level's increment the number of plastforms1
    door = ExitDoor(game, 10, 56, 40, 35)
    platform1 = Platforms(game, PhotoImage(file='./sprite/platform1.gif'), 0, 460, 100, 10)
    platform2 = Platforms(game, PhotoImage(file='./sprite/platform1.gif'), 100, 410, 100, 10)
    platform3 = Platforms(game, PhotoImage(file='./sprite/platform1.gif'), 210, 360, 100, 10)
    platform4 = Platforms(game, PhotoImage(file='./sprite/platform1.gif'), 310, 310, 100, 10)
    platform5 = Platforms(game, PhotoImage(file='./sprite/platform1.gif'), 400, 260, 100, 10)
    platform6 = Platforms(game, PhotoImage(file='./sprite/platform1.gif'), 300, 200, 100, 10)
    platform7 = Platforms(game, PhotoImage(file='./sprite/platform1.gif'), 200, 160, 100, 10)
    platform8 = Platforms(game, PhotoImage(file='./sprite/platform1.gif'), 110, 110, 100, 10)
    platform9 = Platforms(game, PhotoImage(file='./sprite/platform1.gif'), 10, 80, 100, 10)

    game.sprite.append(platform1)
    game.sprite.append(platform2)
    game.sprite.append(platform3)
    game.sprite.append(platform4)
    game.sprite.append(platform5)
    game.sprite.append(platform6)
    game.sprite.append(platform7)
    game.sprite.append(platform8)
    game.sprite.append(platform9)
    stickman = MrStick(game)
    game.sprite.append(stickman)
    game.sprite.append(door)

    game.main()
    # MAIN LOOP
    game.tk.mainloop()
