# { "Depends": "py-genlayer:test" }
#
# Voting — Example GenLayer Intelligent Contract
# Uses: access_control, storage helpers from genlayer-utils
#
# A simple on-chain voting contract with role-based access.
# Admins create proposals, registered voters cast votes,
# and results are tallied transparently.

from dataclasses import dataclass
from genlayer import *


# ─── genlayer-utils: access_control ─────────────────────────────────────────

def require_sender(expected):
    if gl.message.sender_address != expected:
        raise Exception("Unauthorized: caller is not the expected address")


def require_not_zero(address):
    if address == Address("0x" + "0" * 40):
        raise Exception("Zero address not allowed")


# ─── genlayer-utils: storage ────────────────────────────────────────────────

def increment_or_init(data, key, amount=1):
    current = data.get(key, 0)
    data[key] = current + amount


def treemap_paginate(data, offset=0, limit=10):
    items = []
    count = 0
    for k, v in data.items():
        if count < offset:
            count += 1
            continue
        if len(items) >= limit:
            break
        items.append((k, v))
        count += 1
    return items


# ─── Contract ───────────────────────────────────────────────────────────────

@allow_storage
@dataclass
class Proposal:
    id: str
    title: str
    description: str
    creator: str
    yes_votes: u256
    no_votes: u256
    is_active: bool


class Voting(gl.Contract):
    proposals: TreeMap[str, Proposal]
    proposal_count: u256
    # Track who voted on what to prevent double voting
    votes: TreeMap[str, TreeMap[Address, bool]]  # proposal_id -> voter -> voted
    _owner: Address
    _voters: TreeMap[Address, bool]  # registered voters

    def __init__(self):
        self.proposal_count = 0
        self._owner = gl.message.sender_address
        # Owner is automatically a registered voter
        self._voters[gl.message.sender_address] = True

    def _require_owner(self) -> None:
        if gl.message.sender_address != self._owner:
            raise Exception("Only the owner can call this method")

    def _require_voter(self) -> None:
        if not self._voters.get(gl.message.sender_address, False):
            raise Exception("Only registered voters can vote")

    # ─── Admin methods ───────────────────────────────────────────────

    @gl.public.write
    def register_voter(self, voter: Address) -> None:
        """Register a new voter (owner only)."""
        self._require_owner()
        require_not_zero(voter)
        self._voters[voter] = True

    @gl.public.write
    def remove_voter(self, voter: Address) -> None:
        """Remove a voter (owner only)."""
        self._require_owner()
        if voter in self._voters:
            del self._voters[voter]

    @gl.public.write
    def create_proposal(self, title: str, description: str) -> None:
        """Create a new proposal (owner only)."""
        self._require_owner()
        self.proposal_count += 1
        proposal_id = f"prop_{self.proposal_count}"

        self.proposals[proposal_id] = Proposal(
            id=proposal_id,
            title=title,
            description=description,
            creator=gl.message.sender_address.as_hex,
            yes_votes=0,
            no_votes=0,
            is_active=True,
        )

    @gl.public.write
    def close_proposal(self, proposal_id: str) -> None:
        """Close a proposal for voting (owner only)."""
        self._require_owner()
        if proposal_id not in self.proposals:
            raise Exception("Proposal not found")
        self.proposals[proposal_id].is_active = False

    # ─── Voter methods ───────────────────────────────────────────────

    @gl.public.write
    def vote(self, proposal_id: str, support: bool) -> None:
        """Cast a vote on a proposal (registered voters only)."""
        self._require_voter()

        if proposal_id not in self.proposals:
            raise Exception("Proposal not found")

        proposal = self.proposals[proposal_id]
        if not proposal.is_active:
            raise Exception("Proposal is no longer active")

        # Check for double voting
        voter_map = self.votes.get_or_insert_default(proposal_id)
        if voter_map.get(gl.message.sender_address, False):
            raise Exception("Already voted on this proposal")

        # Record vote
        voter_map[gl.message.sender_address] = True

        if support:
            proposal.yes_votes += 1
        else:
            proposal.no_votes += 1

    # ─── View methods ────────────────────────────────────────────────

    @gl.public.view
    def get_proposal(self, proposal_id: str) -> dict:
        if proposal_id not in self.proposals:
            raise Exception("Proposal not found")
        p = self.proposals[proposal_id]
        total = p.yes_votes + p.no_votes
        return {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "creator": p.creator,
            "yes_votes": p.yes_votes,
            "no_votes": p.no_votes,
            "total_votes": total,
            "is_active": p.is_active,
            "result": "yes" if p.yes_votes > p.no_votes else "no" if p.no_votes > p.yes_votes else "tie",
        }

    @gl.public.view
    def get_proposals(self, page: int = 0) -> list:
        """Get proposals with pagination (10 per page)."""
        entries = treemap_paginate(self.proposals, offset=page * 10, limit=10)
        return [
            {"id": p.id, "title": p.title, "is_active": p.is_active,
             "yes_votes": p.yes_votes, "no_votes": p.no_votes}
            for _, p in entries
        ]

    @gl.public.view
    def is_registered_voter(self, address: Address) -> bool:
        return self._voters.get(address, False)

    @gl.public.view
    def has_voted(self, proposal_id: str, voter: Address) -> bool:
        voter_map = self.votes.get_or_insert_default(proposal_id)
        return voter_map.get(voter, False)
