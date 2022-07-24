from .. import create_release_notes
import datetime


def test_str2time():
    given = "Tue, 20 Dec 2016 17:35:40 GMT"
    result = create_release_notes.str2time(given)
    assert isinstance(result, datetime.datetime)
    assert str(result) == "2016-12-20 17:35:40"
