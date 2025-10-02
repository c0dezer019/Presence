# Standard modules
import logging
import traceback
from dataclasses import dataclass
from enum import Enum
from time import perf_counter, perf_counter_ns
from typing import Optional, Dict, List, Union

# Third-party modules
import requests
from nextcord import Member
from requests import Response

from lib.queries import queries
from lib.typings import Member as GQLMember, DiscordGuild, Query


class Environment(Enum):
    """API environment configuration."""

    DEV = "development"
    PROD = "production"


@dataclass
class RequestHandlerConfig:
    """Configuration for the RequestHandler class."""

    api_url_dev: str = "http://localhost:8000/gql"
    api_url_prod: str = "https://combot.bblankenship.me/v1/"
    headers: Dict[str, str] = None

    def __post_init__(self):
        if self.headers is None:
            self.headers = {"Content-Type": "application/json"}


class RequestHandler:
    """Handles GraphQL API requests for the Discord bot."""

    def __init__(
        self,
        environment: Environment = Environment.DEV,
        config: Optional[RequestHandlerConfig] = None,
    ):
        """Initialize the request handler.

        Args:
            environment: The API environment to use (dev/prod)
            config: Optional configuration override
        """
        self._config = config or RequestHandlerConfig()
        self._environment = environment
        self._logger = logging.getLogger(__name__)

    @property
    def api_url(self) -> str:
        """Get the current API URL based on environment."""
        return (
            self._config.api_url_dev
            if self._environment == Environment.DEV
            else self._config.api_url_prod
        )

    @property
    def headers(self) -> Dict[str, str]:
        """Get the request headers."""
        return self._config.headers

    def _log_operation_time(self, operation: str, start_time: float) -> None:
        """Log the time taken for an operation.

        Args:
            operation: Name of the operation
            start_time: Start time from perf_counter()
        """
        end_time = perf_counter()
        time_to_complete = end_time - start_time
        self._logger.info(
            f"{operation} completed in {time_to_complete} seconds.\n-------------------------"
        )

    def get_purge_list(self) -> Response:
        """Get the list of members to be purged.

        Returns:
            Response: The API response containing the purge list
        """
        start_time = perf_counter()
        payload: Query = {"query": queries["purge_list"]}
        self._logger.info("Fetching purge list...")
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self._log_operation_time("Purge list retrieval", start_time)
        return response

    def remove_from_purge_list(self, member_id: int) -> None:
        """Remove a member from the purge list.

        Args:
            member_id: The Discord ID of the member to remove
        """
        start_time = perf_counter()
        payload: Query = {
            "query": queries["delete_purge_entry"],
            "variables": {"memberId": member_id},
        }

        self._logger.info(f"Removing member {member_id} from purge list...")
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self._log_operation_time("Purge list removal", start_time)

        if response.status_code != 200:
            raise Exception(f"Failed to remove member {member_id} from purge list")

    def add_to_purge_list(self, guild_id: int, member_id: int) -> Response:
        """Add a member to the purge list.

        Args:
            guild_id: The Discord ID of the guild
            member_id: The Discord ID of the member

        Returns:
            Response: The API response
        """
        start_time = perf_counter()
        payload: Query = {
            "query": queries["add_to_purge_list"],
            "variables": {"memberId": member_id, "guildId": guild_id},
        }

        self._logger.info("Adding new purge entry...")
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self._log_operation_time("Purge list addition", start_time)
        return response

    def get_guild(self, guild_id: int) -> DiscordGuild:
        """Get information about a specific guild.

        Args:
            guild_id: The Discord ID of the guild

        Returns:
            DiscordGuild: The guild information
        """
        start_time = perf_counter()
        payload: Query = {
            "query": queries["get_guild"],
            "variables": {"guild_id": guild_id},
        }

        self._logger.info(f"Fetching guild {guild_id}...")
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self._log_operation_time("Guild retrieval", start_time)
        return response.json()["data"]["guild"]["guild"]

    def get_guilds(self) -> List[DiscordGuild]:
        """Get information about all guilds.

        Returns:
            List[DiscordGuild]: List of guild information
        """
        start_time = perf_counter()
        payload: Query = {"query": queries["get_guilds"]}

        self._logger.info("Fetching all guilds...")
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self._log_operation_time("Guilds retrieval", start_time)
        return response.json()["data"]["guild"]["guilds"]

    def reset_guild(self, guild_id: int) -> None:
        """Reset a guild's data.

        Args:
            guild_id: The Discord ID of the guild to reset
        """
        self._logger.info(f"Resetting guild data for guild {guild_id}.")
        # TODO: Implement guild reset logic

    def get_members(self) -> GQLMember:
        """Get information about all members.

        Returns:
            GQLMember: Member information
        """
        start_time = perf_counter()
        payload: Query = {"query": queries["get_members"]}

        self._logger.info("Fetching all members...")
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self._log_operation_time("Members retrieval", start_time)
        return response.json()["data"]["member"]["member"]

    def get_member(self, guild_id: int, member: Member) -> GQLMember:
        """Get information about a specific member.

        Args:
            guild_id: The Discord ID of the guild
            member: The Discord member object

        Returns:
            GQLMember: Member information
        """
        start_time = perf_counter()
        payload: Query = {
            "query": queries["get_member"],
            "variables": {
                "guildId": guild_id,
                "memberId": member.id,
            },
        }

        self._logger.info(f"Fetching member {member.id}...")
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self._log_operation_time("Member retrieval", start_time)
        return response.json()["data"]["member"]["member"]

    def update_guild(self, guild_id: int, **data) -> Union[DiscordGuild, int]:
        """Update a guild's information.

        Args:
            guild_id: The Discord ID of the guild
            **data: Key-value pairs of data to update

        Returns:
            Union[DiscordGuild, int]: Updated guild information or status code on error
        """
        start_time = perf_counter()
        self._logger.info("Updating guild...")

        payload: Query = {
            "query": queries["update_guild"],
            "variables": {
                "guildId": guild_id,
                "input": {k: v for k, v in data.items()},
            },
        }

        self._logger.info("Building payload...")

        item_list = list(data.keys())
        loop_times: List[float] = []

        # Process payload items
        for k, v in data.items():
            loop_start = perf_counter_ns() / 1000
            payload["variables"][k] = v
            percentage_complete = int((item_list.index(k) + 1) / len(item_list) * 100)
            loop_end = perf_counter_ns() / 1000
            time_to_complete = loop_end - loop_start
            loop_times.append(time_to_complete)

            self._logger.info(
                f"Payload {percentage_complete}% complete. {time_to_complete} microseconds."
            )

            if percentage_complete == 100:
                self._logger.info("Payload complete.")
                self._logger.info(f"Items to be patched:\n{payload['variables']}\n")
                self._logger.info(
                    f"Operation finished in {sum(loop_times)} microseconds."
                )

        self._logger.info("Patching...")
        response = requests.patch(self.api_url, headers=self.headers, json=payload)

        if response.status_code != 200:
            self._log_operation_time("Guild update (failed)", start_time)
            return response.status_code

        self._log_operation_time("Guild update", start_time)
        return response.json()["data"]["guild"]["guild"]

    def update_member(
        self, guild_id: int, member_id: int, **data
    ) -> Union[GQLMember, int]:
        """Update a member's information.

        Args:
            guild_id: The Discord ID of the guild
            member_id: The Discord ID of the member
            **data: Key-value pairs of data to update

        Returns:
            Union[GQLMember, int]: Updated member information or status code on error
        """
        start_time = perf_counter()
        payload: Query = {
            "query": queries["update_member"],
            "variables": {
                "guildId": guild_id,
                "memberId": member_id,
                "input": {k: v for k, v in data.items()},
            },
        }

        # Process payload items
        item_list = list(data.keys())
        loop_times: List[float] = []

        for k, v in data.items():
            loop_start = perf_counter_ns() / 1000
            payload["variables"][k] = v
            percentage_complete = int((item_list.index(k) + 1) / len(item_list) * 100)
            loop_end = perf_counter_ns() / 1000
            time_to_complete = loop_end - loop_start
            loop_times.append(time_to_complete)

            self._logger.info(
                f"Payload {percentage_complete}% complete. {time_to_complete} microseconds."
            )

            if percentage_complete == 100:
                self._logger.info("Payload complete.")
                self._logger.info(f"Items to be patched:\n{payload['variables']}\n")
                self._logger.info(
                    f"Operation finished in {sum(loop_times)} microseconds."
                )

        self._logger.info("Patching member...")
        response = requests.patch(self.api_url, headers=self.headers, json=payload)

        if response.status_code != 200:
            self._logger.info("Unable to patch member.")
            return response.status_code

        self._log_operation_time("Member update", start_time)
        return response.json()["data"]["member"]["member"]

    def remove_guild(self, guild_id: int) -> None:
        """Remove a guild from the system.

        Args:
            guild_id: The Discord ID of the guild to remove
        """
        start_time = perf_counter()
        payload: Query = {
            "query": queries["delete_guild"],
            "variables": {"guildId": guild_id},
        }

        response = requests.delete(self.api_url, headers=self.headers, json=payload)
        response_data = response.json()["data"]["guild"]

        if response_data["code"] == 200:
            self._logger.info("Guild removed.")
        else:
            self._logger.debug(f"Failed to remove guild.\n\n{traceback.format_exc()}")

        self._log_operation_time("Guild removal", start_time)

    def remove_member(self, member_id: int) -> None:
        """Remove a member from the system.

        Args:
            member_id: The Discord ID of the member to remove
        """
        start_time = perf_counter()
        self._logger.info(f"Removing member {member_id}.")

        payload: Query = {
            "query": queries["delete_member"],
            "variables": {"memberId": member_id},
        }

        response = requests.delete(self.api_url, headers=self.headers, json=payload)
        response_data = response.json()["data"]["member"]

        if response_data["code"] == 200:
            self._logger.info("Member removed.")
        else:
            self._logger.debug(f"Failed to remove member.\n\n{traceback.format_exc()}")

        self._log_operation_time("Member removal", start_time)
