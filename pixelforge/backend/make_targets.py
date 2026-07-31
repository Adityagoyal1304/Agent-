"""
make_targets.py — Generate target PNG screenshots for testing PixelForge.

Creates three handcrafted HTML designs and renders them via Playwright.
These are deliberately achievable targets — well-structured Tailwind components
that a good LLM can reproduce in 3-5 iterations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import tempfile
from pathlib import Path

# Viewport dimensions for Playwright — defined inline to avoid importing config
# (config.py requires GEMINI_API_KEY which is not needed for rendering target PNGs)
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 800


PRICING_CARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pricing</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0f172a] min-h-screen flex items-center justify-center font-sans p-8">
<div class="flex gap-6 items-end">

  <!-- Starter -->
  <div class="bg-[#1e293b] rounded-2xl p-8 w-72 border border-[#334155]">
    <p class="text-[#94a3b8] text-sm font-medium uppercase tracking-widest mb-2">Starter</p>
    <div class="flex items-end gap-1 mb-6">
      <span class="text-5xl font-bold text-[#f1f5f9]">$9</span>
      <span class="text-[#64748b] mb-2">/mo</span>
    </div>
    <ul class="space-y-3 mb-8">
      <li class="flex items-center gap-3 text-[#cbd5e1] text-sm"><span class="text-[#22c55e]">✓</span> 5 projects</li>
      <li class="flex items-center gap-3 text-[#cbd5e1] text-sm"><span class="text-[#22c55e]">✓</span> 10 GB storage</li>
      <li class="flex items-center gap-3 text-[#cbd5e1] text-sm"><span class="text-[#22c55e]">✓</span> Basic analytics</li>
      <li class="flex items-center gap-3 text-[#475569] text-sm"><span class="text-[#475569]">✗</span> API access</li>
    </ul>
    <button class="w-full border border-[#334155] text-[#94a3b8] py-3 rounded-xl text-sm font-medium hover:border-[#64748b] transition-colors">Get started</button>
  </div>

  <!-- Pro (featured) -->
  <div class="bg-[#6366f1] rounded-2xl p-8 w-72 shadow-2xl shadow-[#6366f1]/40 -translate-y-4">
    <div class="flex items-center justify-between mb-2">
      <p class="text-[#c7d2fe] text-sm font-medium uppercase tracking-widest">Pro</p>
      <span class="bg-[#ffffff]/20 text-white text-xs font-bold px-2 py-1 rounded-full">POPULAR</span>
    </div>
    <div class="flex items-end gap-1 mb-6">
      <span class="text-5xl font-bold text-white">$29</span>
      <span class="text-[#c7d2fe] mb-2">/mo</span>
    </div>
    <ul class="space-y-3 mb-8">
      <li class="flex items-center gap-3 text-white text-sm"><span class="text-[#a5f3fc]">✓</span> Unlimited projects</li>
      <li class="flex items-center gap-3 text-white text-sm"><span class="text-[#a5f3fc]">✓</span> 100 GB storage</li>
      <li class="flex items-center gap-3 text-white text-sm"><span class="text-[#a5f3fc]">✓</span> Advanced analytics</li>
      <li class="flex items-center gap-3 text-white text-sm"><span class="text-[#a5f3fc]">✓</span> Full API access</li>
    </ul>
    <button class="w-full bg-white text-[#6366f1] py-3 rounded-xl text-sm font-bold hover:bg-[#f0f0ff] transition-colors">Start free trial</button>
  </div>

  <!-- Enterprise -->
  <div class="bg-[#1e293b] rounded-2xl p-8 w-72 border border-[#334155]">
    <p class="text-[#94a3b8] text-sm font-medium uppercase tracking-widest mb-2">Enterprise</p>
    <div class="flex items-end gap-1 mb-6">
      <span class="text-5xl font-bold text-[#f1f5f9]">$99</span>
      <span class="text-[#64748b] mb-2">/mo</span>
    </div>
    <ul class="space-y-3 mb-8">
      <li class="flex items-center gap-3 text-[#cbd5e1] text-sm"><span class="text-[#22c55e]">✓</span> Everything in Pro</li>
      <li class="flex items-center gap-3 text-[#cbd5e1] text-sm"><span class="text-[#22c55e]">✓</span> 1 TB storage</li>
      <li class="flex items-center gap-3 text-[#cbd5e1] text-sm"><span class="text-[#22c55e]">✓</span> Priority support</li>
      <li class="flex items-center gap-3 text-[#cbd5e1] text-sm"><span class="text-[#22c55e]">✓</span> SSO & audit logs</li>
    </ul>
    <button class="w-full border border-[#334155] text-[#94a3b8] py-3 rounded-xl text-sm font-medium hover:border-[#64748b] transition-colors">Contact sales</button>
  </div>

</div>
</body>
</html>"""


LOGIN_FORM_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#f8fafc] min-h-screen flex items-center justify-center font-sans">
<div class="bg-white rounded-2xl shadow-xl p-10 w-96">

  <!-- Logo placeholder -->
  <div class="flex justify-center mb-8">
    <div class="bg-[#6366f1] rounded-2xl w-12 h-12 flex items-center justify-center">
      <span class="text-white font-bold text-xl">P</span>
    </div>
  </div>

  <h1 class="text-2xl font-bold text-[#0f172a] text-center mb-1">Welcome back</h1>
  <p class="text-[#64748b] text-sm text-center mb-8">Sign in to your account</p>

  <!-- Form -->
  <div class="space-y-5">
    <div>
      <label class="block text-sm font-medium text-[#374151] mb-1.5">Email address</label>
      <input type="email" placeholder="you@example.com"
        class="w-full border border-[#e2e8f0] rounded-xl px-4 py-3 text-sm text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:ring-2 focus:ring-[#6366f1] focus:border-transparent" />
    </div>
    <div>
      <div class="flex items-center justify-between mb-1.5">
        <label class="block text-sm font-medium text-[#374151]">Password</label>
        <a href="#" class="text-xs text-[#6366f1] font-medium">Forgot password?</a>
      </div>
      <input type="password" placeholder="••••••••"
        class="w-full border border-[#e2e8f0] rounded-xl px-4 py-3 text-sm text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:ring-2 focus:ring-[#6366f1] focus:border-transparent" />
    </div>

    <div class="flex items-center gap-2">
      <div class="w-4 h-4 border border-[#d1d5db] rounded"></div>
      <span class="text-sm text-[#64748b]">Keep me signed in</span>
    </div>

    <button class="w-full bg-[#6366f1] text-white py-3 rounded-xl text-sm font-semibold hover:bg-[#4f46e5] transition-colors">
      Sign in
    </button>
  </div>

  <p class="text-center text-sm text-[#64748b] mt-6">
    Don't have an account? <a href="#" class="text-[#6366f1] font-medium">Sign up</a>
  </p>
</div>
</body>
</html>"""


STAT_ROW_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stats</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0f172a] min-h-screen flex items-center justify-center font-sans p-8">
<div class="w-full max-w-5xl">

  <!-- Header -->
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-[#f1f5f9] mb-1">Dashboard Overview</h1>
    <p class="text-[#64748b]">Last 30 days</p>
  </div>

  <!-- Stat cards row -->
  <div class="grid grid-cols-4 gap-5">

    <div class="bg-[#1e293b] rounded-2xl p-6 border border-[#334155]">
      <div class="flex items-center justify-between mb-4">
        <p class="text-[#64748b] text-sm font-medium">Total Revenue</p>
        <div class="bg-[#22c55e]/10 rounded-lg w-9 h-9 flex items-center justify-center">
          <span class="text-[#22c55e] text-lg">$</span>
        </div>
      </div>
      <p class="text-3xl font-bold text-[#f1f5f9] mb-2">$48,295</p>
      <div class="flex items-center gap-1">
        <span class="text-[#22c55e] text-sm font-medium">↑ 12.5%</span>
        <span class="text-[#475569] text-xs">vs last month</span>
      </div>
    </div>

    <div class="bg-[#1e293b] rounded-2xl p-6 border border-[#334155]">
      <div class="flex items-center justify-between mb-4">
        <p class="text-[#64748b] text-sm font-medium">Active Users</p>
        <div class="bg-[#6366f1]/10 rounded-lg w-9 h-9 flex items-center justify-center">
          <span class="text-[#6366f1] text-lg">♟</span>
        </div>
      </div>
      <p class="text-3xl font-bold text-[#f1f5f9] mb-2">12,840</p>
      <div class="flex items-center gap-1">
        <span class="text-[#22c55e] text-sm font-medium">↑ 8.2%</span>
        <span class="text-[#475569] text-xs">vs last month</span>
      </div>
    </div>

    <div class="bg-[#1e293b] rounded-2xl p-6 border border-[#334155]">
      <div class="flex items-center justify-between mb-4">
        <p class="text-[#64748b] text-sm font-medium">Orders</p>
        <div class="bg-[#f59e0b]/10 rounded-lg w-9 h-9 flex items-center justify-center">
          <span class="text-[#f59e0b] text-lg">⊡</span>
        </div>
      </div>
      <p class="text-3xl font-bold text-[#f1f5f9] mb-2">3,291</p>
      <div class="flex items-center gap-1">
        <span class="text-[#ef4444] text-sm font-medium">↓ 3.1%</span>
        <span class="text-[#475569] text-xs">vs last month</span>
      </div>
    </div>

    <div class="bg-[#1e293b] rounded-2xl p-6 border border-[#334155]">
      <div class="flex items-center justify-between mb-4">
        <p class="text-[#64748b] text-sm font-medium">Churn Rate</p>
        <div class="bg-[#ef4444]/10 rounded-lg w-9 h-9 flex items-center justify-center">
          <span class="text-[#ef4444] text-lg">%</span>
        </div>
      </div>
      <p class="text-3xl font-bold text-[#f1f5f9] mb-2">2.4%</p>
      <div class="flex items-center gap-1">
        <span class="text-[#22c55e] text-sm font-medium">↓ 0.8%</span>
        <span class="text-[#475569] text-xs">vs last month</span>
      </div>
    </div>

  </div>
</div>
</body>
</html>"""


async def render_to_png(html: str, output_path: str):
    """Render an HTML string to a PNG via Playwright."""
    from playwright.async_api import async_playwright

    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    tmp.write(html)
    tmp.close()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_viewport_size({"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT})
            file_url = f"file:///{tmp.name.replace(os.sep, '/')}"
            await page.goto(file_url, wait_until="networkidle", timeout=30000)
            import asyncio as _asyncio
            await _asyncio.sleep(0.5)  # Let Tailwind CDN apply
            await page.screenshot(path=output_path, full_page=False)
            await browser.close()
        print(f"  [OK] Rendered: {output_path}")
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


async def main():
    targets_dir = Path(__file__).parent.parent / "targets"
    targets_dir.mkdir(parents=True, exist_ok=True)

    targets = [
        ("pricing_card.png", PRICING_CARD_HTML),
        ("login_form.png", LOGIN_FORM_HTML),
        ("stat_row.png", STAT_ROW_HTML),
    ]

    print("Generating target PNG screenshots...\n")
    for filename, html in targets:
        out = str(targets_dir / filename)
        await render_to_png(html, out)

    print(f"\nDone! Targets saved to: {targets_dir}")


if __name__ == "__main__":
    asyncio.run(main())
