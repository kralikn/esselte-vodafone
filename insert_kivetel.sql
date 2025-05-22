INSERT INTO kivetel (megnevezes, teszor_kod, afa_kulcs, jogcim_id) VALUES
('e-Pack nem teljesítés díja', '61.20.12', '27%', (SELECT id FROM jogcim WHERE nev = 'telefon - nem telj díj' AND afa_kulcs = '27%')),
('e-Pack nem teljesítésének díja', '61.20.4', '5%', (SELECT id FROM jogcim WHERE nev = 'telefon - nem telj díj' AND afa_kulcs = '5%'));