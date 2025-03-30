from sqlalchemy import event

from app.helpers import utc_now
from app.models.team import Team
from app.models.user import User
from app.models.waste import WasteLog


# This function will automatically update the `updated_at` field before any update operation on the model.
def auto_update_timestamp(model_class):
    @event.listens_for(model_class, "before_update")
    def _update(mapper, connection, target):
        if hasattr(target, "updated_at"):
            target.updated_at = utc_now()


auto_update_timestamp(User)
auto_update_timestamp(Team)
auto_update_timestamp(WasteLog)
