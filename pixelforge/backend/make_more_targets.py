"""
make_more_targets.py — Generate 5 additional target screenshots for Phase 3.

Targets: settings panel, notification toast, profile card, pricing table, empty state.
These are more complex than the Phase 1 targets and stress-test the agent more.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import tempfile
from pathlib import Path

VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 800


SETTINGS_PANEL_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Settings</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#f1f5f9] min-h-screen flex items-start justify-center pt-10 font-sans">
<div class="bg-white rounded-2xl shadow-sm border border-[#e2e8f0] w-[640px]">
  <div class="px-8 py-6 border-b border-[#e2e8f0]">
    <h1 class="text-xl font-semibold text-[#0f172a]">Account Settings</h1>
    <p class="text-sm text-[#64748b] mt-1">Manage your profile and preferences</p>
  </div>

  <div class="divide-y divide-[#f1f5f9]">
    <!-- Avatar row -->
    <div class="px-8 py-5 flex items-center gap-4">
      <div class="w-16 h-16 rounded-full bg-[#6366f1] flex items-center justify-center text-white text-2xl font-bold flex-shrink-0">A</div>
      <div class="flex-1">
        <p class="font-medium text-[#0f172a]">Alex Johnson</p>
        <p class="text-sm text-[#64748b]">alex@example.com</p>
      </div>
      <button class="text-sm font-medium text-[#6366f1] border border-[#e2e8f0] px-4 py-2 rounded-lg hover:bg-[#f8fafc]">Change photo</button>
    </div>

    <!-- Toggle rows -->
    <div class="px-8 py-5 flex items-center justify-between">
      <div>
        <p class="font-medium text-[#0f172a] text-sm">Email notifications</p>
        <p class="text-xs text-[#64748b] mt-0.5">Receive digest emails weekly</p>
      </div>
      <div class="w-11 h-6 bg-[#6366f1] rounded-full relative cursor-pointer flex-shrink-0">
        <div class="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow"></div>
      </div>
    </div>

    <div class="px-8 py-5 flex items-center justify-between">
      <div>
        <p class="font-medium text-[#0f172a] text-sm">Two-factor authentication</p>
        <p class="text-xs text-[#64748b] mt-0.5">Add an extra layer of security</p>
      </div>
      <div class="w-11 h-6 bg-[#e2e8f0] rounded-full relative cursor-pointer flex-shrink-0">
        <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow"></div>
      </div>
    </div>

    <div class="px-8 py-5 flex items-center justify-between">
      <div>
        <p class="font-medium text-[#0f172a] text-sm">Marketing emails</p>
        <p class="text-xs text-[#64748b] mt-0.5">Product updates and announcements</p>
      </div>
      <div class="w-11 h-6 bg-[#e2e8f0] rounded-full relative cursor-pointer flex-shrink-0">
        <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow"></div>
      </div>
    </div>

    <!-- Theme selector -->
    <div class="px-8 py-5">
      <p class="font-medium text-[#0f172a] text-sm mb-3">Appearance</p>
      <div class="flex gap-3">
        <button class="flex-1 border-2 border-[#6366f1] rounded-xl p-3 text-sm font-medium text-[#6366f1] bg-[#f5f3ff]">Light</button>
        <button class="flex-1 border border-[#e2e8f0] rounded-xl p-3 text-sm font-medium text-[#64748b]">Dark</button>
        <button class="flex-1 border border-[#e2e8f0] rounded-xl p-3 text-sm font-medium text-[#64748b]">System</button>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <div class="px-8 py-5 flex justify-between items-center border-t border-[#e2e8f0]">
    <button class="text-sm text-[#ef4444] font-medium">Delete account</button>
    <button class="bg-[#0f172a] text-white text-sm font-semibold px-5 py-2.5 rounded-xl">Save changes</button>
  </div>
</div>
</body>
</html>"""


NOTIFICATION_TOAST_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Notifications</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0f172a] min-h-screen flex flex-col items-end justify-start pt-6 pr-6 gap-3 font-sans">

  <!-- Success toast -->
  <div class="bg-[#1e293b] border border-[#22c55e]/30 rounded-2xl p-4 w-80 flex items-start gap-3 shadow-xl">
    <div class="w-9 h-9 rounded-xl bg-[#22c55e]/15 flex items-center justify-center flex-shrink-0 mt-0.5">
      <span class="text-[#22c55e] text-lg">✓</span>
    </div>
    <div class="flex-1">
      <p class="font-semibold text-[#f1f5f9] text-sm">Payment successful</p>
      <p class="text-xs text-[#94a3b8] mt-0.5">Your subscription has been renewed for another year.</p>
    </div>
    <button class="text-[#475569] hover:text-[#94a3b8] flex-shrink-0 mt-0.5">×</button>
  </div>

  <!-- Warning toast -->
  <div class="bg-[#1e293b] border border-[#f59e0b]/30 rounded-2xl p-4 w-80 flex items-start gap-3 shadow-xl">
    <div class="w-9 h-9 rounded-xl bg-[#f59e0b]/15 flex items-center justify-center flex-shrink-0 mt-0.5">
      <span class="text-[#f59e0b] text-lg">!</span>
    </div>
    <div class="flex-1">
      <p class="font-semibold text-[#f1f5f9] text-sm">Storage almost full</p>
      <p class="text-xs text-[#94a3b8] mt-0.5">You've used 92% of your 10 GB storage quota.</p>
    </div>
    <button class="text-[#475569] hover:text-[#94a3b8] flex-shrink-0 mt-0.5">×</button>
  </div>

  <!-- Error toast -->
  <div class="bg-[#1e293b] border border-[#ef4444]/30 rounded-2xl p-4 w-80 flex items-start gap-3 shadow-xl">
    <div class="w-9 h-9 rounded-xl bg-[#ef4444]/15 flex items-center justify-center flex-shrink-0 mt-0.5">
      <span class="text-[#ef4444] text-lg">✕</span>
    </div>
    <div class="flex-1">
      <p class="font-semibold text-[#f1f5f9] text-sm">Upload failed</p>
      <p class="text-xs text-[#94a3b8] mt-0.5">File exceeds the 50 MB limit. Please compress and retry.</p>
    </div>
    <button class="text-[#475569] hover:text-[#94a3b8] flex-shrink-0 mt-0.5">×</button>
  </div>

  <!-- Info toast -->
  <div class="bg-[#1e293b] border border-[#6366f1]/30 rounded-2xl p-4 w-80 flex items-start gap-3 shadow-xl">
    <div class="w-9 h-9 rounded-xl bg-[#6366f1]/15 flex items-center justify-center flex-shrink-0 mt-0.5">
      <span class="text-[#818cf8] text-lg">i</span>
    </div>
    <div class="flex-1">
      <p class="font-semibold text-[#f1f5f9] text-sm">New version available</p>
      <p class="text-xs text-[#94a3b8] mt-0.5">v2.4.0 is ready. Restart to apply updates.</p>
      <button class="mt-2 text-xs font-semibold text-[#818cf8]">Restart now</button>
    </div>
    <button class="text-[#475569] hover:text-[#94a3b8] flex-shrink-0 mt-0.5">×</button>
  </div>
</body>
</html>"""


PROFILE_CARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Profile</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0f172a] min-h-screen flex items-center justify-center font-sans">
<div class="w-80">
  <!-- Card -->
  <div class="bg-[#1e293b] rounded-3xl overflow-hidden border border-[#334155]">
    <!-- Cover -->
    <div class="h-28 bg-gradient-to-r from-[#6366f1] to-[#a78bfa]"></div>

    <!-- Avatar -->
    <div class="px-6 pb-6">
      <div class="-mt-10 mb-4">
        <div class="w-20 h-20 rounded-2xl bg-[#0f172a] border-4 border-[#1e293b] flex items-center justify-center text-3xl font-bold text-[#6366f1]">S</div>
      </div>

      <div class="flex items-start justify-between mb-5">
        <div>
          <h2 class="text-lg font-bold text-[#f1f5f9]">Sarah Chen</h2>
          <p class="text-sm text-[#64748b]">Product Designer</p>
        </div>
        <span class="bg-[#22c55e]/15 text-[#22c55e] text-xs font-semibold px-2.5 py-1 rounded-full">Open to work</span>
      </div>

      <!-- Stats row -->
      <div class="grid grid-cols-3 gap-3 mb-5 bg-[#0f172a] rounded-2xl p-3">
        <div class="text-center">
          <p class="text-lg font-bold text-[#f1f5f9]">142</p>
          <p class="text-xs text-[#64748b]">Projects</p>
        </div>
        <div class="text-center border-x border-[#1e293b]">
          <p class="text-lg font-bold text-[#f1f5f9]">8.2k</p>
          <p class="text-xs text-[#64748b]">Followers</p>
        </div>
        <div class="text-center">
          <p class="text-lg font-bold text-[#f1f5f9]">312</p>
          <p class="text-xs text-[#64748b]">Following</p>
        </div>
      </div>

      <!-- Skills -->
      <div class="flex flex-wrap gap-2 mb-5">
        <span class="bg-[#6366f1]/15 text-[#818cf8] text-xs font-medium px-3 py-1 rounded-full">Figma</span>
        <span class="bg-[#6366f1]/15 text-[#818cf8] text-xs font-medium px-3 py-1 rounded-full">Prototyping</span>
        <span class="bg-[#6366f1]/15 text-[#818cf8] text-xs font-medium px-3 py-1 rounded-full">Design Systems</span>
        <span class="bg-[#6366f1]/15 text-[#818cf8] text-xs font-medium px-3 py-1 rounded-full">User Research</span>
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <button class="flex-1 bg-[#6366f1] text-white text-sm font-semibold py-2.5 rounded-xl">Follow</button>
        <button class="flex-1 border border-[#334155] text-[#94a3b8] text-sm font-medium py-2.5 rounded-xl">Message</button>
      </div>
    </div>
  </div>
</div>
</body>
</html>"""


EMPTY_STATE_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Empty State</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#f8fafc] min-h-screen flex items-center justify-center font-sans">
<div class="text-center max-w-sm">
  <!-- Illustration placeholder -->
  <div class="mx-auto mb-8 w-48 h-48 bg-[#f1f5f9] rounded-3xl flex items-center justify-center border border-[#e2e8f0]">
    <div class="text-center">
      <div class="w-16 h-16 bg-[#e2e8f0] rounded-2xl mx-auto mb-3 flex items-center justify-center">
        <div class="w-8 h-8 bg-[#cbd5e1] rounded-lg"></div>
      </div>
      <div class="w-24 h-2 bg-[#e2e8f0] rounded-full mx-auto mb-2"></div>
      <div class="w-16 h-2 bg-[#f1f5f9] rounded-full mx-auto"></div>
    </div>
  </div>

  <h2 class="text-2xl font-bold text-[#0f172a] mb-3">No projects yet</h2>
  <p class="text-[#64748b] text-sm leading-relaxed mb-8">
    Create your first project to start collaborating with your team. It only takes a minute.
  </p>

  <div class="flex gap-3 justify-center">
    <button class="bg-[#0f172a] text-white font-semibold text-sm px-6 py-3 rounded-xl shadow-sm hover:bg-[#1e293b]">
      Create project
    </button>
    <button class="border border-[#e2e8f0] text-[#64748b] font-medium text-sm px-6 py-3 rounded-xl hover:bg-white">
      Learn more
    </button>
  </div>

  <!-- Recent templates -->
  <div class="mt-10">
    <p class="text-xs font-semibold uppercase tracking-wider text-[#94a3b8] mb-4">Start from a template</p>
    <div class="flex gap-3 justify-center">
      <div class="bg-white border border-[#e2e8f0] rounded-xl p-3 text-left w-28 cursor-pointer hover:border-[#6366f1] transition-colors">
        <div class="w-8 h-8 bg-[#fef3c7] rounded-lg mb-2"></div>
        <p class="text-xs font-medium text-[#0f172a]">Marketing</p>
      </div>
      <div class="bg-white border border-[#e2e8f0] rounded-xl p-3 text-left w-28 cursor-pointer hover:border-[#6366f1] transition-colors">
        <div class="w-8 h-8 bg-[#dbeafe] rounded-lg mb-2"></div>
        <p class="text-xs font-medium text-[#0f172a]">Engineering</p>
      </div>
      <div class="bg-white border border-[#e2e8f0] rounded-xl p-3 text-left w-28 cursor-pointer hover:border-[#6366f1] transition-colors">
        <div class="w-8 h-8 bg-[#fce7f3] rounded-lg mb-2"></div>
        <p class="text-xs font-medium text-[#0f172a]">Design</p>
      </div>
    </div>
  </div>
</div>
</body>
</html>"""


PRICING_TABLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Pricing Table</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0f172a] min-h-screen flex items-center justify-center font-sans p-8">
<div class="w-full max-w-4xl">
  <div class="text-center mb-10">
    <h1 class="text-4xl font-bold text-[#f1f5f9] mb-3">Simple, transparent pricing</h1>
    <p class="text-[#64748b]">No hidden fees. Cancel anytime.</p>
    <div class="inline-flex items-center gap-1 bg-[#1e293b] rounded-full p-1 mt-6">
      <button class="bg-[#6366f1] text-white text-sm font-semibold px-5 py-2 rounded-full">Monthly</button>
      <button class="text-[#64748b] text-sm font-medium px-5 py-2">Annual  <span class="text-[#22c55e] text-xs font-bold">-20%</span></button>
    </div>
  </div>

  <!-- Table -->
  <div class="bg-[#1e293b] rounded-2xl border border-[#334155] overflow-hidden">
    <!-- Header -->
    <div class="grid grid-cols-4 border-b border-[#334155]">
      <div class="p-6">
        <p class="text-[#64748b] text-sm">Feature</p>
      </div>
      <div class="p-6 text-center border-l border-[#334155]">
        <p class="font-semibold text-[#f1f5f9]">Free</p>
        <p class="text-2xl font-bold text-[#f1f5f9] mt-1">$0</p>
        <p class="text-[#64748b] text-xs">/month</p>
      </div>
      <div class="p-6 text-center border-l border-[#334155] bg-[#6366f1]/10">
        <div class="flex items-center justify-center gap-2 mb-1">
          <p class="font-semibold text-[#f1f5f9]">Pro</p>
          <span class="bg-[#6366f1] text-white text-xs font-bold px-2 py-0.5 rounded-full">Popular</span>
        </div>
        <p class="text-2xl font-bold text-[#6366f1] mt-1">$29</p>
        <p class="text-[#64748b] text-xs">/month</p>
      </div>
      <div class="p-6 text-center border-l border-[#334155]">
        <p class="font-semibold text-[#f1f5f9]">Enterprise</p>
        <p class="text-2xl font-bold text-[#f1f5f9] mt-1">$99</p>
        <p class="text-[#64748b] text-xs">/month</p>
      </div>
    </div>

    <!-- Rows -->
    <div class="divide-y divide-[#334155]/50">
      <div class="grid grid-cols-4 items-center">
        <div class="p-5 text-sm text-[#94a3b8]">Storage</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#cbd5e1]">5 GB</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#cbd5e1] bg-[#6366f1]/5">100 GB</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#cbd5e1]">1 TB</div>
      </div>
      <div class="grid grid-cols-4 items-center">
        <div class="p-5 text-sm text-[#94a3b8]">API calls/month</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#cbd5e1]">1,000</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#cbd5e1] bg-[#6366f1]/5">50,000</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#cbd5e1]">Unlimited</div>
      </div>
      <div class="grid grid-cols-4 items-center">
        <div class="p-5 text-sm text-[#94a3b8]">Team members</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#475569]">--</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#cbd5e1] bg-[#6366f1]/5">Up to 10</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#cbd5e1]">Unlimited</div>
      </div>
      <div class="grid grid-cols-4 items-center">
        <div class="p-5 text-sm text-[#94a3b8]">Priority support</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#475569]">--</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#22c55e] bg-[#6366f1]/5">Included</div>
        <div class="p-5 text-center border-l border-[#334155]/50 text-sm text-[#22c55e]">Dedicated CSM</div>
      </div>
    </div>

    <!-- CTA row -->
    <div class="grid grid-cols-4 border-t border-[#334155] p-4 gap-4">
      <div></div>
      <div class="text-center"><button class="w-full border border-[#334155] text-[#94a3b8] text-sm font-medium py-2.5 rounded-xl">Get started</button></div>
      <div class="text-center"><button class="w-full bg-[#6366f1] text-white text-sm font-semibold py-2.5 rounded-xl">Start trial</button></div>
      <div class="text-center"><button class="w-full border border-[#334155] text-[#94a3b8] text-sm font-medium py-2.5 rounded-xl">Contact us</button></div>
    </div>
  </div>
</div>
</body>
</html>"""


async def render_to_png(html, output_path):
    from playwright.async_api import async_playwright
    import asyncio as _asyncio

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
            await _asyncio.sleep(0.5)
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
        ("settings_panel.png", SETTINGS_PANEL_HTML),
        ("notification_toast.png", NOTIFICATION_TOAST_HTML),
        ("profile_card.png", PROFILE_CARD_HTML),
        ("empty_state.png", EMPTY_STATE_HTML),
        ("pricing_table.png", PRICING_TABLE_HTML),
    ]

    print("Generating additional target PNG screenshots...\n")
    for filename, html in targets:
        out = str(targets_dir / filename)
        await render_to_png(html, out)

    print(f"\nDone! Additional targets saved to: {targets_dir}")


if __name__ == "__main__":
    asyncio.run(main())
