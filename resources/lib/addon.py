# SPDX-License-Identifier: GPL-3.0-or-later

import os.path
import sys

import xbmc

# setup the paths in Python
from resources.lib.initializer import Initializer  # nopep8
Initializer.set_unicode()


def run_addon():
    """ Runs Retrospect as a Video Add-On """

    log_file = None

    try:
        from resources.lib.retroconfig import Config
        from resources.lib.helpers.sessionhelper import SessionHelper

        # get a logger up and running
        from resources.lib.logger import Logger

        # only append if there are no active sessions
        if not SessionHelper.is_session_active():
            # first call in the session, so do not append the log
            append_log_file = False
        else:
            append_log_file = True

        log_file = Logger.create_logger(os.path.join(Config.profileDir, Config.logFileNameAddon),
                                        Config.appName,
                                        append=append_log_file,
                                        dual_logger=lambda x, y=4: xbmc.log(x, y))

        from resources.lib.urihandler import UriHandler
        from resources.lib.addonsettings import AddonSettings
        from resources.lib.textures import TextureHandler

        # update the loglevel
        Logger.instance().minLogLevel = AddonSettings.get_log_level()

        use_caching = AddonSettings.cache_http_responses()
        cache_dir = None
        if use_caching:
            cache_dir = Config.cacheDir

        ignore_ssl_errors = AddonSettings.ignore_ssl_errors()
        UriHandler.create_uri_handler(cache_dir=cache_dir,
                                      cookie_jar=os.path.join(Config.profileDir, "cookiejar.dat"),
                                      ignore_ssl_errors=ignore_ssl_errors)

        # start texture handler
        TextureHandler.set_texture_handler(Config, Logger.instance(), UriHandler.instance())

        # run the plugin
        from resources.lib import plugin
        p = plugin.Plugin(sys.argv[0], sys.argv[2], sys.argv[1])
        p.run()

        # make sure we leave no references behind
        AddonSettings.clear_cached_addon_settings_object()
        # close the log to prevent locking on next call
        Logger.instance().close_log()
        log_file = None

    except:
        if log_file:
            log_file.critical("Error running plugin", exc_info=True)
            log_file.close_log()
        raise
