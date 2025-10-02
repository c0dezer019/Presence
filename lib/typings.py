# Standard modules
from datetime import datetime

# Third party modules
from pydantic import BaseModel, Field


class Query(BaseModel):
    query: str
    variables: dict


class Activity(BaseModel):
    type: str
    ch: int
    ts: datetime


class IdleStats(BaseModel):
    times_idle: list[int] = Field(alias="timesIdle")
    avg_idle_time: int = Field(alias="avgIdleTime")
    prev_avgs: list[int] = Field(alias="prevAvgs")


class Member(BaseModel):
    member_id: int = Field(alias="memberId")
    admin_access: bool = Field(alias="adminAccess")
    flags: list[str]
    last_act: Activity = Field(alias="lastAct")
    idle_stats: IdleStats = Field(alias="idleStats")
    status: str
    date_added: datetime = Field(alias="dateAdded")


class Settings(BaseModel):
    kick_inactive_members: bool
    time_before_inactive: list[int]


class DiscordGuild(BaseModel):
    guild_id: int = Field(alias="guildId")
    last_act: Activity = Field(alias="lastAct")
    idle_stats: IdleStats = Field(alias="idleStats")
    status: str
    settings: Settings
    members: list[Member]


class PurgeList(BaseModel):
    guild_id: int
    member_id: int
