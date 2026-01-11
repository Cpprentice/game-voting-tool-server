import collections
from datetime import datetime
from typing import ClassVar

from sqlalchemy import literal_column
from sqlmodel import Field, Relationship, Session

from gvt_logic.util import UrlFactory
from gvt_server.db_models.user_session import UserSession
from gvt_server.db_models.voting_session_game import VotingSessionGame
from gvt_server.db_models.voting_session_user_vote import VotingSessionUserVote
from gvt_server.models.game_votes import GameVotes
from gvt_server.models.user_game_vote import UserGameVote
from gvt_server.models.user_votes import UserVotes
from gvt_server.models.voting_session import VotingSession


class VotingSessionBackend(VotingSession, table=True):
    __tablename__ = 'voting_session'
    id: str = Field(primary_key=True)

    # needs override to drop optional type (I don't know why the generator does this by default)
    start_time: datetime = Field(alias="startTime")

    # Hide the original fields for the database (they will be serialized when converting to the base class only)
    game_votes: ClassVar[list[GameVotes]]
    user_votes: ClassVar[list[UserVotes]]

    # introduce relationships for database handling
    session_user_votes: list[VotingSessionUserVote] = Relationship(back_populates='voting_session')
    session_games: list[VotingSessionGame] = Relationship(
        sa_relationship_kwargs=dict(
            back_populates='voting_session',
            order_by=literal_column('voting_session_game._rowid_')
            # The order_by will use the SQLite rowid feature to ensure the order of the games does not change randomly
        )
    )

    def result(self, session: Session, url_factory: UrlFactory) -> list[GameVotes]:
        max_score, vote_stats = self._score_histogram(session, url_factory)
        return [
            game_vote
            for score in sorted(vote_stats.keys(), reverse=True)
            for game_vote in vote_stats[score]
        ]

    def _score_histogram(self, session: Session, url_factory: UrlFactory) -> tuple[int, dict[int, list[GameVotes]]]:
        votes = self._game_votes(session, url_factory)
        voter_count = len(UserSession.get_active_sessions(session))

        # Example: 4 voters a game with 2 up and 1 down vote
        #  voter_count = 4
        #  missing_votes = 1
        #  max_possible = 2 (up - down + missing)

        vote_stats: dict[int, list[GameVotes]] = collections.defaultdict(list)
        max_score = 0
        for vote in votes:
            missing_votes = voter_count - sum([vote.likes, vote.abstains, vote.dislikes])
            max_possible = vote.likes - vote.dislikes + missing_votes
            vote_stats[max_possible].append(vote)
            max_score = max(max_score, max_possible)

        return max_score, vote_stats

    def is_resolved(self, session: Session, url_factory: UrlFactory) -> bool:
        if len(self.session_games) < 2:
            return False

        max_score, vote_stats = self._score_histogram(session, url_factory)
        return len(vote_stats[max_score]) == 1

    @staticmethod
    def _default_user_votes(
            session_games: list[VotingSessionGame],
            user_sessions: list[UserSession]
    ) -> dict[str, dict[str, UserGameVote]]:
        return {
            session_game.game.id: {
                user_session.id: UserGameVote(
                    user_name=user_session.user_name,
                    value=0
                )
                for user_session in user_sessions
            }
            for session_game in session_games
        }

    def _game_votes(self, session: Session, url_factory: UrlFactory) -> list[GameVotes]:
        active_user_sessions = UserSession.get_active_sessions(session)
        active_user_session_ids = {user_session.id for user_session in active_user_sessions}
        user_vote_lookup = self._default_user_votes(self.session_games, active_user_sessions)
        user_vote_list = self.session_user_votes

        game_votes_likes: dict[str, int] = collections.defaultdict(int)
        game_votes_dislikes: dict[str, int] = collections.defaultdict(int)
        game_votes_abstains: dict[str, int] = collections.defaultdict(int)

        for user_vote in user_vote_list:
            if user_vote.user_session_id not in active_user_session_ids:
                # this ignores all votes if a user logged out - so we can track history but ignore it for calculations
                continue

            user_vote_lookup[user_vote.game_id][user_vote.user_session_id].value = user_vote.value
            if user_vote.value > 0:
                game_votes_likes[user_vote.game_id] += 1
            elif user_vote.value < 0:
                game_votes_dislikes[user_vote.game_id] += 1
            else:
                game_votes_abstains[user_vote.game_id] += 1

        game_user_vote_lists = {
            game_votes.game.id: list(user_vote_lookup[game_votes.game.id].values())
            for game_votes in self.session_games
        }

        game_votes = [
            GameVotes(
                game=session_game.game.get_game(url_factory),
                likes=game_votes_likes[session_game.game_id],
                abstains=game_votes_abstains[session_game.game_id],
                dislikes=game_votes_dislikes[session_game.game_id],
                user_votes=game_user_vote_lists[session_game.game_id]
            )
            for session_game in self.session_games
        ]
        return game_votes

    def _user_votes(self, session: Session) -> list[UserVotes]:
        active_user_sessions = UserSession.get_active_sessions(session)
        user_votes = [
            UserVotes(
                user_name=user_session.user_name,
                votes=len([vote for vote in self.session_user_votes if vote.user_session_id == user_session.id])
            )
            for user_session in active_user_sessions
        ]
        return user_votes

    def get_voting_session(self, url_factory: UrlFactory, session: Session) -> VotingSession:
        return VotingSession(
            user_votes=self._user_votes(session),
            game_votes=self._game_votes(session, url_factory),
            **self.model_dump()
        )

    def find_user_vote(self, game_id: str, user_id: str) -> VotingSessionUserVote | None:
        for vote in self.session_user_votes:
            if vote.game_id == game_id and vote.user_session_id == user_id:
                return vote
        return None

    def cast_vote(self, game_id: str, user_id: str, value: int, session: Session):
        existing_user_vote = self.find_user_vote(game_id, user_id)
        if existing_user_vote is not None:
            if value == 0:
                session.delete(existing_user_vote)
            else:
                existing_user_vote.value = value
                session.add(existing_user_vote)
        else:
            new_vote = VotingSessionUserVote(
                voting_session_id=self.id,
                user_session_id=user_id,
                game_id=game_id,
                value=value
            )
            session.add(new_vote)

    def try_to_add_game(self, game_id: str, user_id: str, session: Session) -> bool:
        if len(self.session_games) == 6:
            # voting session already full
            return False

        if game_id in {session_game.game.id for session_game in self.session_games}:
            # Game is already in voting session
            return False

        user_count = UserSession.get_active_session_count(session)
        allowed_games_per_user = int(len(self.session_games) / user_count) + 1
        game_count_from_user = len([
            session_game
            for session_game in self.session_games
            if session_game.user_session_id == user_id
        ])

        if game_count_from_user < allowed_games_per_user:
            session.add(VotingSessionGame(
                voting_session_id=self.id,
                game_id=game_id,
                user_session_id=user_id,
            ))
            return True
        return False
