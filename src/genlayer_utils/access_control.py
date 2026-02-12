# genlayer-utils: access_control.py
# Owner and role-based access control for GenLayer Intelligent Contracts
#
# Security primitives that don't exist anywhere in the GenLayer ecosystem.
# Copy the functions and patterns you need into your contract file.
#
# Requires: from genlayer import *


from genlayer import *


# =============================================================================
# Guard Functions (standalone — copy these into any contract)
# =============================================================================


def require_sender(expected: Address) -> None:
    """
    Revert the transaction if the sender is not the expected address.

    Args:
        expected: The address that is allowed to call this method

    Example:
        @gl.public.write
        def admin_action(self):
            require_sender(self._owner)
            # ... only owner reaches here
    """
    if gl.message.sender_address != expected:
        raise Exception("Unauthorized: caller is not the expected address")


def require_value(minimum: int = 1) -> None:
    """
    Revert if the transaction does not include at least `minimum` value.

    Args:
        minimum: Minimum GEN value required (default: 1)

    Example:
        @gl.public.write.payable
        def purchase(self):
            require_value(100)  # Must send at least 100 GEN
            # ... process purchase
    """
    if gl.message.value < minimum:
        raise Exception(
            f"Insufficient value: sent {gl.message.value}, need {minimum}"
        )


def require_not_zero(address: Address) -> None:
    """
    Revert if the address is the zero address.

    Args:
        address: The address to validate

    Example:
        @gl.public.write
        def transfer(self, to: Address):
            require_not_zero(to)
            # ... safe to transfer
    """
    if address == Address("0x" + "0" * 40):
        raise Exception("Zero address not allowed")


# =============================================================================
# Ownable Pattern (copy this section into your contract)
# =============================================================================
#
# Add owner-based access control to your contract. The deployer becomes
# the owner automatically.
#
# Usage — copy the methods below into your contract class:
#
#   class MyContract(gl.Contract):
#       _owner: Address
#
#       def __init__(self):
#           self._owner = gl.message.sender_address
#
#       def _require_owner(self) -> None:
#           if gl.message.sender_address != self._owner:
#               raise Exception("Only the owner can call this method")
#
#       def _transfer_ownership(self, new_owner: Address) -> None:
#           self._require_owner()
#           require_not_zero(new_owner)
#           self._owner = new_owner
#
#       @gl.public.view
#       def get_owner(self) -> str:
#           return self._owner.as_hex
#
#       @gl.public.write
#       def dangerous_action(self):
#           self._require_owner()
#           # ... only owner can execute


# =============================================================================
# Role-Based Access Pattern (copy this section into your contract)
# =============================================================================
#
# Add role-based access control using TreeMap storage. Supports multiple
# roles (admin, moderator, editor, etc.) with per-address grants.
#
# Usage — copy the methods below into your contract class:
#
#   class MyContract(gl.Contract):
#       _roles: TreeMap[str, TreeMap[Address, bool]]
#
#       def __init__(self):
#           self._grant_role("admin", gl.message.sender_address)
#
#       def _grant_role(self, role: str, account: Address) -> None:
#           self._roles.get_or_insert_default(role)[account] = True
#
#       def _revoke_role(self, role: str, account: Address) -> None:
#           role_map = self._roles.get_or_insert_default(role)
#           if account in role_map:
#               del role_map[account]
#
#       def _has_role(self, role: str, account: Address) -> bool:
#           role_map = self._roles.get_or_insert_default(role)
#           return role_map.get(account, False)
#
#       def _require_role(self, role: str) -> None:
#           if not self._has_role(role, gl.message.sender_address):
#               raise Exception(f"Missing required role: {role}")
#
#       @gl.public.write
#       def moderate_content(self, post_id: str):
#           self._require_role("moderator")
#           # ... only moderators can execute
#
#       @gl.public.write
#       def add_moderator(self, account: Address):
#           self._require_role("admin")
#           self._grant_role("moderator", account)
