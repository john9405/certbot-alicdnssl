import os
from Tea.core import TeaCore

from alibabacloud_alidns20150109.client import Client as DNSClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as dns_models
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_darabonba_env.client import Client as EnvClient


# 删除 TXT 记录
def delete_dns_txt_record():
    config = open_api_models.Config()
    # 传AccessKey ID入config
    config.access_key_id = EnvClient.get_env("ALI_ACCESS_KEY_ID")
    # 传AccessKey Secret入config
    config.access_key_secret = EnvClient.get_env("ALI_ACCESS_KEY_SECRET")
    config.region_id = 'cn-hangzhou'
    client = DNSClient(config)
    req = dns_models.DeleteDomainRecordRequest()
    certbot_domain = EnvClient.get_env("CERTBOT_DOMAIN")
    with open("/tmp/CERTBOT_" + certbot_domain + "/RECORD_ID", "r") as f:
        req.record_id = f.read()
    os.remove("/tmp/CERTBOT_" + certbot_domain + "/RECORD_ID")
    ConsoleClient.log(f'删除域名解析记录的结果(json)↓')
    try:
        resp = client.delete_domain_record(req)
        ConsoleClient.log(UtilClient.to_jsonstring(TeaCore.to_map(resp)))
    except Exception as error:
        ConsoleClient.log(error.message)


if __name__ == "__main__":
    # 调用函数删除 DNS TXT 记录
    delete_dns_txt_record()
