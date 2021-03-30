


class Point:

    def __init__(self, x, y, delay_before, delay_after):
        self._x = x
        self._y = y
        self._delay_before = delay_before
        self._delay_after = delay_after

    @property
    def get_x(self):
        return self._x

    @property
    def get_y(self):
        return self._y

    @property
    def get_delay_before(self):
        return self._delay_before

    @property
    def get_delay_after(self):
        return self._delay_after


class PointsStorage:

    def __init__(self):
        self._points = []

    def add_point(self, point):
        self._points.append(point)

    def remove_last_point(self):
        if self._points:
            self._points.pop()

    def remove_all_points(self):
        self._points = []

    def get_points(self):
        return tuple(self._points)


def add_point(point):
    points_storage[current_storage].add_point(point)

def remove_last_point():
    points_storage[current_storage].remove_last_point()

def remove_all_points():
    points_storage[current_storage].remove_all_points()

def get_points():
    return points_storage[current_storage].get_points()


def create_point(x, y, delay_before=0.05, delay_after=0.05):
    return Point(x, y, delay_before, delay_after)


current_storage = 0
points_storage = {}

points_storage[current_storage] = PointsStorage()

