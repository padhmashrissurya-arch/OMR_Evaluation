import cv2
import numpy as np
import json
from .utils import normalize_image

def detect_bubbles(thresh_img):
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubble_contours = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 0.8 < area < 1000:  # Adjust based on actual bubble size
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / float(h)
            if 0.8 < aspect_ratio < 1.2:  # Roughly circular
                bubble_contours.append((x, y, w, h))

    bubble_contours.sort(key=lambda b: (b[1], b[0]))  # Sort top-to-bottom, left-to-right

    bubbles = []
    for x, y, w, h in bubble_contours:
        roi = thresh_img[y:y+h, x:x+w]
        filled = cv2.countNonZero(roi) > (roi.size * 0.5)
        bubbles.append(filled)

    return bubbles

def extract_answers(bubbles, num_subjects=5, questions_per_subject=20, options_per_question=4):
    answers = []
    idx = 0
    for _ in range(num_subjects):
        for _ in range(questions_per_subject):
            row = bubbles[idx:idx+options_per_question]
            marked = [i for i, val in enumerate(row) if val]
            if len(marked) == 1:
                answers.append(chr(65 + marked[0]))  # 'A', 'B', ...
            else:
                answers.append(None)
            idx += options_per_question
    return answers

def score_answers(student_ans, key_ans):
    score = 0
    for sa, ka in zip(student_ans, key_ans):
        if sa == ka:
            score += 1
    return score

def process_omr(image_path, answer_key_file, version):
    img = cv2.imread(image_path)
    thresh = normalize_image(img)
    bubbles = detect_bubbles(thresh)
    answers = extract_answers(bubbles)
    with open(answer_key_file) as f:
        key = json.load(f)[version]
    result = {}
    idx = 0
    total_score = 0
    for subj, key_ans in key.items():
        student_ans = answers[idx:idx+20]
        score = score_answers(student_ans, key_ans)
        result[subj] = score
        total_score += score
        idx += 20
    result['total'] = total_score
    result['answers'] = answers
    return result