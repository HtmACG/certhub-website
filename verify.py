# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

URL = "file:///E:/certdsystem/website/index.html"
WIDTHS = [1600, 1280, 1024, 768, 414]

errors, console_errors, failed_imgs, overflow_bad = [], [], [], []

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(URL, wait_until="load")

    # 滚动触发懒加载
    total = page.evaluate("() => document.body.scrollHeight")
    y = 0
    while y < total:
        page.evaluate(f"window.scrollTo(0,{y+500})")
        page.wait_for_timeout(100)
        y += 500
    page.wait_for_timeout(700)
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(300)

    img_info = page.evaluate("""() => [...document.querySelectorAll('img')].map(i => ({
        src: (i.currentSrc || i.src).split('/').pop(),
        ok: i.naturalWidth > 0
    }))""")
    for i in img_info:
        if not i["ok"]:
            failed_imgs.append(i["src"])
    print("图片总数:", len(img_info), " 加载失败:", failed_imgs if failed_imgs else "无")

    print("\n宽度   视口宽   滚动宽   横向溢出")
    for w in WIDTHS:
        page.set_viewport_size({"width": w, "height": 900})
        page.wait_for_timeout(250)
        r = page.evaluate("() => ({iw:document.documentElement.clientWidth,sw:document.documentElement.scrollWidth})")
        bad = r["sw"] > r["iw"]
        if bad: overflow_bad.append(w)
        print(f"{w:<6} {r['iw']:<8} {r['sw']:<8} {'是(异常)' if bad else '否'}")

    # 交互
    page.set_viewport_size({"width": 1440, "height": 900})
    page.click('.demo-tab[data-img="05-access.webp"]')
    page.wait_for_timeout(500)
    active = page.evaluate("() => document.querySelector('.demo-stage img.active').src.split('/').pop()")
    print("\n演示切换:", active, "(期望 05-access.webp)")
    page.click('.faq-item .faq-q')
    page.wait_for_timeout(400)
    print("FAQ 展开:", page.evaluate("() => document.querySelector('.faq-item').classList.contains('open')"))

    # 截图
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(400)
    page.screenshot(path="E:/certdsystem/website/_shot-desktop.png")
    page.set_viewport_size({"width": 414, "height": 900})
    page.wait_for_timeout(400)
    page.screenshot(path="E:/certdsystem/website/_shot-mobile.png")
    browser.close()

print("\n页面JS异常:", errors if errors else "无")
print("控制台错误:", console_errors if console_errors else "无")
ok = (not failed_imgs) and (not errors) and (not console_errors) and (not overflow_bad)
print("验证结果:", "通过" if ok else "存在问题")
