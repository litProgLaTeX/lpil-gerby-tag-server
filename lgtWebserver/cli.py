

import argparse
import os
import yaml

import logging
logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s')

from waitress import serve
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from lgtWebserver.app import createDbApp, createBaseApp
from lgtWebserver.configuration import loadConfig

def cli() :

  # setup the command line arguments
  parser = argparse.ArgumentParser()
  parser.add_argument(
    'configPath',
    help="The path to a TOML file describing how to configure this LPiL Gerby tag->label webserver instance."
  )
  parser.add_argument(
    '-v', '--verbose', action='store_true', default=False,
    help="Be verbose [False]"
  )
  parser.add_argument(
    '-q', '--quiet', action='store_true', default=False,
    help="Be quiet [False]"
  )

  config = loadConfig(vars(parser.parse_args()))

  dbApps = {}
  appTemplateFolder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates'
  )
  for dbName, dbConfig in config['databases'].items() :
    mountPoint = f"/{dbConfig['baseUrl']}"
    theApp = createDbApp(dbName, dbConfig, config)
    theApp.template_folder = appTemplateFolder
    # If the user has specified their own logging level then use it
    if 'flask_log_level' in config :
      theApp.logger.setLevel(config['flask_log_level'])
    #theApp.config["EXPLAIN_TEMPLATE_LOADING"] = True
    dbApps[mountPoint] = theApp

  baseApp = createBaseApp(config)
  #baseApp.config["EXPLAIN_TEMPLATE_LOADING"] = True
  baseApp.template_folder = appTemplateFolder

  app = DispatcherMiddleware(baseApp, dbApps)

  # Adjust the Waitress logging levels....
  if 'waitress_log_level' in config :
    wLogger = logging.getLogger('waitress')
    wLogger.setLevel(config['waitress_log_level'])

  # start the Flask App using Waitress
  if not config['quiet'] :
    print("\nYour Waitress will serve you on:")
    print(f"  http://{config['host']}:{config['port']}")
    print("")

  serve(
    app,
    host=config['host'],
    port=config['port'],
  )
