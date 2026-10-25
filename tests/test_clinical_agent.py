"""
tests/test_clinical_agent.py: Türkçe Klinik Soru Ajanı 10 Soruluk Değerlendirme Seti ve Karşılaştırma Testleri
"""

import pytest
from src.clinical_agent import ClinicalQuestionAgent


SCENARIOS_BENCHMARK = [
    {
        "id": "Q1",
        "question": "Yeni geliştirilen bir antihipertansif ilacın sistolik kan basıncını standart tedaviye göre düşürmedeki etkinliğini iki bağımsız hasta grubunda karşılaştırmak istiyoruz. İki yönlü hipotezde orta düzeyde bir etki büyüklüğü (d=0.50), %5 alfa ve %80 güç için kaç hasta gerekir?",
        "expected_label": "t2-indep",
        "expected_n": 128,
        "is_supported": True
    },
    {
        "id": "Q2",
        "question": "Tip 2 diyabet hastalarında 3 aylık egzersiz programının tedavi öncesi ve sonrası HbA1c değerlerinde oluşturduğu değişimi aynı hastaların takibiyle incelemek istiyoruz.",
        "expected_label": "t-paired",
        "expected_n": None,
        "is_supported": False
    },
    {
        "id": "Q3",
        "question": "Depresyon tedavisinde 10 mg, 20 mg ve 40 mg olmak üzere 3 farklı doz grubunun Hamilton depresyon ölçeği puanlarını karşılaştıracağız.",
        "expected_label": "anova-oneway",
        "expected_n": None,
        "is_supported": False
    },
    {
        "id": "Q4",
        "question": "Aşılanan ve aşılanmayan iki grupta kış sezonunda influenza geçirme oranlarını ve iyileşme yüzdelerini 2x2 kontenjans tablosunda karşılaştıracağız.",
        "expected_label": "chi2-contingency",
        "expected_n": None,
        "is_supported": False
    },
    {
        "id": "Q5",
        "question": "Kardiyovasküler risk araştırmasında yaş, bel çevresi ve sigara paket-yılı bağımsız değişkenlerinin koroner kalsiyum skorunu yordama gücünü çoklu regresyon R2 değişimiyle hesaplamak istiyoruz.",
        "expected_label": "multireg-r2",
        "expected_n": None,
        "is_supported": False
    },
    {
        "id": "Q6",
        "question": "Onkoloji servisinde yeni kemoterapi rejiminin standart rejime göre tümör çapını küçültmede daha üstün olduğunu (tek yönlü) göstermek istiyoruz. Etki büyüklüğü d=0.5, alfa=0.05 ve hedef güç %95 olduğunda iki bağımsız gruba kaç hasta alınmalıdır?",
        "expected_label": "t2-indep",
        "expected_n": 176,
        "is_supported": True
    },
    {
        "id": "Q7",
        "question": "Ortopedi kliniğinde iki ayrı cerrahi tekniğin ameliyat süreleri arasındaki ortalama farkını araştırıyoruz. İki grup t testi için d=0.5, alfa=0.05, güç=0.95 ve eşit grup tahsisinde kaç hasta gerekir?",
        "expected_label": "t2-indep",
        "expected_n": 210,
        "is_supported": True
    },
    {
        "id": "Q8",
        "question": "Hastalara bazı tedaviler uyguladık ancak grupların kaç kişi olduğu ve ölçümün bağımlı mı bağımsız mı olduğu belirsiz, ne yapmalıyım?",
        "expected_label": "ambiguous",
        "expected_n": None,
        "is_supported": False
    },
    {
        "id": "Q9",
        "question": "Evre 4 akciğer kanseri hastalarında 5 yıllık kümülatif sağkalım süresi ve zaman bağımlı Cox orantılı tehlikeler regresyonu modellemesi yapmak istiyoruz.",
        "expected_label": "unsupported",
        "expected_n": None,
        "is_supported": False
    },
    {
        "id": "Q10",
        "question": "Pediatrik cerrahide iki farklı anestezi yönteminin derlenme süresi ortalama farkını 2:1 oranında (deney grubuna iki kat hasta) planlıyoruz. İki bağımsız grup t testi için d=0.5, alfa=0.05, güç=%90 olduğunda örneklem ne olmalıdır?",
        "expected_label": "t2-indep",
        "expected_n": 192,
        "is_supported": True
    }
]


class TestClinicalAgent:
    """Türkçe Klinik Soru Ajanı Testleri."""

    def test_benchmark_classification_accuracy(self):
        """10 soruluk değerlendirme setinde etiketleme doğruluğunu ölçer."""
        agent = ClinicalQuestionAgent()
        correct_count = 0

        for item in SCENARIOS_BENCHMARK:
            res = agent.answer_clinical_question(item["question"])
            label = res["label"]
            assert label == item["expected_label"], (
                f"Soru {item['id']} için beklenen {item['expected_label']}, alınan {label}"
            )
            correct_count += 1

            if item["is_supported"]:
                assert res["calculation"] is not None
                assert res["calculation"]["n_total"] == item["expected_n"]
                assert "Klinik Çalışma Güç Analizi Raporu" in res["response"]
            else:
                assert res["calculation"] is None

        accuracy = (correct_count / len(SCENARIOS_BENCHMARK)) * 100.0
        print(f"\nTürkçe Klinik Soru Ajanı Doğruluk Oranı: %{accuracy:.2f} ({correct_count}/{len(SCENARIOS_BENCHMARK)})")
        assert accuracy == 100.0

    def test_tool_call_logs_and_metrics(self):
        """Araç çağrı loglarının ve süre ölçümlerinin kaydedildiğini doğrular."""
        agent = ClinicalQuestionAgent()
        # Bir soru çözdür
        agent.answer_clinical_question(SCENARIOS_BENCHMARK[0]["question"])
        assert len(agent.call_logs) == 1
        log = agent.call_logs[0]
        assert log["tool_called"] == "t2_indep_a_priori"
        assert log["duration_ms"] > 0
        assert log["tool_output"]["n_total"] == 128
