#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件与网络 - Page 2
"""

import flet as ft
from ui.theme import load_theme


def build_page(data: dict, theme: dict = None) -> list:
    if theme is None:
        theme = load_theme()

    GRAY = theme.get("secondary_text", "#888888")
    GREEN = theme.get("green", "#34a853")
    YELLOW = theme.get("yellow", "#f9ab00")
    RED = theme.get("red", "#ea4335")
    ACCENT = theme.get("accent", "#4a9eff")
    CARD_BG = theme.get("card_bg", "#1B2838")
    DARK_BG = theme.get("dark_bg", "#0A0F1A")
    TEXT_PRI = theme.get("primary_text", "#ffffff")

    cards = []

    # CPU详情
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('💻 CPU 信息', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('型号', data.get('cpu_name', 'N/A'), GRAY, TEXT_PRI),
            _info_row('核心/线程', f"{data.get('cpu_cores','N/A')} 核 / {data.get('cpu_threads','N/A')} 线程", GRAY, TEXT_PRI),
            _info_row('频率', f"{data.get('cpu_freq','N/A')} MHz", GRAY, TEXT_PRI),
            _info_row('当前负载', f"{data.get('cpu_load','N/A')}%", GRAY, TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('BIOS', data.get('bios', 'N/A'), GRAY, TEXT_PRI),
            _info_row('主板', data.get('motherboard', 'N/A'), GRAY, TEXT_PRI),
            _info_row('安全启动', data.get('secure_boot', 'N/A'), GRAY, TEXT_PRI),
        ], spacing=0),
    ))

    # 内存详情（含插槽）
    mem_chip_rows = []
    for chip in data.get('mem_chips', []):
        parts = chip.split('|')
        if len(parts) >= 4:
            mem_chip_rows.append(_info_row(
                f"插槽 {len(mem_chip_rows)+1}",
                f"{parts[0]} {parts[1]} {parts[2]} {parts[3]}",
                GRAY, TEXT_PRI
            ))
    used_slots = data.get('mem_used_slots', 0)
    total_slots = data.get('mem_total_slots', 0)
    if not mem_chip_rows:
        mem_chip_rows.append(_info_row('内存', '无信息', GRAY, TEXT_PRI))
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('🧠 内存信息', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('总容量', f"{data.get('mem_total', 0):.1f} GB", GRAY, TEXT_PRI),
            _info_row('已用', f"{data.get('mem_used', 0):.1f} GB （{data.get('mem_pct', 0):.1f}%）", GRAY, TEXT_PRI),
            _info_row('插槽', f"{used_slots} / {total_slots} （已用/总共）", GRAY, TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
        ] + mem_chip_rows, spacing=0),
    ))

    # GPU详情
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('🎮 GPU 信息', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('显卡', data.get('gpu', 'N/A'), GRAY, TEXT_PRI),
            _info_row('驱动版本', data.get('gpu_driver', 'N/A'), GRAY, TEXT_PRI),
            _info_row('未签名驱动', f"{data.get('unsigned_drivers','0')} 个" if data.get('unsigned_drivers','0') != '0' else '无', GRAY, TEXT_PRI),
        ], spacing=0),
    ))

    # 网络适配器
    adapter_items = []
    for i, a in enumerate(data.get('net_adapters', [])):
        status_color = GREEN if a.get('status') == 'Up' else RED
        adapter_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor=CARD_BG, margin=ft.Margin.only(bottom=6),
            content=ft.Column([
                ft.Row([
                    ft.Text(a.get('name',''), size=13, weight=ft.FontWeight.W_600, color=TEXT_PRI),
                    ft.Container(expand=True),
                    ft.Container(
                        padding=ft.Padding.only(left=8, right=8, top=2, bottom=2),
                        border_radius=6, bgcolor=status_color,
                        content=ft.Text(a.get('status','N/A'), size=10, color=TEXT_PRI),
                    ),
                ]),
                ft.Text(f"速率: {a.get('speed','N/A')}  |  MAC: {a.get('mac','N/A')}", size=10, color=GRAY),
            ], spacing=4),
        ))
        if i < len(data.get('net_adapters', [])) - 1:
            adapter_items.append(ft.Container(height=1, bgcolor="#2A3A4A", margin=ft.Margin.only(bottom=5)))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text('🌐 网络适配器', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI)] + adapter_items,
            spacing=4,
        ),
    ))

    # IP配置
    ip_items = []
    for i, ip in enumerate(data.get('ipv4_addrs', [])):
        ip_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor=CARD_BG, margin=ft.Margin.only(bottom=4),
            content=ft.Row([
                ft.Text(ip.get('iface',''), size=12, weight=ft.FontWeight.W_600, color=ACCENT),
                ft.Text(ip.get('ip','N/A'), size=12, color=TEXT_PRI),
                ft.Container(expand=True),
                ft.Text(f"/{ip.get('prefix','N/A')}  {ip.get('origin','')}", size=10, color=GRAY),
            ], spacing=12),
        ))
        if i < len(data.get('ipv4_addrs', [])) - 1:
            ip_items.append(ft.Container(height=1, bgcolor="#2A3A4A", margin=ft.Margin.only(bottom=4)))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text('📡 IP配置', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI)] + ip_items,
            spacing=4,
        ),
    ))

    # 网关/DNS/连接
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('🔗 网络连接', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('默认网关', data.get('gateway', 'N/A'), GRAY, TEXT_PRI),
            _info_row('DNS服务器', data.get('dns', 'N/A'), GRAY, TEXT_PRI),
            _info_row('已建立连接', f"{data.get('conn_established', 0)} 个", GRAY, TEXT_PRI),
            _info_row('监听端口', f"{data.get('conn_listening', 0)} 个", GRAY, TEXT_PRI),
            _info_row('TIME_WAIT', f"{data.get('conn_timewait', 0)} 个", GRAY, TEXT_PRI),
        ], spacing=0),
    ))

    # 共享文件夹
    if data.get('shares'):
        share_items = []
        for i, s in enumerate(data.get('shares', [])):
            share_items.append(ft.Container(
                padding=8, border_radius=8, bgcolor=CARD_BG, margin=ft.Margin.only(bottom=4),
                content=ft.Row([
                    ft.Text(f"{s.get('name','N/A')} ({s.get('drive','')})", size=12, weight=ft.FontWeight.W_600, color=ACCENT),
                    ft.Text(f"→ {s.get('path','N/A')}", size=10, color=GRAY),
                    ft.Container(expand=True),
                    ft.Text(f"👥 {s.get('users','N/A')}", size=10, color=GRAY),
                ], spacing=8),
            ))
            if i < len(data.get('shares', [])) - 1:
                share_items.append(ft.Container(height=1, bgcolor="#2A3A4A", margin=ft.Margin.only(bottom=4)))

        cards.append(ft.Container(
            padding=16, border_radius=16, bgcolor=CARD_BG,
            content=ft.Column(
                [ft.Text('📁 共享文件夹', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI)] + share_items,
                spacing=4,
            ),
        ))

    return cards


def _info_row(label: str, value: str, gray: str, text_pri: str) -> ft.Container:
    return ft.Container(
        padding=ft.Padding.only(top=5, bottom=5),
        content=ft.Row([
            ft.Text(label, size=12, color=gray, width=90),
            ft.Text(str(value), size=12, color=text_pri),
        ], spacing=8),
    )