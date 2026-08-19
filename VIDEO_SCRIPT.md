# Video Sunum Metni (~2 dakika)

Ekran kaydı öneriyorum: terminal + tarayıcı (Streamlit) yan yana veya sırayla.
Parantez içindekiler ekranda ne göstereceğini belirtir, sesli okunmaz.

---

**[0:00 - 0:15] Giriş**
(Ekranda: proje klasörü / README açık)

"Merhaba, ben bu yaz stajımda Microsoft Foundry Local kullanarak tamamen
offline çalışan bir RAG — yani Retrieval-Augmented Generation — soru-cevap
asistanı geliştirdim. Yani internet bağlantısı olmadan, kendi
dokümanlarımdan bilgi çekip cevap üreten bir yapay zeka."

**[0:15 - 0:35] Problem / Neden RAG**
(Ekranda: docs/ klasörü)

"Normal bir dil modeli sadece eğitildiği genel bilgiyle cevap verir ve
bilmediği konularda uydurabilir. RAG bunu çözüyor: önce soruya en yakın
bilgiyi kendi dokümanlarımdan buluyor, sonra bu bilgiyi modele context
olarak veriyor. Böylece cevaplar hem doğru kaynağa dayanıyor hem de
halüsinasyon riski azalıyor."

**[0:35 - 1:05] Canlı Demo**
(Terminalde `python main.py` çalıştır, ya da Streamlit arayüzü aç)

"Şimdi canlı gösterelim. Sistemde şu an 16 doküman var — projenin kendi
konuları ve test amaçlı eklediğim alakasız konular. Mesela 'Foundry
Local nedir?' diye soruyorum..."
(Cevabı ve kaynak atıflarını ekranda göster)

"Gördüğünüz gibi hangi dokümandan geldiğini de söylüyor. Şimdi bilgi
tabanında olmayan bir şey soralım, mesela 'Fransa'nın başkenti nedir?'"
(Cevabı göster — reddediyor, uydurmuyor)

"Uydurmuyor, çünkü sistem prompt'u ona sadece dokümanlardan cevap
vermesini söylüyor. Ama 'merhaba' dersem de doğal karşılıyor, onu da ret
olarak algılamıyor."

**[1:05 - 1:35] Mimari ve Test**
(Ekranda: proje dosya yapısı ya da TEST_RESULTS.md)

"Mimari kısaca şöyle: dokümanlar parçalara bölünüp embedding'e çevriliyor
ve SQLite'ta saklanıyor. Soru geldiğinde cosine similarity ile en alakalı
parçalar bulunuyor, bunlar Foundry Local üzerinde çalışan yerel bir dil
modeline gönderiliyor. Hem komut satırı hem Streamlit web arayüzü var.
Ayrıca otomatik bir test suite yazdım — cevaplanabilir, cevaplanamaz ve
selamlaşma senaryolarını kapsayan 21 test case, hepsi geçiyor."

**[1:35 - 2:00] Kapanış / Öğrenilenler**
(Ekranda: proje ana ekranı)

"En çok öğrendiğim şey, Foundry Local'ın CLI ve SDK sürümleri arasında
uyumsuzluklar olabildiği ve bunları test ede ede çözmek gerektiğiydi. Ama
sonuçta tamamen offline, kaynak gösteren ve güvenilir bir soru-cevap
sistemi ortaya çıktı. Dinlediğiniz için teşekkürler."

---

## Notlar
- Toplam ~260 kelime, ortalama konuşma hızıyla (~130 kelime/dk) ~2 dakika.
- Demo kısmını canlı yazarken biraz sürebilir; gerekirse "Fransa'nın
  başkenti" sorusunu önceden hazırlayıp kopyala-yapıştır ile hızlandır.
- Ekran kaydına başlamadan önce `python main.py` ya da
  `streamlit run app_streamlit.py` açık ve modeli önceden bir kez
  çalıştırıp ısındırmış olman iyi olur (ilk soru daha hızlı cevaplanır).
