import pytest
import tempfile
import os
from unittest import mock

from main import where_csv, aggregate_csv, processing_csv

# Sample CSV content

csv_samples = {
    "default": [
        ["id", "name", "price"],
        ["1", "Apple", "1.20"],
        ["2", "Banana", "0.80"],
        ["3", "Orange", "1.50"],
        ["4", "Banana", "0.90"]
    ],
    "quoted_fields": [
        ['id', 'name', 'price'],
        ['1', '"Banana, ripe"', '0.80'],
        ['2', '"Apple ""Fuji"""', '1.00']
    ],
    "zero_and_negative": [
        ["id", "name", "price"],
        ["1", "Apple", "0.00"],
        ["2", "Banana", "-1.00"],
        ["3", "Orange", "2.00"]
    ],
    "non_numeric": [
        ["id", "name", "price"],
        ["1", "Apple", "cheap"],
        ["2", "Banana", "0.80"]
    ],
    "headers_only": [
        ["id", "name", "price"]
    ]
}

csv_file_contents = {
    "default": """id,name,price
1,Apple,1.20
2,Banana,0.80
3,Orange,1.50
4,Banana,0.90
""",
    "zero_and_negative": """id,name,price
1,Apple,0.00
2,Banana,-1.00
3,Orange,2.00
""",
    "non_numeric": """id,name,price
1,Apple,cheap
2,Banana,0.80
""",
    "headers_only": "id,name,price\n"
}

# ---- Tests for processing_csv ----

def write_csv_by_key(key):
    tmp = tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='')
    tmp.write(csv_file_contents[key])
    tmp.seek(0)
    tmp.close()
    return tmp.name

@mock.patch("builtins.print")
@pytest.mark.parametrize("csv_key, args, expected_in", [
    ("default", [], ["Apple", "Banana", "Orange"]),
    ("zero_and_negative", ["--aggregate", "price=min"], ["min", "-1"]),
    ("default", ["--where", "name=Banana"], ["Banana"]),
])
def test_processing_csv_varied(mock_print, csv_key, args, expected_in):
    path = write_csv_by_key(csv_key)
    processing_csv(path, *args)
    os.unlink(path)

    out = "\n".join(str(call.args[0]) for call in mock_print.call_args_list)
    for token in expected_in:
        assert token in out

@mock.patch("builtins.print")
@pytest.mark.parametrize("csv_key, args, expected_error", [
    ("headers_only", [], "empty table"),
    ("non_numeric", ["--aggregate", "price=avg"], "incorrect csv file content for aggregation"),
    ("default", ["--where", "weight=5"], "there is no weight"),
])
def test_processing_csv_errors(mock_print, csv_key, args, expected_error):
    path = write_csv_by_key(csv_key)
    processing_csv(path, *args)
    os.unlink(path)

    out = "\n".join(str(call.args[0]) for call in mock_print.call_args_list)
    assert expected_error in out


# ---- Tests for where_csv ----


@pytest.mark.parametrize("csv_key, clause, expected", [
    ("default", "name=Banana", [
        ["id", "name", "price"],
        ["2", "Banana", "0.80"],
        ["4", "Banana", "0.90"]
    ]),
    ("zero_and_negative", "price<0", [
        ["id", "name", "price"],
        ["2", "Banana", "-1.00"]
    ]),
])
def test_where_clause_varied(csv_key, clause, expected):
    result = where_csv(csv_samples[csv_key], clause)
    assert result == expected

@pytest.mark.parametrize("csv_key, clause, error", [
    ("default", "weight=5", "there is no weight in the csv file"),
    ("default", "price>>1.0", "invalid where statement"),
])
def test_where_errors_varied(csv_key, clause, error):
    with pytest.raises(ValueError, match=error):
        where_csv(csv_samples[csv_key], clause)



# ---- Tests for aggregate_csv ----


@pytest.mark.parametrize("csv_key, clause, expected", [
    ("default", "price=avg", [["avg"], [pytest.approx(1.1, 0.01)]]),
    ("zero_and_negative", "price=max", [["max"], [2.00]]),
    ("zero_and_negative", "price=min", [["min"], [-1.00]]),
])
def test_aggregate_varied(csv_key, clause, expected):
    result = aggregate_csv(csv_samples[csv_key], clause)
    assert result == expected

@pytest.mark.parametrize("csv_key, clause, error", [
    ("non_numeric", "price=avg", "incorrect csv file content for aggregation"),
    ("default", "price>avg", "invalid aggregate statement"),
    ("default", "weight=avg", "there is no weight in the csv file"),
])
def test_aggregate_errors_varied(csv_key, clause, error):
    with pytest.raises(ValueError) as exc:
        aggregate_csv(csv_samples[csv_key], clause)
    assert error in str(exc.value)


