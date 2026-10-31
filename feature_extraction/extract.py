"""
Modul ekstraksi fitur: mengubah sebuah URL mentah menjadi 15 fitur yang
dipakai model Random Forest ringan (lihat model/train_lightweight_model.py).

Semua fitur dihitung real-time: fitur berbasis string dari URL itu sendiri,
dan fitur berbasis konten dari HTML halaman yang diambil (fetch) saat itu
juga. URLSimilarityIndex dihitung dengan mendeteksi 5 pola serangan yang
disebutkan pada penelitian asli PhiUSIIL (homograph, punycode, homophone,
bitsquatting, combosquatting) terhadap daftar domain resmi -- bukan
replikasi rumus asli (tidak dipublikasikan), melainkan operasionalisasi
dari definisi konseptualnya.
"""

import difflib
import re
import string
from urllib.parse import urljoin, urlparse

import tldextract
from bs4 import BeautifulSoup
from playwright.sync_api import (
    Error as PlaywrightError,
)
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.sync_api import sync_playwright

from .legit_domains import LEGIT_DOMAINS

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 8  # detik
THIN_CONTENT_LINE_THRESHOLD = 50  # di bawah ini dianggap mencurigakan (indikasi halaman interstitial/consent)

FEATURE_ORDER = [
    "URLSimilarityIndex",
    "NoOfExternalRef",
    "LineOfCode",
    "NoOfSelfRef",
    "NoOfImage",
    "HasSubmitButton",
    "NoOfJS",
    "HasCopyrightInfo",
    "URLTitleMatchScore",
    "HasSocialNet",
    "NoOfCSS",
    "IsResponsive",
    "URLLength",
    "HasFavicon",
    "IsHTTPS",
]

SOCIAL_DOMAINS = [
    "facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com",
    "tiktok.com", "youtube.com", "pinterest.com", "whatsapp.com",
    "telegram.org", "snapchat.com", "discord.com",
]

_tld_extractor = tldextract.TLDExtract(suffix_list_urls=())


def _registered_domain(url_or_host: str) -> str:
    ext = _tld_extractor(url_or_host)
    return ".".join(part for part in [ext.domain, ext.suffix] if part)


HOMOGRAPH_MAP = {
    'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x',
    'і': 'i', 'ѕ': 's', 'ԁ': 'd', 'ɡ': 'g',
}


def _normalize_homograph(text: str) -> str:
    return "".join(HOMOGRAPH_MAP.get(ch, ch) for ch in text)


def _is_punycode(domain: str) -> bool:
    return any(label.startswith("xn--") for label in domain.split("."))


def _decode_punycode_domain(domain: str) -> str:
    decoded_labels = []
    for label in domain.split("."):
        if label.startswith("xn--"):
            try:
                decoded_labels.append(label.encode("ascii").decode("idna"))
            except Exception:
                decoded_labels.append(label)
        else:
            decoded_labels.append(label)
    return ".".join(decoded_labels)


def _soundex(word: str) -> str:
    word = word.upper()
    if not word:
        return ""
    codes = {
        **dict.fromkeys("BFPV", "1"),
        **dict.fromkeys("CGJKQSXZ", "2"),
        **dict.fromkeys("DT", "3"),
        "L": "4",
        **dict.fromkeys("MN", "5"),
        "R": "6"
    }
    first = word[0]
    tail = []
    prev = codes.get(word[0], "")
    for ch in word[1:]:
        code = codes.get(ch, "")
        if code and code != prev:
            tail.append(code)
        if ch not in "HW":
            prev = code
    return (first + "".join(tail) + "000")[:4]


def _is_bitsquat(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    diffs = [i for i in range(len(a)) if a[i] != b[i]]
    if len(diffs) != 1:
        return False
    xor = ord(a[diffs[0]]) ^ ord(b[diffs[0]])
    return xor != 0 and (xor & (xor - 1)) == 0


def _is_combosquat(domain_root: str, brand_root: str) -> bool:
    return brand_root in domain_root and domain_root != brand_root


def url_similarity_index(url: str) -> float:
    domain = _registered_domain(url).lower()
    if not domain:
        return 50.0

    domain_root = domain.split(".")[0]

    for ref in LEGIT_DOMAINS:
        if domain == ref.lower():
            return 100.0

    suspicion = 0.0
    for ref in LEGIT_DOMAINS:
        ref = ref.lower()
        ref_root = ref.split(".")[0]

        if _normalize_homograph(domain_root) == ref_root and domain_root != ref_root:
            suspicion = max(suspicion, 90.0)
        if _is_punycode(domain):
            decoded_root = _decode_punycode_domain(domain).split(".")[0]
            if _normalize_homograph(decoded_root) == ref_root:
                suspicion = max(suspicion, 90.0)
        if _is_bitsquat(domain_root, ref_root):
            suspicion = max(suspicion, 75.0)
        if _is_combosquat(domain_root, ref_root):
            suspicion = max(suspicion, 60.0)
        if _soundex(domain_root) == _soundex(ref_root) and domain_root != ref_root:
            suspicion = max(suspicion, 40.0)

    if suspicion > 0:
        return round(100 - suspicion, 2)
    return 80.0


def url_lexical_features(url: str) -> dict:
    parsed = urlparse(url)
    return {
        "URLLength": len(url),
        "IsHTTPS": 1 if parsed.scheme == "https" else 0,
    }


_playwright = None
_browser = None


def _get_browser():
    global _playwright, _browser
    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=True)
    return _browser


def _consent_cookies_for(domain: str):
    """Cookie consent bawaan untuk domain populer yang menampilkan halaman
    persetujuan cookie di sesi baru -- supaya Playwright langsung dapat
    konten halaman sebenarnya, bukan halaman interstitial consent-nya."""
    if domain.endswith("google.com"):
        return [{"name": "CONSENT", "value": "YES+1", "domain": ".google.com", "path": "/"}]
    return []


def _fetch_html(url: str) -> str:
    browser = _get_browser()
    context = browser.new_context(user_agent=USER_AGENT)

    domain = _registered_domain(url)
    cookies = _consent_cookies_for(domain)
    if cookies:
        context.add_cookies(cookies)

    page = context.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=REQUEST_TIMEOUT * 1000)
        try:
            page.wait_for_load_state("networkidle", timeout=REQUEST_TIMEOUT * 1000)
        except PlaywrightTimeoutError:
            pass

        html = page.content()
        if len(html.splitlines()) < THIN_CONTENT_LINE_THRESHOLD:
            page.wait_for_timeout(1500)
            html = page.content()
        return html
    finally:
        page.close()
        context.close()


def _default_content_features() -> dict:
    return {
        "NoOfExternalRef": 0,
        "LineOfCode": 0,
        "NoOfSelfRef": 0,
        "NoOfImage": 0,
        "HasSubmitButton": 0,
        "NoOfJS": 0,
        "HasCopyrightInfo": 0,
        "URLTitleMatchScore": 0,
        "HasSocialNet": 0,
        "NoOfCSS": 0,
        "IsResponsive": 0,
        "HasFavicon": 0,
    }


def content_features(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    page_domain = _registered_domain(url)

    ref_tags = soup.find_all(["a", "script", "img", "iframe", "link"])
    self_ref, external_ref = 0, 0
    for tag in ref_tags:
        target = tag.get("href") or tag.get("src")
        if not target or target.strip().startswith("#"):
            continue
        full = urljoin(url, target)
        target_domain = _registered_domain(full)
        if not target_domain:
            continue
        if target_domain == page_domain:
            self_ref += 1
        else:
            external_ref += 1

    has_social = 0
    for tag in soup.find_all("a", href=True):
        href = tag["href"].lower()
        if any(social in href for social in SOCIAL_DOMAINS):
            has_social = 1
            break

    has_submit = 0
    if soup.find("input", attrs={"type": re.compile("submit", re.I)}):
        has_submit = 1
    elif soup.find("button", attrs={"type": re.compile("submit", re.I)}):
        has_submit = 1
    elif soup.find("button") and not soup.find("button", attrs={"type": True}):
        has_submit = 1

    has_favicon = 1 if soup.find("link", rel=re.compile("icon", re.I)) else 0
    is_responsive = 1 if soup.find("meta", attrs={"name": re.compile("^viewport$", re.I)}) else 0

    page_text = soup.get_text(" ", strip=True)
    has_copyright = 1 if ("©" in page_text or re.search(r"copyright", page_text, re.I)) else 0

    title_tag = soup.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""
    domain_root = page_domain.split(".")[0] if page_domain else ""

    if title_text and domain_root:
        ratio = difflib.SequenceMatcher(None, domain_root.lower(), title_text.lower()).ratio()
        if domain_root.lower() in title_text.lower():
            ratio = max(ratio, 0.8)
        title_match_score = round(ratio * 100, 2)
    else:
        title_match_score = 0.0

    css_count = (
        len(soup.find_all("link", rel=re.compile("stylesheet", re.I))) +
        len(soup.find_all("style"))
    )

    return {
        "NoOfExternalRef": external_ref,
        "LineOfCode": len(html.splitlines()),
        "NoOfSelfRef": self_ref,
        "NoOfImage": len(soup.find_all("img")),
        "HasSubmitButton": has_submit,
        "NoOfJS": len(soup.find_all("script")),
        "HasCopyrightInfo": has_copyright,
        "URLTitleMatchScore": title_match_score,
        "HasSocialNet": has_social,
        "NoOfCSS": css_count,
        "IsResponsive": is_responsive,
        "HasFavicon": has_favicon,
    }


def extract_features(raw_url: str):
    url = raw_url.strip()
    if not urlparse(url).scheme:
        url = "http://" + url

    features = url_lexical_features(url)
    features["URLSimilarityIndex"] = url_similarity_index(url)

    warning = None
    try:
        html = _fetch_html(url)
        features.update(content_features(url, html))
    except (PlaywrightTimeoutError, PlaywrightError) as exc:
        features.update(_default_content_features())
        warning = f"Halaman tidak bisa diakses ({exc.__class__.__name__}), fitur konten diisi nilai default 0."

    ordered = {name: features[name] for name in FEATURE_ORDER}
    return ordered, warning


def cleanup_browser():
    global _playwright, _browser
    if _browser:
        _browser.close()
        _browser = None
    if _playwright:
        _playwright.stop()
        _playwright = None