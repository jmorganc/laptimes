import yaml

with open('/scripts/dkc_conf.yml', 'r') as config_fh:
    opts = yaml.load(config_fh)
