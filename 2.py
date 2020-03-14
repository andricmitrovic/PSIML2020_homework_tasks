from typing import List
from pydantic import BaseModel
import json



if __name__ == "__main__":

    frame_to_box_joint = {}
    boxes_json = "./label_humans/set/0/bboxes.json"
    joints_json = "./label_humans/set/0/joints.json"

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
        frame_to_box_joint[str(frame_id)].append(joints)


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
                match[str(id)] = [x, y, w, h, {}, {}]
            else:
                match[str(id)][:4] = [x, y, w, h]

        for joint in joints:
            id = joint['identity']
            x = joint['joint']['x']
            y = joint['joint']['y']

            for key, value in match.items():
                if #tacka u okviru pravougaonika radi nesto
