# mastoposter - easy-to-use mastodon-to-[everything] reposter!

Mastoposter is a simple zero-headache* service that forwards your toots from any
Mastodon-compatible Fediverse software (Pleroma also works!) to any of your
other services! For now it supports only Discord webhooks and Telegram, but it
can be easily extended to support pretty much anything!

## Installation

You can run it either on your host machine, or inside a Docker container.
In any case, you have to clone that repo first in order to do anything:
```sh
git clone https://github.com/hatkidchan/mastoposter && cd mastoposter
```

After that, you can either run it in Docker, set up a standalone systemd
service, or just run it as it is!

### Docker:

```sh
docker build -t mastoposter .
docker run --restart=always -dv /path/to/config.ini:/config.ini:ro --name mastoposter mastoposter
```

And you should be good to go

### Systemd

Let's say that you've cloned that repo to the `$MASTOPOSTER_ROOT`, then
configuration should look something like that:

```systemd
[Unit]
Description=Crossposter from Mastodon
After=network.target

[Service]
Type=simple
User=$MASTOPOSTER_USER
ExecStart=/usr/bin/python3 -m mastoposter config.ini
WorkingDirectory=$MASTOPOSTER_ROOT
Restart=on-failure

[Install]
WantedBy=network.target
```

Before running it though, don't forget to install dependencies from the 
./requirements.txt, but it's a good idea to use a virtual environment for that.
Though, that's outside of the scope of that, so I won't cover it here.

### Running manually
Just be in the folder with it, have dependencies installed and run:
python3 -m mastoposter config.ini

## Configuration

Configuration file is just a regular INI file with a couple sections.

### [main]
Section `main` contains settings of your account (ie, your instance, list ID,
user ID, access token), as well as list of modules to load.

#### instance
This is your instance. It should be written without the `https://` part, so,
for example, `mastodon.social`.

#### token
This is your access token.

On Mastodon, you can acquire it by creating an application with the minimum of
`read:statuses` and `read:lists` permissions.

On Pleroma you're out of luck and have to manually lure your token out of the
frontend you're using. For example, in Pleroma FE you can look in the "Network"
tab of the devtools and look for `chats` request. Inside the request headers,
there should be `Authorization: Bearer XXXXXXXXXXX` header. That's your token.

#### user
It's still not properly tested, but you could just leave it as `auto` for now.

In case it fails, on Mastodon you can get your user ID by looking at your
profile picture URL. The part between "/avatars/" and "original/" without all of
the slashes is your user ID.

On Pleroma you're out of luck again, I don't remember how I got mine. Just hope
that "auto" will work, lol.

#### list
That's the main problem of this crossposter: it requires a list to be created
to function properly. Both Pleroma and Mastodon support them, so it shouldn't be
a big deal. Just create a list, add yourself into it and copy its ID (it should
be in the address bar).

List is required to filter incoming events. You can't just listen for home
timeline 'cause some events are not guaranteed to be there (boosts at least).

#### auto-reconnect
You can set it to either `yes` or `no`. When set to `yes`, it will reconnect
on any websocket error, but not on any error related to modules (even if it's a
connection error!!!)

#### modules
More about them later

#### loglevel
Self-explanatory, logging level. Can be either `DEBUG`, `INFO`, `WARNING` or
`ERROR`. Defaults to `INFO`

### Modules
There's two types of modules supported at this point: `telegram` and `discord`.
Both of them are self-explanatory, but we'll go over them real quick.

Each module should contain at least `type` property and its name should start
with the `module/`. `filters` field is also can be specified. Check the
corresponding section to learn more about them.

To use module, add it to the `modules` field in the `main` section. It should
not have the `module/` prefix since it's always there. You can use multiple
modules and separate them using spaces.

#### `type = telegram`
Module with that type will work in Telegram mode.
It requires your Bot token to be set in the `token` field, as well as `chat`
to be set with your chat ID. You can use `@username` if the chat is public.
Also there's a `silent` field, when it's set to `true`, it'll set
`disable_notification` flag on every post sent.

`template` field contains your template for the message. It's pretty much
Jinja2 template. Since we use `parse_mode=html`, your `template` should be
formatted appropriately. Template itself has only `status` variable exposed,
which contains the status/post/toot itself. There's also some handy properties
such as `reblog_or_status` which points to either reblog, or status itself. Or
`name_emojiless` which contains the name without emojis. Or `name` which
contains either `display_name` or `username`, if first one is empty.


#### `type = discord`
Module for Discord webhooks. The only required parameter (besides the `type`) is
`webhook`. It **should** have `wait=true` set. You can also use `thread_id` as a
GET parameter to that. You also can use filters, nothing special about that.

### Filters
Filters are the most powerful feature of this crossposter. They allow you to...

Filter out where posts should and shouldn't go! It's that easy!

There's a couple of filters with different types and options, but all of them
should be contained in sections with names starting with `filter/`, as well
as have a `type` field with filter type.

Also, you can specify multiple filters and they'll be chained together using
AND operator. You can also prefix filter name with either `~` or `!` to invert
its behavior.

#### `type = boost`
Simple filter that passes through posts that are boosted from someone.

It also has an optional `list` property where you can specify the list of
accounts to check from. You can use globbing, but be aware, that it uses
`fnmatch` function to glob stuff, so `@*` doesn't mean "any local user", but
rather it means "any user". NOTE that his behavior is not intended and may be
changed to more appropriate one later. If `list` is empty, any boost will
trigger that filter. If list is not empty, it will allow only users from that
list.

#### `type = mention`
This filter is kinda similar to the `boost` one, but works with mentions.
Also has `list` property, yada yada you got the idea, same deal with fnmatch.

#### `type = spoiler`
Matches posts with spoilers/content-warnings.

Has an optional `regexp` parameter that will allow you to specify regular
expression to match your spoiler text.

#### `type = content`
Filter to match post content against either a regular expression, or a list of
tags. Matching is done on the plaintext version of the post.

You can have one of two properties (but not both because fuck you): `tags` or
`regexp`. It's obvious what does what: if you have `regexp` set, plaintext
version of status is checked against that regular expression, and if you have
`tags` set, then only statuses that have those tags will be allowed.

Please note that in case of tags, you should NOT use `#` symbol in front of
them.

#### `type = visibility`
Simple filter that just checks for post visibility.
Has a single property `options` that is a space-separated list of allowed
visibility levels. Note that `direct` visibility is always ignored so cannot
be used here.

#### `type = media`
Filter that allows only some media types to be posted.

`valid_media` is a space-separated list of media types from Mastodon API
(`image`, `gifv`, `video`, `audio` or `unknown`). If your Fedi software has
support for other types, they also should work.

`mode` option defines the mode of operation: it can be either `include`,
`exclude` or `only`. In case of `include`, filter will trigger when post
has media with that type, but others are allowed as well. `exclude` is the
opposite: if status has media with that type, filter won't trigger. `only`
allows statuses with either no media, or listed types only.

#### `type = combined`
The most powerful filter 'cause it allows you to combine multiple filters using
different operations.

`filters` option should contain space-separated list of filters. You also can
negate them using `!` or `~` prefixes.

`operator` is a type of operation to be used. Can be either `all`, `any` or
`single`. `all` means that all of the filters should be used. `any` means
that if any filter is triggered, this one will also trigger. `single` means
that only one filter should be triggered. Think of it as an XOR operation of
some sort.

## Sample configurations

### For Telegram:
```ini
[main]
modules = tg
instance = expired.mentality.rip
token = haha-no
list = 42
user = auto

[module/tg]
type = telegram
token = 12345:blahblahblah
chat = 12345
```

### For Telegram with a separate shitpost channel:
```ini
[main]
modules = tg tg-shitpost
instance = expired.mentality.rip
token = haha-no
list = 42
user = auto

[module/tg]
type = telegram
token = 12345:blahblahblah
chat = 12345
filters = !shitpost

[module/tg-shitpost]
type = telegram
token = 12345:blahblahblah
chat = @shitposting
filters = shitpost

[filters/shitpost]
type = content
mode = tag
tags = shitpost
```
