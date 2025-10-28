import pytest
from unittest.mock import MagicMock, patch
from math import isclose

from imu2 import IMU_handler

@pytest.fixture
def handler():
    return IMU_handler(
        ApplyTarget=True,
        CarmRangeTilt=[-10, 10],
        CarmRangeRotation=[-25, -10, 10, 25],
        CarmTargetTilt=5,
        CarmTargetRot=[0, -15, 15],
        scale=0.5,
        tol=0.2
    )

def test_set_tilt(handler):
    handler.set_tilt(5.0)
    assert isclose(handler.tilt_angle, 5.0)
    assert isclose(handler.prev_angle, 0.0)
    assert handler.last_stable_time > 0

def test_set_tilt_within_tolerance(handler):
    handler.set_tilt(0.1)  # within tol=0.2
    assert isclose(handler.tilt_angle, 0.0)  # no update
    assert isclose(handler.prev_angle, 0.0)

def test_set_rotation(handler):
    handler.set_rotation(12.0)
    assert isclose(handler.rotation_angle, 12.0)
    assert isclose(handler.prev_rotation_angle, 0.0)
    assert handler.last_stable_time > 0

def test_set_rotation_within_tolerance(handler):
    handler.set_rotation(0.1)  # within tol=0.2
    assert isclose(handler.rotation_angle, 0.0)  # no update
    assert isclose(handler.prev_rotation_angle, 0.0)

@pytest.mark.parametrize("rotation,stage,expected", [
    (-15, 0, 'ob'),   # in range, outside ap
    (2, 0, 'ap'),    # in ap range
    (2, 1, 'ap'),    # same as stage 0
    (-15, 1, None),   # obtarget1 = -15, rotation * obtarget1 > 0 → None
    (0, 1, 'ap'),     # rotation * obtarget1 = 0 → ob
    (10, 2, 'ob'),    # between (ob_min + aptarget)/2 and (ob_max + aptarget)/2
    (-20, 2, 'ob'),   # outside ap zone
])
def test_activeside(handler, rotation, stage, expected):
    handler.set_rotation(rotation)
    result = handler.activeside(stage=stage)
    assert result == expected

def test_activeside_stage3_with_registration(handler):
    handler.iscupreg = True
    handler.set_rotation(10)
    result = handler.activeside(stage=3)
    assert result == 'ob'

    handler.set_rotation(-20)
    handler.used_ob = 15
    result = handler.activeside(stage=3)
    assert result is None

def test_window_shown_initialization(handler):
    assert isinstance(handler.window_shown, bool)

@pytest.mark.parametrize("tilt,stage,expected", [
    (5.1, 0, True),     # within tolerance of tilttarget
    (9.9, 0, False),     # within CarmRangeTilt, applytarget ignored
    (11.0, 0, False),   # outside CarmRangeTilt
    (5.3, 1, False),    # stage > 0, tilt not close to target
    (5.0, 1, True),     # exact match
])
def test_is_tilt_valid(handler, tilt, stage, expected):
    handler.set_tilt(tilt)
    result = handler.is_tilt_valid(stage)
    assert result == expected

@pytest.mark.parametrize("rotation,stage,expected", [
    (0.1, 0, True),    # close to aptarget
    (15.0, 0, True),    # matches obtarget2
    (-15.0, 0, True),   # matches obtarget1
    (0.0, 0, True),     # in rangel/ranger
    (25.1, 0, False),   # outside range
    (0, 1, True),    # matches aptarget
    (15.0, 1, True),    # matches obtarget2
    (-15.0, 1, False),  # rotation * obtarget1 = 225 > 0 → not valid
])
def test_is_rot_valid_basic(handler, rotation, stage, expected):
    handler.set_rotation(rotation)
    result = handler.is_rot_valid(stage)
    assert result == expected

def test_is_rot_valid_with_data_ob_image_none(handler):
    handler.set_rotation(15.0)
    data = {
        'hp1-ap': {'image': None},
        'hp1-ob': {'image': 'some_image'}
    }
    result = handler.is_rot_valid(stage=0, data=data)
    assert result is False  # because ap image is None

def test_is_rot_valid_stage_2_ob_targets(handler):
    handler.set_rotation(15.0)
    result = handler.is_rot_valid(stage=2)
    assert result is True

def test_is_rot_valid_stage_3_with_registration_ap(handler):
    handler.iscupreg = True
    handler.set_rotation(0)
    result = handler.is_rot_valid(stage=3)
    assert result is True

def test_is_rot_valid_stage_3_with_registration_ob(handler):
    handler.istrireg = True
    handler.used_ob = -15.0
    handler.set_rotation(-15.0)
    result = handler.is_rot_valid(stage=3)
    assert result is True




def test_show_icon_true(handler):
    handler.set_tilt(5.0)
    handler.set_rotation(15.0)
    handler.prev_angle = 5.0
    handler.prev_rotation_angle = 15.0
    handler.last_stable_time = 100.0
    data = {'hp1-ap': {'image': 'img'}, 'hp1-ob': {'image': 'img'}}
    with patch("time.time", return_value=103.5):
        result = handler.show_icon(stage=0, data=data)
        assert result is True
        assert handler.icon_shown is True

def test_show_icon_false_due_to_instability(handler):
    handler.set_tilt(5.0)
    handler.set_rotation(15.0)
    handler.prev_angle = 4.0
    handler.prev_rotation_angle = 15.0
    handler.last_stable_time = 100.0
    data = {'hp1-ap': {'image': 'img'}, 'hp1-ob': {'image': 'img'}}
    with patch("time.time", return_value=104.0):
        result = handler.show_icon(stage=0, data=data)
        assert result is False
        assert handler.icon_shown is False

def test_show_icon_false_due_to_invalid_rotation(handler):
    data = {'hp1-ap': {'image': None}, 'hp1-ob': {'image': 'img'}}
    with patch("time.time", return_value=104.0):
        result = handler.show_icon(stage=0, data=data)
        assert result is False
        assert handler.icon_shown is False

def test_show_window_stays_true_on_change(handler):
    handler.prev_angle = 4.0  # change detected
    data = {'hp1-ap': {'image': 'img'}, 'hp1-ob': {'image': 'img'}}
    with patch("time.time", return_value=101.0):
        result = handler.show_window(stage=0, data=data)
        assert result is True
        assert handler.window_shown is True

def test_show_window_turns_false_after_stability(handler):
    handler.window_shown = True
    handler.set_tilt(5.0)
    handler.set_rotation(15.0)
    handler.prev_angle = 5.0
    handler.prev_rotation_angle = 15.0
    handler.last_stable_time = 100.0
    data = {'hp1-ap': {'image': 'img'}, 'hp1-ob': {'image': 'img'}}
    with patch("time.time", return_value=106.0):
        result = handler.show_window(stage=0, data=data)
        assert result is False
        assert handler.window_shown is False

def test_show_window_remains_true_if_not_stable_long_enough(handler):
    handler.window_shown = True
    handler.prev_angle = 5.0
    handler.prev_rotation_angle = 10.0
    data = {'hp1-ap': {'image': 'img'}, 'hp1-ob': {'image': 'img'}}
    with patch("time.time", return_value=104.0):  # < 5s since last_stable_time
        result = handler.show_window(stage=0, data=data)
        assert result is True
        assert handler.window_shown is True

