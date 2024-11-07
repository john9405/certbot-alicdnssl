import os
import sys
import shutil

from datetime import datetime, timedelta

import certbot.main
from Tea.core import TeaCore
from alibabacloud_cdn20180510.client import Client as Cdn20180510Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cdn20180510 import models as cdn_20180510_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_darabonba_env.client import Client as EnvClient

def check_time(domain):
    config = open_api_models.Config(
        # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID。,
        access_key_id=EnvClient.get_env("ALI_ACCESS_KEY_ID"),
        # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET。,
        access_key_secret=EnvClient.get_env("ALI_ACCESS_KEY_SECRET")
    )
    # Endpoint 请参考 https://api.aliyun.com/product/Cdn
    config.endpoint = f'cdn.aliyuncs.com'
    client = Cdn20180510Client(config)
    describe_domain_certificate_info_request = cdn_20180510_models.DescribeDomainCertificateInfoRequest(
        domain_name=domain
    )
    runtime = util_models.RuntimeOptions()
    try:
        # 复制代码运行请自行打印 API 的返回值
        resp = client.describe_domain_certificate_info_with_options(describe_domain_certificate_info_request, runtime)
        print("CertDomainName:", resp.body.cert_infos.cert_info[0].cert_domain_name,
              "CertExpireTime:", resp.body.cert_infos.cert_info[0].cert_expire_time)
        cert_expire_time = datetime.strptime(resp.body.cert_infos.cert_info[0].cert_expire_time,"%Y-%m-%dT%H:%M:%SZ")
        critical_time = datetime.now() + timedelta(days=30)
        return critical_time > cert_expire_time
    except Exception as error:
        # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
        # 错误 message
        print(error.message)
        # 诊断地址
        print(error.data.get("Recommend"))
        UtilClient.assert_as_string(error.message)
        return False


def update_ssl(domain):
    if os.path.exists("/etc/letsencrypt/live/" + domain + "/fullchain.pem"):
        with open("/etc/letsencrypt/live/" + domain + "/fullchain.pem", "r") as f:
            sslpub = f.read()
    else:
        print("证书文件不存在")
        return False

    if os.path.exists("/etc/letsencrypt/live/" + domain + "/privkey.pem"):
        with open("/etc/letsencrypt/live/" + domain + "/privkey.pem", "r") as f:
            sslpri = f.read()
    else:
        print("证书文件不存在")
        return False

    config = open_api_models.Config(
        # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID。,
        access_key_id=EnvClient.get_env("ALI_ACCESS_KEY_ID"),
        # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET。,
        access_key_secret=EnvClient.get_env("ALI_ACCESS_KEY_SECRET")
    )
    # Endpoint 请参考 https://api.aliyun.com/product/Cdn
    config.endpoint = f'cdn.aliyuncs.com'
    client = Cdn20180510Client(config)
    set_cdn_domain_sslcertificate_request = cdn_20180510_models.SetCdnDomainSSLCertificateRequest(
        domain_name=domain,
        sslprotocol='on',
        sslpub=sslpub,
        sslpri=sslpri
    )
    runtime = util_models.RuntimeOptions()
    try:
        # 复制代码运行请自行打印 API 的返回值
        resp = client.set_cdn_domain_sslcertificate_with_options(set_cdn_domain_sslcertificate_request, runtime)
        ConsoleClient.log("SSL证书更新的结果(json)↓")
        ConsoleClient.log(UtilClient.to_jsonstring(TeaCore.to_map(resp)))
        return True
    except Exception as error:
        # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
        # 错误 message
        print(error.message)
        # 诊断地址
        print(error.data.get("Recommend"))
        UtilClient.assert_as_string(error.message)
        return False


def remove_file(domain):
    print("Deleted the relevant files of the certificate, domain name:" + domain)
    shutil.rmtree("/etc/letsencrypt/live/" + domain)
    shutil.rmtree("/etc/letsencrypt/archive/" + domain)
    os.remove("/etc/letsencrypt/renewal/" + domain + ".conf")


def get_dns_challenge(domain):
    try:
        sys.argv = [
            'certbot',
            'certonly',  # 只生成证书，不安装
            '--manual',  # 使用手动验证
            '--preferred-challenges', 'dns',  # 指定 DNS-01 验证
            '--manual-auth-hook', '/path/to/manual-auth-hook.py',
            '--manual-cleanup-hook', '/path/to/manual-cleanup-hook.py',
            '-d', domain
        ]

        # 调用 certbot 主函数
        certbot.main.main()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    for domain in ["www.example.com"]:
        if check_time(domain):
            print(domain + "证书即将过期，开始更新")
            if get_dns_challenge(domain):
                if update_ssl(domain):
                    remove_file(domain)
        else:
            print(domain + "无需更新")


if __name__ == '__main__':
    main()
