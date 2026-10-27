# -*- coding: utf-8 -*-
import os
from playwright.sync_api import sync_playwright

SHOT_DIR = "E:/certdsystem/website/assets/shots"
AUTH_STATE = "E:/certdsystem/website/_auth.json"
os.makedirs(SHOT_DIR, exist_ok=True)

REMOVE_TIP = """() => {
    document.querySelectorAll('.el-popper[role="tooltip"]').forEach(e => {
        if (e.textContent.includes('主题风格')) e.style.display = 'none';
    });
    document.querySelectorAll('.el-message').forEach(e => e.remove());
}"""

def clean(page):
    page.evaluate(REMOVE_TIP)
    page.wait_for_timeout(300)

def shot(page, name):
    clean(page)
    page.screenshot(path=f"{SHOT_DIR}/{name}")

def click_menu(page, text):
    page.locator('.el-menu-item, [class*="menu-item"]').filter(has_text=text).first.click()
    page.wait_for_timeout(1500)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=False)
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        storage_state=AUTH_STATE if os.path.exists(AUTH_STATE) else None,
    )
    page = context.new_page()
    page.goto("http://10.10.12.140", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    if "auth/login" in page.url:
        page.fill('input[placeholder="请输入账号"]', 'admin')
        page.fill('input[placeholder="请输入密码"]', 'Admin@123')
        # 图形验证码由人工完成：等待登录成功（最长 8 分钟）
        print("请在弹出的浏览器窗口中完成图形验证码并点击登录……", flush=True)
        for _ in range(480):
            if "auth/login" not in page.url:
                break
            page.wait_for_timeout(1000)
        if "auth/login" in page.url:
            raise RuntimeError("等待登录超时")
        page.wait_for_timeout(2500)
        context.storage_state(path=AUTH_STATE)
    clean(page)

    # 工作台
    page.goto("http://10.10.12.140/#/certd/dashboard", wait_until="domcontentloaded")
    page.wait_for_timeout(2200)
    shot(page, "01-dashboard.png")

    # 流水线列表
    click_menu(page, "证书流水线")
    shot(page, "02-pipeline-list.png")

    # 历史
    click_menu(page, "执行历史")
    shot(page, "03-history.png")

    # 证书库
    click_menu(page, "证书库")
    shot(page, "04-cert.png")

    # 授权
    click_menu(page, "授权管理")
    shot(page, "05-access.png")

    # 通知
    click_menu(page, "通知渠道")
    shot(page, "06-notify.png")

    # 监控
    click_menu(page, "站点监控")
    shot(page, "07-monitor.png")

    # 画布：从流水线列表进入真实流水线详情
    click_menu(page, "证书流水线")
    page.wait_for_timeout(800)
    page.click('text=主业务流水')
    page.wait_for_timeout(3000)
    # 收起底部日志，让画布更完整（点击"收起"）
    try:
        page.get_by_role("button", name="收起").first.click(timeout=1500)
        page.wait_for_timeout(800)
    except:
        pass
    shot(page, "08-canvas.png")

    # 日志特写：重新进入并展开日志
    click_menu(page, "证书流水线")
    page.wait_for_timeout(800)
    page.click('text=主业务流水')
    page.wait_for_timeout(3200)
    shot(page, "09-log.png")

    browser.close()
    print("全部干净截图完成")
