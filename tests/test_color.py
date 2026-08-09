"""Unit tests for the centralized reflectivity palette."""

import numpy as np
import pytest

from mrms_renderer.palette import DEFAULT_PALETTE, TRANSPARENT, color_values


@pytest.fixture
def palette():
    return DEFAULT_PALETTE


def test_documented_thresholds(palette):
    thresholds = [entry.threshold for entry in palette]
    assert thresholds == [5.0, 10.0, 20.0, 30.0, 40.0, 50.0]


def test_transparent_below_lowest_threshold():
    result = color_values(np.array([0.0, 4.9]))
    assert (result == TRANSPARENT).all()


def test_band_colors():
    samples = np.array([5.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
    result = color_values(samples)
    expected = np.array(
        [
            (80, 180, 255, 150),
            (0, 220, 120, 180),
            (0, 170, 0, 200),
            (255, 200, 0, 220),
            (255, 80, 0, 230),
            (255, 0, 0, 240),
            (255, 0, 0, 240),
        ]
    )
    assert (result == expected).all()


def test_output_shape_and_dtype():
    values = np.zeros(12)
    result = color_values(values)
    assert result.shape == (12, 4)
    assert result.dtype == np.uint8


def test_matches_reference_implementation():
    values = np.array([-5.0, 4.9, 5.0, 7.0, 10.0, 17.5, 20.0, 29.0, 30.0, 45.0, 50.0, 99.0])
    result = color_values(values)
    assert result[0].tolist() == [0, 0, 0, 0]
    assert result[1].tolist() == [0, 0, 0, 0]
    assert result[2].tolist() == [80, 180, 255, 150]
    assert result[5].tolist() == [0, 220, 120, 180]
    assert result[10].tolist() == [255, 0, 0, 240]