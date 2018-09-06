import random
import copy
import world.position_calc
import configuration.system as system_config
import world.position_calc as position_calc
import world.config as config


def get_strike_result_by_ratio(strike_ratio, random_obj):
    result = True
    if system_config.get_hit_prob_enable():
        if random_obj.random() > strike_ratio:
            result = False
    return result

def strike_act_validation_and_initiation(missile_type, fighter_context, detector_context_list, enemy_status, strike_list):
    '''
    打击有效性判断，更新打击列表内容，同时返回该打击动作的有效性指示
    :param missile_type: 导弹类型
    :param fighter_context: 发起攻击的战机上下文
    :param detector_context_list: 己方预警机上下文列表
    :param enemy_status: 目标状态
    :param strike_list: 打击列表[{'attacker_id': 攻击者编号, 'target_id': 目标编号, 'missile_type': 导弹类型(1：远程，2：中程), information_source_type: 信息来源类型（0：L预警机，1:S预警机，2：战机，3：被动侦测） step_count: step计数, op_count: 观测点计数, del_ind: 删除指示(默认false)}]
    :return: valid：打击动作是否有效(False，无效；True，有效)
    '''

    # print(missile_type,'\n')
    # print(fighter_context,'\n')
    # print(detector_context_list,'\n')
    # print(enemy_status,'\n')
    # print(strike_list)
    # b = a

    # 判断是否超出打击距离
    fighter_pos_x = fighter_context['pos_x']
    fighter_pos_y = fighter_context['pos_y']
    enemy_pos_x   = enemy_status['pos_x']
    enemy_pos_y   = enemy_status['pos_y']
    distance = position_calc.get_distance(fighter_pos_x, fighter_pos_y, enemy_pos_x, enemy_pos_y)
    if missile_type == config.get_s_missile_type():
        effective_strike_distance = config.get_s_missile_dis()
    if missile_type == config.get_l_missile_type():
        effective_strike_distance = config.get_l_missile_dis()
    if distance > effective_strike_distance:
        return False

    # 判断enemy是否存活
    if not enemy_status['alive']:
        return False

    sublist_of_strike = {}
    sublist_of_strike['attacker_id'] = fighter_context['id']
    sublist_of_strike['target_id']   = enemy_status['id']
    sublist_of_strike['missile_type'] = missile_type

    if fighter_context['j_enable']:
        for jammed in fighter_context['j_receive_list']:
            if enemy_status['id'] == jammed['id']:
                sublist_of_strike['information_source_type'] = config.get_hit_detection_source_passive()

    for detector in detector_context_list:
        if detector['alive'] and detector['radar_enable']:
            for radar in detector['radar_visible_list']:
                if enemy_status['id'] == radar['id']:
                    sublist_of_strike['information_source_type'] = detector['r_band']
	
    if fighter_context['radar_enable']:
        for radar in fighter_context['radar_visible_list']:
            if enemy_status['id'] == radar['id']:
                sublist_of_strike['information_source_type'] = fighter_context['r_band']
    if not 'information_source_type' in sublist_of_strike:
        print("cannot found information source type")
        print(fighter_context)
        print(detector_context_list)
        print(enemy_status)
        return False

    sublist_of_strike['step_count'] = 0
    sublist_of_strike['op_count'] = 0
    sublist_of_strike['del_ind'] = False
    strike_list.append(sublist_of_strike.copy())

    return True

def strike_judge(strike_context, fighter_radar_visible_list, random_obj):
    '''
    在途打击处理，更新打击上下文内容，判断打击成败
    规则：
    1. 如果是远程导弹，10个step后按概率判断是否打中
    2. 如果是近程导弹，4个step后按概率判断是否打中
    3. 杀伤概率（信息来源杀伤概率×观测点杀伤概率×导弹杀伤概率）
    修正版--杀伤概率（信息来源杀伤概率x导弹杀伤概率-op_countx0.01)
    :param strike_context:打击列表中项目
    :param fighter_radar_visible_list:攻击者雷达可见目标列表
    :param random_obj:随机数对象
    :return: strike_success, 1，打击成功，-1，打击失败，0，打击依然在途
    '''
    # print(strike_context)
    # print(fighter_radar_visible_list)
    # b = a
    strike_context['step_count'] += 1
    for radar in fighter_radar_visible_list:
        if strike_context['target_id'] == radar['id']:
            strike_context['op_count'] += 1

    try:
        missile_type = strike_context['missile_type']
        information_source_type = strike_context['information_source_type']
        op_count = strike_context['op_count']
        step_count = strike_context['step_count']
    except KeyError:
        print('strike_context: ', strike_context)

    strike_success = 0
    kill_prob = 0
    if missile_type == config.get_l_missile_type() and step_count >= 10:
        # kill_prob = config.get_detection_hit_probability(information_source_type) * config.get_l_missile_hit_probability() - \
        # (config.get_l_missile_op_req() - strike_context['op_count']) * 0.01
        kill_prob = (0.06 + 0.01 * op_count) * (config.get_detection_hit_probability(information_source_type)/config.get_detection_hit_probability(0))
        strike = get_strike_result_by_ratio(kill_prob, random_obj)
        if strike:
            strike_success = 1
        else:
            strike_success = -1

    if missile_type == config.get_s_missile_type() and step_count >= 4:
		# kill_prob = config.get_detection_hit_probability(information_source_type) * config.get_s_missile_hit_probability() - \
		# (config.get_s_missile_op_req() - strike_context['op_count']) * 0.01
        kill_prob = (0.14 + 0.01 * op_count) * (config.get_detection_hit_probability(information_source_type)/config.get_detection_hit_probability(0))
        strike = get_strike_result_by_ratio(kill_prob, random_obj)
        if strike:
            strike_success = 1
        else:
            strike_success = -1

    return strike_success




# TODO: uncomplete
def strike_judge_no_delay(strike_context, random_obj):
    print("strike_judge_no_delay")
    return


