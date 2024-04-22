import os
import tomllib
import yaml

# The ConfigManager module loads a TOML based configuration for the
# gerbyRun script and then computes the appropriate gerby.configuration
# constants for use by the Gerby-website code-base, as well as the
# gerbyRun script itself.

# Load the configuration and update gerby.configuration values
def loadConfig(cmdArgs) :

  # default config
  config = {
    'title' : 'LPiL Gerby label databases',
    'databases' : {
      #'fingerPieces' : {
      #  'baseUrl' : 'fp'
      #},
      #'diSimplex' : {
      #  'baseUrl' : 'ds'
      #}
    },
    'working_dir' : '.',
    'port' : 8890,
    'host' : "127.0.0.1",
    'verbose' : cmdArgs['verbose'],
    'quiet' : cmdArgs['quiet']
  }

  # Load the TOML configuration values
  tConfig = {}
  aConfigPath = cmdArgs['configPath']
  try:
    with open(aConfigPath, 'rb') as tomlFile :
      tConfig = tomllib.load(tomlFile)
  except Exception as err :
    print(f"Could not load configuration from [{aConfigPath}]")
    print(repr(err))

  config.update(tConfig)

  # report the configuration if verbose
  if config['verbose'] :
    print(f"Loaded config from: [{aConfigPath}]\n")
    print("----- command line arguments -----")
    print(yaml.dump(cmdArgs))
    print("---------- configuration ---------")
    print(yaml.dump(config))
    print("\n----------------------------------")

  return config

