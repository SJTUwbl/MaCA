import json

class Map:
	def __init__(self, map_path):
		with open(map_path, 'r') as f:
			self.map_info = json.load(f)

	def get_map_size(self):
		return self.map_info['size_x'], self.map_info['size_y']

	def get_unit_num(self):
		return self.map_info['side1_detector_num'], self.map_info['side1_fighter_num'], self.map_info['side2_detector_num'], self.map_info['side2_fighter_num']

	def get_unit_property_list(self):
		return self.map_info['side1_detector_list'], self.map_info['side1_fighter_list'], self.map_info['side2_detector_list'], self.map_info['side2_fighter_list']
