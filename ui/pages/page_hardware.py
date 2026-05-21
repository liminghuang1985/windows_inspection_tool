#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件与网络 - Page 2
"""

import flet as ft

CARD_BG = "#1B2838"
ACCENT  = "#4a9eff"
GREEN   = "#34a853"
RED     = "#ea4335"
GRAY    = "#888888"


def build_page(data: dict) -> list:
    cards = []

    # CPU详情
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('💻 CPU 信息', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF"),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('型号', data.get('cpu_name', 'N/A')),
            _info_row('核心/线程', f"{data.get('cpu_cores','N/A')} 核 / {data.get('cpu_threads','N/A')} 线程"),
            _info_row('频率', f"{data.get('cpu_freq','N/A')} MHz"),
            _info_row('当前负载', f"{data.get('cpu_load','N/A')}%"),
            _info_row('BIOS', data.get('bios', 'N/A')),
            _info_row('主板', data.get('motherboard', 'N/A')),
            _info_row('安全启动', data.get('secure_boot', 'N/A')),
        ], spacing=0),
    ))

    # GPU详情
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('🎮 GPU 信息', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF"),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('显卡', data.get('gpu', 'N/A')),
            _info_row('驱动版本', data.get('gpu_driver', 'N/A')),
            _info_row('未签名驱动', f"{data.get('unsigned_drivers','0')} 个" if data.get('unsigned_drivers','0') != '0' else '无'),
        ], spacing=0),
    ))

    # 网络适配器
    adapter_items = []
    for a in data.get('net_adapters', []):
        status_color = GREEN if a.get('status') == 'Up' else RED
        adapter_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor="#1B2838", margin=ft.Margin.only(bottom=6),
            content=ft.Column([
                ft.Row([
                    ft.Text(a.get('name',''), size=13, weight=ft.FontWeight.W_600, color="#FFFFFF"),
                    ft.Container(expand=True),
                    ft.Container(
                        padding=ft.Padding.only(left=8, right=8, top=2, bottom=2),
                        border_radius=6, bgcolor=status_color,
                        content=ft.Text(a.get('status','N/A'), size=10, color="#FFFFFF"),
                    ),
                ]),
                ft.Text(f"速率: {a.get('speed','N/A')}  |  MAC: {a.get('mac','N/A')}", size=10, color=GRAY),
            ], spacing=4),
        ))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text('🌐 网络适配器', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF")] + adapter_items,
            spacing=4,
        ),
    ))

    # IP配置
    ip_items = []
    for ip in data.get('ipv4_addrs', []):
        ip_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor="#1B2838", margin=ft.Margin.only(bottom=4),
            content=ft.Row([
                ft.Text(ip.get('iface',''), size=12, weight=ft.FontWeight.W_600, color=ACCENT),
                ft.Text(ip.get('ip','N/A'), size=12, color="#FFFFFF"),
                ft.Container(expand=True),
                ft.Text(f"/{ip.get('prefix','N/A')}  {ip.get('origin','')}", size=10, color=GRAY),
            ], spacing=12),
        ))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text('📡 IP配置', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF")] + ip_items,
            spacing=4,
        ),
    ))

    # 网关/DNS/连接
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('🔗 网络连接', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF"),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('默认网关', data.get('gateway', 'N/A')),
            _info_row('DNS服务器', data.get('dns', 'N/A')),
            _info_row('已建立连接', f"{data.get('conn_established', 0)} 个"),
            _info_row('监听端口', f"{data.get('conn_listening', 0)} 个"),
            _info_row('TIME_WAIT', f"{data.get('conn_timewait', 0)} 个"),
        ], spacing=0),
    ))

    # 共享文件夹
    if data.get('shares'):
        share_items = []
        for s in data.get('shares', []):
            share_items.append(ft.Container(
                padding=8, border_radius=8, bgcolor="#1B2838", margin=ft.Margin.only(bottom=4),
                content=ft.Row([
                    ft.Text(f"{s.get('name','N/A')} ({s.get('drive','')})", size=12, weight=ft.FontWeight.W_600, color=ACCENT),
                    ft.Text(f"→ {s.get('path','N/A')}", size=10, color=GRAY),
                    ft.Container(expand=True),
                    ft.Text(f"👥 {s.get('users','N/A')}", size=10, color=GRAY),
                ], spacing=8),
            ))

        cards.append(ft.Container(
            padding=16, border_radius=16, bgcolor=CARD_BG,
            content=ft.Column(
                [ft.Text('📁 共享文件夹', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF")] + share_items,
                spacing=4,
            ),
        ))

    return cards


def _info_row(label: str, value: str) -> ft.Container:
    return ft.Container(
        padding=ft.Padding.only(top=5, bottom=5),
        content=ft.Row([
            ft.Text(label, size=12, color=GRAY, width=90),
            ft.Text(str(value), size=12, color="#FFFFFF"),
        ], spacing=8),
    )
