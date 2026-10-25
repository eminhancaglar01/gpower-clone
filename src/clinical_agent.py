"""
src/clinical_agent.py: Türkçe Klinik Soru Ajanı (Clinical Trial AI Agent)

Hekim ve klinik araştırmacıların Türkçe araştırma senaryolarını anlayarak:
1. İlgili test ailesini sınıflandırır (t2-indep, t-paired, anova-oneway, chi2-contingency, multireg-r2, ambiguous, unsupported).
2. Parametreleri çıkarır ve eksik bilgileri tespit eder.
3. Hesaplama motorunu/MCP aracını çağırır (ASLA kendisi N veya güç tahmin etmez).
4. Hesaplama sonucunu hekimin anlayacağı klinik dille raporlar.
"""

import re
import time
from typing import Dict, Any, List, Optional
from .mcp_server import t2_indep_a_priori_tool


SUPPORTED_FAMILIES = {
    "t2-indep": "İki Bağımsız Grup Ortalama Farkı (Bağımsız İki Örneklem t Testi)",
    "t-paired": "Eşleştirilmiş / Tekrarlı Ölçümler t Testi",
    "anova-oneway": "Tek Yönlü Varyans Analizi (Üç veya Daha Fazla Grup)",
    "chi2-contingency": "Ki-Kare Kontenjans Testi (Kategorik Oran Karşılaştırması)",
    "multireg-r2": "Çoklu Doğrusal Regresyon (R² Değişimi)",
    "ambiguous": "Belirsiz / Yetersiz Bilgi İçeren Senaryo",
    "unsupported": "Desteklenmeyen Test Ailesi (Örn. Sağkalım / Cox Analizi)"
}


class ClinicalQuestionAgent:
    """Türkçe Klinik Araştırma Senaryosu Güç Analizi Ajanı."""

    def __init__(self):
        self.call_logs: List[Dict[str, Any]] = []

    def classify_scenario(self, text: str) -> Dict[str, Any]:
        """
        Klinik metni analiz ederek uygun test ailesini ve güven skorunu belirler.
        """
        text_lower = text.lower()

        # 1. Desteklenmeyen (Survival, Cox, ROC vb.)
        if any(w in text_lower for w in ["sağkalım", "survival", "cox", "kaplan-meier", "hazard ratio", "roc eğrisi"]):
            return {"label": "unsupported", "confidence": 0.95, "reason": "Sağkalım / Cox analizi şu anda desteklenmemektedir."}

        # 2. Belirsiz (Yetersiz bilgi)
        if any(w in text_lower for w in ["hatırlamıyorum", "belirsiz", "emin değilim", "bilmiyorum"]) or len(text.strip().split()) < 5:
            return {"label": "ambiguous", "confidence": 0.90, "reason": "Çalışma tasarımı ve gruplar hakkında yetersiz bilgi."}

        # 3. Ki-Kare / Kategorik — KESİN sinyaller (kontenjans, ki-kare, 2x2, yüzde bağlamı)
        # Bu kural t2-indep'ten önce kontrol edilir çünkü Q4 hem "iki grupta" hem "kontenjans" içerir.
        if any(w in text_lower for w in [
            "ki-kare", "kontenjans", "2x2", "iyileşme yüzdesi", "geçirme oranı",
            "başarı oranı", "iyileşme oranı", "mortalite oranı", "kategorik"
        ]):
            return {"label": "chi2-contingency", "confidence": 0.88, "reason": "Kategorik değişken ve oran karşılaştırması."}

        # 4. İki Bağımsız Grup t Testi (açık t-testi / iki grup / ortalama fark sinyalleri)
        if any(w in text_lower for w in [
            "iki grup", "2 grup", "iki bağımsız", "plasebo ve tedavi", "kontrol ve deney",
            "iki ayrı grup", "iki farklı tedavi", "iki farklı anestezi", "iki farklı cerrahi",
            "iki farklı", "t testi", "ortalama farkı", "bağımsız iki", "bağımsız iki grup",
            "bağımsız grup"
        ]):
            return {"label": "t2-indep", "confidence": 0.94, "reason": "İki bağımsız grubun sayısal ortalamalarının karşılaştırması."}

        # 5. ANOVA (3 veya daha fazla grup)
        if any(w in text_lower for w in ["üç grup", "3 grup", "üç farklı doz", "3 farklı doz", "3 farklı kol", "üç farklı kol", "dört grup", "4 grup", "anova", "varyans analizi"]):
            return {"label": "anova-oneway", "confidence": 0.92, "reason": "İkiden fazla grubun ortalama karşılaştırması."}

        # 6. Eşleştirilmiş / Tekrarlı Ölçüm t Testi (Pre-post)
        if any(w in text_lower for w in ["önce-sonra", "önce ve sonra", "tedavi öncesi", "aynı hastaların", "pre-post", "eşleştirilmiş"]):
            return {"label": "t-paired", "confidence": 0.91, "reason": "Aynı grupta tekrarlanan bağımlı ölçümler."}

        # 7. Çoklu Regresyon
        if any(w in text_lower for w in ["çoklu regresyon", "regresyon", "yordama", "r2", "r kare", "bağımsız değişkenler"]):
            return {"label": "multireg-r2", "confidence": 0.89, "reason": "Çoklu değişken yordama analizi."}

        # Varsayılan belirsiz
        return {"label": "ambiguous", "confidence": 0.60, "reason": "Çalışma tasarımı net anlaşılamadı."}

    def extract_parameters(self, text: str) -> Dict[str, Any]:
        """Metin içerisinden sayısal parametreleri ayıklar."""
        params = {
            "tails": 2,
            "d": None,
            "alpha": 0.05,
            "power": 0.80,
            "ratio": 1.0
        }

        text_lower = text.lower()

        # Kuyruk yönü
        if any(w in text_lower for w in ["daha üstün", "üstünlük", "daha yüksek", "daha düşük", "tek yönlü", "tek taraflı"]):
            params["tails"] = 1
        elif any(w in text_lower for w in ["fark olup olmadığı", "iki yönlü", "iki taraflı"]):
            params["tails"] = 2

        # Etki büyüklüğü (d)
        d_match = re.search(r'\b(?:d|etki büyüklüğü|cohen)\s*[=:]?\s*([0-9]+[.,]?[0-9]*)', text_lower)
        if d_match:
            params["d"] = float(d_match.group(1).replace(",", "."))
        elif "orta etki" in text_lower:
            params["d"] = 0.50
        elif "küçük etki" in text_lower:
            params["d"] = 0.20
        elif "büyük etki" in text_lower:
            params["d"] = 0.80

        # Alfa (alpha)
        alpha_match = re.search(r'\b(?:alfa|alpha|anlamlılık|p)\s*[=:]?\s*(0[.,][0-9]+)', text_lower)
        if alpha_match:
            params["alpha"] = float(alpha_match.group(1).replace(",", "."))

        # Güç (power)
        power_match = re.search(r'\b(?:güç|power)\s*[=:]?\s*(%?\s*[0-9]+[.,]?[0-9]*%?)', text_lower)
        if power_match:
            raw_p = power_match.group(1).replace("%", "").strip().replace(",", ".")
            val = float(raw_p)
            params["power"] = val / 100.0 if val > 1.0 else val

        # Tahsis Oranı (ratio)
        ratio_match = re.search(r'\b(?:oran|ratio|tahsis)\s*[=:]?\s*([0-9]+[.,]?[0-9]*)', text_lower)
        if ratio_match:
            params["ratio"] = float(ratio_match.group(1).replace(",", "."))
        elif "2:1" in text_lower or "2 kat" in text_lower:
            params["ratio"] = 2.0
        elif "1:2" in text_lower:
            params["ratio"] = 0.5

        return params

    def answer_clinical_question(self, question: str) -> Dict[str, Any]:
        """
        Klinik araştırma sorusunu işler, sınıflandırır, motoru çağırır ve
        açıklayıcı Türkçe tıbbi yanıt üretir.
        """
        start_time = time.perf_counter()
        classification = self.classify_scenario(question)
        label = classification["label"]
        confidence = classification["confidence"]

        log_entry = {
            "question": question,
            "classification": classification,
            "tool_called": None,
            "tool_inputs": None,
            "tool_output": None,
            "duration_ms": 0.0,
            "status": "COMPLETED"
        }

        # Sınıflandırma güveni düşükse veya t2-indep değilse
        if confidence < 0.75 or label in ["ambiguous", "unsupported", "t-paired", "anova-oneway", "chi2-contingency", "multireg-r2"]:
            if label == "ambiguous":
                response_text = (
                    "Sayın Araştırmacı, sorunuzdaki araştırma tasarımı tam anlaşılamadı. "
                    "Lütfen çalışmanızdaki grup sayısını, bağımsız olup olmadıklarını ve "
                    "ölçülen değişkenin türünü (sayısal/kategorik) belirtiniz."
                )
            elif label == "t2-indep":
                response_text = "Tasarım güveni yetersiz. Lütfen çalışma detaylarını netleştiriniz."
            else:
                family_name = SUPPORTED_FAMILIES.get(label, label)
                response_text = (
                    f"Araştırma tasarımınız '{family_name}' olarak belirlenmiştir. "
                    f"Ancak bu modül şu anda yalnızca iki bağımsız grubun t testini (t2-indep) "
                    f"desteklemektedir. Diğer test aileleri için lütfen ilgili analitik araçları kullanınız."
                )

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            log_entry["duration_ms"] = round(duration_ms, 2)
            self.call_logs.append(log_entry)
            return {
                "label": label,
                "confidence": confidence,
                "response": response_text,
                "calculation": None
            }

        # Parametreleri çıkar
        params = self.extract_parameters(question)
        if params["d"] is None:
            response_text = (
                "Çalışmanız iki bağımsız grup t testi (t2-indep) için uygundur. "
                "Ancak örneklem hesabı yapabilmek için beklenen etki büyüklüğü (Cohen's d) "
                "veya gruplar arası beklenen ortalama fark ve standart sapma bilgisi eksiktir. "
                "Lütfen hedeflenen etki büyüklüğünü (örn. d=0.50) belirtiniz."
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            log_entry["duration_ms"] = round(duration_ms, 2)
            self.call_logs.append(log_entry)
            return {
                "label": label,
                "confidence": confidence,
                "response": response_text,
                "calculation": None
            }

        # MCP Aracı üzerinden motoru çağır (ASLA KENDİSİ N ÜRETMEZ)
        log_entry["tool_called"] = "t2_indep_a_priori"
        log_entry["tool_inputs"] = params
        calc_result = t2_indep_a_priori_tool(
            tails=params["tails"],
            d=params["d"],
            alpha=params["alpha"],
            power=params["power"],
            ratio=params["ratio"]
        )
        log_entry["tool_output"] = calc_result

        # Hekim dostu Türkçe açıklama oluştur
        n1 = calc_result["n1"]
        n2 = calc_result["n2"]
        n_total = calc_result["n_total"]
        actual_power = calc_result["actual_power"]
        critical_t = calc_result["critical"]
        df = calc_result["df"]

        tail_desc = "çift yönlü (iki taraflı)" if params["tails"] == 2 else "tek yönlü (üstünlük)"
        ratio_desc = "eşit gruplar (1:1)" if params["ratio"] == 1.0 else f"tahsis oranı {params['ratio']}"

        response_text = (
            f"Klinik Çalışma Güç Analizi Raporu:\n\n"
            f"• Tasarım: İki Bağımsız Grup t Testi (t2-indep)\n"
            f"• Test Yönü: {tail_desc}\n"
            f"• Parametreler: Etki Büyüklüğü d={params['d']}, Alfa={params['alpha']}, Hedef Güç=%{params['power']*100:.0f}, {ratio_desc}\n\n"
            f"Gereken Örneklem Büyüklüğü:\n"
            f"  - 1. Grup: {n1} hasta\n"
            f"  - 2. Grup: {n2} hasta\n"
            f"  - TOPLAM: {n_total} hasta\n\n"
            f"İstatistiksel Çıktılar: Gerçekleşen Güç = %{actual_power*100:.2f}, "
            f"Kritik t = {critical_t}, Serbestlik Derecesi (df) = {df}.\n"
            f"Protokol Önerisi: Hedeflenen %{params['power']*100:.0f} istatistiksel gücü sağlamak için "
            f"çalışmaya en az toplam {n_total} hasta dahil edilmelidir."
        )

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        log_entry["duration_ms"] = round(duration_ms, 2)
        self.call_logs.append(log_entry)

        return {
            "label": label,
            "confidence": confidence,
            "response": response_text,
            "calculation": calc_result
        }
