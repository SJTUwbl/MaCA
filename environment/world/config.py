
class GlobalVar:
	api_raw = 0
	api_spatial = 1
	band_L = 0
	band_S = 1
	band_X = 2
	band_fp_num = [20, 20, 10]
	detection_hit_probability = [0.2, 0.3, 0.9, 0.6]
	hit_detection_source_detector_L = 0
	hit_detection_source_detector_S = 1
	hit_detection_source_fighter = 2
	hit_detection_source_passive = 3
	img_obs_reduce_ratio = 10
	j_coverage_angle = [45, 30, 10]
	j_max_range = [400, 400, 300]
	l_missile_dis = 120
	l_missile_hit_probability = 0.8
	l_missile_op_dec_ratio = 0.05
	l_missile_op_req = 10
	l_missile_type = 1
	l_missile_num = 2
	passive_loc_continuous_detection_req = 5
	passive_loc_fighter_num_req = 4
	r_coverage_angle_X = 120
	# major lobe
	r_jammed_angle_mlob = [10, 10, 4]
	r_jammed_range_mlobe = [120, 150, 30]
	# side lobe
	r_jammed_range_slobe_aim = [220, 260, 80]
	r_jammed_range_slobe_block = [300, 320, 120]
	r_max_range = [400, 400, 180]
	s_missile_dis = 50
	s_missile_hit_probability = 0.9
	s_missile_op_dec_ratio = 0.05
	s_missile_op_req = 4
	s_missile_type = 2
	s_missile_num = 4

def get_api_raw():
	return GlobalVar.api_raw
    
def get_api_spatial():
	return GlobalVar.api_spatial
    
def get_band_L():
	return GlobalVar.band_L
    
def get_band_S():
	return GlobalVar.band_S
    
def get_band_X():
	return GlobalVar.band_X
    
def get_band_fp_num(band):
	return GlobalVar.band_fp_num[band]
    
def get_detection_hit_probability(typ):
	return GlobalVar.detection_hit_probability[typ]
    
def get_hit_detection_source_detector_L():
	return GlobalVar.hit_detection_source_detector_L
    
def get_hit_detection_source_detector_S():
	return GlobalVar.hit_detection_source_detector_S
    
def get_hit_detection_source_fighter():
	return GlobalVar.hit_detection_source_fighter
    
def get_hit_detection_source_passive():
	return GlobalVar.hit_detection_source_passive
    
def get_img_obs_redu_ratio():
	return GlobalVar.img_obs_reduce_ratio
    
def get_j_coverage_angle(band):
	return GlobalVar.j_coverage_angle[band]
    
def get_j_max_range(band):
	return GlobalVar.j_max_range[band]
    
def get_l_missile_dis():
	return GlobalVar.l_missile_dis
    
def get_l_missile_hit_probability():
	return GlobalVar.l_missile_hit_probability
    
def get_l_missile_op_dec_ratio():
	return GlobalVar.l_missile_op_dec_ratio
    
def get_l_missile_op_req():
	return GlobalVar.l_missile_op_req
    
def get_l_missile_type():
	return GlobalVar.l_missile_type

def get_l_missile_num():
	return GlobalVar.l_missile_num
    
def get_passive_loc_continuous_detection_req():
	return GlobalVar.passive_loc_continuous_detection_req
    
def get_passive_loc_fighter_num_req():
	return GlobalVar.passive_loc_fighter_num_req
    
def get_r_coverage_angle_X():
	return GlobalVar.r_coverage_angle_X
    
def get_r_jammed_angle_mlob(band):
	return GlobalVar.r_jammed_angle_mlob[band]
    
def get_r_jammed_range_mlobe(band):
	return GlobalVar.r_jammed_range_mlobe[band]
    
def get_r_jammed_range_slobe_aim(band):
	return GlobalVar.r_jammed_range_slobe_aim[band]
    
def get_r_jammed_range_slobe_block(band):
	return GlobalVar.r_jammed_range_slobe_block[band]
    
def get_r_max_range(band):
	return GlobalVar.r_max_range[band]
    
def get_s_missile_dis():
	return GlobalVar.s_missile_dis
    
def get_s_missile_hit_probability():
	return GlobalVar.s_missile_hit_probability
    
def get_s_missile_op_dec_ratio():
	return GlobalVar.s_missile_op_dec_ratio
    
def get_s_missile_op_req():
	return GlobalVar.s_missile_op_req
    
def get_s_missile_type():
	return GlobalVar.s_missile_type

def get_s_missile_num():
	return GlobalVar.s_missile_num
