from infoenergia_api.contrib.data_source import Timescale


def test_init_timescale():
    #Given a data source credentials
    credentials = {
        "username": 'somenergia',
        "password": '1234',
        "host": '',
        "port": '',
        "dbname": 'somenergia'  
    }
    #When we create a instance of a Timescale db
    timescale_db = Timescale(**credentials)
    #Then, we have a instance of Timescale db:
    assert isinstance(timescale_db, Timescale)


def test__get_fact_curves(
    # given a timescale instance
    timescale
):

    # when we search for all cch_fact curves
    curves = timescale.get_cch_fact()

    # then, we obtain a list of cch points
    assert len(curves) > 0