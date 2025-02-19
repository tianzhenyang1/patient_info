import requests
import json
from tkinter import messagebox
import sys
import os
import subprocess

class UpdateChecker:
    def __init__(self):
        self.current_version = "1.0.2"  # 当前版本号
        self.update_url = "https://raw.githubusercontent.com/tianzhenyang1/patient_info/main/version.json"
        self.download_url = "https://github.com/tianzhenyang1/patient_info/releases/download/"

    def check_for_updates(self):
        try:
            response = requests.get(self.update_url)
            if response.status_code == 200:
                update_info = response.json()
                latest_version = update_info.get('version')
                
                if self._compare_versions(latest_version, self.current_version):
                    return update_info
            return None
        except Exception as e:
            print(f"检查更新时出错: {str(e)}")
            return None

    def _compare_versions(self, version1, version2):
        """比较版本号，如果version1比version2新则返回True"""
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        return v1_parts > v2_parts

    def download_update(self, update_info):
        try:
            download_url = update_info.get('download_url')
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                # 保存新版本
                update_file = "new_version.exe"
                with open(update_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return update_file
            return None
        except Exception as e:
            print(f"下载更新时出错: {str(e)}")
            return None 