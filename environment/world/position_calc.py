import math


def get_distance(a_x, a_y, b_x, b_y):
    return math.sqrt((a_x - b_x) ** 2 + (a_y - b_y) ** 2)


def angle_cal(x1, y1, x2, y2):
    '''
    :param x1, y1 the position of start point
    :param x2, y2 the position of end point
    '''
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    if angle < 0:
        angle += 360

    return int(angle)


# TODO: random position
def pos_generate(side1_d_num, side1_f_num, side2_d_num, side2_f_num, size_x, size_y, random, random_pos=False):
    '''
    random_pos == True:
    side1 on the left, side2 on the right
    random_pos == False:
    side1 on the right, side2 on the left
    '''
    if random_pos:
        pos_x = [900] * side1_d_num + [800] * side1_f_num + [100] * side2_d_num + [200] * side2_f_num
        side1_course = 180
        side2_course = 0
    else:
        pos_x = [100] * side1_d_num + [200] * side1_f_num + [900] * side2_d_num + [800] * side2_f_num
        side1_course = 0
        side2_course = 180
    side1_d_pos_y = [int(float(size_y) / (side1_d_num + 1) * (index + 1)) for index in range(side1_d_num)]
    side1_f_pos_y = [int(float(size_y) / (side1_f_num + 1) * (index + 1)) for index in range(side1_f_num)]
    side2_d_pos_y = [int(float(size_y) / (side2_d_num + 1) * (index + 1)) for index in range(side2_d_num)]
    side2_f_pos_y = [int(float(size_y) / (side2_f_num + 1) * (index + 1)) for index in range(side2_f_num)]
    pos_y = side1_d_pos_y + side1_f_pos_y + side2_d_pos_y + side2_f_pos_y

    return pos_x, pos_y, side1_course, side2_course


def pos_update(pos_x, pos_y, course, step, size_x, size_y):
    pos_x += int(math.cos(math.radians(course)) * step)
    pos_y += int(math.sin(math.radians(course)) * step)
    if pos_x < 0:
        pos_x = 0
    if pos_x > size_x:
        pos_x = size_x
    if pos_y < 0:
        pos_y = 0
    if pos_y > size_y:
        pos_y = size_y
        
    return pos_x, pos_y
