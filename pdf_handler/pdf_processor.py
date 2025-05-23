import pdfplumber
import pandas as pd
import re
from database.db_manager import DatabaseManager
import warnings
import logging

# PDF figyelmeztetések elnémítása
logging.propagate = False
logging.getLogger().setLevel(logging.ERROR)
warnings.filterwarnings("ignore")


class PdfProcessor:
    def __init__(self, file_path: str, db: DatabaseManager):
        self.file_path = file_path
        self.db = db
        self.kiszamlazott_dijak_rows = []
        self.szamlaosszesito_rows = []
        self.hibas_ertekek = []
        self.phone_user_map = self._load_phone_user_map()
        self.teszor_category_map = self._load_teszor_category_map()

    def _load_phone_user_map(self):
        # return dict(self.db.get_all_phone_users())
        return {phone: owner for (_, phone, owner) in self.db.get_all_phone_users()}

    def _load_teszor_category_map(self):
        # return dict(self.db.get_all_teszor_categories())
        return {
            teszor_kod: megnevezes
            for teszor_kod, megnevezes in self.db.get_all_teszor_categories()
        }

    def process(self, output_excel_path: str, progress_callback=None):
        try:
            with pdfplumber.open(self.file_path) as pdf:

                is_dijak_section = False
                dijak_lines_accumulator = []

                total_pages = len(pdf.pages)

                for i, page in enumerate(pdf.pages):
                    if progress_callback:
                        progress_callback(i + 1, total_pages)

                    text = page.extract_text()
                    if not text:
                        continue
                    lines = text.split("\n")
                    header = lines[0].strip().upper()

                    if header in ["KISZÁMLÁZOTT DÍJAK", "ÜGYFÉLSZINTŰ DÍJAK"]:
                        is_dijak_section = True  # kezdete
                        dijak_lines_accumulator.extend(lines)
                        # self._process_dijak(lines)
                    elif is_dijak_section:
                        dijak_lines_accumulator.extend(lines)

                    # Ellenőrzés, hogy elértük-e a végét
                    if is_dijak_section and any(
                        "Kiszámlázott díjak összesen" in l for l in lines
                    ):
                        self._process_dijak(dijak_lines_accumulator)
                        is_dijak_section = False
                        dijak_lines_accumulator = []

                    # elif header == "SZÁMLA":
                    if header == "SZÁMLA":
                        self._process_szamla_page(text)

            self._save_to_excel(output_excel_path)
            return True, f"Sikeres mentés: {output_excel_path}"
        except Exception as e:
            return False, f"Hiba feldolgozás közben: {e}"

    def _process_dijak(self, lines):
        telefonszam = "NINCS"
        for line in lines:
            if "Tarifacsomag:" in line:
                break
            match = re.search(r"Telefonszám:\s*(36\d{9})", line)
            if match:
                telefonszam = match.group(1)
                break

        try:
            start_index = next(
                i for i, l in enumerate(lines) if l.strip().startswith("Megnevezés")
            )
            end_index = next(
                i
                for i, l in enumerate(lines)
                if l.strip().startswith("Kiszámlázott díjak összesen")
            )
        except StopIteration:
            return

        for line in lines[start_index + 1 : end_index]:
            teszor_match = re.search(r"\b\d{2}\.\d{2}\.\d{1,2}\b", line)
            if not teszor_match:
                continue
            teszor = teszor_match.group()
            parts = line.rsplit(" ", 4)
            if len(parts) < 5:
                continue
            osszeg, afa_osszeg, afa_kulcs, netto_osszeg = parts[-4:]
            before_values = parts[0]
            megnevezes = (
                before_values.split(teszor)[0].strip()
                if teszor in before_values
                else before_values.strip()
            )

            self.kiszamlazott_dijak_rows.append(
                [
                    telefonszam,
                    megnevezes,
                    teszor,
                    netto_osszeg,
                    afa_kulcs,
                    afa_osszeg,
                    osszeg,
                ]
            )

    def _process_szamla_page(self, text):
        start = text.find("Számlaösszesítő")
        end = text.find("Egyenlegközlő információ")
        if start == -1 or end == -1:
            return
        for line in text[start:end].split("\n"):
            if any(
                k in line
                for k in ["összeg", "Megnevezés", "Összesen", "Számlaösszesítő"]
            ):
                continue

            teszor_match = re.search(r"\b\d{2}\.\d{2}\.\d{1,2}\b", line)
            if teszor_match:
                parts = line.rsplit(" ", 8)
                if len(parts) == 9:
                    self.szamlaosszesito_rows.append(parts)
            else:
                parts = line.rsplit(" ", 7)
                if len(parts) == 8:
                    parts.insert(4, "")  # üres TESZOR mező
                    self.szamlaosszesito_rows.append(parts)

    def _save_to_excel(self, output_path):

        writer = pd.ExcelWriter(output_path, engine="xlsxwriter")

        df_kiszamlazott = None

        if self.kiszamlazott_dijak_rows:
            df = pd.DataFrame(
                self.kiszamlazott_dijak_rows,
                columns=[
                    "Telefonszám",
                    "Megnevezés",
                    "TESZOR szám",
                    "Összesen (Ft)",
                    "ÁFA összege (Ft)",
                    "ÁFA kulcs",
                    "Nettó összeg (Ft)",
                ],
            )
            df["Dolgozó"] = (
                df["Telefonszám"].map(self.phone_user_map).fillna("Ismeretlen")
            )
            df["Kategória"] = (
                df["TESZOR szám"].map(self.teszor_category_map).fillna("egyéb")
            )

            # Jogcím lekérdezés és hozzáfűzés
            jogcim_df = df.apply(self._get_jogcim_adatok, axis=1)
            df = pd.concat([df, jogcim_df], axis=1)

            for col in ["Nettó összeg (Ft)", "ÁFA összege (Ft)", "Összesen (Ft)"]:
                df[col] = df[col].apply(self._clean_float)

            df.to_excel(writer, sheet_name="Kiszámlázott díjak", index=False)
            df_kiszamlazott = df

        if self.szamlaosszesito_rows:
            df = pd.DataFrame(
                self.szamlaosszesito_rows,
                columns=[
                    "Megnevezés",
                    "Mennyiség",
                    "Mennyiségi egység",
                    "Egységár (Ft)",
                    "TESZOR szám",
                    "ÁFA kulcs",
                    "Nettó összeg (Ft)",
                    "ÁFA összeg (Ft)",
                    "Bruttó összeg (Ft)",
                ],
            )
            for col in [
                "Egységár (Ft)",
                "Nettó összeg (Ft)",
                "ÁFA összeg (Ft)",
                "Bruttó összeg (Ft)",
            ]:
                df[col] = (
                    df[col]
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                    .astype(float)
                )

            df.to_excel(writer, sheet_name="Számlaösszesítő", index=False)

        if df_kiszamlazott is not None:
            pivot_df = pd.pivot_table(
                df_kiszamlazott,
                index=[
                    "Telefonszám",
                    "Dolgozó",
                    "ÁFA kulcs",
                    "Jogcím",
                    "ÁFA kód",
                    "Főkönyvi szám",
                ],
                values=["Nettó összeg (Ft)", "ÁFA összege (Ft)"],
                aggfunc="sum",
                fill_value=0,
            ).reset_index()

            pivot_df.to_excel(writer, sheet_name="Kimutatás", index=False)

        writer.close()

    def _clean_float(self, value):
        try:
            cleaned = value.replace(".", "").replace(",", ".").strip()
            return float(cleaned) if re.match(r"^-?\d+(\.\d+)?$", cleaned) else None
        except Exception:
            self.hibas_ertekek.append(value)
            return None

    def _get_jogcim_adatok(self, row):
        info = self.db.get_jogcim_info(
            row["Megnevezés"], row["TESZOR szám"], row["ÁFA kulcs"]
        )
        if info:
            return pd.Series(info, index=["Jogcím", "ÁFA kód", "Főkönyvi szám"])
        else:
            return pd.Series(
                ["ismeretlen", "ismeretlen", "ismeretlen"],
                index=["Jogcím", "ÁFA kód", "Főkönyvi szám"],
            )
