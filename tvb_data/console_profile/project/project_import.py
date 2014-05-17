
## Select the profile with storage enabled, but without web interface:
from tvb.basic.profile import TvbProfile as tvb_profile
tvb_profile.set_profile(["-profile", "CONSOLE_PROFILE"], try_reload=False)

from tvb.core.traits import db_events
from tvb.core.entities import model
from tvb.core.services.user_service import UserService
from tvb.core.services.import_service import ImportService


PROJECT_PATH = "2014-03-28_14-20_Epilepsy.zip"


if __name__ == "__main__":

    ## Hook DB events:
    db_events.attach_db_events()

    ## If we would know a UserID to have as admin, next step would not be necessary.
    ## Make sure at least one user exists in TVB DB:
    user_service = UserService()
    admins = user_service.get_administrators()
    if admins:
        admin = admins[0]
    else:
        ## No Admin user was found, we will create one
        user_service.create_user("admin", "pass", role=model.ROLE_ADMINISTRATOR,
                                 email="info@thevirtualbrain.org", validated=True)
        admin = user_service.get_administrators()[0]

    ## Do the actual import of a project from ZIP:
    import_service = ImportService()
    import_service.import_project_structure(PROJECT_PATH, admin.id)
