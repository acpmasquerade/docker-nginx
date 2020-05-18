#! /usr/bin/python3

import argparse
import os
import jinja2

def main():
    # create dict for template engine
    confdata = {
        'server_name': 'localhost'
    }
    # ssl configuration
    confdata["ssl"] = False
    # server_name
    if "NGINX_SERVER_NAME" in os.environ:
        confdata["server_name"] = os.environ["NGINX_SERVER_NAME"]
    if "NGINX_SSL_CERT" in os.environ and "NGINX_SSL_KEY" in os.environ:
        confdata["ssl"] = True
        confdata["sslcertfile"] = os.environ["NGINX_SSL_CERT"]
        confdata["sslkeyfile"] = os.environ["NGINX_SSL_KEY"]
    # location configuration
    confdata["locations"] = []
    for envvar in os.environ.keys():
        if envvar.startswith("NGINX_LOCATION_"):
            locationarg = os.environ[envvar]
            locationparts = locationarg.split(";")
            if len(locationparts) < 3:
                continue
            location = {
                "name": locationparts[0],
                "location": locationparts[1],
                "url": locationparts[2]
            }
            if location["location"].endswith("/"):
                location["url"] = location["url"].rstrip("/")
                location["trailing_slash"] = True
            confdata["locations"].append(location)

    # create nginx.conf
    template_dir = os.path.dirname(os.path.realpath(__file__)) + "/templates"
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    jinja_tpl = jinja_env.get_template("nginx.conf.tpl")
    output = jinja_tpl.render(confdata)

    # print output to stdout
    print(output)

    # Write the generated config file, if boolean switch is present
    if os.environ.get("NGINX_LOG_CONFIG", "false").lower() in ["yes", "true", "1", "y"]:
        ff=open("/var/log/nginx/nginx.conf.log", "w")
        ff.write(output)
        ff.close()

if __name__  == "__main__":
    main()
