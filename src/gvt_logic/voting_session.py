import datetime
import uuid

from gvt_db.db import get_session
from gvt_server.models.backend import VotingSessionBackend


def create_new_voting_session():
    session = next(get_session())
    voting_session = VotingSessionBackend(id=uuid.uuid4().hex, start_time=datetime.datetime.now())
    session.add(voting_session)
    session.commit()
