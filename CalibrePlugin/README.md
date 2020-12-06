# Calibre plugin

This folder contains the tests to implement a plugin that will send a book from my calibre library to the remarkable, going through the remarkable cloud.
In order to do this, I will use [Calibre's plugin tutorial](https://manual.calibre-ebook.com/creating_plugins.html#adding-translations-to-your-plugin) and [RM's python api](https://github.com/subutux/rmapy/blob/master/rmapy/document.py).

# Develop

Export the calibre dev variable:
```bash
export CALIBRE_DEVELOP_FROM=${PWD}/calibre/src
echo $CALIBRE_DEVELOP_FROM
```

Then calling `callibredb` will use the source located at `$CALIBRE_DEVELOP_FROM`.

Ugly hack to have autocompletion with calibre (create a symlink in the venv :O):
```bash
ln -s ${PWD}/calibre/src/calibre venv/lib/python3.8/site-packages/calibre
```

To add the plugin to calibre, first go to the directory containing the `__init__.py` file then:
```bash
calibre-customize -b .
```

# Takeaways

Configuration is stored using a custom JSONConfig object. See `interface_demo > config.py`.
Interfaces use QT elements, installing PyQt may help with auto completion. See `interface_demo > main.py`.
Plugins will appear in different section depending on the `allow_in_xxx` values set in the `main.py`.
The particular class for device driver is (DevicePlugin)[https://manual.calibre-ebook.com/plugins.html#module-calibre.devices.interface].