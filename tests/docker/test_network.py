"""Test Internal network manager for Supervisor."""

from unittest.mock import MagicMock, patch

import pytest

from supervisor.const import ATTR_ENABLE_IPV6, DOCKER_NETWORK
from supervisor.docker.network import (
    DOCKER_ENABLEIPV6,
    DOCKER_NETWORK_PARAMS,
    DockerNetwork,
)


class MockNetwork:
    """Mock implementation of internal network."""

    def __init__(self, enableIPv6: bool) -> None:
        """Initialize a mock network."""
        self.attrs = {DOCKER_ENABLEIPV6: enableIPv6}

    def remove(self) -> None:
        """Simulate a network removal."""


@pytest.mark.parametrize(ATTR_ENABLE_IPV6, [True, False])
async def test_network_recreation(enable_ipv6: bool):
    """Test network recreation with IPv6 enabled/disabled."""

    with (
        patch(
            "supervisor.docker.network.DockerNetwork._get",
            return_value=MockNetwork(not enable_ipv6),
        ) as mock_get,
        patch(
            "supervisor.docker.network.DockerNetwork._create",
            return_value=MockNetwork(enable_ipv6),
        ) as mock_create,
    ):
        network = DockerNetwork(MagicMock(), enable_ipv6).network

        assert network is not None
        assert network.attrs.get(DOCKER_ENABLEIPV6) is enable_ipv6

        mock_get.assert_called_with(DOCKER_NETWORK)

        network_params = DOCKER_NETWORK_PARAMS.copy()
        network_params[ATTR_ENABLE_IPV6] = enable_ipv6

        mock_create.assert_called_with(**network_params)
