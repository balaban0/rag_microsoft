"""Blender öğrenme rehberi asistanı için merkezi yapılandırma."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_RAW_DIR = BASE_DIR / "dataset_raw"
DATASET_JSON_PATH = DATASET_RAW_DIR / "blender_qa.json"
POSTS_XML_PATH = DATASET_RAW_DIR / "Posts.xml"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "rag.db"

# Foundry Local model takma adları (çalışma zamanında gerçek model id'lerine çözülür).
CHAT_MODEL_ALIAS = "phi-3.5-mini"
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

TOP_K = 3

# Hibrit getirme ağırlıkları: aday rehberleri sıralarken etiket/anahtar-kelime
# örtüşmesine mi yoksa semantik benzerliğe mi ne kadar ağırlık verileceği.
TAG_WEIGHT = 0.6
SEMANTIC_WEIGHT = 0.4

# "Bana bir sonraki en iyi öneriyi ver" olarak tanınan ifadeler (yeni bir
# soru yerine).
ANOTHER_REQUEST_PHRASES = (
    "başka",
    "baska",
    "başka bir şey",
    "başka öner",
    "farklı bir şey",
    "farkli bir sey",
)

# Modelin, iyi bir eşleşme bulunamadığında birebir kullanması istenen cümle.
# main.py'de aday hiç yokken (LLM'e sorulmadan) ve evaluate.py'de bu cümlenin
# varlığını kontrol ederken de aynı metin kullanılıyor -- tek bir kaynak.
NO_MATCH_MESSAGE = "Blender bilgi tabanımda buna uygun iyi bir eşleşme bulamadım."

SYSTEM_PROMPT = (
    "Sen bir Blender öğrenme rehberi asistanısın. Sana Blender Stack "
    "Exchange'den, kullanıcının Blender'da yapmak istediği şeyle en iyi "
    "eşleşen GERÇEK bir soru ve onun kabul edilmiş cevabı veriliyor.\n\n"
    "Bu cevabı, kullanıcının anlattığı hedefe ve (belirtmişse) deneyim "
    "seviyesine uygun, net, teşvik edici, adım adım bir rehbere dönüştür. "
    "SADECE verilen soru/cevaptaki bilgiyi kullan -- orada olmayan adım, "
    "menü adı ya da kısayol uydurma. Cevabı numaralı adımlara ayırman ve "
    "ilgili etiket/araçları isimleriyle anman uygun.\n\n"
    "Kullanıcının mesajı gerçek bir istek değil de bir selamlaşma/sohbet "
    "ise (ör. \"merhaba\", \"teşekkürler\"), bunu yanıtsız bir istek gibi "
    "ELE ALMA -- doğal ve kısa bir şekilde cevap ver, gerçek topluluk "
    "cevaplarına dayanarak Blender teknikleri önerebildiğini belirt.\n\n"
    "Verilen soru/cevap her zaman bulunabilen en yakın eşleşmedir ama "
    "kullanıcının sorduğu şeyi gerçekten karşılamıyor olabilir. Açıkça "
    "karşılamıyorsa -- yanlış araç, yanlış problem, gerçek bir örtüşme yok "
    "-- bunu zorlayarak bir cevaba dönüştürme. Bunun yerine BİREBİR şunu "
    f"yanıtla: \"{NO_MATCH_MESSAGE}\" Yanıtlarını her zaman Türkçe ver. "
    "Dışarıdan bilgi kullanma, uydurma yapma."
)
