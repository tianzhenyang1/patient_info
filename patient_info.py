import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
import json
import requests  # 用于调用API
from version_checker import UpdateChecker
import sys
import os
import subprocess

class PatientInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("卡威尔问诊信息整理系统")
        self.root.geometry("500x750")

        # 初始化更新检查器
        self.update_checker = UpdateChecker()
        
        # 检查更新
        self.check_for_updates()

        # 定义关键字映射
        self.field_keywords = {
            'name': ['姓名'],
            'age': ['年龄'],
            'gender': ['性别'],
            'condition': ['病情自述', '主诉', '症状描述'],
            'vitals': ['血压', '血糖'],
            'symptoms': ['想改善的症状', '需改善症状', '改善症状'],
            'medication': ['日常用药', '用药情况', '服用药物'],
            'allergy': ['过敏史', '过敏反应']
        }

        # 添加火山大模型配置
        self.volc_config = {
            'api_key': 'a908be75-4d7c-41ee-b59f-81d90b58404c',  # 更新为您的API密钥
            'api_secret': '',  # 如果不需要api_secret可以留空
            'url': 'https://api.volcengine.com/v1/llm/chat'
        }

        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建输入框和标签
        self.create_widgets()

    def check_for_updates(self):
        """检查软件更新"""
        update_info = self.update_checker.check_for_updates()
        if update_info:
            msg = f"""发现新版本！
当前版本：{self.update_checker.current_version}
最新版本：{update_info['version']}
更新内容：{update_info.get('description', '无')}

是否现在更新？"""
            if messagebox.askyesno("软件更新", msg):
                self.perform_update(update_info)

    def perform_update(self, update_info):
        """执行更新操作"""
        # 显示更新进度窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("正在更新")
        progress_window.geometry("300x150")
        
        # 进度提示
        ttk.Label(progress_window, 
                 text="正在下载更新...",
                 font=('微软雅黑', 10)).pack(pady=20)
        
        # 进度条
        progress = ttk.Progressbar(progress_window, 
                                 mode='indeterminate')
        progress.pack(fill=tk.X, padx=20)
        progress.start()

        def do_update():
            try:
                # 下载更新
                update_file = self.update_checker.download_update(update_info)
                if update_file:
                    # 准备更新脚本
                    with open('update.bat', 'w') as f:
                        f.write(f'''@echo off
timeout /t 2 /nobreak
del "{sys.argv[0]}"
move /y "{update_file}" "{sys.argv[0]}"
start "" "{sys.argv[0]}"
del "%~f0"
''')
                    
                    # 执行更新
                    progress_window.destroy()
                    messagebox.showinfo("更新就绪", "更新已下载完成，程序将重启以完成更新。")
                    subprocess.Popen(['update.bat'], shell=True)
                    self.root.quit()
                else:
                    progress_window.destroy()
                    messagebox.showerror("更新失败", "下载更新失败，请稍后重试。")
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("更新错误", f"更新过程中出错：{str(e)}")

        # 在新线程中执行更新
        import threading
        threading.Thread(target=do_update).start()

    def create_widgets(self):
        # 样式设置
        style = ttk.Style()
        style.configure('Title.TLabel', font=('微软雅黑', 14, 'bold'))
        style.configure('Field.TLabel', font=('微软雅黑', 10))
        
        # 标题
        title_label = ttk.Label(self.main_frame, text="卡威尔问诊信息登记表", style='Title.TLabel')
        title_label.pack(pady=(0, 15))

        # 基本信息框架
        basic_info_frame = ttk.LabelFrame(self.main_frame, text="基本信息", padding=5)
        basic_info_frame.pack(fill=tk.X, pady=(0, 10))

        # 姓名、年龄和性别行
        info_row_frame = ttk.Frame(basic_info_frame)
        info_row_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 姓名
        ttk.Label(info_row_frame, text="姓名：", style='Field.TLabel').pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(info_row_frame, width=15)
        self.name_entry.pack(side=tk.LEFT, padx=(0, 20))

        # 年龄
        ttk.Label(info_row_frame, text="年龄：", style='Field.TLabel').pack(side=tk.LEFT)
        self.age_entry = ttk.Entry(info_row_frame, width=8)
        self.age_entry.pack(side=tk.LEFT, padx=(0, 20))

        # 性别（改为文本框）
        ttk.Label(info_row_frame, text="性别：", style='Field.TLabel').pack(side=tk.LEFT)
        self.gender_entry = ttk.Entry(info_row_frame, width=5)  # 改用Entry替代Combobox
        self.gender_entry.pack(side=tk.LEFT)

        # 医疗信息框架
        medical_info_frame = ttk.LabelFrame(self.main_frame, text="医疗信息", padding=5)
        medical_info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 调整文本框的高度
        self.create_text_field(medical_info_frame, "病情自述：", "condition_text", 4)
        self.create_text_field(medical_info_frame, "血压/血糖：", "vitals_text", 2)
        self.create_text_field(medical_info_frame, "想改善的症状：", "symptoms_text", 4)
        self.create_text_field(medical_info_frame, "日常用药：", "medication_text", 4)
        self.create_text_field(medical_info_frame, "过敏史：", "allergy_text", 3)

        # 按钮框架
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        # 一键整理按钮
        self.submit_btn = tk.Button(
            button_frame,
            text="一键整理信息",
            command=self.organize_info,
            font=('微软雅黑', 10),
            bg='#4CAF50',
            fg='white',
            width=15,
            height=1,
            relief=tk.RAISED
        )
        self.submit_btn.pack(side=tk.LEFT, padx=5)

        # 自动识别按钮
        self.parse_btn = tk.Button(
            button_frame,
            text="自动识别文本",
            command=self.parse_text,
            font=('微软雅黑', 10),
            bg='#2196F3',
            fg='white',
            width=15,
            height=1,
            relief=tk.RAISED
        )
        self.parse_btn.pack(side=tk.LEFT, padx=5)

        # 添加清除按钮
        self.clear_btn = tk.Button(
            button_frame,
            text="清除所有内容",
            command=self.clear_all_fields,
            font=('微软雅黑', 10),
            bg='#f44336',  # 红色
            fg='white',
            width=15,
            height=1,
            relief=tk.RAISED
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # 在按钮框架中添加检查更新按钮
        self.update_btn = tk.Button(
            button_frame,
            text="检查更新",
            command=self.check_for_updates,
            font=('微软雅黑', 10),
            bg='#9C27B0',  # 紫色
            fg='white',
            width=15,
            height=1,
            relief=tk.RAISED
        )
        self.update_btn.pack(side=tk.LEFT, padx=5)

    def create_text_field(self, parent, label_text, attribute_name, height=3):
        """创建文本框字段的辅助方法"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text=label_text, style='Field.TLabel').pack(anchor=tk.W)
        text_widget = tk.Text(frame, width=40, height=height, font=('微软雅黑', 10))
        text_widget.pack(fill=tk.X, pady=(2, 0))
        setattr(self, attribute_name, text_widget)

    def organize_info(self):
        # 修改获取性别的方式
        info = f"""患者信息整理：
姓名：{self.name_entry.get()}
年龄：{self.age_entry.get()}
性别：{self.gender_entry.get()}
病情自述：{self.condition_text.get("1.0", tk.END).strip()}
血压/血糖：{self.vitals_text.get("1.0", tk.END).strip()}
想改善的症状：{self.symptoms_text.get("1.0", tk.END).strip()}
日常用药：{self.medication_text.get("1.0", tk.END).strip()}
过敏史：{self.allergy_text.get("1.0", tk.END).strip()}"""
        self.show_organized_info(info)

    def show_organized_info(self, info):
        # 创建新窗口显示整理后的信息
        result_window = tk.Toplevel(self.root)
        result_window.title("整理结果")
        result_window.geometry("500x600")

        # 创建主框架
        main_frame = ttk.Frame(result_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建文本框显示结果
        result_text = tk.Text(main_frame, 
                            font=('微软雅黑', 11),
                            wrap=tk.WORD,  # 确保文本自动换行
                            padx=10,
                            pady=10)
        result_text.pack(fill=tk.BOTH, expand=True)
        result_text.insert("1.0", info)
        result_text.config(state=tk.DISABLED)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_text.configure(yscrollcommand=scrollbar.set)

    def analyze_text_with_llm(self, text):
        """使用火山大模型分析文本"""
        prompt = f"""
        请仔细分析以下文本，提取病人信息。特别注意从文本中识别性别相关的信息（如：提到"阿姨"表示女性，"老伴"通常是异性配偶）：
        {text}
        
        请严格按以下格式提取并输出信息：
        姓名：（姓名）
        年龄：（年龄）数字
        性别：（性别，必须输出"男"或"女"）
        病情自述：（症状描述）
        血压/血糖：（相关数值）
        想改善的症状：（需要改善的症状）
        日常用药：（用药情况）
        过敏史：（过敏情况）
        """

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.volc_config["api_key"]}'
        }

        data = {
            "model": "doubao-1-5-pro-256k-250115",
            "messages": [
                {
                    "role": "system",
                    "content": """你是一个专业的医疗信息提取助手。在提取信息时：
1. 性别判断规则：
   - 提到"阿姨"、"奶奶"、"妈妈"等词时，性别为"女"
   - 提到"叔叔"、"爷爷"、"爸爸"等词时，性别为"男"
   - 如果提到"老伴"，需要根据上下文判断说话者的性别
2. 年龄必须提取具体数字
3. 所有信息需要按照固定格式输出"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:
            response = requests.post(
                'https://ark.cn-beijing.volces.com/api/v3/chat/completions',  # 使用正确的API地址
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result:
                    content = result['choices'][0]['message']['content']
                    self.parse_llm_response(content)
                else:
                    messagebox.showerror("错误", "API返回格式不正确")
            else:
                messagebox.showerror("错误", f"调用大模型失败：{response.text}")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误：{str(e)}")

    def parse_llm_response(self, response_text):
        try:
            # 清空现有内容
            self.clear_all_fields()
            
            # 解析大模型返回的文本
            lines = response_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 改进性别识别的解析
                if '姓名' in line:
                    name = line.split('：')[-1].strip().replace('（', '').replace('）', '').replace('(', '').replace(')', '')
                    self.name_entry.insert(0, name)
                elif '年龄' in line:
                    # 提取年龄中的数字
                    age = ''.join(filter(str.isdigit, line.split('：')[-1].strip()))
                    if age:
                        self.age_entry.insert(0, age)
                elif '性别' in line:
                    gender = line.split('：')[-1].strip().replace('（', '').replace('）', '').replace('(', '').replace(')', '')
                    if '男' in gender:
                        self.gender_entry.insert(0, '男')
                    elif '女' in gender:
                        self.gender_entry.insert(0, '女')
                elif '病情自述' in line:
                    content = line.split('：')[-1].strip().replace('（', '').replace('）', '').replace('(', '').replace(')', '')
                    self.condition_text.insert('1.0', content)
                elif '血压' in line or '血糖' in line:
                    content = line.split('：')[-1].strip().replace('（', '').replace('）', '').replace('(', '').replace(')', '')
                    self.vitals_text.insert('1.0', content)
                elif '想改善的症状' in line:
                    content = line.split('：')[-1].strip().replace('（', '').replace('）', '').replace('(', '').replace(')', '')
                    self.symptoms_text.insert('1.0', content)
                elif '日常用药' in line:
                    content = line.split('：')[-1].strip().replace('（', '').replace('）', '').replace('(', '').replace(')', '')
                    self.medication_text.insert('1.0', content)
                elif '过敏史' in line:
                    content = line.split('：')[-1].strip().replace('（', '').replace('）', '').replace('(', '').replace(')', '')
                    self.allergy_text.insert('1.0', content)

        except Exception as e:
            messagebox.showerror("错误", f"解析结果时发生错误：{str(e)}")

    def parse_text(self):
        # 修改原有的parse_text方法，添加大模型调用
        input_window = tk.Toplevel(self.root)
        input_window.title("粘贴文本进行识别")
        input_window.geometry("500x400")

        input_frame = ttk.Frame(input_window, padding="20")
        input_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(input_frame, 
                 text="请将需要识别的文本粘贴到下面：", 
                 font=('微软雅黑', 10)).pack(pady=(0, 10))

        text_input = tk.Text(input_frame, 
                           font=('微软雅黑', 10),
                           wrap=tk.WORD,
                           height=15)
        text_input.pack(fill=tk.BOTH, expand=True)

        def confirm():
            content = text_input.get("1.0", tk.END).strip()
            # 调用大模型进行分析
            self.analyze_text_with_llm(content)
            input_window.destroy()

        tk.Button(input_frame,
                 text="开始识别",
                 command=confirm,
                 font=('微软雅黑', 10),
                 bg='#2196F3',
                 fg='white').pack(pady=(10, 0))

    def clear_all_fields(self):
        # 清空所有输入框
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.gender_entry.delete(0, tk.END)  # 清除性别文本框
        
        # 清空所有文本框
        for field in ['condition', 'vitals', 'symptoms', 'medication', 'allergy']:
            text_widget = getattr(self, f"{field}_text", None)
            if text_widget:
                text_widget.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PatientInfoApp(root)
    root.mainloop() 