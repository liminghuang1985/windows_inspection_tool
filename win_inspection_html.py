#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 系统一键巡检脚本 - 精简HTML报告版 (27项)
"""

import os
import platform
import socket
import datetime
import subprocess
import html as html_mod
from typing import Dict, Any, List, Tuple


def run_command(cmd: str, timeout: int = 30) -> Dict[str, Any]:
    try:
        result = subprocess.run(cmd, capture_output=True, shell=True, timeout=timeout)
        stdout, stderr = '', ''
        for enc in ('utf-8', 'gbk', 'latin-1'):
            try: stdout = result.stdout.decode(enc); break
            except: continue
        for enc in ('utf-8', 'gbk', 'latin-1'):
            try: stderr = result.stderr.decode(enc); break
            except: continue
        return {'success': result.returncode == 0, 'stdout': stdout.replace('\x00',''), 'stderr': stderr.replace('\x00','')}
    except Exception as e:
        return {'success': False, 'stdout': '', 'stderr': str(e)}


def ps(cmd: str, timeout: int = 30) -> str:
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), '_insp.ps1')
    with open(tmp, 'w', encoding='utf-8-sig') as f:
        f.write(f'[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n{cmd}')
    r = run_command(f'powershell -NoProfile -ExecutionPolicy Bypass -File "{tmp}"', timeout)
    try: os.remove(tmp)
    except: pass
    return r['stdout'].strip() if r['success'] else r['stderr'].strip()


def esc(t): return html_mod.escape(str(t))


def status_badge(text, color):
    colors = {'green':'#34a853','yellow':'#f9ab00','red':'#ea4335','blue':'#1a73e8','gray':'#9aa0a6'}
    c = colors.get(color, colors['gray'])
    return f'<span style="background:{c};color:#fff;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:600">{esc(text)}</span>'


def pct_bar(pct, width=100):
    color = '#34a853' if pct < 70 else '#f9ab00' if pct < 90 else '#ea4335'
    return f'<div style="background:#e0e0e0;border-radius:4px;height:18px;width:{width}px;display:inline-block;vertical-align:middle"><div style="background:{color};height:100%;width:{pct}%;border-radius:4px"></div></div> <b>{pct}%</b>'


# ==================== 数据采集(精简) ====================

def collect_all() -> Dict[str, Any]:
    d = {}

    # 1. 系统基本信息
    d['hostname'] = socket.gethostname()
    d['os'] = f"Windows {platform.release()} (v{platform.version()})"
    d['arch'] = f"{platform.architecture()[0]} {platform.machine()}"
    d['user'] = f"{os.environ.get('USERDOMAIN','')}\\{os.environ.get('USERNAME','')}"
    d['cpus'] = os.environ.get('NUMBER_OF_PROCESSORS','N/A')

    # 2. 运行时间
    d['boot_time'] = ps("(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString('yyyy-MM-dd HH:mm:ss')")
    try:
        boot = datetime.datetime.strptime(d['boot_time'].strip(), '%Y-%m-%d %H:%M:%S')
        delta = datetime.datetime.now() - boot
        d['uptime'] = f"{delta.days}天 {int(delta.total_seconds()%86400//3600)}时 {int(delta.total_seconds()%3600//60)}分"
    except:
        d['uptime'] = 'N/A'

    # 3. 许可证
    lic = ps('cscript //Nologo "$env:SystemRoot\\System32\\slmgr.vbs" /dli 2>&1')
    d['license_status'] = '已授权' if '已授权' in lic or 'Licensed' in lic else '未授权/未知'
    d['license_type'] = 'KMS' if 'KMS' in lic else 'MAK' if 'MAK' in lic else 'Retail' if 'RETAIL' in lic else '未知'
    # 提取过期时间
    for line in lic.split('\n'):
        if '分钟' in line and '过期' in line:
            d['license_expire'] = line.split(':')[-1].strip() if ':' in line else line.strip()
            break
    else:
        d['license_expire'] = 'N/A'

    # 4. BIOS
    d['bios'] = ps("$b=Get-CimInstance Win32_BIOS; Write-Output \"$($b.Manufacturer) | $($b.SMBIOSBIOSVersion) | $($b.ReleaseDate.ToString('yyyy-MM-dd'))\"")
    d['motherboard'] = ps("$c=Get-CimInstance Win32_ComputerSystem; Write-Output \"$($c.Manufacturer) $($c.Model)\"")
    d['secure_boot'] = ps("try{if(Confirm-SecureBootUEFI){'已启用'}else{'已禁用'}}catch{'不支持/Legacy BIOS'}")

    # 5. CPU
    cpu = ps("$c=Get-CimInstance Win32_Processor; Write-Output \"$($c.Name)|$($c.NumberOfCores)|$($c.NumberOfLogicalProcessors)|$($c.MaxClockSpeed)|$($c.LoadPercentage)\"")
    parts = cpu.split('|') if '|' in cpu else ['N/A']*5
    d['cpu_name'] = parts[0].strip() if len(parts)>0 else 'N/A'
    d['cpu_cores'] = parts[1].strip() if len(parts)>1 else 'N/A'
    d['cpu_threads'] = parts[2].strip() if len(parts)>2 else 'N/A'
    d['cpu_freq'] = parts[3].strip() if len(parts)>3 else 'N/A'
    d['cpu_load'] = parts[4].strip() if len(parts)>4 else 'N/A'

    # 6. 内存
    mem = ps('$o=Get-CimInstance Win32_OperatingSystem;$t=[math]::Round($o.TotalVisibleMemorySize/1MB,2);$f=[math]::Round($o.FreePhysicalMemory/1MB,2);Write-Output "$t|$f"')
    mp = mem.split('|') if '|' in mem else ['0','0']
    d['mem_total'] = float(mp[0]) if mp[0] else 0
    d['mem_free'] = float(mp[1]) if mp[1] else 0
    d['mem_used'] = round(d['mem_total'] - d['mem_free'], 2)
    d['mem_pct'] = round(d['mem_used']/d['mem_total']*100, 1) if d['mem_total']>0 else 0

    chips = ps("Get-CimInstance Win32_PhysicalMemory|ForEach-Object{Write-Output \"$($_.Manufacturer)|$([math]::Round($_.Capacity/1GB,0))GB|$($_.Speed)MHz|$($_.PartNumber.Trim())\"}")
    d['mem_chips'] = [c.strip() for c in chips.split('\n') if c.strip()] if chips else []

    # 7. 磁盘
    dk = ps("Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3'|ForEach-Object{$t=[math]::Round($_.Size/1GB,1);$f=[math]::Round($_.FreeSpace/1GB,1);$u=[math]::Round($t-$f,1);$p=if($t-gt 0){[math]::Round($u/$t*100,1)}else{0};Write-Output \"$($_.DeviceID)|$($_.VolumeName)|$t|$f|$u|$p\"}")
    d['disks'] = []
    for line in (dk.split('\n') if dk else []):
        p = line.strip().split('|')
        if len(p)>=6:
            d['disks'].append({'drive':p[0],'label':p[1],'total':p[2],'free':p[3],'used':p[4],'pct':p[5]})

    # 8. GPU
    d['gpu'] = ps("(Get-CimInstance Win32_VideoController).Name")
    d['gpu_driver'] = ps("(Get-CimInstance Win32_VideoController).DriverVersion")
    unsigned = ps("(Get-CimInstance Win32_PnPSignedDriver -EA SilentlyContinue|Where-Object{$_.IsSigned -eq $false}).Count")
    d['unsigned_drivers'] = unsigned if unsigned and unsigned != '0' else '0'

    # 9-11. 网络精简
    d['net_adapters'] = []
    adapters = ps("Get-NetAdapter -Physical -EA SilentlyContinue|ForEach-Object{Write-Output \"$($_.Name)|$($_.Status)|$($_.LinkSpeed)|$($_.MacAddress)\"}")
    for line in (adapters.split('\n') if adapters else []):
        p = line.strip().split('|')
        if len(p)>=4: d['net_adapters'].append({'name':p[0],'status':p[1],'speed':p[2],'mac':p[3]})

    ips = ps("Get-NetIPAddress -AddressFamily IPv4 -EA SilentlyContinue|Where-Object{$_.IPAddress -ne '127.0.0.1' -and $_.PrefixOrigin -ne 'WellKnown'}|Sort-Object InterfaceAlias|ForEach-Object{Write-Output \"$($_.InterfaceAlias)|$($_.IPAddress)|$($_.PrefixLength)|$($_.PrefixOrigin)\"}")
    d['ipv4_addrs'] = []
    for line in (ips.split('\n') if ips else []):
        p = line.strip().split('|')
        if len(p)>=4: d['ipv4_addrs'].append({'iface':p[0],'ip':p[1],'prefix':p[2],'origin':p[3]})

    d['gateway'] = ps("(Get-NetRoute -DestinationPrefix '0.0.0.0/0' -EA SilentlyContinue|Select-Object -First 1).NextHop")
    d['dns'] = ps("(Get-DnsClientServerAddress -AddressFamily IPv4 -EA SilentlyContinue|Where-Object{$_.ServerAddresses}|Select-Object -First 1).ServerAddresses -join ', '")

    conn_out = run_command('netstat -an')
    if conn_out['success']:
        lines = conn_out['stdout'].split('\n')
        d['conn_established'] = sum(1 for l in lines if 'ESTABLISHED' in l)
        d['conn_listening'] = sum(1 for l in lines if 'LISTENING' in l)
        d['conn_timewait'] = sum(1 for l in lines if 'TIME_WAIT' in l)
    else:
        d['conn_established'] = d['conn_listening'] = d['conn_timewait'] = 0

    # 10. 监听端口(精简+进程说明)
    ports = ps("Get-NetTCPConnection -State Listen -EA SilentlyContinue|Select-Object LocalAddress,LocalPort,@{N='Process';E={(Get-Process -Id $_.OwningProcess -EA SilentlyContinue).ProcessName}}|Sort-Object LocalPort|ForEach-Object{Write-Output \"$($_.LocalPort)|$($_.Process)|$($_.LocalAddress)\"}",timeout=45)
    d['listen_ports'] = []
    seen = set()
    PORT_DESC = {
        '135':'RPC端点映射','139':'NetBIOS会话','445':'SMB文件共享','902':'VMware远程控制台',
        '912':'VMware认证','3128':'HTTP代理','3389':'远程桌面(RDP)','5040':'Windows推送通知',
        '5357':'Web服务发现','6000':'X Window','7680':'传递优化(WUDO)','7897':'Clash代理',
        '8080':'HTTP代理','8443':'HTTPS','22':'SSH','80':'HTTP','443':'HTTPS',
        '53':'DNS','1433':'SQL Server','3306':'MySQL','5432':'PostgreSQL','6379':'Redis',
        '8475':'百度网盘','10000':'百度网盘云检测','33331':'Clash Verge','35600':'ToDesk远控',
        '37600':'ToDesk远控','49664':'系统服务(动态)','49665':'系统服务(动态)',
        '49666':'系统服务(动态)','49667':'系统服务(动态)','49668':'系统服务(动态)',
        '49669':'系统服务(动态)','49684':'系统服务(动态)',
    }
    for line in (ports.split('\n') if ports else []):
        p = line.strip().split('|')
        if len(p)>=2 and p[0] not in seen:
            seen.add(p[0])
            addr = p[2] if len(p)>=3 else ''
            scope = '本机' if addr in ('127.0.0.1','::1') else '全部' if addr in ('0.0.0.0','::') else addr
            desc = PORT_DESC.get(p[0], '')
            d['listen_ports'].append({'port':p[0],'process':p[1],'scope':scope,'desc':desc})

    # 12. 共享
    shares = ps("Get-SmbShare -EA SilentlyContinue|ForEach-Object{Write-Output \"$($_.Name)|$($_.Path)|$($_.Description)|$($_.CurrentUsers)\"}")
    d['shares'] = []
    for line in (shares.split('\n') if shares else []):
        p = line.strip().split('|')
        if len(p)>=4: d['shares'].append({'name':p[0],'path':p[1],'desc':p[2],'users':p[3]})

    # 13. 进程Top10
    out2 = run_command('tasklist /fo csv /nh')
    procs = []
    if out2['success']:
        for line in out2['stdout'].strip().split('\n'):
            p = line.strip().strip('"').split('","')
            if len(p)>=5:
                try: procs.append((p[0], int(p[4].replace('"','').replace(' K','').replace(',',''))))
                except: pass
    procs.sort(key=lambda x:x[1], reverse=True)
    d['proc_count'] = len(procs)
    d['proc_top10'] = procs[:10]

    svc_count = ps("(Get-Service|Where-Object{$_.Status -eq 'Running'}).Count")
    d['svc_running'] = svc_count if svc_count else 'N/A'

    # 14. 启动项(精简)
    startup = ps("""
$items=@()
'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run','HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'|ForEach-Object{
    if(Test-Path $_){(Get-ItemProperty $_ -EA SilentlyContinue).PSObject.Properties|Where-Object{$_.Name -notlike 'PS*'}|ForEach-Object{$items+="$($_.Name)|$($_.Value)"}}
}
$items -join "`n"
""")
    d['startup_items'] = []
    for line in (startup.split('\n') if startup else []):
        p = line.strip().split('|',1)
        if len(p)==2: d['startup_items'].append({'name':p[0],'cmd':p[1]})

    # 15. 计划任务(非微软)
    tasks = ps("Get-ScheduledTask -EA SilentlyContinue|Where-Object{$_.TaskPath -notlike '\\Microsoft\\*' -and $_.State -ne 'Disabled'}|ForEach-Object{$a=($_.Actions|ForEach-Object{$_.Execute}) -join ';';Write-Output \"$($_.TaskName)|$($_.State)|$a\"}", timeout=45)
    d['sched_tasks'] = []
    for line in (tasks.split('\n') if tasks else []):
        p = line.strip().split('|')
        if len(p)>=3: d['sched_tasks'].append({'name':p[0],'state':p[1],'action':p[2]})
    d['sched_total'] = ps("(Get-ScheduledTask -EA SilentlyContinue).Count")

    # 16. 更新
    updates = ps("Get-HotFix|Sort-Object InstalledOn -Desc -EA SilentlyContinue|Select-Object -First 5|ForEach-Object{Write-Output \"$($_.HotFixID)|$($_.Description)|$($_.InstalledOn.ToString('yyyy-MM-dd'))\"}")
    d['updates'] = []
    for line in (updates.split('\n') if updates else []):
        p = line.strip().split('|')
        if len(p)>=3: d['updates'].append({'id':p[0],'type':p[1],'date':p[2]})

    fw_out = ps("Get-NetFirewallProfile | ForEach-Object { Write-Output \"$($_.Name)|$($_.Enabled)\" }")
    d['fw_domain'] = d['fw_private'] = d['fw_public'] = 'OFF'
    for line in (fw_out.split('\n') if fw_out else []):
        p = line.strip().split('|')
        if len(p)>=2:
            val = 'ON' if p[1].strip() in ('True','1') else 'OFF'
            if p[0].strip() == 'Domain': d['fw_domain'] = val
            elif p[0].strip() == 'Private': d['fw_private'] = val
            elif p[0].strip() == 'Public': d['fw_public'] = val

    # 17. 密码策略
    PW_LABELS = {
        'Force user logoff how long after time expires?': '超时后强制注销',
        'Minimum password age (days)': '密码最短使用期限(天)',
        'Maximum password age (days)': '密码最长使用期限(天)',
        'Minimum password length': '密码最短长度',
        'Length of password history maintained': '密码历史记录长度',
        'Lockout threshold': '账户锁定阈值(次)',
        'Lockout duration (minutes)': '账户锁定时长(分钟)',
        'Lockout observation window (minutes)': '锁定观察窗口(分钟)',
        'Computer role': '计算机角色',
    }
    pw = run_command('net accounts')
    d['pw_policy'] = {}
    if pw['success']:
        for line in pw['stdout'].split('\n'):
            if ':' in line:
                k,v = line.split(':',1)
                k,v = k.strip(),v.strip()
                if k and v and 'command' not in k.lower() and '成功' not in k:
                    label = PW_LABELS.get(k, k)
                    d['pw_policy'][label] = v

    # 18. 审计策略
    audit = run_command('auditpol /get /category:* 2>&1')
    d['audit_available'] = audit['success']

    # 19. BitLocker
    bl = ps("try{Get-BitLockerVolume -EA Stop|ForEach-Object{Write-Output \"$($_.MountPoint)|$($_.ProtectionStatus)|$($_.VolumeStatus)\"}}catch{'unavailable'}")
    d['bitlocker'] = []
    if bl and bl != 'unavailable':
        for line in bl.split('\n'):
            p = line.strip().split('|')
            if len(p)>=3: d['bitlocker'].append({'drive':p[0],'protection':p[1],'status':p[2]})
    d['bitlocker_available'] = bl != 'unavailable' and bool(d['bitlocker'])

    # 20. RDP
    d['rdp_enabled'] = ps("if((Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server' -EA SilentlyContinue).fDenyTSConnections -eq 0){'已启用'}else{'已禁用'}")
    d['rdp_nla'] = ps("if((Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp' -EA SilentlyContinue).UserAuthentication -eq 1){'已启用'}else{'已禁用'}")
    d['rdp_port'] = ps("(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp' -EA SilentlyContinue).PortNumber")

    # 21. 用户
    users_out = ps("Get-LocalUser|ForEach-Object{Write-Output \"$($_.Name)|$($_.Enabled)|$($_.LastLogon)\"}")
    d['local_users'] = []
    for line in (users_out.split('\n') if users_out else []):
        p = line.strip().split('|')
        if len(p)>=3: d['local_users'].append({'name':p[0],'enabled':p[1],'lastlogon':p[2]})

    admins = ps("(Get-LocalGroupMember -Group 'Administrators' -EA SilentlyContinue).Name -join ', '")
    d['admin_members'] = admins if admins else 'N/A'
    d['current_user'] = ps("(quser 2>$null|Select-Object -Skip 1|ForEach-Object{$_ -replace '\\s{2,}','|'}).Trim()")

    # 22. 已安装软件(含安装时间)
    sw = ps("""
$apps=@()
'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*','HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*'|ForEach-Object{
    Get-ItemProperty $_ -EA SilentlyContinue|Where-Object{$_.DisplayName}|ForEach-Object{
        $date=$_.InstallDate
        if($date -and $date.Length -eq 8){$date=$date.Substring(0,4)+'-'+$date.Substring(4,2)+'-'+$date.Substring(6,2)}
        $apps+="$($_.DisplayName)|$($_.DisplayVersion)|$($_.Publisher)|$date"
    }
}
Write-Output "COUNT:$($apps.Count)"
$apps|Sort-Object|Get-Unique|Select-Object -First 25|ForEach-Object{Write-Output $_}
""", timeout=45)
    d['sw_count'] = 0
    d['sw_list'] = []
    for line in (sw.split('\n') if sw else []):
        line = line.strip()
        if line.startswith('COUNT:'): d['sw_count'] = int(line.replace('COUNT:',''))
        elif '|' in line:
            p = line.split('|')
            if len(p)>=4: d['sw_list'].append({'name':p[0],'ver':p[1],'pub':p[2],'date':p[3]})
            elif len(p)>=3: d['sw_list'].append({'name':p[0],'ver':p[1],'pub':p[2],'date':''})

    # 23. 时间同步
    ts = run_command('w32tm /query /source 2>&1')
    d['time_source'] = ts['stdout'].strip() if ts['success'] else '无法获取'
    ts2 = run_command('w32tm /query /status 2>&1')
    d['time_status'] = '正常' if ts2['success'] else '异常/未配置'

    # 24. 还原点
    rp = ps("try{$r=Get-ComputerRestorePoint -EA Stop;Write-Output $r.Count}catch{'unavailable'}")
    d['restore_count'] = rp if rp and rp != 'unavailable' else '不可用'

    # 25. 电源计划
    pw_out = run_command('powercfg /getactivescheme')
    d['power_plan'] = 'N/A'
    if pw_out['success']:
        for seg in pw_out['stdout'].split('('):
            if ')' in seg: d['power_plan'] = seg.split(')')[0].strip(); break

    # 26. 系统日志(聚合分析)
    # 采集最近200条错误���件，按 EventID+Source 聚合
    def collect_log_grouped(logname: str) -> list:
        raw = ps(f"""
Get-WinEvent -FilterHashtable @{{LogName='{logname}';Level=2}} -MaxEvents 200 -EA SilentlyContinue |
    ForEach-Object {{
        $msg = $_.Message.Split([char]10)[0]
        if ($msg.Length -gt 120) {{ $msg = $msg.Substring(0, 120) }}
        Write-Output "$($_.Id)|$($_.ProviderName)|$($_.TimeCreated.ToString('yyyy-MM-dd HH:mm'))|$msg"
    }}
""", timeout=45)
        # 聚合
        groups = {}
        for line in (raw.split('\n') if raw else []):
            p = line.strip().split('|', 3)
            if len(p) >= 4:
                key = f"{p[0]}|{p[1]}"
                if key not in groups:
                    groups[key] = {'id': p[0], 'source': p[1], 'count': 0,
                                   'first': p[2], 'last': p[2], 'msg': p[3]}
                groups[key]['count'] += 1
                groups[key]['last'] = p[2]  # 最新的先输出
                if not groups[key]['first'] or p[2] < groups[key]['first']:
                    groups[key]['first'] = p[2]
        result = sorted(groups.values(), key=lambda x: x['count'], reverse=True)
        return result

    d['log_sys_grouped'] = collect_log_grouped('System')
    d['log_app_grouped'] = collect_log_grouped('Application')
    d['log_sys_total'] = sum(g['count'] for g in d['log_sys_grouped'])
    d['log_app_total'] = sum(g['count'] for g in d['log_app_grouped'])

    # Defender 防病毒状态
    defender = ps("""
try {
    $s = Get-MpComputerStatus -EA Stop
    Write-Output "enabled|$($s.AntivirusEnabled)|$($s.RealTimeProtectionEnabled)|$($s.AntivirusSignatureLastUpdated.ToString('yyyy-MM-dd HH:mm'))|$($s.AntivirusSignatureVersion)|$($s.FullScanEndTime.ToString('yyyy-MM-dd HH:mm'))|$($s.QuickScanEndTime.ToString('yyyy-MM-dd HH:mm'))"
} catch { Write-Output "unavailable" }
""")
    d['defender'] = {}
    if defender and defender.startswith('enabled'):
        p = defender.split('|')
        if len(p)>=7:
            d['defender'] = {
                'antivirus': '已启用' if p[1]=='True' else '已禁用',
                'realtime': '已启用' if p[2]=='True' else '已禁用',
                'sig_date': p[3], 'sig_ver': p[4],
                'full_scan': p[5], 'quick_scan': p[6]
            }

    # 物理磁盘信息
    pdisk = ps("Get-PhysicalDisk -EA SilentlyContinue|ForEach-Object{Write-Output \"$($_.FriendlyName)|$($_.MediaType)|$([math]::Round($_.Size/1GB,0))GB|$($_.HealthStatus)|$($_.BusType)\"}")
    d['physical_disks'] = []
    for line in (pdisk.split('\n') if pdisk else []):
        p = line.strip().split('|')
        if len(p)>=5: d['physical_disks'].append({'name':p[0],'type':p[1],'size':p[2],'health':p[3],'bus':p[4]})

    # 27. 性能
    d['perf_cpu'] = d['cpu_load']
    net_stat = run_command('netstat -e')
    d['net_rx'] = d['net_tx'] = 'N/A'
    if net_stat['success']:
        for line in net_stat['stdout'].split('\n'):
            if 'Bytes' in line or '字节' in line:
                nums = [x.strip() for x in line.split() if x.strip().isdigit()]
                if len(nums)>=2:
                    d['net_rx'] = f"{int(nums[0])/1024/1024/1024:.2f} GB"
                    d['net_tx'] = f"{int(nums[1])/1024/1024/1024:.2f} GB"

    return d


# ==================== HTML 生成(精简) ====================

def generate_html(d: Dict, timestamp: str) -> str:
    cpu_pct = float(d['cpu_load']) if d['cpu_load'] and d['cpu_load'] != 'N/A' else 0
    mem_pct = d['mem_pct']
    max_disk_pct = max((float(dk['pct']) for dk in d['disks']), default=0)
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # 日志时间范围
    all_log_times = []
    for g in d.get('log_sys_grouped', []) + d.get('log_app_grouped', []):
        all_log_times.extend([g['first'], g['last']])
    all_log_times = sorted([t for t in all_log_times if t])
    log_range_start = all_log_times[0] if all_log_times else 'N/A'
    log_range_end = all_log_times[-1] if all_log_times else 'N/A'

    # 总体评估
    issues = []
    if cpu_pct > 90: issues.append(('高', 'CPU 使用率过高'))
    if mem_pct > 90: issues.append(('高', '内存使用率过高'))
    if max_disk_pct > 90: issues.append(('高', '磁盘空间不足'))
    if d['license_status'] != '已授权': issues.append(('中', '系统未激活'))
    if d['fw_domain']=='OFF' or d['fw_private']=='OFF' or d['fw_public']=='OFF': issues.append(('高', '防火墙未全部开启'))
    if d['rdp_enabled'] == '已启用': issues.append(('中', '远程桌面已开启'))
    # 检查日志中的高严重性
    for g in d.get('log_sys_grouped', []):
        if g['id'] == '55' and 'Ntfs' in g['source']: issues.append(('高', f'NTFS 文件系统损坏 ({g["count"]}次)'))
        if g['id'] == '6008': issues.append(('高', f'非正常关机 ({g["count"]}次)'))
        if g['id'] == '41': issues.append(('高', f'意外重启/蓝屏 ({g["count"]}次)'))

    risk_level = '高' if any(i[0]=='高' for i in issues) else '中' if any(i[0]=='中' for i in issues) else '低'
    risk_color = '#ea4335' if risk_level=='高' else '#f9ab00' if risk_level=='中' else '#34a853'

    h = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Windows 系统巡检报告 - {esc(d['hostname'])}</title>
<style>
@page{{margin:20mm 15mm}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Microsoft YaHei','Segoe UI',sans-serif;background:#eef0f2;color:#2c2c2c;line-height:1.7;font-size:13px}}
.ct{{max-width:1020px;margin:0 auto;background:#fff;box-shadow:0 1px 6px rgba(0,0,0,.08)}}

/* ---- 封面 ---- */
.cover{{padding:0;border-bottom:1px solid #e0e0e0}}
.cover-title{{background:#3c3c3c;padding:32px 50px 24px}}
.cover-title h1{{font-size:22px;font-weight:700;color:#fff;letter-spacing:1px;margin-bottom:2px}}
.cover-title .sub{{font-size:13px;color:#aaa;margin:0}}
.cover-meta{{padding:20px 50px 24px}}
.cover table{{width:auto;border:none;margin:0;font-size:13px;border-collapse:separate;border-spacing:0}}
.cover td{{border:none;padding:3px 0;color:#555;vertical-align:top;white-space:nowrap}}
.cover td:first-child{{font-weight:600;color:#1d1d1d;width:90px;padding-right:20px}}
.cover td:last-child{{color:#444}}
.cover .risk{{font-weight:700;color:{risk_color}}}

/* ---- 目录 ---- */
.toc{{background:#f7f8f9;padding:12px 50px;border-bottom:1px solid #e0e0e0;display:flex;flex-wrap:wrap;gap:0}}
.toc a{{color:#555;text-decoration:none;font-size:12px;padding:3px 18px 3px 0;white-space:nowrap}}
.toc a:hover{{color:#1a73e8}}

/* ---- 正文 ---- */
.body{{padding:6px 50px 30px}}

/* 一级标题 - 深灰通栏 */
h2{{font-size:14px;color:#fff;background:#3c3c3c;margin:24px -50px 14px;padding:9px 50px;letter-spacing:.5px;font-weight:600}}

/* 二级标题 */
h3{{font-size:13px;color:#1d1d1d;margin:16px 0 6px;padding-left:10px;border-left:3px solid #3c3c3c;font-weight:600}}

/* ---- 表格 ---- */
table{{width:100%;border-collapse:collapse;margin:6px 0 16px;font-size:12.5px}}
th{{background:#f2f3f5;color:#555;font-size:12px;font-weight:600;text-align:left;padding:7px 12px;border:1px solid #dfe1e5}}
td{{padding:6px 12px;border:1px solid #dfe1e5;vertical-align:top}}
tr:nth-child(even){{background:#fafafa}}
.kv td:first-child{{background:#f2f3f5;font-weight:600;color:#444;width:160px;white-space:nowrap}}

/* ---- 标签 ---- */
.badge{{display:inline-block;padding:1px 8px;border-radius:3px;font-size:11px;font-weight:600;color:#fff}}
.g{{background:#34a853}}.y{{background:#e8a000}}.r{{background:#d93025}}.b{{background:#1a73e8}}.gr{{background:#9aa0a6}}

/* 风险框 */
.risk-box{{display:inline-block;border:2px solid {risk_color};border-radius:4px;padding:5px 16px;margin:6px 0}}
.risk-box .level{{font-size:16px;font-weight:700;color:{risk_color}}}

/* 资源卡片 */
.summary-cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0}}
.sc{{background:#f7f8f9;border:1px solid #e8e8e8;border-radius:4px;padding:10px 12px;text-align:center}}
.sc .v{{font-size:16px;font-weight:700;color:#2c2c2c}}.sc .l{{font-size:11px;color:#888;margin-top:2px}}

/* ---- 目录 ---- */
.toc-section{{padding:30px 50px;border-bottom:1px solid #e0e0e0}}
.toc-section h2{{background:none;color:#1d1d1d;margin:0 0 16px;padding:0 0 8px;font-size:15px;border-bottom:2px solid #3c3c3c}}
.toc-grid{{display:grid;grid-template-columns:1fr 1fr;gap:0;counter-reset:toc}}
.toc-item{{display:flex;align-items:baseline;padding:7px 0;border-bottom:1px dashed #ddd;text-decoration:none;color:#2c2c2c;font-size:13px;transition:color .15s}}
.toc-item:hover{{color:#1a73e8}}
.toc-item .num{{display:inline-block;width:28px;font-weight:700;color:#3c3c3c;flex-shrink:0}}
.toc-item .dots{{flex:1;border-bottom:1px dotted #ccc;margin:0 8px;height:1px;align-self:center}}
.toc-item .page{{font-size:12px;color:#999;flex-shrink:0}}

/* ---- 页脚 ---- */
.footer{{background:#3c3c3c;color:#999;font-size:11px;padding:16px 50px;text-align:center;line-height:1.8}}
.footer b{{color:#ddd}}
</style></head><body><div class="ct">

<!-- ===== 封面 ===== -->
<div class="cover">
<div class="cover-title">
<h1>Windows 系统巡检报告</h1>
<div class="sub">{esc(d['hostname'])} &nbsp;/&nbsp; {esc(d['os'])}</div>
</div>
<div class="cover-meta">
<table>
<tr><td>巡检日期</td><td>{today}</td></tr>
<tr><td>日志范围</td><td>{esc(log_range_start[:10])} ~ {esc(log_range_end[:10])}</td></tr>
<tr><td>报告生成</td><td>{timestamp}</td></tr>
<tr><td>日志来源</td><td>本机实时采集 (System / Application / Security)</td></tr>
<tr><td>巡检人员</td><td>{esc(d['user'])}</td></tr>
<tr><td>综合风险</td><td class="risk">{esc(risk_level)}</td></tr>
</table>
</div>
</div>

<!-- ===== 目录 ===== -->
<div class="toc-section">
<h2>目 录</h2>
<div class="toc-grid">
<a class="toc-item" href="#s1"><span class="num">一</span>目标主机基本信息<span class="dots"></span><span class="page"></span></a>
<a class="toc-item" href="#s2"><span class="num">二</span>硬件资源状态<span class="dots"></span><span class="page"></span></a>
<a class="toc-item" href="#s3"><span class="num">三</span>网络配置与连接<span class="dots"></span><span class="page"></span></a>
<a class="toc-item" href="#s4"><span class="num">四</span>安全配置审计<span class="dots"></span><span class="page"></span></a>
<a class="toc-item" href="#s5"><span class="num">五</span>用户与权限<span class="dots"></span><span class="page"></span></a>
<a class="toc-item" href="#s6"><span class="num">六</span>进程与服务分析<span class="dots"></span><span class="page"></span></a>
<a class="toc-item" href="#s7"><span class="num">七</span>启动项与计划任务<span class="dots"></span><span class="page"></span></a>
<a class="toc-item" href="#s8"><span class="num">八</span>已安装软件<span class="dots"></span><span class="page"></span></a>
<a class="toc-item" href="#s9"><span class="num">九</span>事件日志分析<span class="dots"></span><span class="page"></span></a>
<a class="toc-item" href="#s10"><span class="num">十</span>风险评估与建议<span class="dots"></span><span class="page"></span></a>
</div>
</div>
<div class="body">
"""

    # ===== 一、基本信息 =====
    h += '<h2 id="s1"><span>一</span>、目标主机基本信息</h2>\n<table class="kv">\n'
    rows = [
        ('计算机名', d['hostname']),
        ('操作系统', d['os']),
        ('系统架构', d['arch']),
        ('域/工作组', d.get('user','').split('\\')[0] if '\\' in d.get('user','') else 'N/A'),
        ('当前用户', d['user']),
        ('主板/机型', d['motherboard']),
        ('BIOS', d['bios']),
        ('安全启动', d['secure_boot']),
        ('许可证', f"{d['license_status']} ({d['license_type']})，过期: {d['license_expire']}"),
        ('运行时间', f"{d['uptime']}（启动于 {d['boot_time']}）"),
        ('电源计划', d['power_plan']),
        ('时间同步', f"{d['time_status']}，源: {d['time_source']}"),
    ]
    for k,v in rows: h += f'<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>\n'
    h += '</table>\n'

    # ===== 二、硬件资源 =====
    h += '<h2 id="s2"><span>二</span>、硬件资源状态</h2>\n'

    # 资源概览卡片
    h += '<div class="summary-cards">\n'
    h += f'<div class="sc"><div class="v">{pct_bar(cpu_pct, 80)}</div><div class="l">CPU 使用率</div></div>\n'
    h += f'<div class="sc"><div class="v">{pct_bar(mem_pct, 80)}</div><div class="l">内存 {d["mem_used"]}GB / {d["mem_total"]}GB</div></div>\n'
    h += f'<div class="sc"><div class="v">{pct_bar(max_disk_pct, 80)}</div><div class="l">磁盘最高使用率</div></div>\n'
    h += '</div>\n'

    h += f'<h3>2.1 处理器</h3>\n<table class="kv">\n'
    h += f'<tr><td>CPU</td><td>{esc(d["cpu_name"])}</td></tr>\n'
    h += f'<tr><td>核心/线程</td><td>{esc(d["cpu_cores"])} 核 / {esc(d["cpu_threads"])} 线程 @ {esc(d["cpu_freq"])} MHz</td></tr>\n'
    h += f'<tr><td>当前负载</td><td>{esc(d["cpu_load"])}%</td></tr>\n'
    h += '</table>\n'

    h += '<h3>2.2 内存</h3>\n<table><tr><th>制造商</th><th>容量</th><th>频率</th><th>型号</th></tr>\n'
    for chip in d['mem_chips']:
        p = chip.split('|')
        if len(p)>=4: h += f'<tr><td>{esc(p[0])}</td><td>{esc(p[1])}</td><td>{esc(p[2])}</td><td>{esc(p[3])}</td></tr>\n'
    h += '</table>\n'

    h += '<h3>2.3 磁盘存储</h3>\n<table><tr><th>盘符</th><th>卷标</th><th>总容量</th><th>可用</th><th>已用</th><th>使用率</th></tr>\n'
    for dk in d['disks']:
        pct = float(dk['pct'])
        h += f'<tr><td><b>{esc(dk["drive"])}</b></td><td>{esc(dk["label"])}</td><td>{esc(dk["total"])} GB</td><td>{esc(dk["free"])} GB</td><td>{esc(dk["used"])} GB</td><td>{pct_bar(pct,80)}</td></tr>\n'
    h += '</table>\n'

    if d['physical_disks']:
        h += '<h3>2.4 物理磁盘健康</h3>\n<table><tr><th>名称</th><th>类型</th><th>容量</th><th>总线</th><th>健康状态</th></tr>\n'
        for pd in d['physical_disks']:
            hc = 'g' if pd['health']=='Healthy' else 'r'
            hl = '健康' if pd['health']=='Healthy' else pd['health']
            h += f'<tr><td>{esc(pd["name"])}</td><td>{esc(pd["type"])}</td><td>{esc(pd["size"])}</td><td>{esc(pd["bus"])}</td><td><span class="badge {hc}">{esc(hl)}</span></td></tr>\n'
        h += '</table>\n'

    h += f'<h3>2.5 GPU</h3>\n<table class="kv">\n'
    h += f'<tr><td>显卡</td><td>{esc(d["gpu"])}</td></tr>\n'
    h += f'<tr><td>驱动版本</td><td>{esc(d["gpu_driver"])}</td></tr>\n'
    h += f'<tr><td>未签名驱动</td><td>{esc(d["unsigned_drivers"])} 个</td></tr>\n'
    h += '</table>\n'

    # ===== 三、网络 =====
    h += '<h2 id="s3"><span>三</span>、网络配置与连接</h2>\n'
    h += '<h3>3.1 网络适配器</h3>\n<table><tr><th>适配器</th><th>状态</th><th>速率</th><th>MAC 地址</th></tr>\n'
    for a in d['net_adapters']:
        st = f'<span class="badge g">Up</span>' if a['status']=='Up' else f'<span class="badge gr">{esc(a["status"])}</span>'
        h += f'<tr><td>{esc(a["name"])}</td><td>{st}</td><td>{esc(a["speed"])}</td><td><code>{esc(a["mac"])}</code></td></tr>\n'
    h += '</table>\n'

    h += '<h3>3.2 IP 地址分配</h3>\n<table><tr><th>适配器</th><th>IPv4 地址</th><th>子网</th><th>来源</th></tr>\n'
    origin_map = {'Manual':'手动','Dhcp':'DHCP','WellKnown':'自动','RouterAdvertisement':'路由通告'}
    for a in d['ipv4_addrs']:
        h += f'<tr><td>{esc(a["iface"])}</td><td><b>{esc(a["ip"])}</b></td><td>/{esc(a["prefix"])}</td><td>{esc(origin_map.get(a["origin"],a["origin"]))}</td></tr>\n'
    h += '</table>\n'
    h += f'<table class="kv"><tr><td>默认网关</td><td>{esc(d["gateway"])}</td></tr>\n'
    h += f'<tr><td>DNS 服务器</td><td>{esc(d["dns"])}</td></tr>\n'
    h += f'<tr><td>网络流量</td><td>接收 {d["net_rx"]} / 发送 {d["net_tx"]}</td></tr>\n'
    h += f'<tr><td>连接统计</td><td>已建立 {d["conn_established"]} | 监听 {d["conn_listening"]} | TIME_WAIT {d["conn_timewait"]}</td></tr>\n'
    h += '</table>\n'

    h += '<h3>3.3 监听端口</h3>\n<table><tr><th>端口</th><th>进程</th><th>监听范围</th><th>说明</th></tr>\n'
    for p in d['listen_ports'][:30]:
        h += f'<tr><td><b>{esc(p["port"])}</b></td><td>{esc(p["process"])}</td><td>{esc(p["scope"])}</td><td style="color:#666">{esc(p["desc"])}</td></tr>\n'
    if len(d['listen_ports'])>30: h += f'<tr><td colspan="4" style="color:#888">... 共 {len(d["listen_ports"])} 个端口</td></tr>\n'
    h += '</table>\n'

    h += '<h3>3.4 共享文件夹</h3>\n<table><tr><th>名称</th><th>路径</th><th>说明</th><th>连接数</th></tr>\n'
    for s in d['shares']:
        h += f'<tr><td>{esc(s["name"])}</td><td>{esc(s["path"])}</td><td>{esc(s["desc"])}</td><td>{esc(s["users"])}</td></tr>\n'
    h += '</table>\n'

    # ===== 四、安全配置 =====
    h += '<h2 id="s4"><span>四</span>、安全配置审计</h2>\n'
    h += '<h3>4.1 防护状态</h3>\n<table class="kv">\n'
    fw_text = f'域={d["fw_domain"]}  专用={d["fw_private"]}  公用={d["fw_public"]}'
    fw_ok = all(v=='ON' for v in [d['fw_domain'],d['fw_private'],d['fw_public']])
    h += f'<tr><td>防火墙</td><td><span class="badge {"g" if fw_ok else "r"}">{esc(fw_text)}</span></td></tr>\n'
    h += f'<tr><td>远程桌面 (RDP)</td><td>{esc(d["rdp_enabled"])}（NLA: {esc(d["rdp_nla"])}，端口: {esc(d["rdp_port"])}）</td></tr>\n'
    bl_text = '、'.join(f'{b["drive"]} {b["protection"]} {b["status"]}' for b in d['bitlocker']) if d['bitlocker_available'] else '未启用/不可用'
    h += f'<tr><td>BitLocker 加密</td><td>{esc(bl_text)}</td></tr>\n'
    h += f'<tr><td>审计策略</td><td>{"已配置" if d["audit_available"] else "需要管理员权限查看"}</td></tr>\n'
    if d['defender']:
        dd = d['defender']
        av = f'<span class="badge {"g" if dd["antivirus"]=="已启用" else "r"}">{esc(dd["antivirus"])}</span>'
        rt = f'<span class="badge {"g" if dd["realtime"]=="已启用" else "r"}">{esc(dd["realtime"])}</span>'
        h += f'<tr><td>Defender 防病毒</td><td>{av} | 实时保护: {rt}</td></tr>\n'
        h += f'<tr><td>病毒库版本</td><td>{esc(dd["sig_ver"])}（更新于 {esc(dd["sig_date"])}）</td></tr>\n'
        h += f'<tr><td>最近扫描</td><td>快速: {esc(dd["quick_scan"])} | 完整: {esc(dd["full_scan"])}</td></tr>\n'
    h += '</table>\n'

    h += '<h3>4.2 密码策略</h3>\n<table class="kv">\n'
    for k,v in d['pw_policy'].items():
        h += f'<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>\n'
    h += '</table>\n'

    h += '<h3>4.3 系统更新</h3>\n<table><tr><th>补丁号</th><th>类型</th><th>安装日期</th></tr>\n'
    for u in d['updates']:
        h += f'<tr><td><b>{esc(u["id"])}</b></td><td>{esc(u["type"])}</td><td>{esc(u["date"])}</td></tr>\n'
    h += '</table>\n'

    h += '<h3>4.4 系统维护</h3>\n<table class="kv">\n'
    h += f'<tr><td>时间同步</td><td>{status_badge(d["time_status"],"green" if d["time_status"]=="正常" else "yellow")}  源: {esc(d["time_source"])}</td></tr>\n'
    h += f'<tr><td>系统还原点</td><td>{esc(d["restore_count"])} 个</td></tr>\n'
    h += f'<tr><td>电源计划</td><td>{esc(d["power_plan"])}</td></tr>\n'
    h += '</table>\n'

    # ===== 五、用户 =====
    h += '<h2 id="s5"><span>五</span>、用户与权限</h2>\n'
    h += '<h3>5.1 本地用户账户</h3>\n<table><tr><th>用户名</th><th>启用</th><th>最后登录</th></tr>\n'
    for u in d['local_users']:
        en = f'<span class="badge g">是</span>' if u['enabled']=='True' else f'<span class="badge gr">否</span>'
        h += f'<tr><td>{esc(u["name"])}</td><td>{en}</td><td>{esc(u["lastlogon"])}</td></tr>\n'
    h += '</table>\n'
    h += f'<h3>5.2 管理员组成员</h3>\n<p style="padding:8px 0">{esc(d["admin_members"])}</p>\n'

    # ===== 六、进程 =====
    h += '<h2 id="s6"><span>六</span>、进程与服务分析</h2>\n'
    h += f'<p>当前进程数: <b>{d["proc_count"]}</b> &nbsp;|&nbsp; 运行中服务: <b>{esc(d["svc_running"])}</b></p>\n'
    h += '<h3>6.1 内存占用 Top 10</h3>\n<table><tr><th>进程名</th><th>内存占用</th></tr>\n'
    for name, mem_kb in d['proc_top10']:
        h += f'<tr><td>{esc(name)}</td><td><b>{mem_kb//1024}</b> MB</td></tr>\n'
    h += '</table>\n'

    # ===== 七、启动项 =====
    h += '<h2 id="s7"><span>七</span>、启动项与计划任务</h2>\n'
    h += '<h3>7.1 注册表启动项</h3>\n<table><tr><th>名称</th><th>命令</th></tr>\n'
    for s in d['startup_items']:
        cmd = s['cmd'] if len(s['cmd'])<=90 else s['cmd'][:87]+'...'
        h += f'<tr><td><b>{esc(s["name"])}</b></td><td style="font-size:12px;word-break:break-all">{esc(cmd)}</td></tr>\n'
    h += '</table>\n'

    h += f'<h3>7.2 计划任务（非微软，共 {esc(d["sched_total"])} 个）</h3>\n<table><tr><th>任务名</th><th>状态</th><th>操作</th></tr>\n'
    for t in d['sched_tasks']:
        st = f'<span class="badge b">{esc(t["state"])}</span>' if t['state']=='Running' else esc(t['state'])
        act = t['action'] if len(t['action'])<=70 else t['action'][:67]+'...'
        h += f'<tr><td>{esc(t["name"])}</td><td>{st}</td><td style="font-size:12px;word-break:break-all">{esc(act)}</td></tr>\n'
    h += '</table>\n'

    # ===== 八、软件 =====
    h += f'<h2 id="s8"><span>八</span>、已安装软件（共 {d["sw_count"]} 个）</h2>\n'
    h += '<table><tr><th>名称</th><th>版本</th><th>发布者</th><th>安装日期</th></tr>\n'
    for s in d['sw_list'][:25]:
        h += f'<tr><td>{esc(s["name"])}</td><td>{esc(s["ver"])}</td><td>{esc(s["pub"])}</td><td>{esc(s.get("date",""))}</td></tr>\n'
    if d['sw_count'] > 25: h += f'<tr><td colspan="4" style="color:#888">... 共 {d["sw_count"]} 个，仅显示前 25 个</td></tr>\n'
    h += '</table>\n'

    # ===== 日志 =====
    # 常见事件说明知识库
    EVENT_KB = {
        '10001|Microsoft-Windows-DistributedCOM': ('低', 'DCOM 服务器启动失败，通常是 Windows 小组件/UWP 应用权限问题，已知问题，不影响正常使用'),
        '10016|Microsoft-Windows-DistributedCOM': ('低', 'DCOM 权限警告，Windows 内置组件权限配置不一致，可安全忽略'),
        '7023|Service Control Manager': ('中', '服务异常停止，需检查对应服务是否恢复正常运行'),
        '7031|Service Control Manager': ('中', '服务意外终止并已触发恢复操作'),
        '7034|Service Control Manager': ('中', '服务意外终止，未配置恢复操作'),
        '7030|Service Control Manager': ('低', '服务标记为交互式但系统不允许，通常不影响功能'),
        '7009|Service Control Manager': ('中', '服务启动超时，可能是启动顺序或资源不足导致'),
        '7000|Service Control Manager': ('高', '服务启动失败，需排查服务依赖和配置'),
        '1796|Microsoft-Windows-TPM-WMI': ('低', 'Secure Boot 更新失败，Legacy BIOS 模式下正常现象，不影响使用'),
        '55|Ntfs': ('高', 'NTFS 文件系统损坏，建议尽快运行 chkdsk /f 修复'),
        '153|disk': ('高', '磁盘 I/O 错误，可能是磁盘故障前兆，需密切关注'),
        '11|disk': ('高', '磁盘控制器错误，建议检查磁盘健康和连接线缆'),
        '41|Microsoft-Windows-Kernel-Power': ('高', '意外重启（蓝屏/断电），需排查电源或硬件问题'),
        '1001|Windows Error Reporting': ('低', '应用崩溃报告已生成，查看具体应用日志定位问题'),
        '1000|Application Error': ('中', '应用程序崩溃，查看故障模块定位根因'),
        '86|Microsoft-Windows-CertificateServicesClient-CertEnroll': ('低', '证书自动注册失败，通常因无法访问 Azure 证书服务，不影响正常使用'),
        '36874|Schannel': ('中', 'TLS 握手失败，可能是客户端不支持的协议版本'),
        '36888|Schannel': ('低', 'TLS 连接警告，通常由对端关闭连接触发'),
        '6008|EventLog': ('高', '上次系统关机不正常（非正常断电或蓝屏）'),
        '1014|Microsoft-Windows-DNS-Client': ('低', 'DNS 解析超时，通常是临时网络问题'),
        '4198|Microsoft-Windows-TCPIP': ('中', '检测到 IP 地址冲突'),
        '10010|Microsoft-Windows-DistributedCOM': ('低', 'DCOM 服务器未在超时时间内注册，通常是 UWP 应用延迟启动'),
    }

    def assess_severity(evt):
        """根据知识库评估严重程度，未知事件按次数判定"""
        key = f'{evt["id"]}|{evt["source"]}'
        if key in EVENT_KB:
            return EVENT_KB[key]
        # 未知事件：按次数和来源推断
        if evt['count'] >= 20: return ('中', evt['msg'])
        return ('低', evt['msg'])

    def severity_badge(level):
        colors = {'高': 'r', '中': 'y', '低': 'gr'}
        return f'<span class="badge {colors.get(level, "gr")}">{esc(level)}</span>'

    def render_log_table(grouped, log_name):
        if not grouped:
            return f'<p style="color:#888;padding:8px">无错误事件</p>\n'
        total = sum(g['count'] for g in grouped)
        # 时间范围
        all_times = []
        for g in grouped:
            all_times.extend([g['first'], g['last']])
        all_times = [t for t in all_times if t]
        time_range = f"，时间范围 {min(all_times)} ~ {max(all_times)}" if all_times else ""
        out = f'<p style="margin-bottom:10px;font-size:13px"><b>{esc(log_name)}</b>: 共 <b>{total}</b> 条错误，{len(grouped)} 类事件{time_range}</p>\n'
        out += '<table>\n'
        out += '<tr><th style="min-width:200px">问题</th><th style="width:60px">次数</th><th style="width:70px">严重程度</th><th>时间范围</th><th>说明</th></tr>\n'
        for g in grouped:
            sev, desc = assess_severity(g)
            evt_label = f'{esc(g["source"])} (Event {esc(g["id"])})'
            time_col = f'{esc(g["last"])}' if g['first'] == g['last'] else f'{esc(g["first"])} ~ {esc(g["last"])}'
            out += f'<tr><td style="font-size:12px">{evt_label}</td>'
            out += f'<td style="text-align:center"><b>{g["count"]}</b></td>'
            out += f'<td style="text-align:center">{severity_badge(sev)}</td>'
            out += f'<td style="font-size:12px;white-space:nowrap">{time_col}</td>'
            out += f'<td style="font-size:12px">{esc(desc)}</td></tr>\n'
        out += '</table>\n'
        return out

    # ===== 九、事件日志 =====
    h += '<h2 id="s9"><span>九</span>、事件日志安全分析</h2>\n'
    h += render_log_table(d['log_sys_grouped'], '系统日志')
    h += render_log_table(d['log_app_grouped'], '应用日志')

    # ===== 十、风险评估 =====
    h += '<h2 id="s10"><span>十</span>、风险评估与建议</h2>\n'
    h += f'<div class="risk-box"><span style="font-size:13px;color:#555">综合风险等级：</span><span class="level">{esc(risk_level)}</span></div>\n'

    if issues:
        h += '<h3>10.1 发现的问题</h3>\n<table><tr><th>序号</th><th>风险等级</th><th>问题描述</th></tr>\n'
        for i, (lv, desc) in enumerate(issues, 1):
            lv_cls = 'r' if lv=='高' else 'y' if lv=='中' else 'gr'
            h += f'<tr><td>{i}</td><td><span class="badge {lv_cls}">{esc(lv)}</span></td><td>{esc(desc)}</td></tr>\n'
        h += '</table>\n'

    h += '<h3>10.2 安全建议</h3>\n'
    # 自动生成建议
    suggestions = []
    if any('NTFS' in i[1] for i in issues):
        suggestions.append(('高', '立即对损坏的磁盘卷运行 <code>chkdsk /f</code> 进行修复，并备份重要数据'))
    if any('非正常关机' in i[1] for i in issues):
        suggestions.append(('高', '排查非正常关机原因：检查电源稳定性、硬件故障、蓝屏转储文件 (C:\\Windows\\MEMORY.DMP)'))
    if any('防火墙' in i[1] for i in issues):
        suggestions.append(('高', '启用所有配置文件的 Windows 防火墙，命令: <code>netsh advfirewall set allprofiles state on</code>'))
    if any('远程桌面' in i[1] for i in issues):
        suggestions.append(('中', '如非必要建议关闭 RDP；如需保留，确保启用 NLA 且使用强密码'))
    if d.get('pw_policy',{}).get('密码最短长度','0') == '0':
        suggestions.append(('中', '密码最短长度为 0，建议设置为至少 8 位: <code>net accounts /minpwlen:8</code>'))
    if d.get('pw_policy',{}).get('密码历史记录长度','') in ('None','无'):
        suggestions.append(('低', '未启用密码历史记录，建议设置: <code>net accounts /uniquepw:5</code>'))
    if d.get('secure_boot','') and ('不支持' in d['secure_boot'] or 'Legacy' in d['secure_boot']):
        suggestions.append(('低', '未启用安全启动 (Secure Boot)，建议在 BIOS 中启用 UEFI + Secure Boot'))
    if d.get('time_status','') != '正常':
        suggestions.append(('低', '时间同步异常，建议配置 NTP: <code>w32tm /config /manualpeerlist:ntp.aliyun.com /syncfromflags:manual /update</code>'))
    if d.get('restore_count','') in ('不可用','0'):
        suggestions.append(('低', '无可用系统还原点，建议启用系统保护并创建还原点'))
    if not suggestions:
        suggestions.append(('', '当前未发现需要立即处理的安全问题，系统状态良好'))

    h += '<table><tr><th>优先级</th><th>建议措施</th></tr>\n'
    for lv, desc in suggestions:
        if lv:
            lv_cls = 'r' if lv=='高' else 'y' if lv=='中' else 'gr'
            h += f'<tr><td><span class="badge {lv_cls}">{esc(lv)}</span></td><td>{desc}</td></tr>\n'
        else:
            h += f'<tr><td></td><td>{desc}</td></tr>\n'
    h += '</table>\n'

    h += f"""
</div><!-- end .body -->
<div class="footer">
<b>Windows 系统巡检报告</b><br>
巡检日期: {today} &nbsp;&bull;&nbsp; 主机: {esc(d['hostname'])} &nbsp;&bull;&nbsp; 生成时间: {timestamp}<br>
本报告由自动化巡检工具生成，仅供内部参考
</div>
</div></body></html>"""
    return h


def main():
    print("=" * 50)
    print("  Windows 系统巡检 (27项精简版)")
    print("=" * 50)
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"开始巡检: {ts}\n")

    if os.name != 'nt':
        print("错误: 仅适用于Windows"); return

    print("正在采集数据...")
    data = collect_all()

    print("生成HTML报告...")
    html_content = generate_html(data, ts)
    fname = f"System_Inspection_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n巡检报告: {os.path.abspath(fname)}")
    print(f"完成: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()
