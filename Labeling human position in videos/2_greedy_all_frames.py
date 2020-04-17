import json
from math import sqrt

class BoxInfo(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    def __str__(self):
        return f'{x}, {y}, {w}, {h}'
    def __repr__(self):
        return str(self)

class JointInfo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return f'{x}, {y}'
    def __repr__(self):
        return str(self)


if __name__ == "__main__":

    #boxes_json = input()
    #joints_json = input()

    boxes_json = "./label_humans/set/10/bboxes.json"
    joints_json = "./label_humans/set/10/joints.json"

    box_people_map = {}

    with open(boxes_json, 'r') as f:
        distros_dict = json.load(f)

    frames = distros_dict['frames']

    for frame in frames:
        frame_id = frame['frame_index']
        boxes = frame['bounding_boxes']
        for box in boxes:
            id = box['identity']
            h = box['bounding_box']['h']
            w = box['bounding_box']['w']
            x = box['bounding_box']['x']
            y = box['bounding_box']['y']

            if id not in box_people_map.keys():
                box_people_map[id] = dict([])

            box_people_map[id].update({frame_id: BoxInfo(x, y, w, h)})

    joint_people_map = {}

    with open(joints_json, 'r') as f:
        distros_dict = json.load(f)

    frames = distros_dict['frames']

    for frame in frames:
        frame_id = frame['frame_index']
        joints = frame['joints']
        for joint in joints:
            id = joint['identity']
            x = joint['joint']['x']
            y = joint['joint']['y']

            if str(id) not in joint_people_map.keys():
                joint_people_map[str(id)] = {}

            joint_people_map[id].update({frame_id: JointInfo(x, y)})

    match = dict([])

    for box_person, box_frames in box_people_map.items():
        for box_frame, box_position in box_frames.items():
            for joint_person, joint_frames in list(joint_people_map.items()):
                if box_frame not in joint_frames.keys():
                    left_frame = max([i for i in joint_frames.keys() if i < box_frame], default=None)
                    right_frame = min([i for i in joint_frames.keys() if i > box_frame], default=None)
                    if not left_frame or not right_frame:               #ovde nesto ako hoces da popravis test primer
                        continue
                    interpol_factor = (right_frame - left_frame)
                    new_x = joint_frames[left_frame].x + \
                            (joint_frames[right_frame].x - joint_frames[left_frame].x)/interpol_factor
                    new_y = joint_frames[left_frame].y + \
                            (joint_frames[right_frame].y - joint_frames[left_frame].y)/interpol_factor
                    joint_people_map[joint_person][box_frame] = JointInfo(new_x, new_y)

    for joint_person, joint_frames in joint_people_map.items():
        for joint_frame, joint_position in joint_frames.items():
            for box_person, box_frames in list(box_people_map.items()):
                if joint_frame not in box_frames.keys():
                    left_frame = max([i for i in box_frames.keys() if i < joint_frame], default=None)
                    right_frame = min([i for i in box_frames.keys() if i > joint_frame], default=None)
                    if not left_frame or not right_frame:               #ovde nesto ako hoces da popravis test primer
                        #print("kako je doslo do ovde")
                        continue

                    interpol_factor = (right_frame - left_frame)
                    new_x = box_frames[left_frame].x + \
                            (box_frames[right_frame].x - box_frames[left_frame].x)/interpol_factor
                    new_y = box_frames[left_frame].y + \
                            (box_frames[right_frame].y - box_frames[left_frame].y)/interpol_factor
                    new_w = box_frames[left_frame].w + \
                            (box_frames[right_frame].w - box_frames[left_frame].w)/interpol_factor
                    new_h = box_frames[left_frame].h + \
                            (box_frames[right_frame].h - box_frames[left_frame].h)/interpol_factor
                    box_people_map[box_person][joint_frame] = BoxInfo(new_x, new_y, new_w, new_h)


    for box_person, box_frames in box_people_map.items():
        match[str(box_person)] = dict([])
        for box_frame, box_position in box_frames.items():
            for joint_person, joint_frames in joint_people_map.items():
                if box_frame not in joint_frames.keys():
                    continue

                joint_approx_x = box_position.x + box_position.w/2  # vece od 1?
                joint_approx_y = box_position.y + box_position.h/4 #malo vise gore da bude       #negativno?

                if box_position.w == 0 or box_position.h == 0:
                    continue

                factor_medium = 0
                ### Check if in a box
                if box_position.x <= joint_frames[box_frame].x <= box_position.x + box_position.w \
                    and box_position.y <= joint_frames[box_frame].y <= box_position.y + box_position.h:
                    factor_medium = 1
                else:
                    factor_medium = -2

                ### Check if in a circle
                if factor_medium == 1:
                    radius = max(box_position.w, box_position.h)  #could be zero!!!!
                    euclid = sqrt((joint_frames[box_frame].x - joint_approx_x)**2 +
                                  (joint_frames[box_frame].y - joint_approx_y)**2)
                    factor_medium = 1 - euclid/radius


                if str(joint_person) not in match[str(box_person)].keys():
                    match[str(box_person)][str(joint_person)] = factor_medium
                else:
                    match[str(box_person)][str(joint_person)] += factor_medium


    ### Reap negatives
    reap = 0
    for key, value in match.items():
        for person, factor in list(value.items()):
            if factor < reap:
                del value[person]
            else:
                value[person] -= reap

    chosen_ones = set()

    ### Greedy approach
    necks = set()
    for key, value in match.items():
        for person, factor in list(value.items()):
            necks.add(str(person))

    while len(chosen_ones) != len(necks):
        max_factor = -1
        max_box = -1
        max_neck = -1

        for key, value in match.items():
            for person, factor in list(value.items()):
                if person not in chosen_ones and factor > max_factor:
                    max_factor = factor
                    max_box = key
                    max_neck = person

        if max_box == -1:
            break
        chosen_ones.add(max_neck)
        del match[max_box]
        print(f'{max_neck}:{max_box}')

