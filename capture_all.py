# -*- coding: utf-8 -*-
"""从本地开发环境（localhost:3006）采集官网演示截图。"""
import os
from PIL import Image
from playwright.sync_api import sync_playwright

SHOT_DIR = "E:/certdsystem/website/assets/shots"
BASE = "http://localhost:3006"
os.makedirs(SHOT_DIR, exist_ok=True)

REMOVE_TIP = """() => {
    document.querySelectorAll('.el-popper[role="tooltip"]').forEach(e => {
        if (e.textContent.includes('主题风格')) e.style.display = 'none';
    });
    document.querySelectorAll('.el-message').forEach(e => e.remove());
    // 开发环境专属浮层：Vue DevTools 面板、画布缩略图（会遮挡内容）
    document.querySelectorAll('.vue-devtools__panel').forEach(e => e.remove());
    document.querySelectorAll('.vue-flow__minimap').forEach(e => e.style.display = 'none');
}"""


def clean(page):
    page.evaluate(REMOVE_TIP)
    page.wait_for_timeout(300)


def shot(page, name):
    clean(page)
    name = name.replace(".png", "")
    tmp = f"{SHOT_DIR}/{name}.png"
    page.screenshot(path=tmp)
    Image.open(tmp).convert("RGB").save(f"{SHOT_DIR}/{name}.webp", "WEBP", quality=82, method=6)
    os.remove(tmp)


def click_menu(page, text):
    page.locator('.el-menu-item, [class*="menu-item"]').filter(has_text=text).first.click()
    page.wait_for_timeout(1600)


def open_pipeline(page):
    click_menu(page, "证书流水线")
    page.wait_for_timeout(800)
    page.get_by_text("Let's Encrypt + Nginx（本机）").first.click()
    page.wait_for_timeout(3200)


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    page.goto(BASE + "/", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    if "auth/login" in page.url:
        page.fill('input[placeholder="请输入账号"]', "admin")
        page.fill('input[placeholder="请输入密码"]', "123456")
        page.click("button:has-text('登录')")
        page.wait_for_timeout(3500)
    if "auth/login" in page.url:
        raise RuntimeError("登录失败：" + page.url)
    clean(page)

    # 01 工作台
    page.goto(BASE + "/#/certd/dashboard", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    shot(page, "01-dashboard.png")

    # 02 流水线列表
    click_menu(page, "证书流水线")
    shot(page, "02-pipeline-list.png")

    # 03 执行历史
    click_menu(page, "执行历史")
    shot(page, "03-history.png")

    # 04 证书库
    click_menu(page, "证书库")
    shot(page, "04-cert.png")

    # 05 授权管理
    click_menu(page, "授权管理")
    shot(page, "05-access.png")

    # 06 通知渠道
    click_menu(page, "通知渠道")
    shot(page, "06-notify.png")

    # 07 站点监控
    click_menu(page, "站点监控")
    shot(page, "07-monitor.png")

    # 08 流水线画布（收起日志）
    open_pipeline(page)
    try:
        page.get_by_role("button", name="收起").first.click(timeout=1500)
        page.wait_for_timeout(900)
    except Exception:
        pass
    shot(page, "08-canvas.png")

    # 09 执行日志（展开）
    open_pipeline(page)
    shot(page, "09-log.png")

    browser.close()
    print("全部截图完成")
