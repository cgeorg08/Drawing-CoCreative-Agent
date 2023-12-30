import random
import numpy as np

def randomChoice(pentypes, pensizes, pencolors, lengths):
    chosen_pentype = random.choice(pentypes)
    chosen_pensize = random.choice(pensizes)
    chosen_pencolor = random.choice(pencolors)
    chosen_length = random.choice(lengths)
    return chosen_pentype, chosen_pensize, chosen_pencolor, chosen_length

def draw(canvas,
         selected_pen_type,
         selected_color,
         selected_size,
         prev_x,
         prev_y,
         x,
         y
):
    if selected_pen_type == "line":
        canvas.create_line(prev_x, prev_y, x, y, fill=selected_color, width=selected_size, smooth=True)
    elif selected_pen_type == "round":
        x1 = x - selected_size
        y1 = y - selected_size
        x2 = x + selected_size
        y2 = y + selected_size
        canvas.create_oval(x1, y1, x2, y2, fill=selected_color, outline=selected_color)
    elif selected_pen_type == "square":
        x1 = x - selected_size
        y1 = y - selected_size
        x2 = x + selected_size
        y2 = y + selected_size
        canvas.create_rectangle(x1, y1, x2, y2, fill=selected_color, outline=selected_color)
    elif selected_pen_type == "arrow":
        x1 = x - selected_size
        y1 = y - selected_size
        x2 = x + selected_size
        y2 = y + selected_size
        canvas.create_polygon(x1, y1, x1, y2, x, y2, fill=selected_color, outline=selected_color)
    elif selected_pen_type == "diamond":
        x1 = x - selected_size
        y1 = y
        x2 = x
        y2 = y - selected_size
        x3 = x + selected_size
        y3 = y
        x4 = x
        y4 = y + selected_size
        canvas.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, fill=selected_color, outline=selected_color)

def get_random_starting_point(starts, ends, x_scale, y_scale, width, height):
    choice = random.randint(0, 2)
    chosen_starting_point = random.choice(starts+ends)
    chosen_starting_point = list(chosen_starting_point)

    # find the quarter
    if chosen_starting_point[0] < width/2 and chosen_starting_point[1] < height/2:
        quarter = 1
    elif chosen_starting_point[0] < width/2 and chosen_starting_point[1] > height/2:
        quarter = 3
    elif chosen_starting_point[0] > width/2 and chosen_starting_point[1] < height/2:
        quarter = 2
    else:
        quarter = 4

    # do a random action
    if choice >= 0 and choice <= 1:
        quarters = [1, 2, 3, 4]
        quarters.remove(quarter)
        target_quarter = random.choice(quarters)
        if target_quarter == 1:
            chosen_starting_point[0] = width/2 - abs(chosen_starting_point[0] - width/2)
            chosen_starting_point[1] = height/2 - abs(chosen_starting_point[1] - height/2)
        elif target_quarter == 2:
            chosen_starting_point[0] = width/2 + abs(chosen_starting_point[0] - width/2)
            chosen_starting_point[1] = height/2 - abs(chosen_starting_point[1] - height/2)
        elif target_quarter == 3:
            chosen_starting_point[0] = width/2 - abs(chosen_starting_point[0] - width/2)
            chosen_starting_point[1] = height/2 + abs(chosen_starting_point[1] - height/2)
        else:
            chosen_starting_point[0] = width/2 + abs(chosen_starting_point[0] - width/2)
            chosen_starting_point[1] = height/2 + abs(chosen_starting_point[1] - height/2)
    else:
        chosen_starting_point[0] = chosen_starting_point[0] + random.randint(1, x_scale)
        chosen_starting_point[1] = chosen_starting_point[1] + random.randint(1, y_scale)
        chosen_starting_point[0] = chosen_starting_point[0] if chosen_starting_point[0] < width else width-50
        chosen_starting_point[1] = chosen_starting_point[1] if chosen_starting_point[1] < height else height-50
    return chosen_starting_point

def get_novel_goal(canvas_points, width, height):
    min_x, max_x = 0, width
    min_y, max_y = 0, height
    total_genpoints, K = 10, 5
    
    # step 1: generate points & form the new points (plus if generation>1) and clip them
    long_scp_gen = list()
    for i in range(total_genpoints):
        random_point = (random.uniform(min_x, max_x),random.uniform(min_y, max_y))
        random_point_x, random_point_y = random_point[0], random_point[1]
        random_point_x = random_point_x if random_point_x < max_x else max_x
        random_point_x = random_point_x if random_point_x > min_x else min_x
        random_point_y = random_point_y if random_point_y < max_y else max_y
        random_point_y = random_point_y if random_point_y > min_y else min_y
        random_point_modif = (random_point_x, random_point_y)
        long_scp_gen.append(random_point_modif)
    long_scp_gen_array = np.array(long_scp_gen)

    # step 2: find K neighbours for each generated point
    goal_buffer_array = np.array(canvas_points)
    dist_array = np.zeros((total_genpoints, K))
    for i in range(total_genpoints):
        # 1D array of <goal_buffer_array> size
        cur_distances_array = np.sqrt(np.sum((goal_buffer_array - long_scp_gen_array[i])**2, axis=1))   
        for j in range(min(K, len(canvas_points))):
            min_index = np.argmin(cur_distances_array)
            dist_array[i,j] = cur_distances_array[min_index]
            cur_distances_array = np.delete(cur_distances_array, min_index)

    # step 3: find novelty score for the L points and get the max
    novelty_scores = np.sum(dist_array, axis=1) / K
    chosen_goal = long_scp_gen[np.argmax(novelty_scores)]

    return np.array(chosen_goal)