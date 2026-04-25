from app.rules_engine import check_eligibility, get_deadlines, get_state_rules

def test_eligibility_underage():
    res = check_eligibility(17, True, "CA")
    assert res["eligible"] is False
    assert "18 years old" in res["reasons"][0]

def test_eligibility_non_citizen():
    res = check_eligibility(25, False, "CA")
    assert res["eligible"] is False
    assert "U.S. citizen" in res["reasons"][0]

def test_eligibility_valid_voter():
    res = check_eligibility(25, True, "CA")
    assert res["eligible"] is True

def test_deadlines_known_state():
    res = get_deadlines("CA")
    assert "error" not in res
    assert res["state_name"] == "California"

def test_deadlines_unknown_state_raises():
    res = get_deadlines("XX")
    assert "error" in res
