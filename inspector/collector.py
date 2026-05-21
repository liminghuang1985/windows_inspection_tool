#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 系统巡检数据采集模块
从 win_inspection_html.py 提取的采集逻辑
"""

import os
import platform
import socket
import datetime
import subprocess
import html as html_mod
from typing import Dict, Any, List


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


# ==================== 数据采集 ====================

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

    # 9-11. 网络
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

    # 10. 监听端口
    ports = ps("Get-NetTCPConnection -State Listen -EA SilentlyContinue|Select-Object LocalAddress,LocalPort,@{N='Process';E={(Get-Process -Id $_.OwningProcess -EA SilentlyContinue).ProcessName}}|Sort-Object LocalPort|ForEach-Object{Write-Output \"$($_.LocalPort)|$($_.Process)|$($_.LocalAddress)\"}",timeout=45)
    d['listen_ports'] = []
    seen = set()
    PORT_DESC = {
        '135':'RPC','139':'NetBIOS','445':'SMB','912':'VMware',
        '3389':'RDP','5040':'通知','5357':'发现','6000':'X11',
        '8080':'HTTP代理','8443':'HTTPS','22':'SSH','80':'HTTP','443':'HTTPS',
        '53':'DNS','1433':'SQL Server','3306':'MySQL','5432':'PostgreSQL','6379':'Redis',
        '35600':'ToDesk','33331':'Clash','10000':'百度网盘',
        '49664':'系统服务','49665':'系统服务','49666':'系统服务','49667':'系统服务',
        '49668':'系统服务','49669':'系统服务','49684':'系统服务',
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

    # 14. 启动项
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

    # 15. 计划任务
    tasks = ps("Get-ScheduledTask -EA SilentlyContinue|Where-Object{$_.TaskPath -notlike '\\Microsoft\\*' -and $_.State -ne 'Disabled'}|ForEach-Object{$a=($_.Actions|ForEach-Object{$_.Execute}) -join ';';Write-Output \"$($_.TaskName)|$($_.State)|$a\"}", timeout=45)
    d['sched_tasks'] = []
    for line in (tasks.split('\n') if tasks else []):
        p = line.strip().split('|')
        if len(p)>=3: d['sched_tasks'].append({'name':p[0],'state':p[1],'action':p[2]})
    d['sched_total'] = ps("(Get-ScheduledTask -EA SilentlyContinue).Count")

    # 16. 补丁
    updates = ps("Get-HotFix|Sort-Object InstalledOn -Desc -EA SilentlyContinue|Select-Object -First 10|ForEach-Object{Write-Output \"$($_.HotFixID)|$($_.Description)|$($_.InstalledOn.ToString('yyyy-MM-dd'))\"}")
    d['updates'] = []
    for line in (updates.split('\n') if updates else []):
        p = line.strip().split('|')
        if len(p)>=3: d['updates'].append({'id':p[0],'type':p[1],'date':p[2]})

    # 防火墙
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
        'Force user logoff how long after time expires?': '超时强制注销',
        'Minimum password age (days)': '密码最短期限(天)',
        'Maximum password age (days)': '密码最长期限(天)',
        'Minimum password length': '密码最短长度',
        'Length of password history maintained': '密码历史长度',
        'Lockout threshold': '账户锁定阈值',
        'Lockout duration (minutes)': '锁定时长(分)',
        'Lockout observation window (minutes)': '锁定观察窗口(分)',
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
    d['audit_raw'] = audit['stdout'][:3000] if audit['success'] else audit['stderr']

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

    # 22. 已安装软件
    sw = ps("""
$apps=@()
'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*','HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*'|ForEach-Object{
    Get-ItemProperty $_ -EA SilentlyContinue|Where-Object{$_.DisplayName}|ForEach-Object{
        $date=$_.InstallDate
        if($date -and $date.Length -eq 8){$date=$date.Substring(0,4)+'-'+$date.Substring(4,2)+'-'+$date.Substring(6,2)}
        $apps+="$($_.DisplayName)|$($_.DisplayVersion)|$($_.Publisher)|$date"
    }
}
$apps -join "`n"
""")
    d['software'] = []
    for line in (sw.split('\n') if sw else []):
        p = line.strip().split('|',3)
        if len(p)>=1 and p[0].strip():
            d['software'].append({
                'name': p[0].strip(),
                'version': p[1].strip() if len(p)>1 else '',
                'publisher': p[2].strip() if len(p)>2 else '',
                'install_date': p[3].strip() if len(p)>3 else '',
            })

    # 23. Defender
    d['defender'] = ps("Get-MpComputerStatus -EA SilentlyContinue | ForEach-Object { Write-Output \"$($_.AntivirusEnabled)|$($_.RealTimeProtectionEnabled)|$($_.AntivirusSignatureLastUpdated)|$($_.AntivirusSignatureVersion)\"}")
    d['defender_on'] = 'N/A'
    if d['defender'] and '|' in d['defender']:
        parts = d['defender'].split('|')
        d['defender_on'] = '已启用' if parts[0].strip() == 'True' else '未启用'
        d['defender_rtp'] = '已启用' if parts[1].strip() == 'True' else '未启用'
        d['defender_updated'] = parts[2].strip() if len(parts)>2 else 'N/A'
        d['defender_version'] = parts[3].strip() if len(parts)>3 else 'N/A'

    # 24. 事件日志
    evt = ps("""
$start = (Get-Date).AddDays(-7)
$sys = Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=$start} -MaxEvents 50 -EA SilentlyContinue | ForEach-Object { Write-Output "$($_.TimeGenerated.ToString('yyyy-MM-dd HH:mm:ss'))|$($_.LevelDisplayName)|$($_.Id)|$($_.Message.Substring(0,[Math]::Min(100,$_.Message.Length)))" }
$app = Get-WinEvent -FilterHashtable @{LogName='Application'; StartTime=$start} -MaxEvents 50 -EA SilentlyContinue | ForEach-Object { Write-Output "$($_.TimeGenerated.ToString('yyyy-MM-dd HH:mm:ss'))|$($_.LevelDisplayName)|$($_.Id)|$($_.Message.Substring(0,[Math]::Min(100,$_.Message.Length)))" }
@("$sys","$app") -join "`n"
""", timeout=60)
    d['events'] = []
    EVT_KB = {
        6008:'非正常关机',6005:'事件日志启动',41:'严重宕机',44725:'密码策略变更',
        7045:'新服务安装',4657:'注册表变更',4688:'新进程',4689:'进程退出',
        4720:'账户创建',4722:'账户启用',4723:'密码变更',4726:'账户删除',
        4732:'加入管理员组',4733:'移出管理员组',4740:'账户锁定',
    }
    for line in (evt.split('\n') if evt else []):
        p = line.strip().split('|',3)
        if len(p)>=3 and p[2].strip().isdigit():
            eid = int(p[2])
            d['events'].append({
                'time': p[0].strip(),
                'level': p[1].strip(),
                'id': eid,
                'msg': p[3].strip() if len(p)>3 else '',
                'kb': EVT_KB.get(eid,''),
            })

    # 25. 时间同步
    d['time_sync'] = ps("(Get-Service W32Time).Status")
    d['time_source'] = ps("w32tm /query /source")

    # 26. 风险评估
    risks = []
    if d['mem_pct'] and float(d['mem_pct']) > 85: risks.append(('高','内存使用率 '+str(d['mem_pct'])+'%'))
    if d['rdp_enabled'] == '已启用': risks.append(('中','RDP已启用'))
    if d['unsigned_drivers'] != '0': risks.append(('高','未签名驱动: '+str(d['unsigned_drivers'])+'个'))
    if d['fw_public'] == 'OFF': risks.append(('中','公用网络防火墙关闭'))
    if d['license_status'] == '未授权/未知': risks.append(('高','许可证未授权'))
    if not d['defender_on'] or d['defender_on'] == '未启用': risks.append(('高','Defender未启用'))
    d['risks'] = risks

    # 巡检元信息
    d['_meta'] = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'hostname': d['hostname'],
        'version': '1.0.0',
    }

    return d
