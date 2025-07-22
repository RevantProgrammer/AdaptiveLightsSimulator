import pygame
import random
import math
from time import time


class Car:
    def __init__(self, x, y, c, t, dir, dest, rot=0):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 10
        self.color = c
        self.type = t
        self.dir = dir
        self.rotation = rot
        self.vel = CAR_VEL
        self.dest = dest
        self.creation_time = time()
        self.emergency = False

    def move(self):
        vel = self.vel
        if self.dir == "south":
            if self.type == "F":
                if self.y < 5:
                    return False
            elif self.type == "R":
                if self.x < 5:
                    return False
                if 390 < self.y < 425 and self.rotation < 180:
                    vel = 3
                    if 180-self.rotation >= 6:
                        self.rotation += 6
                    else:
                        self.rotation = 180
            else:
                if self.x > 595:
                    return False
                if 255 < self.y < 415 and self.rotation > 0:
                    vel = 3
                    if self.rotation >= 1.15:
                        self.rotation -= 1.15
                    else:
                        self.rotation = 0
        elif self.dir == "north":
            if self.type == "F":
                if self.y > 595:
                    return False
            elif self.type == "R":
                if self.x > 595:
                    return False
                if 180 < self.y < 215 and self.rotation < 0:
                    vel = 3
                    if -self.rotation >= 6:
                        self.rotation += 6
                    else:
                        self.rotation = 0
            else:
                if self.x < 5:
                    return False
                if 180 < self.y < 340 and self.rotation > -180:
                    vel = 3
                    if self.rotation+180 >= 1.15:
                        self.rotation -= 1.15
                    else:
                        self.rotation = -180
        elif self.dir == "east":
            if self.type == "F":
                if self.x < 5:
                    return False
            elif self.type == "R":
                if self.y > 595:
                    return False
                if 390 < self.x < 425 and self.rotation < 270:
                    vel = 3
                    if 270-self.rotation >= 6:
                        self.rotation += 6
                    else:
                        self.rotation = 270
            else:
                if self.y < 5:
                    return False
                if 250 < self.x < 425 and self.rotation > 90:
                    vel = 3
                    if self.rotation-90 >= 1.15:
                        self.rotation -= 1.15
                    else:
                        self.rotation = 90
        else:
            if self.type == "F":
                if self.x > 595:
                    return False
            elif self.type == "R":
                if self.y < 5:
                    return False
                if 180 < self.x < 215 and self.rotation < 90:
                    vel = 3
                    if 90-self.rotation >= 6:
                        self.rotation += 6
                    else:
                        self.rotation = 90
            else:
                if self.y > 595:
                    return False
                if 175 < self.x < 340 and self.rotation > -90:
                    vel = 3
                    if self.rotation+90 >= 1.15:
                        self.rotation -= 1.15
                    else:
                        self.rotation = -90
        angle = self.rotation * math.pi / 180
        self.y -= vel * math.sin(angle)
        self.x += vel * math.cos(angle)
        return True

    def in_lane(self):
        if self.dir == "north":
            if self.y <= NORTH[1]:
                return True
        elif self.dir == "south":
            if self.y >= SOUTH[1]:
                return True
        elif self.dir == "east":
            if self.x >= EAST[0]:
                return True
        elif self.dir == "west":
            if self.x <= WEST[0]:
                return True

        return False

    def park(self):
        if self.dir == "north":
            if self.y < self.dest:
                if abs(self.dest - self.y) > self.vel:
                    self.y += self.vel
                else:
                    self.y += abs(self.dest - self.y)
                return False
        elif self.dir == "south":
            if self.y > self.dest:
                if abs(self.dest - self.y) > self.vel:
                    self.y -= self.vel
                else:
                    self.y -= abs(self.dest - self.y)
                return False
        elif self.dir == "east":
            if self.x > self.dest:
                if abs(self.dest - self.x) > self.vel:
                    self.x -= self.vel
                else:
                    self.x -= abs(self.dest - self.x)
                return False
        else:
            if self.x < self.dest:
                if abs(self.dest - self.x) > self.vel:
                    self.x += self.vel
                else:
                    self.x += abs(self.dest - self.x)
                return False
        return True

    def at_intersection(self):
        return 175 < self.x < 425 and 175 < self.y < 425


pygame.init()

WIN_WIDTH = 600
WIN_HEIGHT = 600
bg = pygame.image.load("images/Crossroads.png")
window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Adaptive Traffic Lights")

red = pygame.transform.scale_by(pygame.image.load("images/RedRed.png"), 0.5)
yellow = pygame.transform.scale_by(pygame.image.load("images/YellowRed.png"), 0.5)
green = pygame.transform.scale_by(pygame.image.load("images/GreenRed.png"), 0.5)
turn = pygame.transform.scale_by(pygame.image.load("images/RedGreen.png"), 0.5)

SOUTH = (200, 425)
NORTH = (395, 175)
WEST = (175, 200)
EAST = (425, 395)
MAX_CARS_PER_LANE = 9
CAR_VEL = 4

south_cars = []
north_cars = []
east_cars = []
west_cars = []
moving_cars = []
parking = []

margin = 20
north_yf = NORTH[1]
north_yl = NORTH[1]
south_yf = SOUTH[1]
south_yl = SOUTH[1]
east_xf = EAST[0]
east_xl = EAST[0]
west_xf = WEST[0]
west_xl = WEST[0]
cars_cleared = 0


def cost_function(cars, time):
    return (cars+1)**(0.1*time)+cars/50


def list_in_lane(dir, lanes):
    res = []
    for car in dir:
        if car.type in lanes and car.in_lane():
            res.append(car)
    return res


def count_emergency_in_lane(dir, lanes):
    res = 0
    for car in dir:
        if car.type in lanes and car.in_lane() and car.emergency:
            res += 1
    return res


def choose_lane(arr, max_cars):
    choice_list = [0]
    removed = False
    if len(list_in_lane(arr, ["F", "R"])) < max_cars:
        choice_list.pop()
        removed = True
        choice_list.extend([1, 2])
    if len(list_in_lane(arr, ["L"])) < max_cars:
        if not removed:
            choice_list.pop()
        choice_list.append(3)

    n = random.choice(choice_list)
    match n:
        case 0:
            lane = None
        case 1:
            lane = "F"
        case 2:
            lane = "R"
        case 3:
            lane = "L"
    return lane


def append_to_move_list(dir1, dir2, lanes):
    for car in dir1:
        if car.type in lanes and car not in moving_cars:
            moving_cars.append(car)
    for car in dir2:
        if car.type in lanes and car not in moving_cars:
            moving_cars.append(car)


# https://replit.com/@TimSwast1/RotateARectanlge?v=1#main.py
def draw_rectangle(w, x, y, width, height, color, rotation=0):
    """Draw a rectangle, centered at x, y.

    Arguments:
      x (int/float):
        The x coordinate of the center of the shape.
      y (int/float):
        The y coordinate of the center of the shape.
      width (int/float):
        The width of the rectangle.
      height (int/float):
        The height of the rectangle.
      color (str):
        Name of the fill color, in HTML format.
      rotation (float):
        The angle by which the shape is rotated.
    """
    points = []

    # The distance from the center of the rectangle to
    # one of the corners is the same for each corner.
    radius = math.sqrt((height / 2)**2 + (width / 2)**2)

    # Get the angle to one of the corners with respect
    # to the x-axis.
    angle = math.atan2(height / 2, width / 2)

    # Transform that angle to reach each corner of the rectangle.
    angles = [angle, -angle + math.pi, angle + math.pi, -angle]

    # Convert rotation from degrees to radians.
    rot_radians = (math.pi / 180) * rotation

    # Calculate the coordinates of each point.
    for angle in angles:
        y_offset = -1 * radius * math.sin(angle + rot_radians)
        x_offset = radius * math.cos(angle + rot_radians)
        points.append((x + x_offset, y + y_offset))

    pygame.draw.polygon(w, color, points)


def draw(win):
    win.blit(bg, (0, 0))
    win.blit(states[3], (-10, 10))
    win.blit(states[1], (-10, 380))
    win.blit(states[0], (320, 10))
    win.blit(states[2], (320, 380))
    min_time = float('inf')
    min_ob = None
    for car in north_cars+south_cars+east_cars+west_cars:
        if car.creation_time < min_time:
            min_time = car.creation_time
            min_ob = car
    if min_ob:
        c = -200*(time()-min_time)/25 + 200  # LINEAR INTERPOLATION
        c = 0 if c < 0 else c
        min_ob.color = (c, c, c)
    for car in north_cars+south_cars+east_cars+west_cars:
        draw_rectangle(win, car.x, car.y, car.width, car.height, car.color, car.rotation)
    pygame.display.update()


def move_cars():
    global north_cars, south_cars, east_cars, west_cars, cars_cleared
    i = 0
    while i < len(parking):
        if not parking[i] in moving_cars:
            if parking[i].park():
                parking.pop(i)
            else:
                i += 1
        else:
            parking.pop(i)
    temp_l = []
    for car in moving_cars:
        if car.at_intersection() and car in cars_not_cleared:
            cars_not_cleared.remove(car)
        if not car.move():
            temp_l.append(car)
            cars_cleared += 1
            if car.emergency:
                emergency_wait_times.append(time()-car.creation_time)
            else:
                car_wait_times.append(time()-car.creation_time)
            if car.dir == "north":
                north_cars.remove(car)
            elif car.dir == "south":
                south_cars.remove(car)
            elif car.dir == "east":
                east_cars.remove(car)
            else:
                west_cars.remove(car)
    for car in temp_l:
        moving_cars.remove(car)


def create_north(emergency=False):
    global north_yf, north_yl
    lane = choose_lane(north_cars, MAX_CARS_PER_LANE)
    if not lane:
        return
    if lane in ["F", "R"]:
        car_x = NORTH[0]
        col = (0, 0, 255)
        car_y = north_yf
        north_yf -= margin
    else:
        car_x = 335
        col = (0, 0, 100)
        car_y = north_yl
        north_yl -= margin
    ob = Car(car_x, 0, col, lane, "north", car_y, -90)
    if emergency:
        ob.emergency = True
        ob.color = (255, 255, 255)
    north_cars.append(ob)
    parking.append(ob)


def create_south(emergency=False):
    global south_yf, south_yl
    lane = choose_lane(south_cars, MAX_CARS_PER_LANE)
    if not lane:
        return
    if lane in ["F", "R"]:
        car_x = SOUTH[0]
        col = (0, 255, 255)
        car_y = south_yf
        south_yf += margin
    else:
        car_x = 260
        col = (0, 100, 100)
        car_y = south_yl
        south_yl += margin
    ob = Car(car_x, 600, col, lane, "south", car_y, 90)
    if emergency:
        ob.emergency = True
        ob.color = (255, 255, 255)
    south_cars.append(ob)
    parking.append(ob)


def create_east(emergency=False):
    global east_xf, east_xl
    lane = choose_lane(east_cars, MAX_CARS_PER_LANE)
    if not lane:
        return
    if lane in ["F", "R"]:
        car_y = EAST[1]
        col = (0, 255, 0)
        car_x = east_xf
        east_xf += margin
    else:
        car_y = 337
        col = (0, 100, 0)
        car_x = east_xl
        east_xl += margin
    ob = Car(600, car_y, col, lane, "east", car_x, 180)
    if emergency:
        ob.emergency = True
        ob.color = (255, 255, 255)
    east_cars.append(ob)
    parking.append(ob)


def create_west(emergency=False):
    global west_xf, west_xl
    lane = choose_lane(west_cars, MAX_CARS_PER_LANE)
    if not lane:
        return
    if lane in ["F", "R"]:
        car_y = WEST[1]
        col = (255, 0, 0)
        car_x = west_xf
        west_xf -= margin
    else:
        car_y = 265
        col = (100, 0, 0)
        car_x = west_xl
        west_xl -= margin
    ob = Car(0, car_y, col, lane, "west", car_x, 0)
    if emergency:
        ob.emergency = True
        ob.color = (255, 255, 255)
    west_cars.append(ob)
    parking.append(ob)


def cars_inlanes_inphase(phase):
    match phase:
        case 1:
            return list_in_lane(north_cars, ['L']) + list_in_lane(south_cars, ['L'])
        case 2:
            return list_in_lane(north_cars, ['F', 'R']) + list_in_lane(south_cars, ['F', 'R'])
        case 3:
            return list_in_lane(east_cars, ['L']) + list_in_lane(west_cars, ['L'])
        case 4:
            return list_in_lane(east_cars, ['F', 'R']) + list_in_lane(west_cars, ['F', 'R'])
    return "NO"
    

def emergency_inlanes_inphase(phase):
    match phase:
        case 1:
            return count_emergency_in_lane(north_cars, ['L']) + count_emergency_in_lane(south_cars, ['L'])
        case 2:
            return count_emergency_in_lane(north_cars, ['F', 'R']) + count_emergency_in_lane(south_cars, ['F', 'R'])
        case 3:
            return count_emergency_in_lane(east_cars, ['L']) + count_emergency_in_lane(west_cars, ['L'])
        case 4:
            return count_emergency_in_lane(east_cars, ['F', 'R']) + count_emergency_in_lane(west_cars, ['F', 'R'])


def phase(n):
    global north_yf, south_yf, east_xf, west_xf, north_yl, south_yl, east_xl, west_xl, states
    for i in range(1,5):
        if len(cars_inlanes_inphase(i))==0:
            phase_ptimes[i-1] = time()
    if isinstance(n, int):
        phase_ptimes[n - 1] = time()
    match n:
        case 1:
            append_to_move_list(north_cars, south_cars, ['L'])
            states = [turn, turn, red, red]
            north_yl = NORTH[1]
            south_yl = SOUTH[1]
        case 2:
            append_to_move_list(north_cars, south_cars, ['F', 'R'])
            states = [green, green, red, red]
            north_yf = NORTH[1]
            south_yf = SOUTH[1]
        case 3:
            append_to_move_list(east_cars, west_cars, ['L'])
            states = [red, red, turn, turn]
            east_xl = EAST[0]
            west_xl = WEST[0]
        case 4:
            append_to_move_list(east_cars, west_cars, ['F', 'R'])
            states = [red, red, green, green]
            east_xf = EAST[0]
            west_xf = WEST[0]
        case '1yellow':
            states = [yellow, yellow, red, red]
            i = 0
            while i < len(moving_cars):
                if moving_cars[i].in_lane():
                    if moving_cars[i].dir == "north":
                        moving_cars[i].dest = north_yl
                        north_yl -= margin
                    elif moving_cars[i].dir == "south":
                        moving_cars[i].dest = south_yl
                        south_yl += margin
                    parking.append(moving_cars[i])
                    moving_cars.pop(i)
                else:
                    i += 1
        case '2yellow':
            states = [yellow, yellow, red, red]
            i = 0
            while i < len(moving_cars):
                if moving_cars[i].in_lane():
                    if moving_cars[i].dir == "north":
                        moving_cars[i].dest = north_yf
                        north_yf -= margin
                    elif moving_cars[i].dir == "south":
                        moving_cars[i].dest = south_yf
                        south_yf += margin
                    parking.append(moving_cars[i])
                    moving_cars.pop(i)
                else:
                    i += 1
        case '3yellow':
            states = [red, red, yellow, yellow]
            i = 0
            while i < len(moving_cars):
                if moving_cars[i].in_lane():
                    if moving_cars[i].dir == "east":
                        moving_cars[i].dest = east_xl
                        east_xl += margin
                    elif moving_cars[i].dir == "west":
                        moving_cars[i].dest = west_xl
                        west_xl -= margin
                    parking.append(moving_cars[i])
                    moving_cars.pop(i)
                else:
                    i += 1
        case '4yellow':
            states = [red, red, yellow, yellow]
            i = 0
            while i < len(moving_cars):
                if moving_cars[i].in_lane():
                    if moving_cars[i].dir == "east":
                        moving_cars[i].dest = east_xf
                        east_xf += margin
                    elif moving_cars[i].dir == "west":
                        moving_cars[i].dest = west_xf
                        west_xf -= margin
                    parking.append(moving_cars[i])
                    moving_cars.pop(i)
                else:
                    i += 1
                

def clear_intersection():
    for car in moving_cars:
        if car.at_intersection():
            return False
    return True


def record_stats(phase):
    return time() - phase_ptimes[phase-1], len(cars_inlanes_inphase(phase))


def random_car_generation(p_time, c_time, generation_period):
    if c_time - p_time > generation_period:
        n = random.randint(1, 4)
        em = False
        if random.randint(1, 100) == 1:
            em = True
        if n == 1:
            create_north(em)
        elif n == 2:
            create_south(em)
        elif n == 3:
            create_east(em)
        else:
            create_west(em)
        return True
    return False


def sinusoidal_car_generation(p_time, c_time, generation_period, time_period=40):
    if c_time - p_time > generation_period:
        threshhold = int(round(abs(math.sin(time()*math.pi/time_period)), 2)*100)
        n = random.randint(0, 100)
        em = False
        if random.randint(1, 100) == 1:
            em = True
        if n <= threshhold:
            n = random.randint(0, 1)
            if n:
                create_north(em)
            else:
                create_south(em)
        else:
            n = random.randint(0, 1)
            if n:
                create_east(em)
            else:
                create_west(em)
        return True
    return False


def custom_car_generation(p_time, c_time, generation_period, prob_list):
    if c_time - p_time > generation_period:
        n = random.randint(1, 100)
        north_limit = prob_list["north"] * 100
        south_limit = north_limit + prob_list["south"] * 100
        east_limit = south_limit + prob_list["east"] * 100
        west_limit = east_limit + prob_list["west"] * 100
        em = False
        if random.randint(1, 100) == 1:
            em = True
        if n <= north_limit:
            create_north(em)
        elif n <= south_limit:
            create_south(em)
        elif n <= east_limit:
            create_east(em)
        else:
            create_west(em)
        return True
    return False


def control_standard_lights(p_time, c_time, current_phase, decide=False):
    if decide:
        return (current_phase % 4) + 1
    if c_time - p_time > 3:
        return "yellow"
    return False


def control_smart_lights_v1(p_time, c_time, current_phase, decide=False):
    global MAX_TIME_V1
    phase_costs = []
    if decide:
        for i in range(1, 5):
            phase_costs.append(cost_function(len(cars_inlanes_inphase(i)), time()-phase_ptimes[i-1]))
        target_phase = phase_costs.index(max(phase_costs))+1
        MAX_TIME_V1 = math.sqrt(len(cars_inlanes_inphase(target_phase))) * 10 / CAR_VEL
        MAX_TIME_V1 = 75/CAR_VEL if MAX_TIME_V1 > 75/CAR_VEL else MAX_TIME_V1
        return target_phase
    if c_time - p_time > MAX_TIME_V1 or (len(cars_inlanes_inphase(current_phase)) == 0 and c_time - p_time > 1.5):
        return "yellow"
    return False


def control_smart_lights_v2(p_time, c_time, current_phase, decide=False, threshhold=2):
    global MIN_TIME_V2
    phase_costs = []
    for i in range(1, 5):
        phase_costs.append(cost_function(len(cars_inlanes_inphase(i)), time() - phase_ptimes[i - 1]))
    if decide:
        target_phase = phase_costs.index(max(phase_costs)) + 1
        MIN_TIME_V2 = 5 * math.sqrt(len(cars_inlanes_inphase(target_phase))) / (2 * CAR_VEL)
        MIN_TIME_V2 = 25 / CAR_VEL if MIN_TIME_V2 > 25 / CAR_VEL else MIN_TIME_V2
        return target_phase
    if c_time - p_time > MIN_TIME_V2 and (len(cars_inlanes_inphase(current_phase)) == 0 or max(phase_costs) > threshhold):
        return "yellow"
    return False


def control_smart_lights_v3(p_time, c_time, current_phase, decide=False, threshhold=2):
    global MIN_TIME_V2
    phase_costs = []
    em_vehicles = []
    em_car_moving = False
    for i in range(1, 5):
        em_vehicles.append(emergency_inlanes_inphase(i))
    for car in moving_cars:
        if car.emergency and (car.at_intersection() or car.in_lane()):
            em_car_moving = True
            break

    for i in range(1, 5):
        min_time = float('inf')
        min_ob = None
        for car in cars_inlanes_inphase(i):
            if car.creation_time < min_time:
                min_time = car.creation_time
                min_ob = car
        if min_ob:
            phase_costs.append(cost_function(len(cars_inlanes_inphase(i)), time() - min_time))
        else:
            phase_costs.append(1)
    if decide:
        if max(em_vehicles) > 0:
            cars_not_cleared.clear()
            cars_not_cleared.extend(cars_inlanes_inphase(em_vehicles.index(max(em_vehicles)) + 1))
            print(f"EMERGENCY DECISION: {em_vehicles.index(max(em_vehicles)) + 1}")
            return em_vehicles.index(max(em_vehicles)) + 1
        target_phase = phase_costs.index(max(phase_costs)) + 1
        MIN_TIME_V2 = 5 * math.sqrt(len(cars_inlanes_inphase(target_phase))) / (2 * CAR_VEL)
        MIN_TIME_V2 = 25 / CAR_VEL if MIN_TIME_V2 > 25 / CAR_VEL else MIN_TIME_V2
        cars_not_cleared.extend(cars_inlanes_inphase(target_phase))
        return target_phase
    if max(em_vehicles) > 0 and not em_car_moving:
        return "yellow"
    if not cars_not_cleared and c_time - p_time > MIN_TIME_V2 and (len(cars_inlanes_inphase(current_phase)) == 0 or max(phase_costs) > threshhold):
        return "yellow"
    return False


def handle_keypress(key):
    global start
    match key:
        case pygame.K_q:
            print(pygame.mouse.get_pos())
        case pygame.K_n:
            create_north()
        case pygame.K_e:
            create_east()
        case pygame.K_s:
            create_south()
        case pygame.K_w:
            create_west()
        case pygame.K_b:
            start = not start
        case pygame.K_1:
            phase(1)
        case pygame.K_2:
            phase(2)
        case pygame.K_3:
            phase(3)
        case pygame.K_4:
            phase(4)


states = [red, red, red, red]
run = True
start = True
curr_phase = 0
yellow_phase = False
ptime_car = time()
ptime_lights = time()
ptime_yellow = time()
start_time = time()
custom_prob = {
    "north": 1.0,
    "south": 0.,
    "east": 0.,
    "west": 0.
}

phase_ptimes = [time() for _ in range(4)]
phase_wait_times = []
car_wait_times = []
emergency_wait_times = []
cars_not_cleared = []
MAX_TIME_V1 = 3
MIN_TIME_V2 = 3
min_yellow_time = 5/CAR_VEL
while run:
    pygame.time.delay(20)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            handle_keypress(event.key)
    ctime_car = time()
    # if custom_car_generation(ptime_car, ctime_car, 0.4, custom_prob):
    if sinusoidal_car_generation(ptime_car, ctime_car, 0.4):
        ptime_car = ctime_car
    if not yellow_phase and start:
        phase(curr_phase)
    if start and not yellow_phase:
        ctime_lights = time()
        result = control_smart_lights_v3(ptime_lights, ctime_lights, curr_phase)
        if result:
            prev_phase = curr_phase
            yellow_phase = True
            ptime_yellow = time()
    if start and yellow_phase:
        ctime_yellow = time()
        if ctime_yellow - ptime_yellow < min_yellow_time or not clear_intersection():
            phase(str(prev_phase)+"yellow")
        else:
            yellow_phase = False
            curr_phase = control_smart_lights_v3(ptime_lights, ctime_lights, curr_phase, True)
            t_elapsed, cars = record_stats(curr_phase)
            phase_wait_times.append(t_elapsed)
            print(f"Time waited: {t_elapsed}")
            print(f"Cars affected: {cars}")
            print()
            ptime_lights = time()

    move_cars()
    draw(window)


pygame.quit()

elapsed = time()-start_time
print()
print("*"*30)
print("Summary")
print(f"Cars passed: {cars_cleared}")
print(f"Time elapsed: {elapsed:.3f}")
print(f"Car cleared per second: {cars_cleared/elapsed:.3f} cars/sec")
print(f"Average wait time per phase: {sum(phase_wait_times)/len(phase_wait_times):.3f} sec")
print(f"Average wait time per car: {sum(car_wait_times)/len(car_wait_times):.3f} sec")
print(f"Maximum time waited by a car: {max(car_wait_times):.3f} sec")
print(f"Maximum time waited by an emergency vehicle: {max(emergency_wait_times):.3f} sec")
