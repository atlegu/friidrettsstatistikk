"""
13_opplasting.py — A6: opplastingsmappen til Measurement in Physical Education and Exercise Science
(MPEES_opplasting/). Var 13_jss_pakke.py; JSS-pakken ligger i commit 3b8911e.

Kjøres sist i RUN_ALL.sh, etter at alle kontroller er grønne, så mappen bare oppdateres fra en
kontrollert tilstand. Innhold:
  01_Manuscript_with_author_details.pdf   manus/main.pdf
  02_Manuscript_anonymous.pdf             manus/main_anonymous.pdf (portalen krever begge)
  03_Supplementary_material.pdf           manus/supplement.pdf (uten forfatteropplysninger)
  04_Cover_letter.pdf                     manus/cover_letter.pdf (utkast til forfatterne)
  Figure1.tif … Figure3.tif       figurene i trykkrekkefølgen fra main.tex (S-figurene står i supplementet): RGB på hvit bunn, LZW, 300 dpi
  MANIFEST.sha256                 sha256 for filene over
README_opplasting.md er håndskrevet og overskrives ikke; skriptet stopper hvis den ikke nevner hver fil.

Inndata: manus/*.pdf, manus/main.tex, figures/*.png
Utdata:  MPEES_opplasting/
"""

import hashlib
import logging
import re
import shutil
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
MANUS = HERE / "manus"
FIG = HERE / "figures"
UT = HERE / "MPEES_opplasting"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PDF = {"01_Manuscript_with_author_details.pdf": MANUS / "main.pdf",
       "02_Manuscript_anonymous.pdf": MANUS / "main_anonymous.pdf",
       "03_Supplementary_material.pdf": MANUS / "supplement.pdf",
       "04_Cover_letter.pdf": MANUS / "cover_letter.pdf"}


def main():
    UT.mkdir(exist_ok=True)
    # PDF-er fra en tidligere filliste skal ikke bli liggende
    for x in UT.glob("*.pdf"):
        if x.name not in PDF:
            x.unlink()
    filer = []
    for navn, kilde in PDF.items():
        shutil.copyfile(kilde, UT / navn)
        filer.append(navn)
    # figurene i rekkefølgen manus tar dem inn, så nummeret følger trykket
    figurer = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+\.png)\}", (MANUS / "main.tex").read_text())
    for i, fil in enumerate(figurer, 1):
        bilde = Image.open(FIG / fil)
        hvit = Image.new("RGB", bilde.size, "white")
        hvit.paste(bilde, mask=bilde.getchannel("A") if bilde.mode == "RGBA" else None)
        navn = f"Figure{i}.tif"
        hvit.save(UT / navn, compression="tiff_lzw", dpi=(300, 300))
        filer.append(navn)
        logger.info("%s ← %s (%d × %d px)", navn, fil, *bilde.size)
    # gamle figurfiler fra en kjøring med flere figurer skal ikke bli liggende
    for x in UT.glob("Figure*.tif"):
        if x.name not in filer:
            logger.info("fjerner foreldet %s", x.name)
            x.unlink()
    (UT / "MANIFEST.sha256").write_text(
        "".join(f"{hashlib.sha256((UT / n).read_bytes()).hexdigest()}  {n}\n" for n in filer))
    readme = UT / "README_opplasting.md"
    if not readme.exists():
        raise SystemExit("MPEES_opplasting/README_opplasting.md mangler")
    mangler = [n for n in filer if n not in readme.read_text()]
    if mangler:
        raise SystemExit(f"README_opplasting.md nevner ikke: {mangler}")
    logger.info("opplastingsmappen: %d filer + MANIFEST.sha256 i %s", len(filer), UT)


if __name__ == "__main__":
    main()
