from __future__ import annotations

import numpy as np
import pytest

from bigimtools import tiler


@pytest.mark.parametrize("tile_size", ((10, 10), (10, 23), (10, 23)))
@pytest.mark.parametrize("overlap", ((0, 0), (5, 5), (3, 6), (6, 3)))
def test_round_trip(imcamera, tile_size, overlap):

    tiles = dict(tiler.split_into_tiles(imcamera, tile_size, overlap))

    for v in tiles.values():
        assert v.shape == tile_size

    merge = tiler.join_tiles(tiles, overlap)

    sh = imcamera.shape
    np.testing.assert_almost_equal(merge[: sh[0], : sh[1]], imcamera)


@pytest.mark.parametrize("tile_size", ((10, 10), (10, 23), (10, 23)))
@pytest.mark.parametrize("overlap", ((5, 5), (3, 6), (6, 3)))
@pytest.mark.parametrize("init", ((1, 1), (5, 10), (10, 5)))
def test_equalize_simple1(imcamera, tile_size, overlap, init):
    tiles = dict(tiler.split_into_tiles(imcamera, tile_size, overlap))
    corrections = tiler.equalize_tiles(
        tiles, overlap, init, est_func=lambda x, y: 2
    )

    # we need to skip the first which is the init tile.
    np.testing.assert_almost_equal(
        np.fromiter(corrections.values(), dtype=float)[1:], 2
    )


@pytest.mark.parametrize("tile_size", ((10, 10), (10, 23), (10, 23)))
@pytest.mark.parametrize("overlap", ((5, 5), (3, 6), (6, 3)))
@pytest.mark.parametrize("init", ((1, 1), (5, 10), (10, 5)))
def test_equalize_simple2(imcamera, tile_size, overlap, init):
    tiles = dict(tiler.split_into_tiles(imcamera, tile_size, overlap))
    corrections = tiler.equalize_tiles(
        tiles, overlap, init, agg_func=lambda x: 3
    )

    # we need to skip the first which is the init tile.
    np.testing.assert_almost_equal(
        np.fromiter(corrections.values(), dtype=float)[1:], 3
    )


@pytest.mark.parametrize("tile_size", ((10, 10), (10, 23), (10, 23)))
@pytest.mark.parametrize("overlap", ((5, 5), (3, 6), (6, 3)))
@pytest.mark.parametrize("init", ((1, 1), (5, 10), (10, 5)))
def test_equalize(imcamera, tile_size, overlap, init):
    tiles = dict(tiler.split_into_tiles(imcamera, tile_size, overlap))
    merge = tiler.join_tiles(tiles, overlap, tiler.ConstantDict(13))

    sh = imcamera.shape
    np.testing.assert_almost_equal(
        merge[: sh[0], : sh[1]], 13 * imcamera
    )


@pytest.mark.parametrize("tile_size", ((10, 10), (10, 23), (10, 23)))
@pytest.mark.parametrize("overlap", ((5, 5), (3, 6), (6, 3)))
@pytest.mark.parametrize("init", ((1, 1), (5, 10), (10, 5)))
def test_equalize_change_init(imcamera, tile_size, overlap, init):

    tiles = dict(tiler.split_into_tiles(imcamera, tile_size, overlap))

    tiles[init] = tiles[init] * 13.0

    corrections = tiler.equalize_tiles(tiles, overlap, init)
    merge = tiler.join_tiles(tiles, overlap, corrections)

    sh = imcamera.shape
    np.testing.assert_almost_equal(
        merge[: sh[0], : sh[1]], 13.0 * imcamera
    )


@pytest.mark.parametrize("tile_size", ((10, 10), (10, 23), (10, 23)))
@pytest.mark.parametrize("overlap", ((5, 5), (3, 6), (6, 3)))
@pytest.mark.parametrize("init", ((1, 1), (5, 10), (10, 5)))
def test_equalize_changed(imcamera, tile_size, overlap, init):

    tiles = dict(tiler.split_into_tiles(imcamera, tile_size, overlap))

    for ndx0 in (3, 5, 13):
        for ndx1 in (4, 7, 20):
            tiles[(ndx0, ndx1)] = tiles[(ndx0, ndx1)] * 13.0

    corrections = tiler.equalize_tiles(tiles, overlap, init)

    for ndx0 in (3, 5, 13):
        for ndx1 in (4, 7, 20):
            assert corrections[(ndx0, ndx1)] == 1 / 13.0


# Crashes test suite! Beware
# @pytest.mark.parametrize("tile_size", ((3, 3), (5, 10), (10, 10)))
# @pytest.mark.parametrize("overlap", ((5, 5), (3, 6), (6, 3)))
# @pytest.mark.parametrize("init", ((1, 1), (5, 10), (10, 5)))
# def test_ov_equalize_changed(imcamera, tile_size, overlap, init):

#     tiles = dict(tiler.split_into_tiles(imcamera, tile_size, overlap))

#     for ndx0 in (3, 5, 13):
#         for ndx1 in (4, 7, 20):
#             tiles[(ndx0, ndx1)] = tiles[(ndx0, ndx1)] * 13.0
#     overlap_mat = tiler.overlap_matrix(tiles, overlap)
#     corrections = tiler.coef_matrix_brute_force(overlap_mat)
#     print(corrections)
#     for ndx0 in (3, 5, 13):
#         for ndx1 in (4, 7, 20):
#             assert corrections[(ndx0, ndx1)] == 1 / 13.0
