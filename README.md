# Yerel RAG Soru-Cevap Asistanı (Foundry Local)

"Microsoft Foundry Local ile Yerel RAG AI Asistanı" yaz programı için
geliştirilmiş, tamamen çevrimdışı çalışan bir doküman soru-cevap
asistanı. İlgili pasajları yerel olarak (SQLite + gömme vektörleri)
bularak ve bunları [Microsoft Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/what-is-foundry-local)
üzerinden çalışan yerel bir LLM'e vererek küçük bir doküman koleksiyonu
hakkındaki soruları yanıtlar — çıkarım (inference) sırasında bulut hesabı
veya ağ çağrısı gerekmez.

## Nasıl çalışır

1. **Alım (Ingestion)** (`ingest.py`): `docs/` klasöründeki dokümanlar
   paragraf tabanlı parçalara (chunk) bölünür, yerel bir gömme (embedding)
   modeliyle vektörleştirilir ve kaynak dosya adlarıyla birlikte bir
   SQLite veritabanında (`data/rag.db`) saklanır.
2. **Getirme (Retrieval)** (`retrieval.py`): kullanıcının sorusu aynı
   modelle vektörleştirilir, kosinüs benzerliği kullanılarak saklanan
   her parçayla karşılaştırılır ve en alakalı ilk K (top-K) parça
   seçilir.
3. **Üretim (Generation)** (`foundry_client.py`, `main.py`): getirilen
   parçalar sistem promptlu bir bağlama (context) eklenir ve yerel
   sohbet modeli bu bağlama dayalı bir yanıt üretir. Bağlam yanıtı
   içermiyorsa asistan tahmin yürütmek yerine bunu belirtir. Sıradan
   selamlaşmalar/küçük sohbetler ("merhaba", "teşekkürler") ayrıca
   tanınır ve yanıtlanamaz sorular olarak değil, doğal bir şekilde
   yanıtlanır.

```
Kullanıcı sorusu -> vektörleştir -> SQLite parçalarıyla kosinüs benzerliği -> ilk K parça
              -> bağlam + soru -> yerel LLM (Foundry Local) -> yanıt
```

## Gereksinimler

- Windows, macOS veya Linux
- Python 3.9+
- [Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/get-started)
  kurulu olmalı ve `foundry` CLI'ı PATH üzerinde erişilebilir olmalı
  (Windows: `winget install Microsoft.FoundryLocal`)

## Kurulum

```powershell
cd rag_assistant
pip install -r requirements.txt
```

`foundry_client.py`, bazı kurulumlarda REST istemcisi güncel Foundry
Local sunucu sürümleriyle senkronizasyondan çıkmış olan
`foundry-local-sdk` Python paketi yerine `foundry` CLI'ını doğrudan
yönetir (`server status/start`, `model download/load/info`). pip
bağımlılığı olarak yalnızca `openai` ve `numpy` gereklidir.

## Çalıştırma

```powershell
python main.py
```

İlk çalıştırmada bu komut şunları yapar:
- Foundry Local servisini başlatır ve henüz önbelleğe alınmamışsa sohbet
  modelini (`phi-3.5-mini`) ve gömme modelini (`qwen3-embedding-0.6b`)
  indirir,
- `docs/` klasöründeki her `.md`/`.txt` dosyasını `data/rag.db`'ye alır,
- soru sorabileceğiniz interaktif bir istem (prompt) açar.

Çıkmak için `exit` veya `quit` yazın. `docs/` içindeki dokümanları
değiştirdikten sonra yeniden alımı zorlamak için
`python main.py --reingest` kullanın.

## Kendi dokümanlarınızı ekleme

`docs/` klasörüne herhangi bir `.md` veya `.txt` dosyası bırakın ve
`python main.py --reingest` komutunu çalıştırın. Dokümanları makul
ölçüde kısa tutun (ders notları, SSS, kılavuzlar) — parçalar
`CHUNK_MAX_CHARS`'a kadar (bkz. `config.py`) paragraf sınırlarında
bölünür.

## Web Arayüzü (Streamlit)

CLI'nin kullandığı aynı `answer_query()` işlem hattı üzerine kurulu,
sade, sohbet tarzı bir web ön yüzü:

```powershell
streamlit run app_streamlit.py
```

http://localhost:8501 adresinde açılır. Kenar çubuğunda alınan kaynak
dokümanlar listelenir; sohbet alanında her yanıt, alındığı kaynak
dosya(lar) ile birlikte gösterilir.

## Test Etme

`evaluate.py`, program planının 5. hafta işlevsel test kilometre taşını
gerçekleştirir: sabit bir yanıtlanabilir ve yanıtlanamaz soru kümesi,
iki selamlaşma/küçük sohbet regresyon senaryosu, artı uç durumlar (boş
girdi, belirsiz/genel bir soru).

```powershell
python evaluate.py
```

Bu komut, yanıt süreleriyle birlikte bir geçti/kaldı raporunu
`TEST_RESULTS.md` dosyasına yazar. Yanıtlanabilir sorular, beklenen
kaynak doküman getirildiğinde geçer; yanıtlanamaz sorular ise yanıt bir
ret gibi okunduğunda geçer (geniş kapsamlı bir anahtar kelime kontrolü —
model her seferinde reddini sistem promptunun tam ifadesini tekrarlamak
yerine kendi cümleleriyle ifade ettiğinden, bu doğası gereği kesin
eşleşme değil, yaklaşık bir kontroldür). `docs/`, `config.py` veya
prompt değiştikten sonra yeniden çalıştırın.

## Proje yapısı

```
rag_assistant/
  main.py             CLI giriş noktası / interaktif döngü
  app_streamlit.py     Aynı pipeline üzerine kurulu Streamlit web arayüzü
  evaluate.py           İşlevsel test paketi -> TEST_RESULTS.md
  config.py             Model takma adları, yollar, parçalama + prompt ayarları
  foundry_client.py     Foundry Local sarmalayıcısı (sohbet + gömme)
  db.py                 Parçalar + gömme vektörleri için SQLite depolama
  ingest.py             Doküman parçalama + alım işlem hattı
  retrieval.py           Kosinüs benzerliğiyle ilk-K getirme
  docs/                  Bilgi tabanı: 16 kısa not. 12'si bu projenin
                          kendisi hakkında (RAG, Foundry Local, gömme
                          vektörleri, SQLite, prompt mühendisliği, mimari,
                          proje yapısı, parçalama, model ödünleşimleri,
                          test etme, web arayüzü, SSS) + bilgi tabanının
                          tek bir alana özgü (hardcoded) olmadığını
                          göstermek için eklenen 4 alakasız konu (Blender
                          modelleme, Unity URP, anlatı tasarımı, mesh/LOD)
                          -- herhangi bir kısa doküman çalışır
  data/rag.db            İlk çalıştırmada oluşturulur
  TEST_RESULTS.md         evaluate.py tarafından oluşturulur
```

## Yapılandırma

Değiştirmek için `config.py` dosyasını düzenleyin:
- `CHAT_MODEL_ALIAS` / `EMBEDDING_MODEL_ALIAS` — `foundry model list`'ten herhangi bir takma ad
- `TOP_K` — soru başına kaç parçanın getirileceği
- `CHUNK_MAX_CHARS` — alım sırasında parça başına maksimum karakter
- `SYSTEM_PROMPT` — modele verilen bağlamlandırma/atıf talimatları

## Bilinen sınırlamalar

- Getirme işlemi, Python içinde saklanan tüm parçalar üzerinde
  kaba kuvvet (brute-force) kosinüs benzerliğiyle yapılır — küçük
  doküman kümeleri için uygundur, büyük külliyatlara ölçeklenmek için
  tasarlanmamıştır (bunun için gerçek bir vektör veritabanı gerekir).
- Bilgi tabanı yalnızca bu projenin kendi alanını kapsar (RAG, Foundry
  Local, gömme vektörleri, SQLite, test etme vb.). `docs/` dışındaki
  gerçek sorular, modelin genel bilgisinden yanıtlanmak yerine doğru
  bir şekilde reddedilir — bu kasıtlıdır (bkz. `05_prompt_engineering.md`
  / `10_testing_and_evaluation.md`), bir hata değildir. Yanıtlayabildiği
  konuları genişletmek için `docs/` klasörüne daha fazla doküman ekleyip
  yeniden alım yapın.
- Bu geliştirme makinesinde (özel GPU olmadan), soru başına ortalama
  yanıt süresi ~6-10 saniyedir; bu, planın ~1-3 saniyelik hedefinin
  üzerindedir — güncel sayılar ve iyileştirme seçenekleri (daha küçük
  model, daha düşük `TOP_K`) için `TEST_RESULTS.md` dosyasına bakın.
