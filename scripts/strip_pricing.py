#!/usr/bin/env python3
"""Strip ThermaForge-pricing strings from public site. Idempotent."""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def resolve(name):
    p = REPO / name
    if p.exists():
        return p
    raise FileNotFoundError(f"Could not locate {name} under {REPO}")

EDITS = [
    # ---------- INDEX / HOME ----------
    ("index.html",
     'Every engagement bundles the Carson Systems platform stack into the monthly fee \u2014 no separate platform invoices. Routebook ($1,499/mo retail) ships with every engagement. Scale adds Frontline ($499/mo retail) and the full content engine. Stack value alone exceeds $24K/year, bundled.',
     'Every engagement bundles the Carson Systems platform stack \u2014 no separate platform invoices. Routebook ships with every engagement. Scale adds Frontline and the full content engine. The stack alone replaces multiple vendor contracts when sourced piecemeal.'),

    ("index.html",
     "Frontline costs $499/mo retail, bundled into Scale.",
     "Frontline is bundled into Scale."),

    ("index.html",
     "Both tiers are annual engagements with a six-client cap across the firm. Equity is negotiated per engagement and aligned with the recap or exit horizon. Operate is the right entry point for most $5M\u2013$15M shops. Scale is for owners pushing past $10M who want to compress brand and recruiting on the same timeline as ops.",
     "Both tiers are annual engagements with a six-client cap across the firm. Investment is scoped to the engagement and equity-aligned with your recap or exit horizon \u2014 discussed on the fit call once we both confirm the match. Operate is the right entry point for most $5M\u2013$15M shops. Scale is for owners pushing past $10M who want to compress brand and recruiting on the same timeline as ops."),

    ("index.html",
     '<div><span class="tf-price">$8,000</span><span class="tf-price-suffix">/ mo + equity</span></div>',
     '<div><span class="tf-price">Annual</span><span class="tf-price-suffix">engagement + equity-aligned</span></div>'),

    ("index.html",
     '<div><span class="tf-price">$14,500</span><span class="tf-price-suffix">/ mo + equity</span></div>',
     '<div><span class="tf-price">Annual</span><span class="tf-price-suffix">engagement + equity-aligned</span></div>'),

    ("index.html",
     "You're not paying $8k+ a month and giving up equity to wake up one morning",
     "You're not signing an annual engagement and giving up equity to wake up one morning"),

    ("index.html",
     '<li><a href="/operate">Operate \u2014 $8K/mo</a></li>',
     '<li><a href="/operate">Operate</a></li>'),

    ("index.html",
     '<li><a href="/scale">Scale \u2014 $14.5K/mo</a></li>',
     '<li><a href="/scale">Scale</a></li>'),

    ("index.html",
     '"priceRange": "$8000-$14500/month",\n      ',
     ''),

    ("index.html",
     "It's included in the engagement at no extra cost.",
     "It's bundled into every engagement."),

    # ---------- OPERATE ----------
    ("operate.html",
     "<title>ThermaForge Operate \u2014 $8K/mo + equity \u00b7 Operating partner for HVAC</title>",
     "<title>ThermaForge Operate \u2014 Operating partner for HVAC</title>"),

    ("operate.html",
     '<meta name="description" content="ThermaForge Operate: the operating partner in the seat. $8,000/month + equity. Annual engagement. Routebook ERP included. For $5M\u2013$15M HVAC shops." />',
     '<meta name="description" content="ThermaForge Operate: the operating partner in the seat. Annual engagement. Routebook ERP included. For $5M\u2013$15M HVAC shops." />'),

    ("operate.html",
     '<meta property="og:title" content="ThermaForge Operate \u2014 $8K/mo + equity" />',
     '<meta property="og:title" content="ThermaForge Operate \u2014 Operating partner for HVAC" />'),

    ("operate.html",
     "deployed inside your engagement at no incremental cost. Migration",
     "deployed inside your engagement, bundled. Migration"),

    ("operate.html",
     "Two weeks typical, no extra cost.",
     "Two weeks typical, included."),

    ("operate.html",
     '<tr><td>Annual cost</td><td>$96K + equity</td><td>$60\u2013120K</td><td>$120\u2013180K</td><td>$200K+</td></tr>',
     ''),

    ("operate.html",
     '<li><a href="/operate">Operate \u2014 $8K/mo</a></li>',
     '<li><a href="/operate">Operate</a></li>'),

    ("operate.html",
     '<li><a href="/scale">Scale \u2014 $14.5K/mo</a></li>',
     '<li><a href="/scale">Scale</a></li>'),

    # ---------- SCALE ----------
    ("scale.html",
     "<title>ThermaForge Scale \u2014 $14.5K/mo + equity \u00b7 Operating partner + demand engine</title>",
     "<title>ThermaForge Scale \u2014 Operating partner + demand engine</title>"),

    ("scale.html",
     '<meta name="description" content="ThermaForge Scale: the full demand engine attached to the seat. $14,500/month + equity. For $10M+ HVAC shops scaling brand and recruiting alongside ops." />',
     '<meta name="description" content="ThermaForge Scale: the full demand engine attached to the seat. Annual engagement. For $10M+ HVAC shops scaling brand and recruiting alongside ops." />'),

    ("scale.html",
     '<meta property="og:title" content="ThermaForge Scale \u2014 $14.5K/mo + equity" />',
     '<meta property="og:title" content="ThermaForge Scale \u2014 Operating partner + demand engine" />'),

    ("scale.html",
     "transfers urgents to the on-call manager. The retail price is $499/mo and it's bundled into Scale.",
     "transfers urgents to the on-call manager. Bundled into Scale at no separate invoice."),

    ("scale.html",
     '<span class="figure">~$290K / yr</span>',
     '<span class="figure">Five separate vendors</span>'),

    ("scale.html",
     '<a href="/#pricing" style="color: var(--tf-orange); border-bottom: 1px solid var(--tf-orange);">See engagement pricing</a> for the all-in figure.',
     '<a href="/#pricing" style="color: var(--tf-orange); border-bottom: 1px solid var(--tf-orange);">See engagement detail \u2192</a>'),

    ("scale.html",
     '<li><a href="/operate">Operate \u2014 $8K/mo</a></li>',
     '<li><a href="/operate">Operate</a></li>'),

    ("scale.html",
     '<li><a href="/scale">Scale \u2014 $14.5K/mo</a></li>',
     '<li><a href="/scale">Scale</a></li>'),

    # ---------- APPLY ----------
    ("apply.html",
     "<option>Operate ($8K/mo)</option>",
     "<option>Operate \u2014 operating partner in the seat</option>"),

    ("apply.html",
     "<option>Scale ($14.5K/mo)</option>",
     "<option>Scale \u2014 operating partner + full demand engine</option>"),

    ("apply.html",
     '<li><a href="/operate">Operate \u2014 $8K/mo</a></li>',
     '<li><a href="/operate">Operate</a></li>'),

    ("apply.html",
     '<li><a href="/scale">Scale \u2014 $14.5K/mo</a></li>',
     '<li><a href="/scale">Scale</a></li>'),

    # ---------- PLATFORM ----------
    ("platform.html",
     '<meta name="description" content="The Carson Systems platform stack ThermaForge clients deploy at no incremental cost. Routebook ERP, Frontline AI, content engine, and more." />',
     '<meta name="description" content="The Carson Systems platform stack ThermaForge clients deploy. Routebook ERP, Frontline AI, content engine, and more." />'),

    ("platform.html",
     "ThermaForge clients deploy a Carson Systems platform stack at no incremental cost.",
     "ThermaForge clients deploy a Carson Systems platform stack as part of every engagement."),

    ("platform.html",
     "Migration handled by the engagement at no extra cost.",
     "Migration handled by the engagement."),

    ("platform.html",
     '<li><a href="/operate">Operate \u2014 $8K/mo</a></li>',
     '<li><a href="/operate">Operate</a></li>'),

    ("platform.html",
     '<li><a href="/scale">Scale \u2014 $14.5K/mo</a></li>',
     '<li><a href="/scale">Scale</a></li>'),
]

REGEX_DELETIONS = [
    ("index.html",
     re.compile(r',\s*\n\s*"priceSpecification":\s*\{\s*\n\s*"@type":\s*"UnitPriceSpecification",\s*\n\s*"price":\s*"\d+",\s*\n\s*"priceCurrency":\s*"USD",\s*\n\s*"unitText":\s*"MONTH"\s*\n\s*\}'),
     ''),
]

def main():
    misses = []
    hits = 0
    for name, old, new in EDITS:
        p = resolve(name)
        text = p.read_text()
        if old not in text:
            misses.append((name, old[:80]))
            continue
        text = text.replace(old, new)
        p.write_text(text)
        hits += 1
        print(f"\u2713 {name}: {old[:60].strip()}\u2026")
    for name, pattern, repl in REGEX_DELETIONS:
        p = resolve(name)
        text = p.read_text()
        new_text, n = pattern.subn(repl, text)
        if n == 0:
            misses.append((name, f"REGEX: {pattern.pattern[:80]}"))
            continue
        p.write_text(new_text)
        hits += 1
        print(f"\u2713 {name}: regex deleted {n} priceSpecification block(s)")
    print(f"\nTotal edits applied: {hits}")
    if misses:
        print("\n\u26a0\ufe0f  UNMATCHED \u2014 investigate manually:")
        for n, s in misses:
            print(f"   {n}: {s}")
        sys.exit(1)
    print("\n\u2705 All edits applied cleanly.")

if __name__ == "__main__":
    main()
