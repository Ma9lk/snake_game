import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from enum import Enum
from random import randint
from time import sleep


class Direction(Enum):
    KEY_UP = 'UP'
    KEY_RIGHT = 'RIGHT'
    KEY_DOWN = 'DOWN'
    KEY_LEFT = 'LEFT'


class Point:
    def __init__(self, x, y, s):
        self.x = x
        self.y = y
        self.symbol = s

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, Line):
            return any([self.x == p.x and self.y == p.y for p in other.points])
        else:
            raise TypeError("Cannot compare Point object with {}".format(type(other)))

    def copy(self):
        return self.__class__(self.x, self.y, self.symbol)


class FoodPoint(Point):
    def __init__(self, x, y, symbol='$'):
        super().__init__(x, y, symbol)


class WallPoint(Point):
    def __init__(self, x, y, symbol='*'):
        super().__init__(x, y, symbol)


class SnakePoint(Point):
    def __init__(self, x, y, symbol='#'):
        super().__init__(x, y, symbol)

    def move(self, offset, direction):
        if direction == Direction.KEY_UP:
            self.y -= offset
        elif direction == Direction.KEY_RIGHT:
            self.x += offset
        elif direction == Direction.KEY_DOWN:
            self.y += offset
        elif direction == Direction.KEY_LEFT:
            self.x -= offset
        else:
            raise TypeError("Wrong type of value was given as direction.")
        return self


class SnakeGame:
    def __init__(self):
        x_size = 80
        y_size = 20
        self.console = Console(x_size, y_size)
        tail = SnakePoint(10, 10)
        snake_length = 4
        self.snake = Snake(tail, snake_length, Direction.KEY_RIGHT, self.console)
        self.wall = Wall(0, x_size - 1, 0, y_size - 1, self.console)
        self.food_maker = FoodMaker(x_size, y_size, self.console)

    def start(self):
        self.wall.draw()
        self.snake.draw()
        self.food_maker.add_new_food()
        while True:
            self.snake.move()
            self.snake.update_direction(self.console.get_user_entry())
            if self.snake.hits_food(self.food_maker.current_food_point):
                self.snake.eats_food()
                self.food_maker.add_new_food()
            if self.snake.hits_wall(self.wall):
                break

    def end(self):
        self.console.close()


class Snake:
    def __init__(self, tail, length, direction, console):
        self._direction = direction
        self._points = [SnakePoint(tail.x, tail.y).move(offset, direction) for offset in range(length)]
        self._console = console

    def move(self):
        self._drop_tail()
        self._update_head()

    def draw(self):
        self._console.draw_line(self._points)

    def update_direction(self, user_entry):
        if user_entry == KEY_UP:
            self._direction = Direction.KEY_UP
        elif user_entry == KEY_RIGHT:
            self._direction = Direction.KEY_RIGHT
        elif user_entry == KEY_DOWN:
            self._direction = Direction.KEY_DOWN
        elif user_entry == KEY_LEFT:
            self._direction = Direction.KEY_LEFT

    def hits_food(self, point):
        if self.head == point:
            return True
        return False

    def eats_food(self):
        self._add_tail()

    @property
    def head(self):
        return self._points[-1]

    def _update_head(self):
        offset = 1
        new_head = self.head.copy().move(offset, self._direction)
        self._points.append(new_head)
        self._console.draw_point(new_head)

    def _drop_tail(self):
        tail = self._points.pop(0)
        tail.symbol = ' '
        self._console.draw_point(tail)

    def _add_tail(self):
        self._points.insert(0, self._points[0].copy())

    def hits_wall(self, wall):
        return any(self.head == wall for wall in wall.walls)


class FoodMaker:
    def __init__(self, x_size, y_size, console):
        self.console = console
        offset_from_wall = 2
        self.y_min = offset_from_wall
        self.y_max = y_size - offset_from_wall
        self.x_min = offset_from_wall
        self.x_max = x_size - offset_from_wall
        self.current_food_point = None

    def add_new_food(self):
        x = randint(self.x_min, self.x_max)
        y = randint(self.y_min, self.y_max)
        food_point = FoodPoint(x, y)
        self.current_food_point = food_point
        self.console.draw_point(food_point)


class Wall:
    def __init__(self, x_min, x_max, y_min, y_max, console):
        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max
        self._left_line = VerticalLine(x_min, y_min, y_max)
        self._right_line = VerticalLine(x_max, y_min, y_max)
        self._upper_line = HorizontalLine(x_min, x_max, y_max)
        self._lower_line = HorizontalLine(x_min, x_max, y_min)
        self.console = console

    def draw(self):
        for wall in self.walls:
            self.console.draw_line(wall.points)

    @property
    def walls(self):
        return [self._left_line, self._right_line, self._upper_line, self._lower_line]


class Line:
    def __init__(self):
        pass


class HorizontalLine(Line):
    def __init__(self, x_min, x_max, y):
        super().__init__()
        self.points = [WallPoint(x, y) for x in range(x_min, x_max)]


class VerticalLine(Line):
    def __init__(self, x, y_min, y_max):
        super().__init__()
        self.points = [WallPoint(x, y) for y in range(y_min, y_max)]


class Console:
    def __init__(self, x_size, y_size):
        self._x_length = x_size
        self._y_length = y_size
        self._win = self._create_console_window()

    def draw_line(self, points):
        for point in points:
            self.draw_point(point)

    def get_user_entry(self):
        return self._win.getch()

    def draw_point(self, point):
        self._win.addch(point.y, point.x, point.symbol)

    @staticmethod
    def close():
        curses.endwin()

    def _create_console_window(self):
        curses.initscr()
        win = curses.newwin(self._y_length, self._x_length)
        win.keypad(1)
        # curses.noecho()
        curses.curs_set(0)
        win.border(0)
        # win.nodelay(1)
        win.timeout(500)
        return win


if __name__ == '__main__':
    game = SnakeGame()
    game.start()
    sleep(3)
    game.end()
