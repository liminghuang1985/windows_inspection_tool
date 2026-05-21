#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML报告生成器
"""

import datetime
import html as html_mod
from typing import Dict, Any

def esc(t): return html_mod.escape(str(t))

def status_badge(text, color):
    colors = {'green':'#34a853','yellow':'#f9ab00','red':'#ea4335','blue':'#1a73e8','gray':'#9aa0a6'}
    c = colors.get(color, colors['gray'])
    return f'<span style="background:{c};color:#fff;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:600">{esc(text)}</span>'

def pct_bar(pct, width=120):
    color = '#34a853' if float(pct or 0) < 70 else '#f9ab00' if float(pct or 0) < 90 else '#ea4335'
    return f'<div style="background:#2d2d2d;border-radius:4px;height:16px;width:{width}px;display:inline-block;vertical-align:middle"><div style="background:{color};height:100%;width:{pct}%;border-radius:4px"></div></div> <b>{pct}%</b>'

def risk_color(level):
    return {'高':'#ea4335','中':'#f9ab00','低':'#34a853'}.get(level,'#9aa0a6')


def generate_html(data: Dict[str, Any]) -> str:
    hostname = data.get('hostname','N/A')
    os_name = data.get('os','N/A')
    meta = data.get('_meta',{})

    risk_level = '低'
    if any(r[0]=='高' for r in data.get('risks',[])):
        risk_level = '高'
    elif any(r[0]=='中' for r in data.get('risks',[])):
        risk_level = '中'

    risk_color_map = {'高':'#ea4335','中':'#f9ab00','低':'#34a853'}

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Windows 系统巡检报告 - {hostname}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:"Segoe UI","Microsoft YaHei",sans-serif;background:#1a1a2e;color:#e0e0e0}}
.cover{{background:linear-gradient(135deg,#1a1a2e,#16213e);padding:60px 40px;text-align:center;min-height:100vh;display:flex;flex-direction:column;justify-content:center}}
.cover h1{{font-size:2.4em;color:#fff;margin-bottom:10px}}
.cover .meta{{color:#aaa;font-size:1.1em;margin:10px 0}}
.badge{{display:inline-block;padding:8px 24px;border-radius:20px;font-size:1.1em;font-weight:700;color:#fff;margin-top:20px}}
.toc{{max-width:900px;margin:40px auto}}
.toc-item{{display:flex;align-items:center;padding:12px 20px;background:#1e1e3f;margin:6px 0;border-radius:8px;color:#aaa;text-decoration:none;transition:.2s}}
.toc-item:hover{{background:#2a2a5a;color:#fff}}
.toc-item span{{margin-left:auto;color:#888;font-size:0.9em}}
.section{{max-width:900px;margin:40px auto;padding:0 20px}}
.section h2{{color:#fff;border-left:4px solid #4a9eff;padding-left:12px;margin:30px 0 15px;font-size:1.4em}}
table{{width:100%;border-collapse:collapse;background:#1e1e3f;border-radius:8px;overflow:hidden}}
th{{background:#2a2a5a;padding:12px 16px;text-align:left;color:#4a9eff;font-size:.9em}}
td{{padding:10px 16px;border-bottom:1px solid #2d2d5a;font-size:.9em;color:#ccc}}
tr:last-child td{{border-bottom:none}}
tr:hover td{{background:#252550}}
.section-nav{{position:fixed;top:20px;right:20px;background:#1e1e3f;padding:15px 20px;border-radius:10px;font-size:.85em;max-height:80vh;overflow-y:auto}}
.section-nav a{{display:block;color:#888;padding:4px 0;text-decoration:none}}
.section-nav a:hover{{color:#4a9eff}}
</style>
</head>
<body>
<div class="cover">
  <h1>🖥️ Windows 系统巡检报告</h1>
  <div class="meta">{hostname} &nbsp;|&nbsp; {os_name}</div>
  <div class="meta">巡检日期: {meta.get('timestamp','N/A')}</div>
  <div class="meta">巡检人员: {data.get('user','N/A')}</div>
  <div class="badge" style="background:{risk_color_map[risk_level]};color:#fff">
    综合风险: {risk_level}
  </div>
</div>

<div class="section-nav">
  <div style="color:#4a9eff;font-weight:bold;margin-bottom:10px">目录</div>
  <a href="#s1">一、基本信息</a>
  <a href="#s2">二、硬件资源</a>
  <a href="#s3">三、网络配置</a>
  <a href="#s4">四、安全审计</a>
  <a href="#s5">五、用户与权限</a>
  <a href="#s6">六、进程与服务</a>
  <a href="#s7">七、启动与任务</a>
  <a href="#s8">八、已安装软件</a>
  <a href="#s9">九、事件日志</a>
  <a href="#s10">十、风险评估</a>
</div>

<div class="section">
<h2 id="s1">一、基本信息</h2>
<table>
<tr><th style="width:30%">项目</th><th>值</th></tr>
<tr><td>计算机名</td><td>{esc(data.get('hostname','N/A'))}</td></tr>
<tr><td>操作系统</td><td>{esc(data.get('os','N/A'))}</td></tr>
<tr><td>架构</td><td>{esc(data.get('arch','N/A'))}</td></tr>
<tr><td>许可证状态</td><td>{esc(data.get('license_status','N/A'))} {status_badge(data.get('license_type','N/A'),'green')}</td></tr>
<tr><td>运行时间</td><td>{esc(data.get('uptime','N/A'))}</td></tr>
<tr><td>BIOS</td><td>{esc(data.get('bios','N/A'))}</td></tr>
<tr><td>主板</td><td>{esc(data.get('motherboard','N/A'))}</td></tr>
<tr><td>安全启动</td><td>{esc(data.get('secure_boot','N/A'))}</td></tr>
<tr><td>CPU</td><td>{esc(data.get('cpu_name','N/A'))}</td></tr>
<tr><td>核心/线程</td><td>{esc(data.get('cpu_cores','N/A'))} 核 / {esc(data.get('cpu_threads','N/A'))} 线程</td></tr>
</table>

<h2 id="s2">二、硬件资源</h2>
<table>
<tr><th>项目</th><th>值</th></tr>
<tr><td>内存总量</td><td>{data.get('mem_total',0):.1f} GB</td></tr>
<tr><td>内存使用</td><td>{data.get('mem_used',0):.1f} GB ({pct_bar(data.get('mem_pct',0))})</td></tr>
<tr><td>CPU负载</td><td>{pct_bar(data.get('cpu_load','0'))}</td></tr>
</table>
<h3 style="color:#aaa;margin:10px 0 5px">磁盘</h3>
<table>
<tr><th>盘符</th><th>卷标</th><th>总量(GB)</th><th>可用(GB)</th><th>使用率</th></tr>
'''
    for disk in data.get('disks',[]):
        html += f'<tr><td>{esc(disk.get("drive","N/A"))}</td><td>{esc(disk.get("label","N/A"))}</td><td>{esc(disk.get("total","N/A"))}</td><td>{esc(disk.get("free","N/A"))}</td><td>{pct_bar(disk.get("pct","0"))}</td></tr>\n'

    html += f'''</table>
<h3 style="color:#aaa;margin:10px 0 5px">GPU</h3>
<table>
<tr><th style="width:30%">项目</th><th>值</th></tr>
<tr><td>显卡</td><td>{esc(data.get('gpu','N/A'))}</td></tr>
<tr><td>驱动版本</td><td>{esc(data.get('gpu_driver','N/A'))}</td></tr>
<tr><td>未签名驱动</td><td>{status_badge(data.get('unsigned_drivers','N/A'),"red" if data.get('unsigned_drivers','0')!='0' else 'green')}</td></tr>
</table>

<h2 id="s3">三、网络配置</h2>
<table>
<tr><th>适配器</th><th>状态</th><th>速率</th><th>MAC</th></tr>
'''
    for adapter in data.get('net_adapters',[]):
        status_color = 'green' if adapter.get('status')=='Up' else 'red'
        html += f'<tr><td>{esc(adapter.get("name","N/A"))}</td><td>{status_badge(adapter.get("status","N/A"),status_color)}</td><td>{esc(adapter.get("speed","N/A"))}</td><td>{esc(adapter.get("mac","N/A"))}</td></tr>\n'

    html += f'''</table>
<h3 style="color:#aaa;margin:10px 0 5px">IP配置</h3>
<table>
<tr><th>接口</th><th>IP地址</th><th>前缀</th><th>来源</th></tr>
'''
    for ip in data.get('ipv4_addrs',[]):
        html += f'<tr><td>{esc(ip.get("iface","N/A"))}</td><td>{esc(ip.get("ip","N/A"))}</td><td>{esc(ip.get("prefix","N/A"))}</td><td>{esc(ip.get("origin","N/A"))}</td></tr>\n'

    html += f'''</table>
<h3 style="color:#aaa;margin:10px 0 5px">网络连接</h3>
<table>
<tr><th>项目</th><th>值</th></tr>
<tr><td>默认网关</td><td>{esc(data.get('gateway','N/A'))}</td></tr>
<tr><td>DNS服务器</td><td>{esc(data.get('dns','N/A'))}</td></tr>
<tr><td>已建立连接</td><td>{data.get('conn_established',0)}</td></tr>
<tr><td>监听端口</td><td>{data.get('conn_listening',0)}</td></tr>
<tr><td>TIME_WAIT</td><td>{data.get('conn_timewait',0)}</td></tr>
</table>
<h3 style="color:#aaa;margin:10px 0 5px">监听端口</h3>
<table>
<tr><th>端口</th><th>进程</th><th>范围</th><th>说明</th></tr>
'''
    for port in data.get('listen_ports',[])[:30]:
        html += f'<tr><td>{esc(port.get("port","N/A"))}</td><td>{esc(port.get("process","N/A"))}</td><td>{esc(port.get("scope","N/A"))}</td><td>{esc(port.get("desc","N/A"))}</td></tr>\n'

    if data.get('shares'):
        html += f'''</table>
<h3 style="color:#aaa;margin:10px 0 5px">共享文件夹</h3>
<table>
<tr><th>名称</th><th>路径</th><th>说明</th><th>当前用户</th></tr>
'''
        for share in data.get('shares',[]):
            html += f'<tr><td>{esc(share.get("name","N/A"))}</td><td>{esc(share.get("path","N/A"))}</td><td>{esc(share.get("desc","N/A"))}</td><td>{esc(share.get("users","N/A"))}</td></tr>\n'

    html += f'''</table>

<h2 id="s4">四、安全审计</h2>
<table>
<tr><th>项目</th><th>状态</th></tr>
<tr><td>防火墙(域)</td><td>{status_badge(data.get('fw_domain','OFF'),'green' if data.get('fw_domain')=='ON' else 'red')}</td></tr>
<tr><td>防火墙(专用)</td><td>{status_badge(data.get('fw_private','OFF'),'green' if data.get('fw_private')=='ON' else 'red')}</td></tr>
<tr><td>防火墙(公用)</td><td>{status_badge(data.get('fw_public','OFF'),'green' if data.get('fw_public')=='ON' else 'red')}</td></tr>
<tr><td>RDP远程桌面</td><td>{status_badge(data.get('rdp_enabled','N/A'),'yellow' if data.get('rdp_enabled')=='已启用' else 'green')}</td></tr>
<tr><td>RDP NLA</td><td>{esc(data.get('rdp_nla','N/A'))}</td></tr>
<tr><td>RDP端口</td><td>{esc(data.get('rdp_port','3389'))}</td></tr>
<tr><td>BitLocker</td><td>{status_badge("已启用" if data.get('bitlocker_available') else "未启用/不可用",'green' if data.get('bitlocker_available') else 'gray')}</td></tr>
<tr><td>Windows Defender</td><td>{status_badge(data.get('defender_on','N/A'),'green' if data.get('defender_on')=='已启用' else 'red')}</td></tr>
<tr><td>实时保护</td><td>{esc(data.get('defender_rtp','N/A'))}</td></tr>
<tr><td>时间同步</td><td>{esc(data.get('time_sync','N/A'))} | 源: {esc(data.get('time_source','N/A'))}</td></tr>
</table>
<h3 style="color:#aaa;margin:10px 0 5px">密码策略</h3>
<table>
<tr><th>策略</th><th>值</th></tr>
'''
    for k,v in data.get('pw_policy',{}).items():
        html += f'<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>\n'

    html += f'''</table>
<h3 style="color:#aaa;margin:10px 0 5px">最近补丁 (Top10)</h3>
<table>
<tr><th>KB编号</th><th>类型</th><th>安装日期</th></tr>
'''
    for u in data.get('updates',[]):
        html += f'<tr><td>{esc(u.get("id","N/A"))}</td><td>{esc(u.get("type","N/A"))}</td><td>{esc(u.get("date","N/A"))}</td></tr>\n'

    html += f'''</table>

<h2 id="s5">五、用户与权限</h2>
<table>
<tr><th>用户名</th><th>是否启用</th><th>最后登录</th></tr>
'''
    for u in data.get('local_users',[]):
        en_color = 'green' if u.get('enabled','N/A') == 'True' else 'red'
        html += f'<tr><td>{esc(u.get("name","N/A"))}</td><td>{status_badge("已启用" if u.get("enabled")=="True" else "已禁用",en_color)}</td><td>{esc(u.get("lastlogon","N/A"))}</td></tr>\n'

    html += f'''</table>
<h3 style="color:#aaa;margin:10px 0 5px">管理员组成员</h3>
<p style="color:#ccc;font-size:.9em">{esc(data.get('admin_members','N/A'))}</p>

<h2 id="s6">六、进程与服务</h2>
<table>
<tr><th>项目</th><th>值</th></tr>
<tr><td>进程总数</td><td>{data.get('proc_count','N/A')}</td></tr>
<tr><td>运行服务数</td><td>{data.get('svc_running','N/A')}</td></tr>
</table>
<h3 style="color:#aaa;margin:10px 0 5px">内存 Top10 进程</h3>
<table>
<tr><th>进程名</th><th>内存(KB)</th></tr>
'''
    for name, mem in data.get('proc_top10',[]):
        html += f'<tr><td>{esc(name)}</td><td>{mem:,}</td></tr>\n'

    html += f'''</table>

<h2 id="s7">七、启动项与计划任务</h2>
<h3 style="color:#aaa;margin:10px 0 5px">注册表启动项</h3>
<table>
<tr><th>名称</th><th>命令</th></tr>
'''
    for item in data.get('startup_items',[]):
        html += f'<tr><td>{esc(item.get("name","N/A"))}</td><td style="max-width:400px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{esc(item.get("cmd","N/A"))}</td></tr>\n'

    html += f'''</table>
<h3 style="color:#aaa;margin:10px 0 5px">非微软计划任务 (共 {esc(data.get('sched_total','N/A'))} 个)</h3>
<table>
<tr><th>任务名</th><th>状态</th><th>执行操作</th></tr>
'''
    for t in data.get('sched_tasks',[]):
        html += f'<tr><td>{esc(t.get("name","N/A"))}</td><td>{esc(t.get("state","N/A"))}</td><td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{esc(t.get("action","N/A"))}</td></tr>\n'

    html += f'''</table>

<h2 id="s8">八、已安装软件</h2>
<table>
<tr><th>软件名称</th><th>版本</th><th>发布者</th><th>安装日期</th></tr>
'''
    for s in data.get('software',[])[:50]:
        html += f'<tr><td>{esc(s.get("name","N/A"))}</td><td>{esc(s.get("version","N/A"))}</td><td>{esc(s.get("publisher","N/A"))}</td><td>{esc(s.get("install_date","N/A"))}</td></tr>\n'

    if len(data.get('software',[])) > 50:
        html += f'<tr><td colspan="4" style="color:#888;text-align:center">... 共 {len(data.get("software",[]))} 个软件，显示前50条</td></tr>\n'

    html += f'''</table>

<h2 id="s9">九、事件日志 (近7天)</h2>
<table>
<tr><th>时间</th><th>级别</th><th>ID</th><th>事件</th><th>说明</th></tr>
'''
    for e in data.get('events',[])[:50]:
        level_color = {'错误':'red','警告':'yellow','信息':'blue','未知':'gray'}.get(e.get('level',''),'gray')
        html += f'<tr><td>{esc(e.get("time","N/A"))}</td><td>{status_badge(e.get("level","未知"),level_color)}</td><td>{e.get("id","N/A")}</td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{esc(e.get("msg","N/A"))}</td><td>{esc(e.get("kb","N/A"))}</td></tr>\n'

    html += f'''</table>

<h2 id="s10">十、风险评估</h2>
<table>
<tr><th>风险等级</th><th>问题</th></tr>
'''
    for level, desc in data.get('risks',[]):
        html += f'<tr><td><b style="color:{risk_color(level)}">{status_badge(level,level)}</b></td><td>{esc(desc)}</td></tr>\n'

    if not data.get('risks'):
        html += f'<tr><td colspan="2" style="color:#34a853;text-align:center">{status_badge("未发现高风险项","green")}</td></tr>\n'

    html += f'''</table>
<div style="text-align:center;color:#555;font-size:.8em;padding:40px 0">
  <p>报告生成时间: {meta.get('timestamp','N/A')} | Windows 系统巡检工具 v{meta.get('version','1.0.0')}</p>
</div>
</div>
</body>
</html>'''

    return html


def save_html_report(data: Dict[str, Any], output_dir: str = None) -> str:
    """保存HTML报告到文件"""
    import os, datetime
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'System_Inspection_Report_{ts}.html'
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(generate_html(data))
    return filepath
