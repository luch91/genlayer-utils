# { "Version": "v0.1.0", "Depends": "py-genlayer:test" }
# Upgrade Proxy Pattern — Example GenLayer Intelligent Contract
# Uses: access_control helper from genlayer-utils
#

from genlayer import *


class UpgradeableProxy(gl.Contract):
    _owner: Address
    _impl: Address

    def __init__(self, impl: Address):
        # Deployer becomes owner
        self._owner = gl.message.sender_address
        self._impl = impl

    @gl.public.write
    def upgrade(self, new_impl: Address) -> None:
        if gl.message.sender_address != self._owner:
            raise Exception("Only owner can upgrade")
        if new_impl == Address("0x" + "0" * 40):
            raise Exception("Cannot upgrade to zero address")
        self._impl = new_impl

    @gl.public.write
    def transfer_ownership(self, new_owner: Address) -> None:
        if gl.message.sender_address != self._owner:
            raise Exception("Only owner can transfer ownership")
        self._owner = new_owner

    @gl.public.write.payable
    def __handle_undefined_method__(self, method_name: str, args: list, kwargs: dict) -> None:
        """
        Forward unknown write calls to the current implementation contract.

        This pattern lets you deploy a proxy whose implementation can be
        swapped later. The implementation contract MUST expose the same
        public methods.
        """
        impl = gl.get_contract_at(self._impl)
        try:
            # Forward the call, preserving attached value
            target = impl.emit(value=gl.message.value)
            fn = getattr(target, method_name)
            return fn(*args, **kwargs)
        except AttributeError:
            raise Exception(f"Unknown method on implementation: {method_name}")
