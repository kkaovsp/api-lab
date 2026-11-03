import pytest


# Boundary values for updating stars: 1 and 5 succeed (200), 0 and 6 are refused (400) leaving the rating unchanged.
@pytest.mark.parametrize("stars,expected_status", [
    (1, 200),
    (5, 200),
    (0, 400),
    (6, 400),
])
def test_update_rating_boundary_values(api, auth, rating, stars, expected_status):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": stars}, headers=auth)
    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["stars"] == stars
    else:
        # A refused update must leave the rating as it was
        check_res = api.get(path, headers=auth)
        assert check_res.status_code == 200
        assert check_res.json()["stars"] == rating["stars"]
