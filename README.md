# QR Toolkit

Acest proiect implementeaza un cititor de coduri QR in Python, parcurgand urmatorii pasi:

1. **Preprocesarea imaginii**  
   - Se foloseste OpenCV pentru a citi imaginea (ex. `qr-code.png`) in mod grayscale.
   - Imaginea este convertita intr-o imagine binara (folosind un prag), unde pixelii au valoarea 0 (negru) sau 255 (alb).

2. **Detectarea si extragerea modelului QR**  
   - **Detectarea colturilor (finder patterns):** Functia `find_coordonates` identifica zonele caracteristice ale codului QR.
   - **Extragerea matricei QR:** Functia `get_qr` extrage datele din imagine, construind o matrice (2D list) in care fiecare element este un modul (0 sau 1).
   - **Alinierea QR-ului:** Functia `positioned_qr` roteste si translateaza matricea astfel incat QR-ul sa fie orientat corect, pe baza coordonatelor gasite.

3. **Eliminarea mastii de date**  
   - Codurile QR au o masca aplicata pentru a evita aparitia unor pattern-uri nedorite.
   - Functia `get_mask_id` extrage identificatorul mastii.
   - Functia `remove_mask` elimina masca aplicata, folosind o matrice rezervata (calculata in `get_reserved_matrix` din `utils.py`) care indica zonele functionale ce nu trebuie afectate.

4. **Decodarea bitstream-ului**  
   - Se determina tipul de codificare (Numeric, Alfanumeric, Byte, Kanji) prin analiza unor module din zona de date.
   - Se extrage lungimea mesajului si se parcurge bitstream-ul conform specificatiilor QR, printr-o lectura zig-zag care traverseaza matricea de la dreapta la stanga si de sus in jos.
   - Functia `get_message` interpreteaza bitstream-ul obtinut si decodifica mesajul final.

5. **Corectia erorilor**  
   - Daca nivelul de corectie a erorilor este diferit de "L", functia `correct_bitstream` aplica algoritmul Reed–Solomon (folosind libraria `reedsolo`) pentru a repara eventualele erori din bitstream.
   - Bitstream-ul este completat cu zerouri pentru a avea o lungime ce este multiplu de 8, convertit in codewords (grupuri de 8 biti), corectat, iar rezultatul este reconvertit intr-un sir binar pentru decodare ulterioara.

Prin combinarea acestor pasi, proiectul parcurge intregul flux de procesare a unui cod QR: de la citirea imaginii, preprocesare, extragerea si alinierea datelor, eliminarea mastii aplicate, corectia erorilor (daca este necesar) si pana la decodarea mesajului final.

Referinte in cadrul proiectului:  
- Preprocesarea si citirea imaginii: `__main__.py`  
- Extragerea si pozitionarea matricei QR: `read.py`  
- Eliminarea mastii: `mask.py`  
- Decodarea mesajului: `decode.py`  
- Corectia erorilor: `correction.py`  
- Marcare zone rezervate: `utils.py`