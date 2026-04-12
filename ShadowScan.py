import requests
import threading
import socket
import sys
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

"""
线程锁和退出锁定
"""
print_lock = threading.Lock()
exit_flag = False

def signal_handler(sig, frame):
    """
    处理 Ctrl+C 信号
    """
    global exit_flag
    exit_flag = True
    print("\n")
    print('\033[91m[*]已退出程序\033[0m')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def show_banner():
    """
    启动界面
    """
    # Logo 渐变色阶 (亮青 -> 深蓝)
    logo_colors = [45, 45, 39, 33, 27, 21]

    ascii_art = [
        "███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗███████╗ ██████╗ █████╗ ███╗   ██╗",
        "██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██║██║    ██║██╔════╝██╔════╝██╔══██╗████╗  ██║",
        "███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║███████╗██║     ███████║██╔██╗ ██║",
        "╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║╚════██║██║     ██╔══██║██║╚██╗██║",
        "███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝███████║╚██████╗██║  ██║██║ ╚████║",
        "╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝"
    ]

    # 打印 Logo
    for i, line in enumerate(ascii_art):
        color = f"\033[38;5;{logo_colors[i % len(logo_colors)]}m"
        print(f"{color}{line}")

    # 分割线 141 (亮紫)，信息 93 (深紫)
    banner_text = f"""\033[38;5;141m———————— ShadowScan v1.1.2 - Trace the Shadow, Link All Hidden Domains ————————\033[38;5;93m
[*]项目地址：https://github.com/SweetSour520/ShadowScan
[*]BY.SweetSour\033[0m"""
    print(banner_text)


def show_help():
    """
    显示帮助信息
    """
    help_text = """\033[38;5;45m
命令格式：
    python ShadowScan.py [选项]

可选参数：
    -h,     --help          显示此帮助信息
    -s,     --status Code   筛选状态码 (逗号分割)
    -x,     --exclude Code  排除指定状态码 (逗号分割)
    -ip,    --show_ip       显示域名解析的IP地址

示例：
    python ShadowScan.py -s 200,301 -x 404 -ip\033[0m"""
    print(help_text)


def parse_status_codes(code):
    """
    解析状态码参数
    """
    if not code:
        return None
    codes = []
    for c in code.split(','):
        c = c.strip()
        if c:
            try:
                codes.append(int(c))
            except ValueError:
                print(f'\033[91m[!]无效的状态码：{c}\033[0m')
    return codes if codes else None


def parse_args():
    """
    解析命令行参数
    """
    args = {
        'status_include': None,
        'status_exclude': None,
        'show_ip': False,
        'help': False,
    }

    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] in ['-h', '--help']:
            args['help'] = True
            i += 1
        elif argv[i] in ['-s', '--status']:
            if i + 1 < len(argv):
                args['status_include'] = parse_status_codes(argv[i + 1])
                i += 2
            else:
                print(f'\033[91m[!]缺少状态码参数：{argv[i]}\033[0m')
                show_help()
                sys.exit(1)
        elif argv[i] in ['-x', '--exclude']:
            if i + 1 < len(argv):
                args['status_exclude'] = parse_status_codes(argv[i + 1])
                i += 2
            else:
                print(f'\033[91m[!]缺少状态码参数：{argv[i]}\033[0m')
                show_help()
                sys.exit(1)
        elif argv[i] in ['-ip', '--show_ip']:
            args['show_ip'] = True
            i += 1
        else:
            print(f'\033[91m[!]无效的参数：{argv[i]}\033[0m')
            show_help()
            sys.exit(1)
        i += 1

    return args


def remove_prefix(url):
    """
    删除字符串开头的指定前缀
    """
    if url.startswith('http://'):
        return url[7:]
    elif url.startswith('https://'):
        return url[8:]
    return url


def req(url, directory='directory/domain_list.txt', status_include=None, status_exclude=None, show_ip=False, threads=10):
    """
    发起请求
    """
    try:
        result_file = f'URL/{url}.txt'
        if not os.path.exists('URL'):
            os.mkdir('URL')
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write('')
        with open(directory, 'r', encoding='utf-8') as f:
            domain_list = f.read().splitlines()
    except Exception as e:
        print(f'\033[91m[!]读取字典失败：{e}\033[0m')
        return

    targets = [f'http://{domain}.{url}' for domain in domain_list if domain]

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_single, t, url, status_include, status_exclude, show_ip): t for t in targets}
        for future in as_completed(futures):
            if exit_flag:
                executor.shutdown(wait=False, cancel_futures=True)
                break


def scan_single(target, url, status_include=None, status_exclude=None, show_ip=False):
    """
    扫描单个目标
    """
    if exit_flag:
        return

    ip_add = ''
    if show_ip:
        try:
            domain = remove_prefix(target)
            ip_add = socket.gethostbyname(domain)
            ip_add = f'[{ip_add}]'
        except:
            ip_add = '[N/A]'
    
    try:
        res = requests.get(target, headers=header, timeout=2.5)
        res.encoding = 'utf-8'
        title = re.findall('<title>(.*?)</title>', res.text)
        title = title[0] if title else '无标题'
        status_code = res.status_code

        # 状态码过滤
        if status_include and status_code not in status_include:
            return
        if status_exclude and status_code in status_exclude:
            return

        # 正常输出逻辑
        with print_lock:
            if exit_flag:
                return
            if status_code == 200:
                print(f'\033[92m[+]{target}[{res.status_code}][{title}][{len(res.text)}][{ip_add}]\033[0m')
                with open(f'URL/{url}.txt', 'a', encoding='utf-8') as f:
                    f.write(f'[+]\t{target}\t[{res.status_code}]\t[{title}]\t[{len(res.text)}]\t[{ip_add}]\n')
            elif status_code == 404:
                print(f'\033[91m[-]{target}[{res.status_code}][{title}][{len(res.text)}][{ip_add}]\033[0m')
                with open(f'URL/{url}.txt', 'a', encoding='utf-8') as f:
                    f.write(f'[-]\t{target}\t[{res.status_code}]\t[{title}]\t[{len(res.text)}]\t[{ip_add}]\n')
            else:
                print(f'\033[93m[*]{target}[{res.status_code}][{title}][{len(res.text)}][{ip_add}]\033[0m')
                with open(f'URL/{url}.txt', 'a', encoding='utf-8') as f:
                    f.write(f'[*]\t{target}\t[{res.status_code}]\t[{title}]\t[{len(res.text)}]\t[{ip_add}]\n')
    except requests.exceptions.Timeout:
        with print_lock:
            if exit_flag:
                return
            if not status_include:
                if not status_exclude or 0 not in status_exclude:
                    print(f'\033[91m[!]{target} 请求超时\033[0m')
    except requests.exceptions.ConnectionError:
        with print_lock:
            if exit_flag:
                return
            if (not status_exclude or 0 not in status_exclude) and (not status_exclude or 404 not in status_exclude):
                print(f'\033[91m[!]{target} DNS解析失败或连接被拒绝\033[0m')
    except requests.exceptions.RequestException as e:
        with print_lock:
            if exit_flag:
                return
            if not status_include:
                if not status_exclude or 0 not in status_exclude:
                    print(f'\033[91m[!]{target} 请求异常：{e}\033[0m')


def main():
    show_banner()
    args = parse_args()

    if args['help']:
        show_help()
        return

    domain = input('\033[38;5;141m请输入域名：\033[0m')
    r_domain = remove_prefix(domain)

    thread_input = input('\033[38;5;141m请输入线程数（默认10）：\033[0m')
    threads = int(thread_input) if thread_input.isdigit() and int(thread_input) > 0 else 10

    directory_choice = input('\033[38;5;141m请选择字典类型：\n\033[38;5;45m1.默认字典\n2.自定义字典\n\033[38;5;141m请输入选项：\033[0m')

    if directory_choice == '1' or directory_choice == '':
        print('\033[38;5;141m[—————————————————————————————————— 开始扫描 ———————————————————————————————————]\033[0m')
        req(r_domain, status_include=args['status_include'], status_exclude=args['status_exclude'], show_ip=args['show_ip'], threads=threads)
    elif directory_choice == '2':
        directory = input('\033[38;5;141m请输入字典路径：')
        print('\033[38;5;141m[—————————————————————————————————— 开始扫描 ———————————————————————————————————]\\033[0m')
        req(r_domain, directory, status_include=args['status_include'], status_exclude=args['status_exclude'], show_ip=args['show_ip'], threads=threads)
    else:
        print('\033[91m[!]无效的选项，将使用默认字典\033[0m')
        print('\033[38;5;141m[—————————————————————————————————— 开始扫描 ———————————————————————————————————]\\033[0m')
        req(r_domain, status_include=args['status_include'], status_exclude=args['status_exclude'], show_ip=args['show_ip'], threads=threads)

    print('\033[38;5;141m[—————————————————————————————————— 扫描结束 ———————————————————————————————————]\033[0m')


if __name__ == "__main__":
    main()