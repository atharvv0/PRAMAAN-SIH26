import os

from services.sandbox.runner.local_runner import LocalRunner
from services.sandbox.runner.runtime_factory import create_runtime


def test_default_runtime():
    os.environ.pop("SANDBOX_RUNTIME", None)

    runtime = create_runtime()

    assert isinstance(runtime, LocalRunner)


def test_local_runtime():
    os.environ["SANDBOX_RUNTIME"] = "local"

    runtime = create_runtime()

    assert isinstance(runtime, LocalRunner)

    os.environ.pop("SANDBOX_RUNTIME", None)


if __name__ == "__main__":
    test_default_runtime()
    test_local_runtime()
    print("All RuntimeFactory tests passed.")