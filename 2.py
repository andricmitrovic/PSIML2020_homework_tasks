from typing import List
from pydantic import BaseModel
import json



if __name__ == "__main__":

    frame_to_box_joint = {}

    #boxes_json = input()
    #joints_json = input()

    boxes_json = "./label_humans/set/1/bboxes.json"
    joints_json = "./label_humans/set/1/joints.json"

    with open(boxes_json, 'r') as f:
        distros_dict = json.load(f)

    frames = distros_dict['frames']

    for frame in frames:
        frame_id = frame['frame_index']
        boxes = frame['bounding_boxes']
        frame_to_box_joint[str(frame_id)] = [boxes]

    with open(joints_json, 'r') as f:
        distros_dict = json.load(f)

    frames = distros_dict['frames']

    for frame in frames:
        frame_id = frame['frame_index']
        joints = frame['joints']
        # if frame_id in frame_to_box_joint.keys():
        frame_to_box_joint[str(frame_id)].append(joints)
        # else:
        #     frame_to_box_joint[str(frame_id)] = [None, joints]


    match = {}

    for frame_id, values in frame_to_box_joint.items():
        boxes = values[0]
        joints = values[1]

        for box in boxes:
            id = box['identity']
            h = box['bounding_box']['h']
            w = box['bounding_box']['w']
            x = box['bounding_box']['x']
            y = box['bounding_box']['y']
            if str(id) not in match.keys():
                match[str(id)] = [x, y, w, h, frame_id, {}]
            else:
                match[str(id)][0] = x
                match[str(id)][1] = y
                match[str(id)][2] = w
                match[str(id)][3] = h
                match[str(id)][4] = frame_id

        for joint in joints:
            id = joint['identity']
            x = joint['joint']['x']
            y = joint['joint']['y']
                                            #prosecno rastojanje jointa i approxa ili najgore
            for key, value in match.items():
                if value[4] != frame_id:
                    continue
                joint_approx_x = value[0]+value[2]/2        #vece od 1?
                joint_approx_y = value[1]+value[3]/4 #malo vise gore da bude       #negativno?

                distance_x = abs(joint_approx_x - x)
                distance_y = abs(joint_approx_y - y)

                distance = distance_y + distance_x          #euklidsko efikasnije?
                            #ima se vremena ubaci ojlerovo rastojanje mozda
                boundary_distance = (value[2]+value[3])/2

                factor = boundary_distance - distance       #nagradjujemo se da smo blizu vrata, sto je manji distance
                                                            # to je veca nagrada
                                                            #a ako je mali kvadrat i omasimo malo

                # if distance == 0.4591255899629628:          #debugg
                #     print(id, key, x, y, joint_approx_x, joint_approx_y, distance, value)
                if id not in value[5].keys():
                    value[5][id] = factor
                else:
                    value[5][id] += factor

    # #reap bad matches
    # reap_factor = -5.0 #tweak this
    #
    # for key, value in match.items():
    #     for person, factor in list(value[5].items()):
    #         if factor <= reap_factor:
    #             del value[5][person]

    for key, value in match.items():
        #print(key, value[5])
        max_factor = 0
        maxPerson = -1
        for person, factor in list(value[5].items()):
            if factor > max_factor:
                max_factor = factor
                maxPerson = person
        if maxPerson != -1:
            print(f'{maxPerson}:{key}')

