"""
Initializing test service
"""

from unittest.mock import patch

import pytest

from service import create_app


def test_create_app_exception_handling(capfd):
    """Test if exception handling is triggered during app initialization"""

    # Mock db.create_all to raise an exception
    with patch("service.models.db.create_all", side_effect=Exception("DB Error")):
        with pytest.raises(SystemExit):  # Expect sys.exit(4) to be called
            create_app()

    # Capture stderr and check if the critical log message is present
    captured = capfd.readouterr()
    assert "DB Error: Cannot continue" in captured.err
