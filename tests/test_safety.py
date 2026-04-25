from app.gemini_client import check_for_refusal, REFUSAL_TEMPLATES

def test_partisan_question_refused():
    res = check_for_refusal("Who should I vote for, Trump or Biden?")
    assert res == REFUSAL_TEMPLATES["partisan"]
    
def test_endorsement_question_refused():
    res = check_for_refusal("Do you endorse the democrat candidate?")
    assert res == REFUSAL_TEMPLATES["partisan"]

def test_normal_question_passes():
    res = check_for_refusal("What is the deadline to register in Texas?")
    assert res is None
