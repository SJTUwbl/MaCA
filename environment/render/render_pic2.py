import traceback
import pygame
import traceback
import os
import copy
from render.render_pic3 import Render as Render3

class Render:
    def __init__(self, size_x, size_y):#, o_detector_num, o_fighter_num, e_detector_num, e_fighter_num):
        self.render3 = Render3(size_x, size_y)
        return
        pygame.init()
        self.screen = pygame.display.set_mode((size_x, size_y))
        image_path = os.getcwd() + '/environment/render/resource/'
        self.detector_red  = pygame.image.load(image_path + 'detector-red-20.png')
        self.detector_blue = pygame.image.load(image_path + 'detector-blue-20.png')
        self.fighter_red   = pygame.image.load(image_path + 'fighter-red-20.png')
        self.fighter_bue   = pygame.image.load(image_path + 'fighter-blue-20.png')
        self.detector_red_rect = self.detector_red.get_rect()
        self.detector_blue_rect = self.detector_blue.get_rect()
        self.fighter_red_rect = self.fighter_red.get_rect()
        self.fighter_blue_rect = self.fighter_blue.get_rect() 
        self.side1_detector = []
        self.side1_fighter  = []
        self.side2_detector = []
        self.side2_fighter  = []

        for index in range(o_detector_num):
            detector = {}
            detector['detector'] = copy.deepcopy(self.detector_red)
            detector['rect'] = copy.deepcopy(self.detector_red_rect)
            self.side1_detector.append(detector.copy())

        for index in range(o_fighter_num):
            fighter = {}
            fighter['fighter'] = copy.deepcopy(self.fighter_red)
            fighter['rect'] = copy.deepcopy(self.fighter_red_rect)
            self.side1_fighter.append(fighter.copy())

        for index in range(e_detector_num):
            detector = {}
            detector['detector'] = copy.deepcopy(self.detector_blue)
            detector['rect'] = copy.deepcopy(self.detector_blue_rect)
            self.side2_detector.append(detector.copy())

        for index in range(e_fighter_num):
            fighter = {}
            fighter['fighter'] = copy.deepcopy(self.fighter_blue)
            fighter['rect'] = copy.deepcopy(self.fighter_blue_rect)
            self.side2_fighter.append(fighter.copy())


        self.state_time = pygame.time.Clock()

        

    def dis_update(self, done, step, o_detector_data_obs_list, o_fighter_data_obs_list, e_detector_data_obs_list, e_fighter_data_obs_list, o_detector_data_reward_list, o_fighter_data_reward_list, e_detector_data_reward_list, e_fighter_data_reward_list, o_all_reward, e_all_reward):
        print('update')
        print((o_detector_data_obs_list))
        print((o_fighter_data_obs_list))
        print((o_detector_data_reward_list))
        print((o_fighter_data_reward_list))
        print((o_all_reward))
        # b=a
        return self.render3.dis_update(done, step, o_detector_data_obs_list, o_fighter_data_obs_list, e_detector_data_obs_list, e_fighter_data_obs_list, o_detector_data_reward_list, o_fighter_data_reward_list, e_detector_data_reward_list, e_fighter_data_reward_list, o_all_reward, e_all_reward)
        
        color = 255, 255, 255
        speed = [5, 5]

        self.detector_red_rect = self.detector_red_rect.move(speed)
        self.detector_blue_rect = self.detector_blue_rect.move(speed)
        self.screen.fill(color)
        self.screen.blit(self.detector_red, self.detector_red_rect)
        self.screen.blit(self.detector_blue, self.detector_blue_rect)
        pygame.display.update()
        self.state_time.tick(30)

        return
    def dis_update_done_font(self):
        print('update done font')
        return self.render3.dis_update_done_font()
    def dis_update_font(self, step, red_reward, blue_reward, red_detector_num, blue_detector_num, red_fighter_num, blue_fighter_num, red_missile_num, blue_missile_num):
        print('dis_update_font')
        return self.render3.dis_update_font(step, red_reward, blue_reward, red_detector_num, blue_detector_num, red_fighter_num, blue_fighter_num, red_missile_num, blue_missile_num)
    def dis_update_pos(self, o_detector_pos_list, o_fighter_pos_list, e_detector_pos_list, e_fighter_pos_list):
        print('dis_update_pos')
        return self.render3.dis_update_pos(o_detector_pos_list, o_fighter_pos_list, e_detector_pos_list, e_fighter_pos_list)
    def draw_course(self, center_point_x, center_point_y, course, course_r):
        print('draw_course')
        return self.render3.draw_course(center_point_x, center_point_y, course, course_r)
    def draw_fight_rela(self, center_point_x, center_point_y, striking_list, detector_list, fighter_list, line_colour):
        print('draw_fight_rela')
        return self.render3.draw_fight_rela(center_point_x, center_point_y, striking_list, detector_list, fighter_list, line_colour)
