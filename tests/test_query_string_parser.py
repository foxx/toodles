"""."""
import pytest

from toodles.parse.query_string_parser import QueryStringParser


def test_parse():
    """."""

    items = [
        "filter.age=12&filter.age.lala=13",
        "filter.age=between:1,20",
        "filter.age=in:20,21,23",
        "filter.age=gt:20",
        "filter.age=gte:20",
        "filter.age=lt:20",
        "filter.age=lte:20",
        "filter.name=Bob&filter.friend.name=John&filter.age=gte:42",
        "filter.full_name=Bob Bobinsky&filter.occupation=in:Mice Circus Owner,gentleman",
        "filter.name=bob,glob,sam",
        "filter.age=between:20,32.13"
    ]

    qsp = QueryStringParser()

    for i in items:
        qsp.parse(i, max_query_key_tokens=2)
