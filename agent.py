import numpy as np
import copy
import random
import helper
import time

class Agent:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = np.zeros((self.width, self.height),dtype=np.int8)     # 2D array of cells
        
        self.actions_user = list()       # [[user_act_path],[],[],...]
        self.actions_user_steps = dict() # {step1:[[actions1],[actions2],[...]]
        self.actions_user_start = list() # [(x,y),(x,y),...]
        self.actions_user_end = list()   # [(x,y),(x,y),...]
        self.actions_user_len = list()   # [len1,len2,len3,...]
        self.actions_user_pensize = list()  # [size1,size2,size3,...]
        self.actions_user_pencolor = list() # [color1,color2,color3,...]
        self.actions_user_pentype = list()  # [pentype1,pentype2,pentype3,...]

        self.actions_agent_start = list()
        self.actions_agent_end = list()

        self.mc_tm = dict()
        self.mc_start = list()
        self.mc_order = 3

        self.mc_local_tm = dict()
        self.mc_local_start = list()
        self.mc_local_order = 2

        self.canvaspoints = list()
        self.current_drawing = list()

    def adjustGridsize(self, current_width, current_height):
        if current_width == self.width and current_height == self.height:
            return
        new_grid = np.zeros((current_width, current_height),dtype=np.int8)
        new_grid[:self.grid.shape[0], :self.grid.shape[1]] = self.grid
        self.grid = copy.deepcopy(new_grid)
        self.width = current_width
        self.height = current_height

    def preprocessUserActions(self):
        # keep only unique points & update start and end positions
        points_path = list()
        start = (self.current_drawing[0][0], self.current_drawing[0][1])
        self.actions_user_start.append(start)
        self.actions_user_end.append((self.current_drawing[-1][2], self.current_drawing[-1][3]))
        points_path.append(start)
        for p_list in self.current_drawing:
            p_coord = (p_list[2],p_list[3])
            points_path.append(p_coord)
        return points_path
    
    def getRelativePath(self, path):
        rel_path = list()
        for i in range(len(path)-1):
            cur_pos = path[i]
            next_pos = path[i+1]
            rel_step = (next_pos[0]-cur_pos[0], next_pos[1]-cur_pos[1])
            rel_path.append(rel_step)
        return rel_path
    
    def udpate_mc(self, rel_path, manner):
        if manner == 'global':
            if self.mc_order == 1:
                self.mc_start.append(rel_path[0])
                for i, key in enumerate(rel_path):
                    if (i+1) < len(rel_path):
                        next_key = rel_path[i+1]
                        if key not in self.mc_tm:
                            self.mc_tm[key] = [next_key]
                        else:
                            self.mc_tm[key].append(next_key)
            elif self.mc_order == 2:
                starting_state = (rel_path[0], rel_path[1])
                self.mc_start.append(starting_state)
                for i, key1 in enumerate(rel_path):
                    if (i+2) < len(rel_path):
                        key2 = rel_path[i+1]
                        next_key = rel_path[i+2]
                        if (key1, key2) not in self.mc_tm:
                            self.mc_tm[(key1, key2)] = [next_key]
                        else:
                            self.mc_tm[(key1, key2)].append(next_key)
            elif self.mc_order == 3:
                starting_state = (rel_path[0], rel_path[1], rel_path[2])
                self.mc_start.append(starting_state)
                for i, key1 in enumerate(rel_path):
                    if (i+3) < len(rel_path):
                        key2 = rel_path[i+1]
                        key3 = rel_path[i+2]
                        next_key = rel_path[i+3]
                        if (key1, key2, key3) not in self.mc_tm:
                            self.mc_tm[(key1, key2, key3)] = [next_key]
                        else:
                            self.mc_tm[(key1, key2, key3)].append(next_key)
            else:
                print(f'[ERROR:] mc_order {self.mc_order} is not supported.')
                exit(1)
        elif manner == 'local':
            if self.mc_local_order == 1:
                self.mc_local_start.append(rel_path[0])
                for i, key in enumerate(rel_path):
                    if (i+1) < len(rel_path):
                        next_key = rel_path[i+1]
                        if key not in self.mc_local_tm:
                            self.mc_local_tm[key] = [next_key]
                        else:
                            self.mc_local_tm[key].append(next_key)
            elif self.mc_local_order == 2:
                starting_state = (rel_path[0], rel_path[1])
                self.mc_local_start.append(starting_state)
                for i, key1 in enumerate(rel_path):
                    if (i+2) < len(rel_path):
                        key2 = rel_path[i+1]
                        next_key = rel_path[i+2]
                        if (key1, key2) not in self.mc_local_tm:
                            self.mc_local_tm[(key1, key2)] = [next_key]
                        else:
                            self.mc_local_tm[(key1, key2)].append(next_key)
            else:
                print(f'[ERROR:] mc_order {self.mc_local_order} is not supported.')
                exit(1)
        else:
            print(f'[ERROR:] manner {manner} is not supported.')
            exit(1)

    def storeDrawing(self, from_x, from_y, to_x, to_y):
        self.current_drawing.append([from_x, from_y, to_x, to_y])

    def preproDrawing(self, size, color, pentype, current_step):
        actions_path = self.preprocessUserActions()
        self.current_drawing = list()
        actions_path_rel = self.getRelativePath(actions_path)
        self.udpate_mc(actions_path_rel, 'global')

        self.actions_user.append(actions_path)
        self.actions_user_len.append(len(actions_path_rel))
        self.actions_user_pensize.append(size)
        self.actions_user_pencolor.append(color)
        self.actions_user_pentype.append(pentype)
        if current_step > len(self.actions_user_steps):
            self.actions_user_steps[current_step] = [actions_path_rel]
        else:
            self.actions_user_steps = dict()
            self.mc_local_tm = dict()
            self.mc_local_start = list()
            self.actions_user_steps[current_step] = [actions_path_rel]
        self.udpate_mc(actions_path_rel, 'local')

    def useMarkovChain(self, length, manner):
        if manner == 'global':
            this_tm = self.mc_tm
            this_start = self.mc_start
            this_order = self.mc_order
        elif manner == 'local':
            this_tm = self.mc_local_tm
            this_start = self.mc_local_start
            this_order = self.mc_local_order
        else:
            print(f'[ERROR:] manner {manner} is not supported.')
            exit(1)

        chain = list()
        starting_point_rel = random.choice(this_start) 
        if this_order == 1:
            chain.append(starting_point_rel)
        elif this_order == 2:
            chain.append(starting_point_rel[0])
            chain.append(starting_point_rel[1])
        elif this_order == 3:
            chain.append(starting_point_rel[0])
            chain.append(starting_point_rel[1])
            chain.append(starting_point_rel[2])
        else:
            print(f'[ERROR:] mc_order {this_order} is not supported.')
            exit(1)
        current_point = starting_point_rel

        for _ in range(length):  
            # print('current_point:',current_point)
            next_point = random.choice(this_tm[current_point])
            chain.append(next_point)
            if this_order == 1:
                current_point = next_point
            elif this_order == 2:
                current_point = (current_point[1], next_point)
                if current_point not in this_tm:
                    current_point = starting_point_rel # full backtrack
            elif this_order == 3:
                current_point = (current_point[1], current_point[2], next_point)
                if current_point not in this_tm:
                    current_point = starting_point_rel
            else:
                print(f'[ERROR:] mc_order {this_order} is not supported.')
                exit(1)
        return chain

    def agentGenerate(self, canvas, given_stpoint, width, height, manner):
        # choose method, size, color, pentype
        chosen_pentype, chosen_pensize, chosen_pencolor, chosen_length = helper.randomChoice(self.actions_user_pentype, 
                                                                                             self.actions_user_pensize, 
                                                                                             self.actions_user_pencolor, 
                                                                                             self.actions_user_len)

        if given_stpoint is None:
            chosen_starting_point = helper.get_random_starting_point(self.actions_user_start,self.actions_user_end, 200, 200, width, height)
        else:
            chosen_starting_point = given_stpoint
        chosen_starting_point = tuple(chosen_starting_point)
        mc_seq = self.useMarkovChain(chosen_length, manner)

        chosen_seq = list()
        chosen_seq.append(chosen_starting_point)
        # print(f'**** chosen length from = {self.actions_user_len} ****')
        # print(f'**** chosen length = {len(mc_seq)} -- {mc_seq}****')
        for i in range(len(mc_seq)):
            point = mc_seq[i]
            point = list(point)
            point[0] = (int)(point[0]) + (int)(chosen_seq[-1][0])
            point[1] = (int)(point[1]) + (int)(chosen_seq[-1][1])
            point = tuple(point)
            chosen_seq.append(point)

        self.actions_agent_start.append(chosen_seq[0])
        self.actions_agent_end.append(chosen_seq[-1])
        self.storeCanvasPoints(chosen_seq)

        for i in range(len(chosen_seq)-1):
            helper.draw(canvas=canvas, 
                        selected_pen_type=chosen_pentype,
                        selected_color=chosen_pencolor,
                        selected_size=chosen_pensize,
                        prev_x=chosen_seq[i][0],
                        prev_y=chosen_seq[i][1],
                        x=chosen_seq[i+1][0],
                        y=chosen_seq[i+1][1])

    def agentReplicate(self, canvas, given_stpoint, width, height):
        lines_counter = 0
        lines_ep = len(self.actions_user_steps)
        for key, value in self.actions_user_steps.items():
            lines_counter += 1
            if lines_counter == 1:
                if given_stpoint is None:
                    chosen_starting_point = helper.get_random_starting_point(self.actions_user_start,self.actions_user_end, 200, 200, width, height)
                else:
                    chosen_starting_point = given_stpoint
                chosen_starting_point = tuple(chosen_starting_point)
            else:
                cur_pointer = lines_ep - lines_counter + 1
                cur_st = list(self.actions_user_start[-cur_pointer])
                prev_st = list(self.actions_user_start[-(cur_pointer+1)])
                chosen_starting_point = list(chosen_starting_point)
                chosen_starting_point[0] = chosen_starting_point[0] + (cur_st[0] - prev_st[0])
                chosen_starting_point[1] = chosen_starting_point[1] + (cur_st[1] - prev_st[1])

            actions = value[0]
            chosen_seq = list()
            chosen_seq.append(chosen_starting_point)
            for i in range(len(actions)):
                point = actions[i]
                point = list(point)
                point[0] = (int)(point[0]) + (int)(chosen_seq[-1][0])
                point[1] = (int)(point[1]) + (int)(chosen_seq[-1][1])
                point = tuple(point)
                chosen_seq.append(point)
            
            self.actions_agent_start.append(chosen_seq[0])
            self.actions_agent_end.append(chosen_seq[-1])
            self.storeCanvasPoints(chosen_seq)

            chosen_pentype, chosen_pensize, chosen_pencolor, chosen_length = helper.randomChoice(self.actions_user_pentype, 
                                                                                        self.actions_user_pensize, 
                                                                                        self.actions_user_pencolor, 
                                                                                        self.actions_user_len)
            for i in range(len(chosen_seq)-1):
                helper.draw(canvas=canvas, 
                            selected_pen_type=chosen_pentype,
                            selected_color=chosen_pencolor, 
                            selected_size=chosen_pensize,
                            prev_x=chosen_seq[i][0],
                            prev_y=chosen_seq[i][1],
                            x=chosen_seq[i+1][0],
                            y=chosen_seq[i+1][1])
                
    def agentMirror(self, canvas, given_stpoint, width, height, manner):
        lines_counter = 0
        lines_ep = len(self.actions_user_steps)
        drawings = list()
        for key, value in self.actions_user_steps.items():
            lines_counter += 1
            if lines_counter == 1:
                if given_stpoint is None:
                    chosen_starting_point = helper.get_random_starting_point(self.actions_user_start,self.actions_user_end, 200, 200, width, height)
                else:
                    chosen_starting_point = given_stpoint
                chosen_starting_point = tuple(chosen_starting_point)
            else:
                cur_pointer = lines_ep - lines_counter + 1
                cur_st = list(self.actions_user_start[-cur_pointer])
                prev_st = list(self.actions_user_start[-(cur_pointer+1)])
                chosen_starting_point = list(chosen_starting_point)
                chosen_starting_point[0] = chosen_starting_point[0] + (cur_st[0] - prev_st[0])
                chosen_starting_point[1] = chosen_starting_point[1] + (cur_st[1] - prev_st[1])

            actions = value[0]
            tmp_seq = list()
            tmp_seq.append(chosen_starting_point)
            for i in range(len(actions)):
                point = actions[i]
                point = list(point)
                point[0] = (int)(point[0]) + (int)(tmp_seq[-1][0])
                point[1] = (int)(point[1]) + (int)(tmp_seq[-1][1])
                point = tuple(point)
                tmp_seq.append(point)

            drawings.append(tmp_seq)

        # until here: the same intuition as replicate
        ref_point = -1
        for drawing in drawings:
            if manner == 'hor':
                x_points = [point[0] for point in drawing]
                if max(x_points) > ref_point:
                    ref_point = max(x_points)
            elif manner == 'ver':
                y_points = [point[1] for point in drawing]
                if max(y_points) > ref_point:
                    ref_point = max(y_points)
            else:
                print(f'[ERROR:] manner {manner} is not supported.')
                exit(1)

        for drawing in drawings:
            if manner == 'hor':
                chosen_seq = [(ref_point+abs(ref_point-point[0]), point[1]) for point in drawing]
            elif manner == 'ver':
                chosen_seq = [(point[0], ref_point+abs(ref_point-point[1])) for point in drawing]
            else:
                print(f'[ERROR:] manner {manner} is not supported.')
                exit(1)
            
            self.actions_agent_start.append(chosen_seq[0])
            self.actions_agent_end.append(chosen_seq[-1])
            self.storeCanvasPoints(chosen_seq)

            chosen_pentype, chosen_pensize, chosen_pencolor, chosen_length = helper.randomChoice(self.actions_user_pentype, 
                                                                                        self.actions_user_pensize, 
                                                                                        self.actions_user_pencolor, 
                                                                                        self.actions_user_len)
            for i in range(len(chosen_seq)-1):
                helper.draw(canvas=canvas, 
                            selected_pen_type=chosen_pentype,
                            selected_color=chosen_pencolor, 
                            selected_size=chosen_pensize,
                            prev_x=chosen_seq[i][0],
                            prev_y=chosen_seq[i][1],
                            x=chosen_seq[i+1][0],
                            y=chosen_seq[i+1][1])
                
    def agentMerge(self, canvas):
        all_starts = self.actions_user_start + self.actions_agent_start
        all_ends = self.actions_user_end + self.actions_agent_end
        [p1,p2] = np.random.choice(len(all_starts),2,replace = False)
        start = all_starts[p1]
        end = all_ends[p2]

        chosen_pentype, chosen_pensize, chosen_pencolor, chosen_length = helper.randomChoice(self.actions_user_pentype, 
                                                                                self.actions_user_pensize, 
                                                                                self.actions_user_pencolor, 
                                                                                self.actions_user_len)
        helper.draw(canvas=canvas, 
                    selected_pen_type=chosen_pentype,
                    selected_color=chosen_pencolor, 
                    selected_size=chosen_pensize,
                    prev_x=start[0],
                    prev_y=start[1],
                    x=end[0],
                    y=end[1])

    def agentBalance(self, canvas, width, height):
        point = helper.get_novel_goal(self.canvaspoints, width, height)
        self.canvaspoints.append(point)
        choice = random.randint(0, 4)
        if choice == 0:
            self.agentGenerate(canvas, point, width, height, 'local')
        elif choice == 1:
            self.agentReplicate(canvas, point, width, height)
        elif choice == 2:
            self.agentMirror(canvas, point, width, height, 'hor')
        elif choice == 3:
            self.agentMirror(canvas, point, width, height, 'ver')
        else:
            self.agentGenerate(canvas, point, width, height, 'global')

    def storeCanvasPoints(self, points_list):
        for point in points_list:
            self.canvaspoints.append(point)

    def printAgentInfo(self):
        print('-'*50)
        print(f'[AGENT:] width: {self.width}, height: {self.height}')
        # print(f'[AGENT:] grid: {self.grid}')
        print(f'[AGENT:] actions: {self.actions_user}')
        print(f'[AGENT:] actions len: {self.actions_user_len}')
        print(f'[AGENT:] actions pensize: {self.actions_user_pensize}')
        print(f'[AGENT:] actions color: {self.actions_user_pencolor}')
        print(f'[AGENT:] actions pentype: {self.actions_user_pentype}')
        print('-'*50)