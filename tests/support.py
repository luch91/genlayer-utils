import importlib
import sys
import types


class FakeAddress(str):
    @property
    def as_hex(self):
        return str(self)


class FakeTreeMap(dict):
    def get_or_insert_default(self, key):
        if key not in self:
            self[key] = FakeDynArray()
        return self[key]


class FakeDynArray(list):
    pass


def install_fake_genlayer(
    monkeypatch,
    *,
    sender="0x" + "1" * 40,
    value=0,
    exec_prompt=None,
    web_get=None,
    web_render=None,
    strict_eq=None,
    prompt_comparative=None,
    get_contract_at=None,
):
    if web_get is None:
        def web_get(url, headers=None):
            return types.SimpleNamespace(status=200, body=b"{}", headers=headers or {})

    if web_render is None:
        def web_render(url, mode="text", wait_after_loaded=None):
            return f"rendered:{url}:{mode}:{wait_after_loaded}"

    if exec_prompt is None:
        def exec_prompt(prompt, response_format="json"):
            if response_format == "json":
                return {"ok": True}
            return "ok"

    if strict_eq is None:
        def strict_eq(fn):
            return fn()

    if prompt_comparative is None:
        def prompt_comparative(fn, principle):
            return fn()

    if get_contract_at is None:
        def get_contract_at(_impl_address):
            raise NotImplementedError("get_contract_at was not configured for this test")

    fake_gl = types.SimpleNamespace(
        nondet=types.SimpleNamespace(
            web=types.SimpleNamespace(get=web_get, render=web_render),
            exec_prompt=exec_prompt,
        ),
        eq_principle=types.SimpleNamespace(
            strict_eq=strict_eq,
            prompt_comparative=prompt_comparative,
        ),
        message=types.SimpleNamespace(
            sender_address=FakeAddress(sender),
            value=value,
        ),
        get_contract_at=get_contract_at,
    )

    module = types.ModuleType("genlayer")
    module.gl = fake_gl
    module.Address = FakeAddress
    module.TreeMap = FakeTreeMap
    module.DynArray = FakeDynArray
    module.u256 = int

    monkeypatch.setitem(sys.modules, "genlayer", module)
    monkeypatch.setitem(sys.modules, "genlayer.gl", fake_gl)
    return fake_gl


def fresh_import(module_name: str):
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)
