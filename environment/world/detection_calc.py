import copy
import world.config as config
import world.position_calc as position_calc


def passive_detection_calc(self_context, enemy_fighter_context_list):
    '''
    根据敌方战机干扰机接收情况，更新自身上下文中无源侦测计数器，根据可侦测标准对自身上下文中可侦测指示赋值
    需确定的问题：干扰机被动侦测雷达信号，能够全向接收雷达信号还是指向性接收？目前认为干扰机接收信号与干扰信号发射的指向性相同
    :param self_context: ：自身上下文
    :param enemy_fighter_context_list: 敌方战机上下文列表
    :return:
    '''

    for index, enemy in enumerate(enemy_fighter_context_list):
        exist = False
        for j_receive in enemy['j_receive_list']:
            if self_context['id'] == j_receive['id']:
                exist = True
        if exist:
            self_context['detection_count_list'][index] += 1
        else:
            self_context['detection_count_list'][index] = 0

def radar_visible_calc(self_context, enemy_detector_context_list, enemy_fighter_context_list):
    '''
    计算自身雷达的可见敌方目标，将自身上下文中雷达可见目标列表更新
    规则：
    1. 当一个雷达收到n个干扰机干扰时，在干扰机方向±5°范围内收到主瓣干扰，在其他方向收到副瓣干扰
    2. 若有n个干扰机对一个雷达进行干扰，只要有瞄准式干扰存在，则雷达整体受到瞄准式副瓣干扰影响，若无瞄准式干扰存在，则雷达受到阻塞式干扰影响
    3. 预警机雷达为全向探测，战机雷达为扇形方向探测
    :param self_context:自身上下文
    :param enemy_detector_context_list:敌方预警机上下文列表
    :param enemy_fighter_context_list:敌方战机上下文列表
    :return: 新发现detector数量和fighter数量
    '''

    radar_list = []
    r_band = self_context['r_band']
    o_pos_x = self_context['pos_x']
    o_pos_y = self_context['pos_y']
    course = self_context['course']
    r_max_range = config.get_r_max_range(r_band)

    # 预警机雷达为全向探测
    if r_band == config.get_band_L() or r_band == config.get_band_S():
        for unit in (enemy_detector_context_list + enemy_fighter_context_list):
            # 战机已被摧毁
            if not unit['alive']:
                continue
            e_pos_x = unit['pos_x']
            e_pos_y = unit['pos_y']
            distance = position_calc.get_distance(o_pos_x, o_pos_y, e_pos_x, e_pos_y)
            if distance <= r_max_range:
                radar_list.append(unit)
    # 战机雷达为扇形方向探测
    else:
        r_coverage_angle_X = config.get_r_coverage_angle_X()
        r_angle_low_bound = course - r_coverage_angle_X/2
        r_angle_up_bound  = course + r_coverage_angle_X/2

        for unit in (enemy_detector_context_list + enemy_fighter_context_list):
            # 战机已被摧毁
            if not unit['alive']:
                continue

            e_pos_x = unit['pos_x']
            e_pos_y = unit['pos_y']
            distance = position_calc.get_distance(o_pos_x, o_pos_y, e_pos_x, e_pos_y)
            angle = position_calc.angle_cal(o_pos_x, o_pos_y, e_pos_x, e_pos_y)
            # the coverage angle cross the horizon line
            if r_angle_low_bound < 0 and r_angle_up_bound > 0:
                if distance <= r_max_range and (angle >= (r_angle_low_bound + 360) or angle <= r_angle_up_bound):
                    radar_list.append(unit)
            elif r_angle_low_bound < 360 and r_angle_up_bound > 360:
                if distance <= r_max_range and (angle >= r_angle_low_bound or angle <= (r_angle_up_bound - 360)):
                    radar_list.append(unit)
            else:
                if distance <= r_max_range and angle >= r_angle_low_bound and angle <= r_angle_up_bound:
                    radar_list.append(unit)

    # 计算雷达新发现目标的数量，用于确定无人机的奖励
    new_detector_count = 0
    new_fighter_count  = 0
    id_list = []
    for item in self_context['radar_visible_list']:
        id_list.append(item['id'])
    for item in radar_list:
        if not item['id'] in id_list:
            if item['id'] > len(enemy_detector_context_list):
                new_fighter_count += 1
            else:
                new_detector_count += 1

    self_context['radar_visible_list'].clear()
    for radar in radar_list:
        enemy = {}
        enemy['id'] = radar['id']
        if radar['r_band'] == config.get_band_L() or radar['r_band'] == config.get_band_S():
            enemy['type'] = 0
        else:
            enemy['type'] = 1
        enemy['pos_x'] = radar['pos_x']
        enemy['pos_y'] = radar['pos_y']
        self_context['radar_visible_list'].append(enemy)

    return new_detector_count, new_fighter_count

# TODO: uncomplete
def under_jam_check(rader_x, radar_y, radar_band, jammer_x, jammer_y, jammer_course):
    '''
    判断雷达是否处于干扰机的干扰范围内
    :param rader_x:雷达机横坐标
    :param radar_y: 雷达机纵坐标
    :param radar_band: 雷达波段
    :param jammer_x: 干扰机横坐标
    :param jammer_y: 干扰机纵坐标
    :param jammer_course: 干扰机航向
    :return: True：处于干扰范围, False: 不处于干扰范围
    '''
    print('under_jam_check')
    result = null
    return result
