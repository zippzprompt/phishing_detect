# Daftar domain legitimate populer, dipakai sebagai referensi untuk
# menghitung pendekatan URLSimilarityIndex (kemiripan URL yang dimasukkan
# user terhadap domain-domain terkenal, untuk menangkap serangan
# typosquatting / homograph / combosquatting).
#
# Ini BUKAN daftar resmi dari dataset PhiUSIIL (algoritma similarity index
# aslinya tidak dipublikasikan secara rinci) -- ini adalah pendekatan
# praktis dengan konsep yang sama: TF-IDF character n-gram + cosine
# similarity terhadap domain populer.

LEGIT_DOMAINS = [
    # Tech / email / cloud
    "google.com", "gmail.com", "youtube.com", "microsoft.com", "outlook.com",
    "live.com", "office.com", "apple.com", "icloud.com", "amazon.com",
    "aws.amazon.com", "yahoo.com", "adobe.com", "dropbox.com", "zoom.us",
    "github.com", "gitlab.com", "wordpress.com", "cloudflare.com",
    # Social media
    "facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com",
    "tiktok.com", "pinterest.com", "reddit.com", "whatsapp.com",
    "telegram.org", "snapchat.com", "discord.com",
    # E-commerce / marketplace (termasuk lokal Indonesia)
    "ebay.com", "aliexpress.com", "alibaba.com", "shopee.co.id",
    "tokopedia.com", "bukalapak.com", "lazada.co.id", "blibli.com",
    "olx.co.id",
    # Perbankan & pembayaran (global + Indonesia)
    "paypal.com", "visa.com", "mastercard.com", "stripe.com",
    "bankofamerica.com", "chase.com", "wellsfargo.com", "hsbc.com",
    "bca.co.id", "bri.co.id", "bni.co.id", "mandiri.co.id", "cimbniaga.co.id",
    "ocbcnisp.com", "danamon.co.id", "permatabank.com", "gopay.co.id",
    "ovo.id", "dana.id", "linkaja.id",
    # Pemerintahan / pendidikan Indonesia
    "go.id", "kemdikbud.go.id", "pajak.go.id", "bpjs-kesehatan.go.id",
    "ac.id", "umk.ac.id",
    # Streaming / hiburan
    "netflix.com", "spotify.com", "disneyplus.com", "twitch.tv",
    # Berita / referensi
    "wikipedia.org", "cnn.com", "bbc.com", "detik.com", "kompas.com",
    "tempo.co",
    # Travel
    "booking.com", "airbnb.com", "traveloka.com", "tiket.com",
    "garuda-indonesia.com",
]
