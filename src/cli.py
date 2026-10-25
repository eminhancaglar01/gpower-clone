"""
src/cli.py: gpower-clone Komut Satırı Arayüzü (CLI Interface)

YZM301 Teardown Sprint için G*Power t2-indep CLI sözleşmesini uygular.
Başarılı çağrıda tek satır JSON çıktısı üretir.
Hatalı çağrıda standart çıktıya {"error":"açıklama"} JSON nesnesi yazar
ve sıfırdan farklı çıkış kodu (exit code = 1) ile sonlanır.
"""

import sys
import json
import argparse
from typing import List, Optional

from .engine import solve_a_priori, solve_post_hoc, ValidationError, CalculationError


class StrictArgumentParser(argparse.ArgumentParser):
    """
    Standart argparse hata davranışını ezen sınıf.
    Hataları standart hataya (stderr) basmak yerine yakalar ve
    JSON error sözleşmesine dönüştürmek üzere ValidationError fırlatır.
    """
    def error(self, message: str):
        raise ValidationError(f"Argüman ayrıştırma hatası: {message}")

    def exit(self, status: int = 0, message: Optional[str] = None):
        if status != 0:
            raise ValidationError(message or "Bilinmeyen CLI hatası.")
        sys.exit(0)


def build_parser() -> StrictArgumentParser:
    """CLI argüman ayrıştırıcısını oluşturur."""
    parser = StrictArgumentParser(
        prog="gpower-clone",
        description="G*Power iki bağımsız grup t testi (t2-indep) yeniden gerçekleştirim CLI aracı.",
        add_help=False
    )
    
    # Genel parametreler
    parser.add_argument("--help", "-h", action="store_true", help="Yardım mesajını gösterir.")
    parser.add_argument("--test", type=str, required=False, help="Test ailesi (örn. t2-indep)")
    parser.add_argument("--mode", type=str, required=False, help="Hesaplama modu: a-priori veya post-hoc")
    parser.add_argument("--tails", type=int, required=False, help="Kuyruk sayısı: 1 veya 2")
    parser.add_argument("--d", type=float, required=False, help="Cohen's d etki büyüklüğü (d > 0)")
    parser.add_argument("--alpha", type=float, required=False, help="I. tip hata payı (0 < alpha < 1)")
    parser.add_argument("--power", type=float, required=False, help="Hedef güç (a-priori modu için)")
    parser.add_argument("--ratio", type=float, default=1.0, help="Grup büyüklüğü oranı N2/N1 (varsayılan: 1.0)")
    
    # Post-hoc parametreleri
    parser.add_argument("--n1", type=int, required=False, help="1. grup örneklem büyüklüğü (post-hoc için)")
    parser.add_argument("--n2", type=int, required=False, help="2. grup örneklem büyüklüğü (post-hoc için)")
    parser.add_argument("--n-total", "--ntotal", type=int, dest="n_total", required=False, help="Toplam örneklem büyüklüğü")

    return parser


def run_cli(args_list: Optional[List[str]] = None) -> int:
    """
    CLI giriş noktası.
    Başarı durumunda 0, hata durumunda 1 döndürür.
    Çıktı daima standart çıktıya (stdout) tek satır JSON olarak basılır.
    """
    if args_list is None:
        args_list = sys.argv[1:]

    parser = build_parser()

    # Yardım talebi kontrolü
    if "--help" in args_list or "-h" in args_list:
        help_info = {
            "name": "gpower-clone",
            "usage": "gpower-clone --test t2-indep --mode <a-priori|post-hoc> [parametreler]",
            "supported_tests": ["t2-indep"],
            "modes": ["a-priori", "post-hoc"],
            "parameters": {
                "--tails": "1 veya 2",
                "--d": "Cohen's d (pozitif ondalık)",
                "--alpha": "I. tip hata (0 < alpha < 1)",
                "--power": "Hedef güç (a-priori için)",
                "--ratio": "Grup tahsis oranı N2/N1 (varsayılan: 1.0)",
                "--n1": "1. grup büyüklüğü (post-hoc için)",
                "--n2": "2. grup büyüklüğü (post-hoc için)",
                "--n-total": "Toplam örneklem büyüklüğü (post-hoc için)"
            }
        }
        sys.stdout.write(json.dumps(help_info, ensure_ascii=False) + "\n")
        return 0

    try:
        parsed_args, unknown = parser.parse_known_args(args_list)
        if unknown:
            raise ValidationError(f"Bilinmeyen veya desteklenmeyen parametre(ler): {' '.join(unknown)}")

        # Zorunlu parametre kontrolleri
        if not parsed_args.test:
            raise ValidationError("Eksik parametre: --test belirtilmelidir (örn. --test t2-indep).")
        
        if parsed_args.test != "t2-indep":
            raise ValidationError(
                f"Desteklenmeyen test ailesi: '{parsed_args.test}'. Bu sürümde yalnızca 't2-indep' desteklenmektedir."
            )

        if not parsed_args.mode:
            raise ValidationError("Eksik parametre: --mode belirtilmelidir ('a-priori' veya 'post-hoc').")

        if parsed_args.tails is None:
            raise ValidationError("Eksik parametre: --tails belirtilmelidir (1 veya 2).")

        if parsed_args.d is None:
            raise ValidationError("Eksik parametre: --d (etki büyüklüğü) belirtilmelidir.")

        if parsed_args.alpha is None:
            raise ValidationError("Eksik parametre: --alpha (anlamlılık düzeyi) belirtilmelidir.")

        # Mod bazlı çalıştırma
        mode = parsed_args.mode.lower()
        if mode == "a-priori":
            if parsed_args.power is None:
                raise ValidationError("A priori modu için --power (hedef güç) parametresi zorunludur.")

            result = solve_a_priori(
                tails=parsed_args.tails,
                d=parsed_args.d,
                alpha=parsed_args.alpha,
                power=parsed_args.power,
                ratio=parsed_args.ratio
            )

        elif mode == "post-hoc":
            result = solve_post_hoc(
                tails=parsed_args.tails,
                d=parsed_args.d,
                alpha=parsed_args.alpha,
                n1=parsed_args.n1,
                n2=parsed_args.n2,
                ratio=parsed_args.ratio,
                n_total=parsed_args.n_total
            )

        else:
            raise ValidationError(f"Geçersiz mod: '{parsed_args.mode}'. Yalnızca 'a-priori' veya 'post-hoc' desteklenir.")

        # Başarılı tek satır JSON çıktısı (makine tarafından okunabilir)
        output_json = json.dumps(result, separators=(',', ':'), ensure_ascii=False)
        sys.stdout.write(output_json + "\n")
        sys.stdout.flush()
        return 0

    except (ValidationError, CalculationError) as err:
        error_output = json.dumps({"error": str(err)}, separators=(',', ':'), ensure_ascii=False)
        sys.stdout.write(error_output + "\n")
        sys.stdout.flush()
        return 1
    except Exception as exc:
        error_output = json.dumps({"error": f"Beklenmeyen sistem hatası: {str(exc)}"}, separators=(',', ':'), ensure_ascii=False)
        sys.stdout.write(error_output + "\n")
        sys.stdout.flush()
        return 1


def main():
    """Konsol komut giriş noktası."""
    exit_code = run_cli()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
