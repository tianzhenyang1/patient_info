import requests
import json
from tkinter import messagebox
import sys
import os
import subprocess

class UpdateChecker:
    def __init__(self):
        self.current_version = "1.0.3"  # 当前版本号
        self.update_url = "https://raw.githubusercontent.com/tianzhenyang1/patient_info/main/version.json"
        self.download_url = "https://github.com/tianzhenyang1/patient_info/releases/download/"
        self.force_update = True  # 添加强制更新标志

    def check_for_updates(self):
        try:
            print(f"当前版本: {self.current_version}")  # 添加调试信息
            response = requests.get(self.update_url)
            print(f"更新检查状态码: {response.status_code}")  # 添加调试信息
            if response.status_code == 200:
                update_info = response.json()
                print(f"获取到的最新版本: {update_info.get('version')}")  # 添加调试信息
                latest_version = update_info.get('version')
                force_update = update_info.get('force_update', False)
                
                if self._compare_versions(latest_version, self.current_version):
                    update_info['force_update'] = force_update
                    return update_info
            return None
        except Exception as e:
            print(f"检查更新时出错: {str(e)}")  # 添加错误信息
            return None

    def _compare_versions(self, version1, version2):
        """比较版本号，如果version1比version2新则返回True"""
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        return v1_parts > v2_parts

    def download_update(self, update_info):
        try:
            download_url = update_info.get('download_url')
            print(f"正在从以下地址下载更新：{download_url}")  # 调试信息
            
            response = requests.get(download_url, stream=True)
            print(f"下载状态码：{response.status_code}")  # 添加状态码输出
            
            if response.status_code == 200:
                # 保存新版本
                update_file = "new_version.exe"
                with open(update_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return update_file
            else:
                print(f"下载失败，状态码：{response.status_code}")  # 错误信息
                print(f"错误内容：{response.text}")  # 添加错误内容输出
                return None
        except Exception as e:
            print(f"下载更新时出错: {str(e)}")  # 详细错误信息
            return None 