# Remarkable 2

This file contains the knowledge about remarkable 2.
Useful links:
* [remarkable github](https://github.com/reMarkable)
* [hack on RM2](https://github.com/reHackable/awesome-reMarkable)
* [dev on remarkable 1](https://dragly.org/2017/12/01/developing-for-the-remarkable/)

# Connect to it

Can ssh through usb. Have to enable usb interface through `Menu > Settings > Storage`. The password is displayed on `Menu > Settings > Help > Copyright and licences`'s end of page. The user is `root`.

# Characteristics

The definition is `1404 x 1872`, images are in png/svg format in 8-bit color RGBA (guess greyscale will suffice tho).
Linux kernel version: 4.14.78 (december 05th 2020).
Architecture: armv7l
OS: Codex Linux v2.5.2 (`cat /etc/os-releases`)

# File locations

* System files (such as boot/sleep screen): `/usr/share/remarkable`
* templates: `/usr/share/remarkable/templates`. Contains png+svg for the template itself, which must be listed in `templates.json`
* books/notes: seems to be `~/.local/share/remarkable/<some_id ?>` in a hashed form. The `<some_id ?>` part is `xochitl`, the first mortal women in aztech mythology
* configuration files (pwd, email etc...): `/home/root/.config/remarkable/xochitl.conf`

# Change sleep screen

Craft the image in the right definition (see above). Replace the file at `/usr/share/remarkable/suspended.png` (don't forget to save it).

# Add custom templates

When changing stuff, I needed to reboot the RM.

Examples of template entries:
```json
{
  "templates": [
    {
      "name": "Blank",
      "filename": "Blank",
      "iconCode": "\ue9fe",
      "categories": [
        "Creative",
        "Lines",
        "Grids",
        "Life/organize"
      ]
    },
    {
      "name": "Dayplanner",
      "filename": "P Day",
      "iconCode": "\ue991",
      "categories": [
        "Life/organize"
      ]
    }
}
```

Hunch was that we just need to add a random category to make it appear. Hunch was right, just need to reboot !

Seems to be possible to put a template into multiple categories.

The `iconCode` corresponds to the icon displayed on "Select template" interface.

Only the png seems to suffice as a template. Or I might guess only one of png or svg will suffice. svg seems to be lighter than png (x2 ~ x7).

The rights are `644` for all the files (owner is root).
