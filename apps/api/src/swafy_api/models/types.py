from sqlalchemy.dialects.postgresql import ENUM

from swafy_api.models.enums import LabelSource, PhotoState, ReportCategory, ReportStatus, UserRole


def enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


USER_ROLE_DB = ENUM(UserRole, name="user_role", values_callable=enum_values)
REPORT_CATEGORY_DB = ENUM(ReportCategory, name="report_category", values_callable=enum_values)
REPORT_STATUS_DB = ENUM(ReportStatus, name="report_status", values_callable=enum_values)
PHOTO_STATE_DB = ENUM(PhotoState, name="photo_state", values_callable=enum_values)
LABEL_SOURCE_DB = ENUM(LabelSource, name="label_source", values_callable=enum_values)
