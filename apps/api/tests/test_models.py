from geoalchemy2 import Geometry

from swafy_api.db import Base
from swafy_api.models import Confirmation, RefreshToken, Report, StatusHistory, User


def test_required_tables_are_registered():
    assert {"users", "reports", "status_history", "confirmations", "refresh_tokens"}.issubset(
        set(Base.metadata.tables)
    )


def test_report_uses_postgis_point_and_gist_index():
    location = Report.__table__.c.location.type
    assert isinstance(location, Geometry)
    assert location.geometry_type == "POINT"
    assert location.srid == 4326
    gist_indexes = [
        index for index in Report.__table__.indexes if index.name == "ix_reports_location_gist"
    ]
    assert len(gist_indexes) == 1
    assert gist_indexes[0].dialect_options["postgresql"]["using"] == "gist"


def test_expected_model_classes_exist():
    assert User.__tablename__ == "users"
    assert Report.__tablename__ == "reports"
    assert StatusHistory.__tablename__ == "status_history"
    assert Confirmation.__tablename__ == "confirmations"
    assert RefreshToken.__tablename__ == "refresh_tokens"
