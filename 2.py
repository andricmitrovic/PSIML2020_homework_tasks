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


def max_sum(dataset, chosen_ones, max, k, global_max, result, current_path):
    if k == len(dataset):
        if max > global_max[0]:
            result[:] = current_path.copy()
            global_max[0] = max
            #print(global_max, result, current_path)
        return

    for index, (key, value) in enumerate(dataset.items()):
        if k == index:
            for person, factor in value.items():
                if person not in chosen_ones:
                    chosen_ones.add(person)
                    current_path.append((key, person))
                    max_sum(dataset, chosen_ones, max + factor, k + 1, global_max, result, current_path)
                    current_path.pop()
                    chosen_ones.remove(person)
            max_sum(dataset, chosen_ones, max, k + 1, global_max, result, current_path)
            break
    return

if __name__ == "__main__":

    #boxes_json = input()
    #joints_json = input()

    boxes_json = "./label_humans/set/15/bboxes.json"
    joints_json = "./label_humans/set/15/joints.json"

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
        match[str(box_person)] = dict([])
        for box_frame, box_position in box_frames.items():
            for joint_person, joint_frames in joint_people_map.items():
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
                    joint_frames.update({box_frame: JointInfo(new_x, new_y)})

                joint_approx_x = box_position.x + box_position.w/2  # vece od 1?
                joint_approx_y = box_position.y + box_position.h/4 #malo vise gore da bude       #negativno?

                if box_position.x < joint_frames[box_frame].x < box_position.x + box_position.w \
                    and box_position.y < joint_frames[box_frame].y < box_position.y + box_position.h/2:
                    factor_medium = 1
                else:
                    factor_medium = -1



                if str(joint_person) not in match[str(box_person)].keys():
                    match[str(box_person)][str(joint_person)] = factor_medium
                else:
                    match[str(box_person)][str(joint_person)] += factor_medium

    chosen_ones = set()

    result = {}

    # for key, value in match.items():
    #     print(key, value)

    ### Reap negatives
    reap = 0
    for key, value in match.items():
        for person, factor in list(value.items()):
            if factor < reap:
                del value[person]
            else:
                value[person] -= reap

    # ### Reap all except 5 maximums for optimizing recursive function
    # for key, value in match.items():
    #     reaper = set()
    #     maximums = {k: v for k, v in sorted(value.items(), key=lambda item: item[1])}
    #     print(maximums)

    ### Print sure ones and remove them
    for key, value in list(match.items()):
        if len(value) == 1:
            for person, factor in list(value.items()):
                if factor < reap:
                    del value[person]
                else:
                    value[person] -= reap
                chosen_ones.add(person)
                print(f'{person}:{key}')
            del match[key]

    result = []

    global_max = [0]

    max_sum(match, chosen_ones, 0, 0, global_max, result, [])

    for first, second in result:
        print(f'{second}:{first}')
