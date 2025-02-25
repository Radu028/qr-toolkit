# QR Toolkit

Acest proiect implementeaza un cititor si generarea de coduri QR in Python, parcurgand urmatorii pasi:

## Citire

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

## Generare

1. **Codarea mesajului**
    Procesul incepe cu functia `encode` din `matrix_to_hoto.py`, care primeste mesajul ca input si genereaza un sir binar ce respecta specificatiile QR:
    - Se adauga indicatorul de mod (pentru modul Byte, se foloseste "0100").
    - Se calculeaza dimensiunea campului de numar de caractere, alegand 8, 16 sau 24 de biti in functie de lungimea mesajului.
    - Fiecarui caracter ii este atribuita forma binara pe 8 biti.
    - Se adauga un camp terminator ("0000") si, ulterior, se completeaza cu zerouri pentru ca lungimea sirului sa fie un multiplu de 8.

2. **Corectia erorilor cu Reed–Solomon**
    Dupa codarea initiala, se aplica corectia erorilor:
    - Functia `encode_rs` transforma sirul binar in array de octeti (fiecare grup de 8 biti devine un octet).
    - Per totalul de octeti pentru corectie (care se introduce din consola), se instantiaza un obiect de la biblioteca `reedsolo.RSCodec`.
    - Mesajul (reprezentat ca array de octeti) este codificat suplimentar, adaugand simboluri de corectie.
    - Rezultatul este reconvertit intr-un sir binar completat cu codurile de verificare.

3. **Aplicarea mastii de date**
    in alte parti ale proiectului (`mask.py`) se gestioneaza aplicarea mastii QR. Aici se elimina zonele functionale rezervate (cum ar fi punctele de localizare si zonele de sincronizare) folosind o matrice rezervata, definita in `utils.py`. Mastile sunt concepute pentru a evita aparitia unor modele nedorite in matricea finala.

4. **Construirea matricei QR**
    Dupa obtinerea unui sir binar complet (cu codificare initiala si corectie a erorilor) si dupa aplicarea mastii, se construieste o matrice 2D. Fiecare element reprezinta un modul (sau punct), 0 pentru alb si 1 pentru negru. Integrarea zonelor functionale si a semnalelor de orientare se face pe baza specificatiilor QR.

5. **Generarea imaginii QR**
    Ultimul pas este conversia matricei 2D intr-o imagine. Acest lucru se realizeaza folosind biblioteca `matplotlib` (importata la inceputul `matrix_to_hoto.py`). Functiile specifice se ocupa de:
    - Redarea unui grid vizual, unde modulele au culori contrastante (negru si alb).
    - Salvarea imaginii finale care reprezinta codul QR gata de scanare.

Prin parcurgerea acestor pasi, proiectul asigura generarea corecta a unui cod QR, de la codarea mesajului initial pana la crearea imaginii finale.

---

Referinte in cadrul proiectului:  
- Preprocesarea si citirea imaginii: `__main__.py`  
- Extragerea si pozitionarea matricei QR: `read.py`  
- Eliminarea mastii: `mask.py`  
- Decodarea mesajului: `decode.py`  
- Corectia erorilor: `correction.py`  
- Marcare zone rezervate: `utils.py`
- Generare QR: `matrix_to_hoto.py`

Librarii folosite in cadrul acestui proiect:
- OpenCV (cv): folosita pentru citirea imaginilor (`__main__.py`, `read.py`)
- Matplotlib: utilizata pentru redarea si salvarea imaginii QR (`matrix_to_hoto.py`)
- Reedsolo: folosita pentru corectia erorilor cu algoritmul Reed-Solomon

---

### Cum se foloseste

1. Se ruleaza fisisrul `__main__.py`
2. Se introduce **0** pentru citirea codului sau **1** pentru generarea unuia.
3. Pentru citire se introduce numele fisierului cu imaginea codului QR (cu tot cu extensie .png/.jpg/etc)
    Pentru generare se introduce mesajul dorit
4. Pentru generare se introduce numarul de octeti pentru corectie

---

Echipa Pheonix a realizat acest proiect:
- Bâcă Ionut-Adelin (Grupa 132)
- Popa Radu-Stefan (Grupa 132)
- Popescu Iulia-Maria (Grupa 131)

### Bibliografie
- https://www.nayuki.io/page/creating-a-qr-code-step-by-step
- https://www.thonky.com/qr-code-tutorial/format-version-information
- https://medium.com/@r00__/decoding-a-broken-qr-code-39fc3473a034
- https://www.thonky.com/qr-code-tutorial/data-encoding
- https://www.thonky.com/qr-code-tutorial/module-placement-matrix
- https://qr.blinry.org/
- https://www.thonky.com/qr-code-tutorial/data-analysis
- https://www.youtube.com/watch?v=pamazHwk0hg
- https://www.youtube.com/watch?v=KMsvtqQqz5g
- https://www.youtube.com/watch?v=sRgUrKWiXQs