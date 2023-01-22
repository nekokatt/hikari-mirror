<div align="center">
<h1>hikari</h1>
<a href="https://pypi.org/project/hikari"><img height="20" alt="Supported python versions" src="https://img.shields.io/pypi/pyversions/hikari"></a>
<a href="https://pypi.org/project/hikari"><img height="20" alt="PyPI version" src="https://img.shields.io/pypi/v/hikari"></a>
<br>
<a href="https://github.com/hikari-py/hikari/actions"><img height="20" alt="CI status" src="https://github.com/hikari-py/hikari/actions/workflows/ci.yml/badge.svg?branch=master&event=push"></a>
<a href="https://pypi.org/project/mypy/"><img height="20" alt="Mypy badge" src="https://img.shields.io/badge/mypy-checked-blue"></a>
<a href="https://pypi.org/project/black"><img height="20" alt="Black badge" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://codeclimate.com/github/hikari-py/hikari/test_coverage"><img height="20" alt="Test coverage" src="https://api.codeclimate.com/v1/badges/f95070b25136a69b0589/test_coverage"></a>
<br>
<a href="https://discord.gg/Jx4cNGG"><img height="20" alt="Discord invite" src="https://discord.com/api/guilds/574921006817476608/widget.png"></a>
<a href="https://docs.hikari-py.dev/en/stable"><img height="20" alt="Documentation Status" src="https://readthedocs.org/projects/hikari-py/badge/?version=latest"></a>
</div>

An opinionated, static typed Discord microframework for Python3 and asyncio that supports Discord's v10 REST and
Gateway APIs.

Built on good intentions and the hope that it will be extendable and reusable, rather than an obstacle for future
development.

Python 3.8, 3.9, 3.10 and 3.11 are currently supported.

## Installation

Install Hikari from PyPI with the following command:

```bash
python -m pip install -U hikari
# Windows users may need to run this instead...
py -3 -m pip install -U hikari
```

----

## Bots

```py
import hikari

bot = hikari.GatewayBot(token="...")

@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    """If a non-bot user mentions your bot, respond with 'Pong!'."""

    # Do not respond to bots nor webhooks pinging us, only user accounts
    if not event.is_human:
        return

    me = bot.get_me()

    if me.id in event.message.user_mentions_ids:
        await event.message.respond("Pong!")

bot.run()
```

This will only respond to messages created in guilds. You can use `DMMessageCreateEvent` instead to only listen on
DMs, or `MessageCreateEvent` to listen to both DMs and guild-based messages.

[Logging](https://docs.python.org/3/library/logging.html) will be automatically configured for you if you do not
enable it manually. This has been implemented after seeing a large number of new bot developers struggle with
writing their first bot in other frameworks simply because of working blind after not understanding or knowing how
to set up standard logging messages.

If you wish to customize the intents being used in order to change which events your bot is notified about, then you
can pass the `intents` kwarg to the `GatewayBot` constructor:

```py
# the default is to enable all unprivileged intents (all events that do not target the
# presence, activity of a specific member nor message content).
bot = hikari.GatewayBot(intents=hikari.Intents.ALL, token="...")
```

The above example would enable all intents, thus enabling events relating to member presences to be received
(you'd need to whitelist your application first to be able to start the bot if you do this).
[Other options also exist](https://docs.hikari-py.dev/en/stable/reference/hikari/impl/bot/#hikari.impl.bot.GatewayBot)
such as [customizing timeouts for requests](https://docs.hikari-py.dev/en/stable/reference/hikari/impl/config/#hikari.impl.config.HTTPSettings.timeouts)
and [enabling a proxy](https://docs.hikari-py.dev/en/stable/reference/hikari/impl/config/#hikari.impl.config.ProxySettings).

Also note that you could pass extra options to `bot.run` during development, for example:

```py
bot.run(
    asyncio_debug=True,             # enable asyncio debug to detect blocking and slow code.

    coroutine_tracking_depth=20,    # enable tracking of coroutines, makes some asyncio
                                    # errors clearer.

    propagate_interrupts=True,      # Any OS interrupts get rethrown as errors.
)
```

[Many other helpful options](https://docs.hikari-py.dev/en/stable/reference/hikari/impl/bot/#hikari.impl.bot.GatewayBot.run)
exist for you to take advantage of if you wish.

Events are determined by the type annotation on the event parameter, or alternatively as a type passed to the
`@bot.listen()` decorator, if you do not want to use type hints.

```py
@bot.listen()
async def ping(event: hikari.MessageCreateEvent):
    ...

# or

@bot.listen(hikari.MessageCreateEvent)
async def ping(event):
    ...
```

---

## REST-only applications

You may only want to integrate with the REST API, for example if writing a web dashboard.

This is relatively simple to do:

```py
rest = hikari.RESTApp()

async def print_my_user(token):
    # We acquire a client with a given token. This allows one REST app instance
    # with one internal connection pool to be reused.
    async with rest.acquire(token) as client:
        my_user = await client.fetch_my_user()
        print(my_user)

asyncio.run(print_my_user("user token acquired through OAuth here"))
```

---

## Optional Features

Optional features can be specified when installing hikari:

* `server` - Install dependencies required to enable Hikari's standard interaction server (RESTBot) functionality.
* `speedups` - Detailed in [`hikari[speedups]`](#hikarispeedups).

Example:

```bash
# To install hikari with the speedups feature:
python -m pip install -U hikari[speedups]

# To install hikari with both the speedups and server features:
python -m pip install -U hikari[speedups, server]
```

## Additional resources

You may wish to use a command framework on top of Hikari so that you can start writing a bot quickly without
implementing your own command handler.

Hikari does not include a command framework by default, so you will want to pick a third party library to do it:

- [`lightbulb`](https://github.com/tandemdude/hikari-lightbulb) - a simple and easy to use command framework for Hikari.
- [`tanjun`](https://github.com/FasterSpeeding/Tanjun) - a flexible command framework designed to extend Hikari.
- [`crescent`](https://github.com/magpie-dev/hikari-crescent) - a command handler for Hikari that keeps your project neat and tidy.

There are also third party libraries to help you manage components:

- [`miru`](https://github.com/HyperGH/hikari-miru) -  A component handler for hikari, inspired by discord.py's views. 
- [`flare`](https://github.com/brazier-dev/hikari-flare/) - A component manager designed to write simple persistent buttons.

---

## Making your application more efficient

As your application scales, you may need to adjust some things to keep it performing nicely.

### Python optimization flags

CPython provides two optimization flags that remove internal safety checks that are useful for development, and change
other internal settings in the interpreter.

- `python bot.py` - no optimization - this is the default.
- `python -O bot.py` - first level optimization - features such as internal assertions will be disabled.
- `python -OO bot.py` - second level optimization - more features (**including all docstrings**) will be removed from
  the loaded code at runtime.

**A minimum of first level of optimization** is recommended when running bots in a production environment.

### `hikari[speedups]`

If you have a C compiler (Microsoft VC++ Redistributable 14.0 or newer, or a modern copy of GCC/G++, Clang, etc), it is
recommended you install Hikari using `pip install -U hikari[speedups]`. This will install `aiohttp` with its available
speedups, and `ciso8601` which will provide you with a small performance boost.

### `uvloop`

**If you use a UNIX-like system**, you will get additional performance benefits from using a library called `uvloop`.
This replaces the default `asyncio` event loop with one that uses `libuv` internally. You can run `pip install uvloop`
and then amend your script to be something similar to the following example to utilise it in your application:

```py
import os
import hikari

if os.name != "nt":
    import uvloop
    uvloop.install()

bot = hikari.GatewayBot(...)
...
```

### Compiled extensions

Eventually, we will start providing the option to use compiled components of this library over pure Python ones if it
suits your use case. This should also enable further scalability of your application, should
[_PEP 554 -- Multiple Interpreters in the Stdlib_](https://www.python.org/dev/peps/pep-0554/#abstract) be accepted.

Currently, this functionality does not yet exist.

---

## Developing Hikari

To familiarize yourself a bit with the project, we recommend reading our
[contributing manual](https://github.com/hikari-py/hikari/blob/master/CONTRIBUTING.md).

If you wish to contribute something, you should first start by cloning the repository.

In the repository, make a virtual environment (`python -m venv .venv`) and enter it (`source .venv/bin/activate` on
Linux, or for Windows use one of `.venv\Scripts\activate.ps1`, `.venv\Scripts\activate.bat`,
`source .venv/Scripts/activate`).

The first thing you should run is `pip install -r dev-requirements/nox.txt` to install nox.
This handles running predefined tasks and pipelines.

Once this is complete, you can run `nox` without any arguments to ensure everything builds and is correct.

### Where can I start?

Check out the issues tab on GitHub. If you are nervous, look for issues marked as "good first issue" for something
easy to start with!

[![good-first-issues](https://img.shields.io/github/issues/hikari-py/hikari/good%20first%20issue)](https://github.com/hikari-py/hikari/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22)

Feel free to also join our [Discord](https://discord.gg/Jx4cNGG) to directly ask questions to the maintainers! They will
be glad to help you out and point you in the right direction.
