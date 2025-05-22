INSERT INTO teszor (teszor_kod, afa_kulcs, jogcim_id) VALUES
('61.20.12', '27%', (SELECT id FROM jogcim WHERE nev = 'telefon' AND afa_kulcs = '27%')),
('61.10.11', '27%', (SELECT id FROM jogcim WHERE nev = 'telefon' AND afa_kulcs = '27%')),
('61.20.4',  '5%',  (SELECT id FROM jogcim WHERE nev = 'internet' AND afa_kulcs = '5%')),
('61.10.43', '5%',  (SELECT id FROM jogcim WHERE nev = 'internet' AND afa_kulcs = '5%')),
('61.10.43', '27%',  (SELECT id FROM jogcim WHERE nev = 'internet' AND afa_kulcs = '27%')),
('52.21.24', '27%', (SELECT id FROM jogcim WHERE nev = 'parkolás' AND afa_kulcs = '27%')),
('52.21.22', '27%', (SELECT id FROM jogcim WHERE nev = 'autópálya' AND afa_kulcs = '27%')),
('61.10.44', '5%',  (SELECT id FROM jogcim WHERE nev = 'internet' AND afa_kulcs = '5%')),
('61.10.04', '5%',  (SELECT id FROM jogcim WHERE nev = 'internet' AND afa_kulcs = '5%'));