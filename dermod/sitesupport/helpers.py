import settings_file
import requests

def get_resource(res):
    with requests.Session() as s:
        s.headers = {
            'User-Agent': 'DBooru/2.0 (Api checker module)(github.com/mcilya/DBooru)',
            'Accept': 'application/json'
            }
        if settings_file.enable_proxy is False:
            raw_data = s.get(
                "{resource}".format(resource=res),
                verify=settings_file.ssl_verify, timeout=settings_file.time_wait)
        else:
            raw_data = s.get(
                "{domain}".format(resource=res),
                proxies=dict(
                    https='{}://{}:{}'.format(
                        settings_file.proxy_type, settings_file.proxy_ip, settings_file.proxy_port),
                    http='{}://{}:{}'.format(settings_file.proxy_type, settings_file.proxy_ip, settings_file.proxy_port)),
                verify=settings_file.ssl_verify, timeout=settings_file.time_wait)
    return raw_data
