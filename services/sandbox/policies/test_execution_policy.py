from execution_policy import ExecutionPolicyValidator


validator = ExecutionPolicyValidator()


def test_valid_policy():
    validator.validate(
        timeout_seconds=10,
        memory_mb=512,
        network_enabled=False,
    )


def test_timeout_too_large():
    try:
        validator.validate(
            timeout_seconds=31,
            memory_mb=512,
            network_enabled=False,
        )
        assert False
    except ValueError as error:
        assert "timeout_seconds" in str(error)


def test_memory_too_large():
    try:
        validator.validate(
            timeout_seconds=10,
            memory_mb=2048,
            network_enabled=False,
        )
        assert False
    except ValueError as error:
        assert "memory_mb" in str(error)


def test_network_blocked():
    try:
        validator.validate(
            timeout_seconds=10,
            memory_mb=512,
            network_enabled=True,
        )
        assert False
    except ValueError as error:
        assert "network" in str(error)


if __name__ == "__main__":
    test_valid_policy()
    test_timeout_too_large()
    test_memory_too_large()
    test_network_blocked()
    print("All ExecutionPolicy tests passed.")