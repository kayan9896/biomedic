import pytest
from unittest.mock import MagicMock, patch
import json
import time
import cv2
from confirmaphip_core.core_model import Model
from exam import Exam
from config_manager import ConfigManager
import confirmap_dataclasses.frame_data as dataclass

with open(f"./Calibration/02OEC9900-9in-II/hardware.json", 'r') as file:
    select_carm = json.load(file)

with open(f"./config/templates/template-l.json", 'r') as file:
    template = json.load(file)


model = Model(on_simulation=True, config=ConfigManager(), carm=select_carm)



model.default_templates=[template['landmarks']]
newscn = 'frm:hp1-ap:bgn'
frame = cv2.imread('C:/Users/Torus_Dev/Desktop/biomedic/exams/exam76/2/image.png')

t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
time.sleep(5)
t0 = time.perf_counter()
analysis_type, data_for_model, data_for_vm, data_for_exam = model.exec(newscn, frame)
dt = time.perf_counter() - t0
print("exec----------------------------",dt)
model.update(analysis_type, data_for_model)




