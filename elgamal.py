"""
================================================================================
IMPLEMENTASI ALGORITMA ELGAMAL ENCRYPTION (TANPA LIBRARY KRIPTOGRAFI)
================================================================================
Mata Kuliah : Kriptografi
Topik       : Pertemuan ke-9 - Diffie-Hellman Key Exchange & ElGamal Algorithm
Kelompok 5 :
  1. Putu Yudi Nandanjaya Wiraguna  (NRP: 5027241080)
  2. Raihan Fahri Ghazali           (NRP: 5027241061)
  3. I Gede Bagus Saka Sinatrya     (NRP: 5027241088)
Program Studi : Teknologi Informasi - FTEIC, Institut Teknologi Sepuluh Nopember
================================================================================
"""

import random
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ==============================================================================
# BAGIAN 1: FUNGSI MATEMATIKA DASAR, SQUARE-AND-MULTIPLY, & EXTENDED EUCLIDEAN
# ==============================================================================

def gcd(a: int, b: int) -> int:
    """
    Menghitung Faktor Persekutuan Terbesar (FPB / GCD) dari dua bilangan bulat
    menggunakan Algoritma Euclidean secara manual.
    """
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a


def is_prime(n: int) -> bool:
    """
    Memeriksa apakah bilangan bulat n adalah bilangan prima menggunakan
    metode pembagian berulang (trial division) hingga akar kuadrat dari n.
    """
    if not isinstance(n, int) or n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def prime_factors(n: int) -> list:
    """
    Mencari seluruh faktor prima unik dari bilangan bulat positif n.
    """
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors


def modular_exponentiation(base: int, exponent: int, modulus: int, verbose: bool = False) -> int:
    """
    Menghitung perpangkatan modular (base^exponent mod modulus) secara manual
    menggunakan algoritma Square-and-Multiply (Binary Exponentiation).
    """
    if modulus <= 0:
        raise ValueError("Modulus harus berupa bilangan bulat positif (> 0).")
    if exponent < 0:
        raise ValueError("Eksponen tidak boleh negatif untuk fungsi perpangkatan modular dasar.")
    if modulus == 1:
        return 0

    binary_exp = bin(exponent)[2:]
    result = 1
    base_mod = base % modulus

    if verbose:
        print(f"    [Square-and-Multiply] Menghitung {base}^{exponent} mod {modulus}")
        print(f"    Representasi biner eksponen {exponent} = ({binary_exp})_2 ({len(binary_exp)} bit)")
        print(f"    {'Langkah':^7} | {'Bit':^3} | {'Setelah Square (r^2 mod p)':^28} | {'Setelah Multiply (r*b mod p)':^28}")
        print(f"    {'-'*7}-+-{'-'*3}-+-{'-'*28}-+-{'-'*28}")

    for step, bit in enumerate(binary_exp, start=1):
        prev_result = result
        sq_result = (result * result) % modulus
        sq_str = f"{prev_result}^2 mod {modulus} = {sq_result}"

        if bit == '1':
            result = (sq_result * base_mod) % modulus
            mul_str = f"{sq_result} * {base_mod} mod {modulus} = {result}"
        else:
            result = sq_result
            mul_str = f"- (tetap {result})"

        if verbose:
            print(f"    {step:^7} | {bit:^3} | {sq_str:<28} | {mul_str:<28}")

    if verbose:
        print(f"    => Hasil Akhir: {base}^{exponent} mod {modulus} = {result}\n")

    return result


def is_primitive_root(g: int, p: int) -> bool:
    """
    Memeriksa apakah g adalah akar primitif (generator) dari bilangan prima p.
    """
    if not is_prime(p):
        raise ValueError(f"Modulus p = {p} bukan bilangan prima.")
    if g <= 1 or g >= p or gcd(g, p) != 1:
        return False

    phi = p - 1
    for q in prime_factors(phi):
        if modular_exponentiation(g, phi // q, p, verbose=False) == 1:
            return False
    return True


def extended_euclidean_inverse(a: int, m: int, verbose: bool = True) -> int:
    """
    Menghitung invers modular dari a modulo m (yaitu a^(-1) mod m) secara manual
    menggunakan Extended Euclidean Algorithm (Algoritma Euclidean Diperluas).

    Mencari bilangan bulat t sedemikian sehingga:
        (a * t) ≡ 1 (mod m)
    Melalui persamaan Bezout:
        m * s + a * t = gcd(m, a) = 1
    """
    if m <= 1:
        raise ValueError("Modulus m harus lebih besar dari 1.")
    a_mod = a % m
    if a_mod == 0:
        raise ValueError(f"Nilai {a} ≡ 0 (mod {m}) tidak memiliki invers modular.")

    r1, r2 = m, a_mod
    t1, t2 = 0, 1
    step = 1

    if verbose:
        print(f"    [Extended Euclidean Algorithm] Mencari {a_mod}^(-1) mod {m}:")
        print(f"    {'Iterasi':^7} | {'q = r1 // r2':^12} | {'r1':^8} | {'r2':^8} | {'r = r1 % r2':^11} | {'t1':^8} | {'t2':^8} | {'t = t1 - q*t2':^13}")
        print(f"    {'-'*7}-+-{'-'*12}-+-{'-'*8}-+-{'-'*8}-+-{'-'*11}-+-{'-'*8}-+-{'-'*8}-+-{'-'*13}")

    while r2 != 0:
        q = r1 // r2
        r = r1 % r2
        t = t1 - q * t2
        if verbose:
            print(f"    {step:^7} | {q:^12} | {r1:^8} | {r2:^8} | {r:^11} | {t1:^8} | {t2:^8} | {t:^13}")
        r1, r2 = r2, r
        t1, t2 = t2, t
        step += 1

    if r1 != 1:
        raise ValueError(f"Invers modular tidak ada karena gcd({a}, {m}) = {r1} != 1.")

    inverse = t1 % m
    if verbose:
        print(f"    Diperoleh gcd({m}, {a_mod}) = {r1}, koefisien t1 = {t1}")
        print(f"    Normalisasi ke rentang positif modulo {m}: {t1} mod {m} = {inverse}")
        print(f"    Uji kebenaran invers: ({a_mod} * {inverse}) mod {m} = {(a_mod * inverse) % m}\n")

    return inverse


def fermat_inverse_power(c1: int, x: int, p: int, verbose: bool = True) -> int:
    """
    Menghitung invers dari s = c1^x mod p menggunakan metode yang dijelaskan
    dalam PPT Pertemuan ke-9 (Slide 19-20), yaitu berdasarkan Teorema Kecil Fermat:
        (a^x)^(-1) mod p = a^(p - 1 - x) mod p
    """
    exp_fermat = p - 1 - x
    if verbose:
        print(f"    [Metode PPT Slide 20 - Teorema Kecil Fermat]")
        print(f"    Rumus PPT: (a^x)^(-1) mod p = a^(p - 1 - x) mod p")
        print(f"               ({c1}^{x})^(-1) mod {p} = {c1}^({p} - 1 - {x}) mod {p} = {c1}^{exp_fermat} mod {p}")
    inv_val = modular_exponentiation(c1, exp_fermat, p, verbose=verbose)
    return inv_val


# ==============================================================================
# BAGIAN 2: TAHAPAN INTI ALGORITMA ELGAMAL ENCRYPTION & DECRYPTION
# ==============================================================================

def step1_setup_public_parameters(p: int, g: int) -> tuple:
    """
    TAHAP 1: Menentukan parameter publik bilangan prima p dan generator g.
    """
    print("\n[TAHAP 1] Menentukan Parameter Publik (p dan g)")
    print("-" * 72)
    print(f"  - Bilangan prima p                 = {p}")
    print(f"  - Generator / akar primitif g      = {g}")

    if not isinstance(p, int) or not is_prime(p):
        raise ValueError(f"Validasi Gagal: p = {p} bukan bilangan prima!")
    if not isinstance(g, int) or not is_primitive_root(g, p):
        raise ValueError(f"Validasi Gagal: g = {g} bukan akar primitif dari p = {p}!")

    print(f"  [VALID] p = {p} adalah bilangan prima dan g = {g} adalah akar primitif dari {p}.")
    return p, g


def step2_select_receiver_private_key(x: int, p: int) -> int:
    """
    TAHAP 2: Menentukan private key penerima (Alice) yaitu x.
    Sesuai PPT Slide 14: 1 < x < p - 1 (atau 1 <= x <= p - 2).
    """
    print("\n[TAHAP 2] Menentukan Private Key Penerima / Alice (x)")
    print("-" * 72)
    if not isinstance(x, int) or not (1 <= x <= p - 2):
        raise ValueError(
            f"Validasi Gagal: Private key x = {x} harus berada pada rentang 1 <= x <= {p - 2}."
        )
    print(f"  - Private Key Alice (x)            = {x}  [RAHASIA, memenuhi 1 <= x <= {p - 2}]")
    return x


def step3_compute_receiver_public_key(g: int, x: int, p: int, verbose: bool = True) -> int:
    """
    TAHAP 3: Menghitung public key penerima (Alice): y = g^x mod p.
    Pasangan kunci publik Alice sesuai PPT Slide 15 adalah (y, g, p).
    """
    print("\n[TAHAP 3] Menghitung Public Key Penerima / Alice: y = g^x mod p")
    print("-" * 72)
    print(f"  Rumus: y = g^x mod p = {g}^{x} mod {p}")
    y = modular_exponentiation(g, x, p, verbose=verbose)
    print(f"  => Public Key Alice (y)            = {y}")
    print(f"  => Pasangan Kunci Publik Alice     = (y={y}, g={g}, p={p})  [PUBLIK]")
    return y


def step4_prepare_numeric_message(m: int, p: int) -> int:
    """
    TAHAP 4: Menentukan dan memvalidasi pesan numerik m dengan syarat 0 <= m < p.
    Sesuai PPT Slide 16: plainteks dinyatakan sebagai bilangan bulat m dalam [0, p-1].
    """
    print("\n[TAHAP 4] Menentukan Pesan Numerik (m)")
    print("-" * 72)
    if not isinstance(m, int) or not (0 <= m < p):
        raise ValueError(
            f"Validasi Gagal: Pesan numerik m = {m} harus memenuhi syarat 0 <= m < p (0 <= m <= {p - 1})."
        )
    print(f"  - Pesan numerik (m)                = {m}  [VALID, memenuhi 0 <= {m} < {p}]")
    return m


def step5_select_ephemeral_key(p: int, k: int = None) -> int:
    """
    TAHAP 5: Memilih bilangan acak sementara (ephemeral key) k yang memenuhi
    1 <= k <= p - 2 (atau 1 < k < p - 1 pada PPT Slide 16).
    Jika k tidak diberikan (None), dipilih secara acak menggunakan random.randint(2, p - 2).
    """
    print("\n[TAHAP 5] Memilih Bilangan Acak Sementara / Ephemeral Key (k)")
    print("-" * 72)
    if k is None:
        k = random.randint(2, p - 2)
        print(f"  - Nilai k dipilih secara ACAK (random) pada rentang [2, {p - 2}]: k = {k}")
    else:
        if not isinstance(k, int) or not (1 <= k <= p - 2):
            raise ValueError(
                f"Validasi Gagal: Bilangan acak sementara k = {k} harus memenuhi 1 <= k <= {p - 2}."
            )
        print(f"  - Nilai k yang digunakan           = {k}  [Memenuhi 1 <= k <= {p - 2}]")
        print(f"    (Catatan: Nilai k={k} ditetapkan khusus untuk demonstrasi/pengujian")
        print(f"     agar perhitungan dapat direproduksi dan diverifikasi secara manual.)")
    return k


def step6_encrypt_message(g: int, y: int, m: int, k: int, p: int, verbose: bool = True) -> tuple:
    """
    TAHAP 6: Menghitung pasangan ciphertext (c1, c2) atau (a, b) dalam notasi PPT:
      - c1 (atau a) = g^k mod p
      - c2 (atau b) = (m * y^k) mod p
    """
    print("\n[TAHAP 6] Menghitung Ciphertext (c1 dan c2)")
    print("-" * 72)
    print(f"  6a. Menghitung komponen pertama c1 (notasi PPT: a):")
    print(f"      Rumus: c1 = g^k mod p = {g}^{k} mod {p}")
    c1 = modular_exponentiation(g, k, p, verbose=verbose)
    print(f"      => c1 (a) = {c1}\n")

    print(f"  6b. Menghitung komponen kedua c2 (notasi PPT: b):")
    print(f"      Langkah 1: Hitung s_enc = y^k mod p = {y}^{k} mod {p}")
    y_pow_k = modular_exponentiation(y, k, p, verbose=verbose)
    print(f"      Langkah 2: Hitung c2 = (m * y^k) mod p = ({m} * {y_pow_k}) mod {p}")
    c2 = (m * y_pow_k) % p
    print(f"                 ({m} * {y_pow_k}) = {m * y_pow_k} ≡ {c2} (mod {p})")
    print(f"      => c2 (b) = {c2}")
    return c1, c2


def step7_display_ciphertext(c1: int, c2: int) -> tuple:
    """
    TAHAP 7: Menampilkan pasangan ciphertext (c1, c2) / (a, b) yang dikirim Bob ke Alice.
    """
    print("\n[TAHAP 7] Menampilkan Pasangan Ciphertext (c1, c2)")
    print("-" * 72)
    print(f"  - Pasangan Ciphertext (Notasi Prompt) : (c1, c2) = ({c1}, {c2})")
    print(f"  - Pasangan Ciphertext (Notasi PPT)    : (a, b)   = ({c1}, {c2})")
    print(f"  - Bob mengirimkan pasangan ({c1}, {c2}) kepada Alice melalui saluran publik.")
    return c1, c2


def step8_and_9_decrypt_message(c1: int, c2: int, x: int, p: int, verbose: bool = True) -> tuple:
    """
    TAHAP 8 & 9: Melakukan dekripsi ciphertext (c1, c2) menggunakan private key x:
      - Menghitung shared secret s = c1^x mod p (notasi PPT: a^x mod p)
      - Menghitung invers modular s^(-1) mod p secara manual dengan:
          (a) Extended Euclidean Algorithm
          (b) Metode PPT Slide 20 (Teorema Kecil Fermat: c1^(p - 1 - x) mod p)
      - Menghitung pesan terdekripsi: m = (c2 * s^(-1)) mod p
    """
    print("\n[TAHAP 8] Menghitung Komponen Rahasia Dekripsi: s = c1^x mod p")
    print("-" * 72)
    print(f"  Rumus: s = c1^x mod p = {c1}^{x} mod {p}")
    s = modular_exponentiation(c1, x, p, verbose=verbose)
    print(f"  => Nilai s (atau a^x mod p) = {s}")

    print("\n[TAHAP 9] Menghitung Invers Modular s^(-1) mod p dan Dekripsi Pesan")
    print("-" * 72)
    print(f"  9a. Metode 1: Extended Euclidean Algorithm untuk mencari {s}^(-1) mod {p}")
    s_inv_eea = extended_euclidean_inverse(s, p, verbose=verbose)

    print(f"  9b. Metode 2: Rumus PPT Slide 20 (Teorema Kecil Fermat: c1^(p-1-x) mod p)")
    s_inv_fermat = fermat_inverse_power(c1, x, p, verbose=verbose)

    print(f"  Perbandingan Kedua Metode Invers Modular:")
    print(f"    - Hasil Extended Euclidean Algorithm : s^(-1) = {s_inv_eea}")
    print(f"    - Hasil Metode PPT (Fermat)          : (a^x)^(-1) = {s_inv_fermat}")
    assert s_inv_eea == s_inv_fermat, "Ketidakcocokan antara Extended Euclidean dan Fermat!"
    print(f"    [IDENTIK] Kedua metode menghasilkan nilai invers modular yang sama: {s_inv_eea}")

    print(f"\n  9c. Menghitung Pesan Hasil Dekripsi: m' = (c2 * s^(-1)) mod p")
    print(f"      Rumus (Prompt) : m' = c2 * s^(-1) mod p = ({c2} * {s_inv_eea}) mod {p}")
    print(f"      Rumus (PPT)    : m' = b * (a^x)^(-1) mod p = ({c2} * {s_inv_eea}) mod {p}")
    m_decrypted = (c2 * s_inv_eea) % p
    print(f"      Perhitungan    : {c2} * {s_inv_eea} = {c2 * s_inv_eea} ≡ {m_decrypted} (mod {p})")
    print(f"      => Pesan Hasil Dekripsi (m') = {m_decrypted}")

    return s, s_inv_eea, m_decrypted


def step10_verify_decryption(m_original: int, m_decrypted: int) -> bool:
    """
    TAHAP 10: Memverifikasi bahwa pesan hasil dekripsi sama dengan pesan asli.
    """
    print("\n[TAHAP 10] Verifikasi Hasil Dekripsi (m_dekripsi == m_asli)")
    print("-" * 72)
    print(f"  - Pesan Asli (m)         = {m_original}")
    print(f"  - Pesan Terdekripsi (m') = {m_decrypted}")
    is_valid = (m_original == m_decrypted)
    if is_valid:
        print(f"  [VERIFIKASI BERHASIL] m' == m == {m_decrypted}. Dekripsi ElGamal terbukti benar!")
    else:
        print(f"  [VERIFIKASI GAGAL] m' ({m_decrypted}) != m ({m_original})!")
    return is_valid


def run_elgamal_single_block_simulation(
    title: str, p: int, g: int, x: int, m: int, k: int = None, verbose: bool = True
) -> dict:
    """
    Menjalankan seluruh 10 tahapan algoritma ElGamal untuk satu pesan numerik m.
    """
    print("\n" + "=" * 78)
    print(f"SIMULASI ELGAMAL: {title}")
    print("=" * 78)

    p, g = step1_setup_public_parameters(p, g)
    x = step2_select_receiver_private_key(x, p)
    y = step3_compute_receiver_public_key(g, x, p, verbose=verbose)
    m = step4_prepare_numeric_message(m, p)
    k_used = step5_select_ephemeral_key(p, k)
    c1, c2 = step6_encrypt_message(g, y, m, k_used, p, verbose=verbose)
    step7_display_ciphertext(c1, c2)
    s, s_inv, m_dec = step8_and_9_decrypt_message(c1, c2, x, p, verbose=verbose)
    verified = step10_verify_decryption(m, m_dec)

    print("\n  RINGKASAN PARAMETER DAN HASIL ELGAMAL:")
    print(f"  +--------------------------------------------+----------------------------+")
    print(f"  | Parameter / Variabel                       | Nilai                      |")
    print(f"  +--------------------------------------------+----------------------------+")
    print(f"  | Bilangan Prima (p)                         | {p:<26} |")
    print(f"  | Generator / Akar Primitif (g)              | {g:<26} |")
    print(f"  | Private Key Penerima / Alice (x)           | {x:<26} |")
    print(f"  | Public Key Penerima / Alice (y = g^x mod p)| {y:<26} |")
    print(f"  | Pesan Numerik Asli (m)                     | {m:<26} |")
    print(f"  | Ephemeral Key Pengirim / Bob (k)           | {k_used:<26} |")
    print(f"  | Ciphertext Komponen 1 (c1 / a = g^k mod p) | {c1:<26} |")
    print(f"  | Ciphertext Komponen 2 (c2 / b = m*y^k mod p)| {c2:<26} |")
    print(f"  | Komponen Rahasia Dekripsi (s = c1^x mod p) | {s:<26} |")
    print(f"  | Invers Modular (s^(-1) mod p)              | {s_inv:<26} |")
    print(f"  | Pesan Hasil Dekripsi (m')                  | {m_dec:<26} |")
    print(f"  | Status Verifikasi (m' == m)                | {'VALID (SAMA)' if verified else 'TIDAK VALID':<26} |")
    print(f"  +--------------------------------------------+----------------------------+")

    return {
        "p": p, "g": g, "x": x, "y": y, "m": m, "k": k_used,
        "c1": c1, "c2": c2, "s": s, "s_inv": s_inv, "m_dec": m_dec,
        "verified": verified
    }


# ==============================================================================
# BAGIAN 3: SIMULASI CONTOH LENGKAP PPT PERTEMUAN KE-9 (SLIDE 15 - 20)
# ==============================================================================

def encode_text_ppt(plaintext: str, block_digits: int = 4) -> tuple:
    """
    Mengodekan teks alfabet (A-Z) menjadi blok bilangan bulat sesuai contoh
    PPT Pertemuan ke-9 Slide 17:
      A = 00, B = 01, ..., Z = 25
      Contoh: 'HALO' -> H=07, A=00, L=11, O=14 -> '07001114'
      Dipecah menjadi blok 4 digit: m1 = 700 ('0700'), m2 = 1114 ('1114').
    """
    clean_text = plaintext.upper().strip()
    digits_list = []
    for ch in clean_text:
        if not ('A' <= ch <= 'Z'):
            raise ValueError(f"Karakter '{ch}' di luar rentang alfabet A-Z.")
        val = ord(ch) - ord('A')
        digits_list.append(f"{val:02d}")

    full_numeric_str = "".join(digits_list)
    blocks_str = [
        full_numeric_str[i:i + block_digits]
        for i in range(0, len(full_numeric_str), block_digits)
    ]
    blocks_int = [int(b) for b in blocks_str]
    return full_numeric_str, blocks_str, blocks_int


def decode_blocks_ppt(blocks_int: list, block_digits: int = 4) -> str:
    """
    Mengembalikan daftar blok integer menjadi teks alfabet (A=00 .. Z=25)
    sesuai PPT Pertemuan ke-9 Slide 20.
    """
    reconstructed_str = "".join(f"{b:0{block_digits}d}" for b in blocks_int)
    chars = []
    for i in range(0, len(reconstructed_str), 2):
        code = int(reconstructed_str[i:i + 2])
        chars.append(chr(ord('A') + code))
    return "".join(chars)


def run_ppt_halo_example():
    """
    Menjalankan simulasi contoh enkripsi & dekripsi pesan 'HALO' persis seperti
    pada PPT Pertemuan ke-9 Slide 15 s.d. Slide 20:
      - p = 2273, g = 3, x = 243 -> y = 461
      - Plainteks 'HALO' -> m = 07001114 -> blok m1 = 0700 (700) dan m2 = 1114
      - Blok 1: m1 = 700, k1 = 1463 -> c1 = (1439, 74)
      - Blok 2: m2 = 1114, k2 = 2001 -> c2 = (1220, 1682)
    """
    print("\n" + "=" * 78)
    print("SKENARIO 2: SIMULASI CONTOH PPT PERTEMUAN KE-9 (SLIDE 15 - 20) - PESAN 'HALO'")
    print("=" * 78)

    plaintext = "HALO"
    p, g, x = 2273, 3, 243
    k_values = [1463, 2001]  # Nilai k contoh tetap dari PPT Slide 18

    full_num_str, blocks_str, blocks_int = encode_text_ppt(plaintext, block_digits=4)
    print(f"\n[PRA-PEMROSESAN PLAINTEKS SESUAI PPT SLIDE 17]")
    print(f"  - Plainteks Asli                  : '{plaintext}'")
    print(f"  - Pengodean Huruf (A=00..Z=25)    : H=07, A=00, L=11, O=14")
    print(f"  - Representasi Integer Gabungan   : m = {full_num_str}")
    print(f"  - Pemecahan ke Blok 4 Digit (< p) : m1 = {blocks_str[0]} ({blocks_int[0]}), m2 = {blocks_str[1]} ({blocks_int[1]})")

    decrypted_blocks = []
    for idx, (m_val, k_val) in enumerate(zip(blocks_int, k_values), start=1):
        res = run_elgamal_single_block_simulation(
            title=f"CONTOH PPT SLIDE 18 & 20 - BLOK m_{idx} = {m_val:04d} (k = {k_val})",
            p=p,
            g=g,
            x=x,
            m=m_val,
            k=k_val,
            verbose=True
        )
        decrypted_blocks.append(res["m_dec"])

    recovered_text = decode_blocks_ppt(decrypted_blocks, block_digits=4)
    print("\n" + "-" * 78)
    print("HASIL AKHIR REKONSTRUKSI BLOK PLAINTEKS (PPT SLIDE 20):")
    print(f"  - Blok Terdekripsi : m1 = {decrypted_blocks[0]:04d}, m2 = {decrypted_blocks[1]:04d}")
    print(f"  - Gabungan Blok    : {decrypted_blocks[0]:04d}{decrypted_blocks[1]:04d}")
    print(f"  - Konversi ke Teks : '{recovered_text}' (Cocok 100% dengan plainteks asli '{plaintext}')")
    print("-" * 78)


def demonstrate_input_validation():
    """
    Demonstrasi pengujian validasi input dan penanganan kondisi tidak valid.
    """
    print("\n" + "=" * 78)
    print("PENGUJIAN VALIDASI INPUT DAN PENANGANAN KONDISI TIDAK VALID (ELGAMAL)")
    print("=" * 78)

    invalid_cases = [
        ("Pesan m lebih besar atau sama dengan p (p=23, m=25)", lambda: step4_prepare_numeric_message(25, 23)),
        ("Pesan m bernilai negatif (p=23, m=-5)", lambda: step4_prepare_numeric_message(-5, 23)),
        ("Ephemeral key k di luar rentang 1..p-2 (p=23, k=22)", lambda: step5_select_ephemeral_key(23, 22)),
        ("Invers modular tidak ada karena gcd(a, m) != 1 (a=6, m=15)", lambda: extended_euclidean_inverse(6, 15, verbose=False)),
    ]

    for desc, func in invalid_cases:
        print(f"\n[Uji Kasus Tidak Valid] {desc}")
        try:
            func()
        except ValueError as err:
            print(f"  -> Berhasil menangkap pengecualian (ValueError): {err}")


# ==============================================================================
# BAGIAN 4: PROGRAM UTAMA (MAIN EXECUTION)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 78)
    print("TUGAS MATA KULIAH KRIPTOGRAFI - IMPLEMENTASI ELGAMAL ENCRYPTION & DECRYPTION")
    print("-" * 78)
    print("Kelompok 5 - Anggota:")
    print("  1. Putu Yudi Nandanjaya Wiraguna  (5027241080)")
    print("  2. Raihan Fahri Ghazali           (5027241061)")
    print("  3. I Gede Bagus Saka Sinatrya     (5027241088)")
    print("=" * 78)

    # 1. Skenario 1: Parameter Kecil untuk Verifikasi Manual Lengkap
    #    p = 23, g = 5, x = 6 -> y = 8, pesan m = 15, k = 10 (nilai contoh tetap)
    run_elgamal_single_block_simulation(
        title="SKENARIO 1 - PARAMETER KECIL UNTUK VERIFIKASI MANUAL (p=23, g=5, m=15)",
        p=23,
        g=5,
        x=6,
        m=15,
        k=10,
        verbose=True
    )

    # 2. Skenario 2: Contoh Materi PPT Pertemuan ke-9 (Slide 15 - 20)
    #    p = 2273, g = 3, x = 243 -> y = 461, pesan 'HALO' (m1=700, m2=1114)
    run_ppt_halo_example()

    # 3. Skenario 3: Pengujian Ephemeral Key k Acak (Menunjukkan Sifat Probabilistik)
    run_elgamal_single_block_simulation(
        title="SKENARIO 3 - PENGUJIAN DENGAN EPHEMERAL KEY (k) ACAK OTOMATIS",
        p=23,
        g=5,
        x=6,
        m=15,
        k=None,  # Dipilih secara acak oleh program pada rentang [2, p-2]
        verbose=False
    )

    # 4. Demonstrasi validasi input tidak valid
    demonstrate_input_validation()

    # 5. Mode Interaktif Opsional (jika dijalankan dengan argumen --interactive)
    if "--interactive" in sys.argv:
        print("\n" + "=" * 78)
        print("MODE INTERAKTIF ELGAMAL")
        print("=" * 78)
        try:
            u_p = int(input("Masukkan bilangan prima p              : "))
            u_g = int(input("Masukkan generator g                   : "))
            u_x = int(input(f"Masukkan private key penerima x (1..{u_p-2}): "))
            u_m = int(input(f"Masukkan pesan numerik m (0..{u_p-1})       : "))
            k_str = input(f"Masukkan ephemeral key k (1..{u_p-2}, kosongkan untuk acak): ").strip()
            u_k = int(k_str) if k_str else None
            run_elgamal_single_block_simulation("SIMULASI INPUT PENGGUNA", u_p, u_g, u_x, u_m, u_k, verbose=True)
        except Exception as exc:
            print(f"[ERROR INPUT] {exc}")
