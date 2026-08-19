# Blender Öğrenme Rehberi — Microsoft Foundry Local

Blender'da ne yapmak istediğini anlattığında sana en uygun gerçek çözümü
öneren, tamamen offline çalışan bir RAG (Retrieval-Augmented Generation)
uygulaması. İnternet bağlantısı gerekmez (ilk kurulumdaki veri seti indirme
adımı hariç). Öneri yeterince iyi değilse "başka" diyerek bir sonraki en
uygun eşleşme istenebilir.

Veri seti: [Blender Stack Exchange](https://blender.stackexchange.com)'in
resmi Stack Exchange Data Dump'ı (archive.org, CC BY-SA 4.0 lisanslı) —
skoru yüksek ve kabul edilmiş bir cevabı olan **1.500 gerçek soru+cevap**,
her biri tek bir "rehber" kaydı olarak işlenip embed edildi.

## Mimari

```
Kullanıcı: "Düşük poly bir karakter yapmak istiyorum, Blender'da yeniyim"
      │
      ▼
[app_streamlit.py]  ──► "başka" mı istendi, yoksa yeni istek mi? (session state)
      │
      ▼
[retrieval.py - get_candidates()]
      │  1) Semantik benzerlik: sorgu embedding'i ←→ 1.500 sorunun
      │     (başlık+etiket+soru metni) embedding'i (kosinüs)
      │  2) Etiket örtüşmesi: sorunun etiketlerinden/başlık kelimelerinden
      │     kaçı kullanıcının metninde geçiyor
      │  3) Hibrit skor = 0.6 × etiket_örtüşmesi + 0.4 × semantik_benzerlik
      ▼
En uygun soru+cevap (daha önce önerilenler hariç tutularak)
      │
      ▼
[main.py - get_recommendation()]  ──► Foundry Local (phi-3.5-mini) gerçek
      cevabı adım adım bir rehbere dönüştürüp sunar
      │
      ▼
Adımlar + hangi gerçek soruya dayandığı bilgisiyle kullanıcıya cevap
```

## Kurulum (Windows)

**1. Foundry Local CLI'ı kur** (winget ile):

```powershell
winget install Microsoft.FoundryLocal
```

**2. Python bağımlılıklarını kur** (proje kökünde, tercihen bir virtual env
içinde):

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**3. Foundry Local sunucusunu başlat ve doğrula:**

```powershell
foundry server start
foundry model list
```

`server start` daemon'ı arka planda ayağa kaldırır (bir kez çalıştırman
yeterli, bilgisayarı kapatana kadar açık kalır). `model list` bir model
listesi gösteriyorsa Foundry Local çalışıyor demektir.

**4. Veri setini indir** (bir kerelik, internet gerekir):
[archive.org'daki resmi Stack Exchange Data Dump](https://archive.org/download/stackexchange/blender.stackexchange.com.7z)
mirror'ından `blender.stackexchange.com.7z` dosyasını (~200 MB) indir,
proje kökünde `dataset_raw/` klasörüne koy ve 7-Zip ile içindeki
`Posts.xml`'i aynı klasöre çıkar. Sonucun `dataset_raw/Posts.xml` olması
gerekiyor (diğer XML dosyalarına — Users, Comments, Votes vb. —
ihtiyacımız yok, silinebilir).

## Çalıştırma

```powershell
# 0) Foundry Local sunucusu çalışmıyorsa başlat (bkz. yukarı)
foundry server start

# 1) Ham veriyi işle: Posts.xml'den yüksek skorlu, kabul edilmiş
#    cevabı olan soruları filtrele, HTML'i temizle, JSON'a yaz
python -m source.prepare_dataset

# 2) Her soru+cevabı embed edip
#    data/rag.db'ye yaz
python -m source.main

# 3) Web arayüzünü başlat
streamlit run source/app_streamlit.py
```

`source/main.py` ilk çalıştırmada veritabanı boşsa otomatik ingest eder;
`dataset_raw/blender_qa.json`'ı değiştirdikten sonra yeniden ingest için
`python -m source.main --reingest` kullan. Komut satırından hızlı test
için de aynı komut kullanılabilir — "başka" yazarak alternatif iste.

`source/ingest.py` ve `source/prepare_dataset.py`,
`source/foundry_client.py` içindeki `FoundryClient` üzerinden çalışır: bu
sınıf ilgili modeli otomatik indirir (`foundry model download`) ve belleğe
yükler (`foundry model load`), sonra Foundry Local'ın OpenAI-uyumlu REST
arayüzüne bağlanan bir `openai` istemcisi kurar. Bu yaklaşım
`foundry-local-sdk` paketine bağımlı değildir — o paketin REST istemcisi
bazı kurulumlarda güncel Foundry Local sürümleriyle senkronizasyondan
çıkmış olabiliyor; `foundry` CLI'ının `-o json` çıktısı daha stabil.

Tarayıcı otomatik açılacak (genelde http://localhost:8501). "Düşük poly
bir karakter yapmak istiyorum, yeniyim" gibi bir istek yazıp test
edebilirsin. Öneriyi beğenmezsen "🔁 Başka bir şey öner" butonuna bas ya
da "başka" yaz — aynı isteğe göre ama farklı bir soru+cevap önerir.

## Proje yapısı

```
source/
  main.py             CLI giriş noktası / interaktif döngü, get_recommendation()
  app_streamlit.py     Aynı pipeline üzerine kurulu Streamlit web arayüzü
  evaluate.py           Fonksiyonel test paketi -> TEST_RESULTS.md
  config.py             Model alias'ları, yollar, hibrit skor ağırlıkları, prompt
  foundry_client.py     Foundry Local sarmalayıcısı (sohbet + embedding)
  db.py                 Rehberler + embedding'ler için SQLite katmanı
  prepare_dataset.py    Posts.xml -> dataset_raw/blender_qa.json (tek seferlik)
  ingest.py             blender_qa.json -> embed -> data/rag.db
  retrieval.py           Hibrit skorla (etiket örtüşmesi + semantik) getirme
dataset_raw/            İndirilen ham veri + işlenmiş JSON (gitignore'da)
data/rag.db             İlk çalıştırmada oluşur
```

## Yapılandırma

`source/config.py` içinde değiştirebilecekleriniz:
- `CHAT_MODEL_ALIAS` / `EMBEDDING_MODEL_ALIAS` — `foundry model list`'teki herhangi bir takma ad
- `TOP_K` — bir seferde kaç aday değerlendirileceği
- `TAG_WEIGHT` / `SEMANTIC_WEIGHT` — hibrit skordaki ağırlıklar (toplamları 1 olmalı)
- `SYSTEM_PROMPT` — modele verilen rehber-oluşturma/atıf talimatları

`source/prepare_dataset.py` içinde değiştirebilecekleriniz:
- `MIN_QUESTION_SCORE` — bir sorunun veri setine girmesi için gereken minimum topluluk skoru
- `MAX_TUTORIALS` — ingest edilecek maksimum soru+cevap sayısı (yerel, GPU'suz embedding süresini makul tutmak için)

## Bilinen sınırlamalar

- Getirme, tıpkı orijinal projede olduğu gibi her zaman en iyi K adayı
  döndürür — sabit bir benzerlik eşiği yok. Alakasız bir istek geldiğinde
  "iyi bir eşleşme yok" kararını modelin kendisi, sistem promptundaki
  talimata göre veriyor (retrieved soru+cevap gerçekten alakasızsa
  zorlamadan reddediyor).
- Bu geliştirme makinesinde (özel GPU olmadan) soru başına ortalama
  yanıt süresi birkaç saniyedir. Gelişmiş donanımla daha az olabilir.
