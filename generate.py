#!/usr/bin/env python3

import json
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
COMMANDS_FILE = ROOT / "commands.json"

# 引数があればその場所へ出力
# なければ ./feed.xml
if len(sys.argv) >= 2:
    FEED_FILE = Path(sys.argv[1])
else:
    FEED_FILE = ROOT / "feed.xml"


# 1日目に使用する日付
START_DATE = datetime(2026, 10, 6, tzinfo=timezone.utc).date()


def load_commands():
    with COMMANDS_FILE.open("r", encoding="utf-8") as f:
        commands = json.load(f)

    if not isinstance(commands, list):
        raise ValueError("commands.json must contain a JSON array")

    if not commands:
        raise ValueError("commands.json is empty")

    for command in commands:
        if not all(
            key in command
            for key in ("command", "description", "example")
        ):
            raise ValueError(
                "Each command must contain "
                "'command', 'description', and 'example'"
            )

    return commands


def get_today_command(commands):
    today = datetime.now(timezone.utc).date()

    days = (today - START_DATE).days

    # START_DATEより前の日付でも正常に循環する
    index = days % len(commands)

    return commands[index], index, today


def create_feed(command, index, today):
    now = datetime.now(timezone.utc)

    rss = ET.Element("rss")
    rss.set("version", "2.0")

    channel = ET.SubElement(rss, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "PowerShell Command of the Day"

    link = ET.SubElement(channel, "link")
    link.text = "https://panier-tech.github.io/powershell-command-of-the-day/"

    description = ET.SubElement(channel, "description")
    description.text = (
        "PowerShellの便利なコマンドを1日1個紹介します。"
    )

    language = ET.SubElement(channel, "language")
    language.text = "ja"

    last_build_date = ET.SubElement(channel, "lastBuildDate")
    last_build_date.text = format_datetime(now)

    item = ET.SubElement(channel, "item")

    item_title = ET.SubElement(item, "title")
    item_title.text = command["command"]

    item_description = ET.SubElement(item, "description")

    item_description.text = (
        f'{command["description"]}\n\n'
        f'例:\n'
        f'{command["example"]}'
    )

    guid = ET.SubElement(item, "guid")
    guid.set("isPermaLink", "false")

    # 日付を含めることで、毎日別のRSS itemになる
    guid.text = (
        f"powershell-command-{today.isoformat()}-{index}"
    )

    pub_date = ET.SubElement(item, "pubDate")
    pub_date.text = format_datetime(now)

    return ET.ElementTree(rss)


def main():
    commands = load_commands()

    command, index, today = get_today_command(commands)

    print(f"Date: {today}")
    print(f"Command: {command['command']}")
    print(f"Description: {command['description']}")
    print(f"Example: {command['example']}")

    FEED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    tree = create_feed(
        command,
        index,
        today
    )

    ET.indent(
        tree,
        space="  "
    )

    tree.write(
        FEED_FILE,
        encoding="utf-8",
        xml_declaration=True
    )

    print(f"RSS written to: {FEED_FILE}")


if __name__ == "__main__":
    main()
