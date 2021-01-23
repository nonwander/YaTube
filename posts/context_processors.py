import datetime as dt


def year(request):
    data_year = dt.datetime.now().year
    return {
        "year": data_year,
    }
