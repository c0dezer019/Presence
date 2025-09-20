# Presence

Most bots that monitor user activity only go by number of messages sent. Unlike those
bots, Presence aims to measure time idle by monitoring the time between all activities,
whether that is messages, joining a voice chat, or any other user action. Basically any
action performed by a user is timestamped by the bot. The ultimate goal of Presence is
to give server admins and owners a snapshot of activity in their servers, and beyond
that, to help clean out inactive channels and users.

Presence is written in Python using Nextcord and uses Redis for caching to reduce work on
the backend. It is backed by a GraphQL + PostgreSQL backend for long-term persistence.

## Features

- Long-term data persistence with PostgreSQL.
- Data caching with Redis for reduced read/write operations on the database and faster
  data recall.
- Uses GraphQL to further reduce the number of calls and the amount of data required.
- Logs user activity timestamps in channels that the bot can see.
- Calculates user idle times based on the timestamp of the last activity.
- Flags a user as active or inactive based on a configured idle threshold.
- Applies an inactive role to inactive users.
- Auto-kicks inactive users after a configured timeout.
- Rich settings configurable by server administrators.

## Setup

In order to use Presence locally, you will need:

- Python 3.x
- Redis Cloud (paid) or Open Source (free)
- A Discord account
- A [Discord Application](https://discord.com/developers/applications)

### Adding bot to a server

1. Go to your Discord application, located using the link above.
2. Navigate to the OAuth2 menu.
3. In OAuth2 URL Generator, check bot.
4. Presence by default needs the following permissions:
   1. Kick Members
   2. View Channels
   3. Send Messages
   4. Use Slash Commands
5. Make sure integration type is set as Guild
6. Navigate to the generated url (the rest is self explanatory)

## Usage Guide

Upon invitation to a server, the bot will catalogue every user on the server (except
other bots), storing their 18-digit user ID so it can distinguish one user from another.
The bot uses the ID to ensure consistent activity tracking.

### Commands

Presence primarily uses slash commands, but still includes some prefixed commands used
mainly for developer-only operations.

#### Developer Commands

##### **?reset**

The purpose of this command is in its name: it resets all data associated with the
guild where it is run. The bot will temporarily disconnect to prevent new data from
being recorded during the reset. Redis values will be cleared and a reset request will
be sent to the backend where a soft reset will be performed (values returned to
defaults).

##### **?delete <type> <target_id>**

This commmand will delete all data on target from Redis and perform a hard reset on the
backend (delete db rows and re-add).

##### **?reload <cog?>**

Reloads all or a specified cog. Useful when a command is changed, removed, or added.

##### **?setup**

Runs the setup sequence (for development purposes, if the bot did not successfully
perform on_guild_join functions).
