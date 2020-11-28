import cv2
import face_recognition
from datetime import datetime, timedelta
import numpy as np
import platform
import pickle
import pymysql
import face_model_pi
import argparse

# import secert

# Our list of known face encodings and a matching list of metadata about each face.
known_face_encodings = []
known_face_metadata = []

dict_feature_person = {}


def save_known_faces():
    with open("known_faces.dat", "wb") as face_data_file:
        face_data = [known_face_encodings, known_face_metadata]
        pickle.dump(face_data, face_data_file)
        print("Known faces backed up to disk.")


def load_known_faces():
    global known_face_encodings, known_face_metadata

    # try:
    #     with open("known_faces.dat", "rb") as face_data_file:
    #         known_face_encodings, known_face_metadata = pickle.load(face_data_file)
    #         print("Known faces loaded from disk.")
    # except FileNotFoundError as e:
    #     print("No previous face data found - starting with a blank known face list.")
    #     pass


def running_on_jetson_nano():
    return platform.machine() == "aarch64"


def get_jetson_gstreamer_source(capture_width=1280, capture_height=720, display_width=1280, display_height=720,
                                framerate=60, flip_method=0):
    """
    Return an OpenCV-compatible video source description that uses gstreamer to capture video from the camera on a Jetson Nano
    """
    return (
            f'nvarguscamerasrc ! video/x-raw(memory:NVMM), ' +
            f'width=(int){capture_width}, height=(int){capture_height}, ' +
            f'format=(string)NV12, framerate=(fraction){framerate}/1 ! ' +
            f'nvvidconv flip-method={flip_method} ! ' +
            f'video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! ' +
            'videoconvert ! video/x-raw, format=(string)BGR ! appsink'
    )


def register_new_face(face_encoding, face_image):
    """
    Add a new person to our list of known faces
    """
    # Add the face encoding to the list of known faces
    known_face_encodings.append(face_encoding)
    # Add a matching dictionary entry to our metadata list.
    # We can use this to keep track of how many times a person has visited, when we last saw them, etc.
    new_metadata = {
        "first_seen": datetime.now(),
        "first_seen_this_interaction": datetime.now(),
        "last_seen": datetime.now(),
        "seen_count": 1,
        "seen_frames": 1,
        "face_image": face_image,
        "person_id": len(known_face_encodings) + 1
    }
    known_face_metadata.append(new_metadata)
    return new_metadata


def lookup_known_face(face_encoding):
    """
    See if this is a face we already have in our face list
    """
    metadata = None

    # If our known face list is empty, just return nothing since we can't possibly have seen this face.
    if len(known_face_encodings) == 0:
        return metadata

    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    best_match_index = np.argmin(face_distances)
    if face_distances[best_match_index] < 0.65:
        metadata = known_face_metadata[best_match_index]
        metadata["last_seen"] = datetime.now()
        metadata["seen_frames"] += 1

        if datetime.now() - metadata["first_seen_this_interaction"] > timedelta(minutes=5):
            metadata["first_seen_this_interaction"] = datetime.now()
            metadata["seen_count"] += 1

    return metadata


def save_json2db(save_dict, name_db):
    keys = save_dict.keys()
    values = save_dict.values()


def main_loop():
    if running_on_jetson_nano():
        video_capture = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
    else:
        video_capture = cv2.VideoCapture('/home/muyun99/MyGithub/face_tracking/hamilton_clip.mp4')

    parser = argparse.ArgumentParser(description='face model test')
    # general
    parser.add_argument('--image-size', default='112,112', help='')
    parser.add_argument('--model', default='', help='path to load model.')
    parser.add_argument('--gpu', default=0, type=int, help='gpu id')
    args = parser.parse_args()

    vec = args.model.split(',')
    model_prefix = vec[0]
    model_epoch = int(vec[1])
    model = face_model_pi.FaceModel(args.gpu, model_prefix, model_epoch)
    number_of_faces_since_save = 0

    index = 0

    while True:
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        # face_locations = face_recognition.face_locations(rgb_small_frame)
        result = model.detector.detect(rgb_small_frame, threshold=0.8)
        face_boxes = result[0]
        face_locations = []
        for face_box in face_boxes:
            face_locations.append([int(face_box[0]), int(face_box[1]), int(face_box[2]), int(face_box[3])])

        if index > 1e10:
            index = 0
        if index % 4 == 0:
            pic_time = datetime.now()
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_labels = []
            for face_location, face_encoding in zip(face_locations, face_encodings):
                metadata = lookup_known_face(face_encoding)
                if metadata is not None:
                    time_at_door = datetime.now() - metadata['first_seen_this_interaction']
                    face_label = f"At door {int(time_at_door.total_seconds())}s"

                else:
                    face_label = "New visitor!"
                    xmin, ymin, xmax, ymax = face_location

                    face_image = small_frame[ymin:ymax, xmin:xmax]
                    face_image = cv2.resize(face_image, (150, 150))

                    metadata = register_new_face(face_encoding, face_image)

                    sql_insert = f'INSERT INTO face_feature (p_id, p_feature_1) VALUES ("{known_face_metadata[-1]["person_id"]}","{face_encoding}");'
                    print(sql_insert)
                    effect_row = cursor.execute(sql_insert)
                    conn.commit()

                sql_insert = f'INSERT INTO pic_face (pic_id, pic_gps, pic_time, face_loc, face_feature, face_id) VALUES ("{index}","A","{pic_time}", "{face_location}", "{face_encoding}", "{metadata["person_id"]}");'
                # print(sql_insert)
                effect_row = cursor.execute(sql_insert)
                conn.commit()

                face_labels.append(face_label)
        #         before_face_labels=face_labels
        #         before_face_locations=face_locations
        # else:
        #      face_labels = before_face_labels
        #      face_locations = before_face_locations
        index += 1

        # Draw a box around each face and label each face
        for (xmin, ymin, xmax, ymax), face_label in zip(face_locations, face_labels):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            xmin *= 4
            ymin *= 4
            xmax *= 4
            ymax *= 4

            # Draw a box around the face
            # cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (1, 1), (100, 100), (0, 0, 255), 2)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (xmin, ymax - 35), (xmax, ymax), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, face_label, (xmin + 6, ymax - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        # Display recent visitor images
        number_of_recent_visitors = 0
        for metadata in known_face_metadata:
            # If we have seen this person in the last minute, draw their image
            if datetime.now() - metadata["last_seen"] < timedelta(seconds=10) and metadata["seen_frames"] > 5:
                # Draw the known face image
                x_position = number_of_recent_visitors * 150
                frame[30:180, x_position:x_position + 150] = metadata["face_image"]
                number_of_recent_visitors += 1

                # Label the image with how many times they have visited
                visits = metadata['seen_count']
                visit_label = f"{visits} visits"
                if visits == 1:
                    visit_label = "First visit"
                cv2.putText(frame, visit_label, (x_position + 10, 170), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255),
                            1)

        if number_of_recent_visitors > 0:
            cv2.putText(frame, "Visitors at Door", (5, 18), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        # Display the final frame of video with boxes drawn around each detected fames
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            save_known_faces()
            break

        # We need to save our known faces back to disk every so often in case something crashes.
        if len(face_locations) > 0 and number_of_faces_since_save > 100:
            save_known_faces()
            number_of_faces_since_save = 0
        else:
            number_of_faces_since_save += 1

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    user = 'hack'
    passwd = 'SoonAfterPapapa'

    conn = pymysql.connect(host='192.168.1.104', port=3306, user=user, passwd=passwd, db='Hackathon')
    cursor = conn.cursor()

    load_known_faces()
    main_loop()

    cursor.close()
    conn.close()
