# Access Control

## The Problem

GenLayer has no built-in access control. Every contract that needs owner-only or role-based methods manually checks `gl.message.sender_address`. This is error-prone, inconsistent, and repeated across every contract.

## Guard Functions

Standalone functions you can drop into any contract.

### `require_sender(expected)`

Revert if the caller is not the expected address.

```python
@gl.public.write
def admin_action(self):
    require_sender(self._owner)
    # ... only owner reaches here
```

### `require_value(minimum)`

Revert if the transaction doesn't include enough value.

```python
@gl.public.write.payable
def purchase(self):
    require_value(100)  # Must send at least 100 GEN
    # ... process purchase
```

### `require_not_zero(address)`

Revert if the address is the zero address. Prevents accidental burns.

```python
@gl.public.write
def transfer_ownership(self, new_owner: Address):
    require_not_zero(new_owner)
    self._owner = new_owner
```

## Ownable Pattern

Copy these methods into your contract for owner-based access control:

```python
class MyContract(gl.Contract):
    _owner: Address

    def __init__(self):
        self._owner = gl.message.sender_address

    def _require_owner(self) -> None:
        if gl.message.sender_address != self._owner:
            raise Exception("Only the owner can call this method")

    def _transfer_ownership(self, new_owner: Address) -> None:
        self._require_owner()
        require_not_zero(new_owner)
        self._owner = new_owner

    @gl.public.view
    def get_owner(self) -> str:
        return self._owner.as_hex

    @gl.public.write
    def dangerous_action(self):
        self._require_owner()
        # ... owner-only logic
```

## Role-Based Access Pattern

For contracts with multiple access levels (admin, moderator, editor, etc.):

```python
class MyContract(gl.Contract):
    _roles: TreeMap[str, TreeMap[Address, bool]]

    def __init__(self):
        self._grant_role("admin", gl.message.sender_address)

    def _grant_role(self, role: str, account: Address) -> None:
        self._roles.get_or_insert_default(role)[account] = True

    def _revoke_role(self, role: str, account: Address) -> None:
        role_map = self._roles.get_or_insert_default(role)
        if account in role_map:
            del role_map[account]

    def _has_role(self, role: str, account: Address) -> bool:
        role_map = self._roles.get_or_insert_default(role)
        return role_map.get(account, False)

    def _require_role(self, role: str) -> None:
        if not self._has_role(role, gl.message.sender_address):
            raise Exception(f"Missing required role: {role}")

    @gl.public.write
    def moderate(self, post_id: str):
        self._require_role("moderator")
        # ... moderator-only logic

    @gl.public.write
    def add_moderator(self, account: Address):
        self._require_role("admin")
        self._grant_role("moderator", account)
```

## Example

See [voting.py](../examples/voting.py) for a complete contract using owner guards, voter registration, and double-vote prevention.
