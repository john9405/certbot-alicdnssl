import os
from Tea.core import TeaCore
import tldextract
from alibabacloud_alidns20150109.client import Client as DNSClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as dns_models
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_darabonba_env.client import Client as EnvClient

# 解析和添加 TXT 记录
def add_dns_txt_record():
    config = open_api_models.Config()
    # 传AccessKey ID入config
    config.access_key_id = EnvClient.get_env("ALI_ACCESS_KEY_ID")
    # 传AccessKey Secret入config
    config.access_key_secret = EnvClient.get_env("ALI_ACCESS_KEY_SECRET")
    config.region_id = 'cn-hangzhou'
    client = DNSClient(config)
    certbot_domain = EnvClient.get_env("CERTBOT_DOMAIN")
    tl = tldextract.extract(certbot_domain)
    req = dns_models.AddDomainRecordRequest()
    req.domain_name = tl.domain + "." + tl.suffix
    req.rr = "_acme-challenge." + tl.subdomain
    req.type = 'TXT'
    req.value = EnvClient.get_env("CERTBOT_VALIDATION")
    try:
        resp = client.add_domain_record(req)
        ConsoleClient.log(f'添加域名解析记录的结果(json)↓')
        ConsoleClient.log(UtilClient.to_jsonstring(TeaCore.to_map(resp)))
        if not os.path.exists("/tmp/CERTBOT_" + certbot_domain):
            os.mkdir("/tmp/CERTBOT_" + certbot_domain)
        with open("/tmp/CERTBOT_" + certbot_domain + "/RECORD_ID", "w") as f:
            f.write(resp.body.record_id)
    except Exception as error:
        ConsoleClient.log(error.message)


if __name__ == "__main__":
    # 调用函数添加 DNS TXT 记录
    add_dns_txt_record()
