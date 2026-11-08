from backend.app.citations import check_citations

PASSAGES = [{"sid": "S1"}, {"sid": "S2"}]


def test_valid_citation():
    assert check_citations("Adults need 7 to 9 hours [S1].", PASSAGES)


def test_no_citation_fails():
    assert not check_citations("Adults need 7 to 9 hours.", PASSAGES)


def test_invented_citation_fails():
    assert not check_citations("Adults need 7 to 9 hours [S7].", PASSAGES)
