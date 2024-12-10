"""
Defined tests for persistent base
"""

from unittest.mock import patch

import pytest

from service.common.error_handlers import DataValidationError
from service.models import PersistentBase


def test_update_raises_exception():
    """Test update method raises an exception when commit fails"""
    instance = PersistentBase()
    instance.id = 1

    with patch(
        "service.models.db.session.commit", side_effect=Exception("DB Commit Error")
    ):
        with patch("service.models.db.session.rollback") as mock_rollback:
            with pytest.raises(DataValidationError) as excinfo:
                instance.update()

            mock_rollback.assert_called_once()

            assert "DB Commit Error" in str(excinfo.value)
