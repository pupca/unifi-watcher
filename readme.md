# Unifi Watcher

This is a small python library used to monitor the unifi store and alert via telegram in case the item is in stock. The notification is send only once a day to prevent spaming.

# Env Variables

| Parameter | Function |
| :----: | --- |
| `-e BOT_TOKEN=XXX` | Telegram Bot Token |
| `-e BOT_CHAT=XXX` | Telegram Group/Chat ID |
| `-e ITEM_URL=XXX` | URL of Unifi Item |
| `-e ITEM_NAME=XXX` | Name of the Unifi Item |