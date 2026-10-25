"""
web/app.py: gpower-clone Web Arayüzü — Flask Backend
YZM301 — Teardown Sprint: G*Power 3.1.9.7 Bağımsız Yeniden Gerçekleştirim Workbench
"""
import sys
import os
import csv
import math
import numpy as np
import scipy.stats as stats
from flask import Flask, request, jsonify, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine import solve_a_priori, solve_post_hoc, ValidationError, CalculationError
from src.clinical_agent import ClinicalQuestionAgent

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["JSON_AS_ASCII"] = False
agent = ClinicalQuestionAgent()

# Referans kıyaslama vektörleri (G*Power 3.1.9.7 resmi verileri)
BENCHMARKS = []
csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "oracle", "gpower_reference.csv")
if os.path.exists(csv_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            BENCHMARKS.append(row)


def compute_distribution_curves(df: int, ncp: float, tcrit: float, tails: int):
    """
    G*Power'ın meşhur merkezi ve merkezi-olmayan t dağılım eğrilerini üretir.
    H0: t(df) (delta = 0)
    H1: nct(df, ncp) (delta = ncp)
    """
    xmin = min(-4.5, -tcrit - 1.5, ncp - 4.5)
    xmax = max(4.5, tcrit + 2.0, ncp + 4.5)
    xs = np.linspace(xmin, xmax, 160).tolist()
    y_null = stats.t.pdf(xs, df).tolist()
    y_alt = stats.nct.pdf(xs, df, ncp).tolist()

    return {
        "x": [round(float(x), 4) for x in xs],
        "y_null": [round(float(y), 5) for y in y_null],
        "y_alt": [round(float(y), 5) for y in y_alt],
        "tcrit": tcrit,
        "ncp": ncp,
        "df": df,
        "tails": tails
    }


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json() or {}
    try:
        mode = data.get("mode", "a-priori")
        tails = int(data.get("tails", 2))
        d = float(data.get("d", 0.5))
        alpha = float(data.get("alpha", 0.05))

        if mode == "a-priori":
            power = float(data.get("power", 0.95))
            ratio = float(data.get("ratio", 1.0))
            result = solve_a_priori(tails=tails, d=d, alpha=alpha, power=power, ratio=ratio)
            cli_cmd = f"gpower-clone --test t2-indep --mode a-priori --tails {tails} --d {d} --alpha {alpha} --power {power} --ratio {ratio}"
        else:
            n1 = int(data.get("n1", 50))
            n2 = int(data.get("n2", 50))
            result = solve_post_hoc(tails=tails, d=d, alpha=alpha, n1=n1, n2=n2)
            cli_cmd = f"gpower-clone --test t2-indep --mode post-hoc --tails {tails} --d {d} --alpha {alpha} --n1 {n1} --n2 {n2}"

        # Dağılım eğrisi verileri
        distribution = compute_distribution_curves(
            df=result["df"],
            ncp=result["ncp"],
            tcrit=result["critical"],
            tails=tails
        )

        return jsonify({
            "ok": True,
            "mode": mode,
            "result": result,
            "distribution": distribution,
            "cli_cmd": cli_cmd
        })
    except (ValidationError, CalculationError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"Beklenmeyen hata: {str(e)}"}), 500


@app.route("/api/determine-d", methods=["POST"])
def determine_d():
    """
    G*Power'daki 'Determine =>' penceresi işlevi:
    İki grubun ortalama ve standart sapmalarından Cohen's d hesaplar.
    """
    data = request.get_json() or {}
    try:
        m1 = float(data.get("mean1", 0.0))
        sd1 = float(data.get("sd1", 1.0))
        m2 = float(data.get("mean2", 0.0))
        sd2 = float(data.get("sd2", 1.0))

        if sd1 <= 0 or sd2 <= 0:
            return jsonify({"ok": False, "error": "Standart sapma pozitif olmalıdır (SD > 0)."}), 400

        # Pooled standard deviation
        s_pooled = math.sqrt((sd1**2 + sd2**2) / 2.0)
        d_val = abs(m1 - m2) / s_pooled

        return jsonify({
            "ok": True,
            "d": round(d_val, 4),
            "s_pooled": round(s_pooled, 4)
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/benchmarks", methods=["GET"])
def get_benchmarks():
    """G*Power 3.1.9.7 resmi referans vektörlerini listeler."""
    return jsonify({"ok": True, "benchmarks": BENCHMARKS})


@app.route("/api/clinical", methods=["POST"])
def clinical():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"ok": False, "error": "Soru metni boş olamaz."}), 400
    try:
        result = agent.answer_clinical_question(question)
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] gpower-clone Scientific Workbench -> http://localhost:{port}")
    app.run(debug=False, port=port)
