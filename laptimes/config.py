import yaml

with open('/var/www/laptimes/dkc_conf.yml', 'r') as config_fh:
    opts = yaml.load(config_fh)
