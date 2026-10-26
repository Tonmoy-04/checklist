from mychecklist import __version__


def test_release_version_is_consistent():
    assert __version__ == "1.0.0"
