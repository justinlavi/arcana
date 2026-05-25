from validate_format import short_table_delimiter_rows


def test_short_table_delimiter_rows_are_caught():
    content = "\n".join(
        [
            "| A | B |",
            "|--|--|",
            "| 1 | 2 |",
        ]
    )

    assert list(short_table_delimiter_rows(content)) == [(2, "|--|--|")]


def test_table_delimiters_inside_code_fences_are_ignored():
    content = "\n".join(
        [
            "```md",
            "| A | B |",
            "|--|--|",
            "```",
        ]
    )

    assert list(short_table_delimiter_rows(content)) == []
