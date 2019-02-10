def test_pypi_compatible():
    from vpip.pypi import is_compatible
    assert is_compatible("0.1.0", "0.2.0") is False
    assert is_compatible("1.1.0", "1.2.0") is True
    assert is_compatible("1.1.0", "2.2.0") is False
    