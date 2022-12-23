#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:__init__.py
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description: 此处demo使用MINIO项目UI测试作为示例

MINIO Windows本地临时部署：
# 1、下载minio二进制文件
    https://min.io/docs/minio/windows/index.html
# 2、本地准备数据存储路径，如：
    D:\minio\data\
# 3、cmd终端中启动服务
    PS D:\minio> .\minio.exe server D:\minio\data\
    MinIO Object Storage Server
    Copyright: 2015-2022 MinIO, Inc.
    License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl-3.0.html>
    Version: RELEASE.2022-08-26T19-53-15Z (go1.18.5 windows/amd64)

    Status:         1 Online, 0 Offline.
    API: http://10.1.2.12:9000  http://192.168.153.1:9000  http://192.168.204.1:9000  http://127.0.0.1:9000
    RootUser: minioadmin
    RootPass: minioadmin
    Console: http://10.1.2.12:59379 http://192.168.153.1:59379 http://192.168.204.1:59379 http://127.0.0.1:59379
    RootUser: minioadmin
    RootPass: minioadmin

    Command-line: https://docs.min.io/docs/minio-client-quickstart-guide
       $ mc.exe alias set myminio http://10.1.2.12:9000 minioadmin minioadmin

    Documentation: https://docs.min.io

    +-----------------------------------------------------------------+
    | You are running an older version of MinIO released 3 months ago |
    | Update: Run `mc admin update`                                   |
    +-----------------------------------------------------------------+

"""


if __name__ == '__main__':
    pass
