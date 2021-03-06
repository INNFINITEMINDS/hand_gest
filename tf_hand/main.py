from tf_hand.utils import detector_utils as detector_utils
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf
import multiprocessing
from multiprocessing import Queue, Pool
import time
import datetime

def worker(input_q, output_q, cap_params, frame_processed):
    print(">> loading frozen model for worker")
    detection_graph, sess = detector_utils.load_inference_graph()
    sess = tf.Session(graph=detection_graph)
    while True:
        print("> ===== in worker loop, frame ", frame_processed)
        frame = input_q.get()
        if frame is not None:
            # actual detection
            boxes, scores = detector_utils.detect_objects(
                frame, detection_graph, sess)
            # draw bounding boxes
            detector_utils.draw_box_on_image(
                cap_params['num_hands_detect'], cap_params["score_thresh"], scores, boxes, cap_params['im_width'], cap_params['im_height'], frame)
            output_q.put(frame)
            frame_processed += 1
        else:
            output_q.put(frame)
    sess.close()


if __name__ == "__main__":

    cam = cv2.VideoCapture(0)
    input_q = Queue(maxsize=10)
    output_q = Queue(maxsize=10)

    cap_params = {}
    frame_processed = 0
    fps = 0

    cap_params['im_width'], cap_params['im_height'] = 640, 380
    cap_params['score_thresh'] = 0.3

    # max number of hands we want to detect/track
    cap_params['num_hands_detect'] = 2
    c = 0

    # num_workers = 5

    # To parallelize detection
    pool = Pool(
        5, worker, (input_q, output_q, cap_params, frame_processed)
    )

    while True:
        c += 1
        _, frame = cam.read()
        frame = cv2.flip(frame, 1)
        fram_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        input_q.put(fram_rgb)
        output_frame = output_q.get()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
