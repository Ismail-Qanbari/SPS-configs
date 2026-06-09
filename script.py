import re
import os
from collections import defaultdict

def read_configs(file_path):
    """خواندن فایل و استخراج کانفیگ‌ها (هر خط یک کانفیگ)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def parse_protocol_port(config):
    """تشخیص پروتکل و پورت از کانفیگ"""
    # تشخیص پروتکل: vless:// یا trojan://
    protocol = None
    if config.startswith('vless://'):
        protocol = 'vless'
    elif config.startswith('trojan://'):
        protocol = 'trojan'
    else:
        return None, None
    
    # استخراج پورت با regex
    # الگو: @IP:PORT یا @DOMAIN:PORT
    port_match = re.search(r'@[^:]+:(\d+)', config)
    if port_match:
        port = port_match.group(1)
        return protocol, port
    
    return None, None

def select_one_per_port_protocol(configs):
    """برای هر پورت، از هر پروتکل یک کانفیگ انتخاب کن"""
    # ساختار: {port: {protocol: config}}
    grouped = defaultdict(lambda: {})
    
    for config in configs:
        protocol, port = parse_protocol_port(config)
        if protocol and port:
            # فقط اگه برای این پورت و پروتکل هنوز کانفیگی انتخاب نشده
            if protocol not in grouped[port]:
                grouped[port][protocol] = config
    
    # تبدیل به لیست تخت
    selected = []
    for port, protocols in grouped.items():
        for protocol, config in protocols.items():
            selected.append(config)
    
    return selected

def read_ips(ip_file_path):
    """خواندن IP ها از فایل ip.txt"""
    if not os.path.exists(ip_file_path):
        print(f"⚠️ فایل {ip_file_path} پیدا نشد!")
        return []
    
    with open(ip_file_path, 'r', encoding='utf-8') as f:
        ips = [line.strip() for line in f if line.strip()]
    
    return ips

def replace_ip_in_config(config, new_ip):
    """جایگزینی IP در کانفیگ"""
    # الگوی @IP:PORT یا @DOMAIN:PORT
    pattern = r'(@)([^:]+)(:\d+)'
    
    def replacer(match):
        return f"{match.group(1)}{new_ip}{match.group(3)}"
    
    return re.sub(pattern, replacer, config)

def process_file(input_file, output_file, ips):
    """پردازش یک فایل کانفیگ"""
    print(f"\n📁 پردازش فایل: {input_file}")
    
    # مرحله 1: خواندن کانفیگ‌ها
    all_configs = read_configs(input_file)
    print(f"   - تعداد کل کانفیگ‌ها: {len(all_configs)}")
    
    # مرحله 2: انتخاب یک کانفیگ از هر پورت و پروتکل
    selected_configs = select_one_per_port_protocol(all_configs)
    print(f"   - کانفیگ‌های انتخاب شده (پایه): {len(selected_configs)}")
    
    # مرحله 3: اگر IP وجود دارد، برای هر کانفیگ پایه، به تعداد IP ها کانفیگ جدید بساز
    if ips:
        final_configs = []
        for base_config in selected_configs:
            # برای هر IP، یک کانفیگ جدید با آن IP بساز
            for ip in ips:
                new_config = replace_ip_in_config(base_config, ip)
                final_configs.append(new_config)
        print(f"   - تعداد کل کانفیگ‌های تولید شده: {len(final_configs)} ( {len(selected_configs)} کانفیگ پایه × {len(ips)} IP )")
    else:
        final_configs = selected_configs
        print(f"   - بدون جایگزینی IP (فایل ip.txt خالی یا وجود ندارد)")
    
    # مرحله 4: ذخیره در فایل خروجی
    with open(output_file, 'w', encoding='utf-8') as f:
        for config in final_configs:
            f.write(config + '\n')
    
    print(f"   ✅ خروجی ذخیره شد: {output_file}")
    
    # نمایش آمار پورت‌ها
    port_stats = defaultdict(lambda: defaultdict(int))
    for config in selected_configs:
        protocol, port = parse_protocol_port(config)
        if protocol and port:
            port_stats[port][protocol] += 1
    
    if port_stats:
        print(f"   📊 آمار پورت‌ها (کانفیگ‌های پایه):")
        for port in sorted(port_stats.keys()):
            protocols = port_stats[port]
            info = ', '.join([f"{p}: {count}" for p, count in protocols.items()])
            print(f"      - پورت {port}: {info}")

def main():
    # تنظیم مسیرها
    base_dir = r"D:\Documents\GitHub\SPS-configs"
    
    input_files = [
        ("GET-127.txt", "127.txt"),
        ("GET-128.txt", "128.txt")
    ]
    
    # خواندن IP ها
    ip_file = os.path.join(base_dir, "ip.txt")
    ips = read_ips(ip_file)
    if ips:
        print(f"📥 IP های یافت شده در ip.txt: {len(ips)} عدد")
        for i, ip in enumerate(ips, 1):
            print(f"   {i}. {ip}")
    else:
        print("⚠️ هیچ IP ای در فایل ip.txt یافت نشد (جایگزینی انجام نخواهد شد)")
    
    # پردازش هر فایل
    for input_name, output_name in input_files:
        input_path = os.path.join(base_dir, input_name)
        output_path = os.path.join(base_dir, output_name)
        
        if not os.path.exists(input_path):
            print(f"❌ فایل {input_path} پیدا نشد!")
            continue
        
        process_file(input_path, output_path, ips)
    
    print("\n🎉 عملیات با موفقیت کامل شد!")

if __name__ == "__main__":
    main()