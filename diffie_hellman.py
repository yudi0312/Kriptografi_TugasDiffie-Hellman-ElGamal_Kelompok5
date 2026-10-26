"""
================================================================================
IMPLEMENTASI ALGORITMA DIFFIE-HELLMAN KEY EXCHANGE (TANPA LIBRARY KRIPTOGRAFI)
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

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ==============================================================================
# BAGIAN 1: FUNGSI MATEMATIKA DASAR & ARITMETIKA MODULAR MANUAL
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
    Digunakan untuk menguji syarat akar primitif dari bilangan prima p,
    yaitu faktor-faktor prima dari phi(p) = p - 1.
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

    Prinsip Algoritma:
      Representasikan eksponen dalam bentuk biner: e = (b_{k-1} ... b_1 b_0)_2
      Iterasi dari bit paling signifikan (MSB) ke bit paling tidak signifikan (LSB):
        1. Square   : result = (result * result) mod modulus
        2. Multiply : jika bit b_i == 1, maka result = (result * base) mod modulus
    """
    if modulus <= 0:
        raise ValueError("Modulus harus berupa bilangan bulat positif (> 0).")
    if exponent < 0:
        raise ValueError("Eksponen tidak boleh negatif untuk fungsi perpangkatan modular dasar.")
    if modulus == 1:
        return 0

    binary_exp = bin(exponent)[2:]  # Representasi biner tanpa prefix '0b'
    result = 1
    base_mod = base % modulus

    if verbose:
        print(f"    [Square-and-Multiply] Menghitung {base}^{exponent} mod {modulus}")
        print(f"    Representasi biner eksponen {exponent} = ({binary_exp})_2 ({len(binary_exp)} bit)")
        print(f"    {'Langkah':^7} | {'Bit':^3} | {'Setelah Square (r^2 mod p)':^28} | {'Setelah Multiply (r*g mod p)':^28}")
        print(f"    {'-'*7}-+-{'-'*3}-+-{'-'*28}-+-{'-'*28}")

    for step, bit in enumerate(binary_exp, start=1):
        prev_result = result
        # Tahap 1: Square (pengkuadratan modular)
        sq_result = (result * result) % modulus
        sq_str = f"{prev_result}^2 mod {modulus} = {sq_result}"

        # Tahap 2: Multiply (perkalian modular jika bit == '1')
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


def is_primitive_root(g: int, p: int, show_cycle: bool = False) -> bool:
    """
    Memeriksa apakah g adalah akar primitif (generator) dari bilangan prima p.

    Sesuai PPT Pertemuan ke-9 (Slide 4-6):
      Bilangan bulat g disebut akar primitif dari bilangan prima p jika
      perpangkatan g^1, g^2, ..., g^(p-1) (mod p) menghasilkan nilai-nilai
      yang semuanya berbeda (panjang siklus = phi(p) = p - 1).

      Secara matematis, untuk p prima, g adalah akar primitif modulo p jika dan
      hanya jika gcd(g, p) == 1 dan untuk setiap faktor prima q dari (p - 1)
      berlaku: g^((p - 1) / q) mod p != 1.
    """
    if not is_prime(p):
        raise ValueError(f"Modulus p = {p} bukan bilangan prima.")
    if g <= 1 or g >= p:
        return False
    if gcd(g, p) != 1:
        return False

    phi = p - 1

    # Jika p cukup kecil dan diminta menampilkan siklus (seperti Slide 5-6 PPT)
    if show_cycle and p <= 31:
        powers = [modular_exponentiation(g, i, p, verbose=False) for i in range(1, p)]
        unique_powers = set(powers)
        print(f"    Perpangkatan {g}^i mod {p} untuk i = 1..{phi}:")
        terms = [f"{g}^{i} mod {p} = {val}" for i, val in enumerate(powers, start=1)]
        for idx in range(0, len(terms), 3):
            print("      " + "   |   ".join(terms[idx:idx + 3]))
        print(f"    Himpunan hasil perpangkatan : {powers}")
        print(f"    Jumlah nilai unik           : {len(unique_powers)} dari {phi} kemungkinan nilai (1..{phi})")

    factors = prime_factors(phi)
    for q in factors:
        if modular_exponentiation(g, phi // q, p, verbose=False) == 1:
            return False
    return True


# ==============================================================================
# BAGIAN 2: TAHAPAN INTI ALGORITMA DIFFIE-HELLMAN KEY EXCHANGE
# ==============================================================================

def step1_setup_public_parameters(p: int, g: int, show_cycle: bool = False) -> tuple:
    """
    TAHAP 1: Menentukan dan memvalidasi parameter publik berupa bilangan prima p
    (atau n dalam notasi PPT Slide 10) dan generator / akar primitif g.
    """
    print("\n[TAHAP 1] Menentukan Parameter Publik (p dan g)")
    print("-" * 72)
    print(f"  Parameter publik yang disepakati Alice dan Bob:")
    print(f"  - Bilangan prima p (atau n di PPT) = {p}")
    print(f"  - Generator / akar primitif g      = {g}")

    if not isinstance(p, int) or not is_prime(p):
        raise ValueError(f"Validasi Gagal: p = {p} bukan bilangan prima!")
    print(f"  [VALID] p = {p} terverifikasi sebagai bilangan prima (phi(p) = p - 1 = {p - 1}).")

    if not isinstance(g, int) or not is_primitive_root(g, p, show_cycle=show_cycle):
        raise ValueError(f"Validasi Gagal: g = {g} bukan akar primitif dari p = {p}!")
    factors = prime_factors(p - 1)
    checks = [f"{g}^({(p-1)}//{q}) mod {p} = {modular_exponentiation(g, (p-1)//q, p)} != 1" for q in factors]
    print(f"  [VALID] g = {g} terverifikasi sebagai akar primitif dari p = {p}.")
    print(f"          Uji faktor prima (p-1={p-1}): {', '.join(checks)}")
    return p, g


def step2_select_private_keys(a: int, b: int, p: int) -> tuple:
    """
    TAHAP 2: Menentukan dan memvalidasi kunci privat Alice (a / x) dan Bob (b / y).
    Syarat kunci privat: bilangan bulat acak pada rentang 1 <= private_key <= p - 2.
    """
    print("\n[TAHAP 2] Menentukan Private Key Alice (a) dan Bob (b)")
    print("-" * 72)
    for key, owner, sym_prompt, sym_ppt in [(a, "Alice", "a", "x"), (b, "Bob", "b", "y")]:
        if not isinstance(key, int) or not (1 <= key <= p - 2):
            raise ValueError(
                f"Validasi Gagal: Private key {owner} ({sym_prompt} = {key}) harus berupa "
                f"bilangan bulat dalam rentang 1 <= {sym_prompt} <= {p - 2}."
            )
        print(f"  - Private Key {owner:<5} ({sym_prompt} / notasi PPT {sym_ppt}) = {key}  [RAHASIA, rentang 1..{p-2}]")
    return a, b


def step3_compute_alice_public_key(g: int, a: int, p: int, verbose: bool = True) -> int:
    """
    TAHAP 3: Menghitung public key Alice: A = g^a mod p (atau X = g^x mod n di PPT).
    """
    print("\n[TAHAP 3] Menghitung Public Key Alice: A = g^a mod p")
    print("-" * 72)
    print(f"  Rumus (Prompt) : A = g^a mod p = {g}^{a} mod {p}")
    print(f"  Rumus (PPT)    : X = g^x mod n = {g}^{a} mod {p}")
    A = modular_exponentiation(g, a, p, verbose=verbose)
    print(f"  => Public Key Alice (A / X) = {A}  [PUBLIK]")
    return A


def step4_compute_bob_public_key(g: int, b: int, p: int, verbose: bool = True) -> int:
    """
    TAHAP 4: Menghitung public key Bob: B = g^b mod p (atau Y = g^y mod n di PPT).
    """
    print("\n[TAHAP 4] Menghitung Public Key Bob: B = g^b mod p")
    print("-" * 72)
    print(f"  Rumus (Prompt) : B = g^b mod p = {g}^{b} mod {p}")
    print(f"  Rumus (PPT)    : Y = g^y mod n = {g}^{b} mod {p}")
    B = modular_exponentiation(g, b, p, verbose=verbose)
    print(f"  => Public Key Bob (B / Y)   = {B}  [PUBLIK]")
    return B


def step5_exchange_public_keys(A: int, B: int, g: int, p: int) -> tuple:
    """
    TAHAP 5: Simulasi pertukaran public key melalui saluran komunikasi publik.
    """
    print("\n[TAHAP 5] Pertukaran Public Key melalui Saluran Komunikasi")
    print("-" * 72)
    print(f"  - Alice mengirimkan Public Key A (X) = {A} kepada Bob.")
    print(f"    (Pasangan Kunci Publik Alice sesuai PPT: (X={A}, g={g}, n={p}))")
    print(f"  - Bob mengirimkan Public Key B (Y)   = {B} kepada Alice.")
    print(f"    (Pasangan Kunci Publik Bob sesuai PPT  : (Y={B}, g={g}, n={p}))")
    print(f"  - Informasi yang diketahui penyadap (Eve) di saluran publik:")
    print(f"    p (n) = {p}, g = {g}, A (X) = {A}, B (Y) = {B}")
    print(f"    Penyadap TIDAK mengetahui a (x) maupun b (y), dan harus memecahkan")
    print(f"    Discrete Logarithm Problem (DLP) untuk mendapatkan kunci sesi.")
    received_by_alice = B
    received_by_bob = A
    return received_by_alice, received_by_bob


def step6_compute_alice_shared_secret(B: int, a: int, p: int, verbose: bool = True) -> int:
    """
    TAHAP 6: Menghitung shared secret di sisi Alice: K_A = B^a mod p (K = Y^x mod n di PPT).
    """
    print("\n[TAHAP 6] Menghitung Shared Secret di Sisi Alice: K_A = B^a mod p")
    print("-" * 72)
    print(f"  Rumus (Prompt) : K_A = B^a mod p = {B}^{a} mod {p}")
    print(f"  Rumus (PPT)    : K   = Y^x mod n = {B}^{a} mod {p}")
    K_A = modular_exponentiation(B, a, p, verbose=verbose)
    print(f"  => Shared Secret Alice (K_A / K) = {K_A}")
    return K_A


def step7_compute_bob_shared_secret(A: int, b: int, p: int, verbose: bool = True) -> int:
    """
    TAHAP 7: Menghitung shared secret di sisi Bob: K_B = A^b mod p (K' = X^y mod n di PPT).
    """
    print("\n[TAHAP 7] Menghitung Shared Secret di Sisi Bob: K_B = A^b mod p")
    print("-" * 72)
    print(f"  Rumus (Prompt) : K_B = A^b mod p = {A}^{b} mod {p}")
    print(f"  Rumus (PPT)    : K'  = X^y mod n = {A}^{b} mod {p}")
    K_B = modular_exponentiation(A, b, p, verbose=verbose)
    print(f"  => Shared Secret Bob (K_B / K')  = {K_B}")
    return K_B


def step8_verify_shared_secret(K_A: int, K_B: int, g: int, a: int, b: int, p: int) -> bool:
    """
    TAHAP 8: Memverifikasi bahwa K_A == K_B secara aljabar dan numerik.
    """
    print("\n[TAHAP 8] Verifikasi Kesamaan Shared Secret (K_A == K_B)")
    print("-" * 72)
    print(f"  - Nilai Shared Secret Alice (K_A / K)  = {K_A}")
    print(f"  - Nilai Shared Secret Bob   (K_B / K') = {K_B}")
    print(f"  - Bukti Matematis : K_A = B^a mod p = (g^b mod p)^a mod p = g^(a*b) mod p")
    print(f"                      {g}^({a}*{b}) mod {p} = {g}^{a*b} mod {p} = {modular_exponentiation(g, a * b, p)}")
    is_valid = (K_A == K_B)
    if is_valid:
        print(f"  [VERIFIKASI BERHASIL] K_A == K_B == {K_A}. Kunci sesi simetri berhasil disepakati!")
    else:
        print(f"  [VERIFIKASI GAGAL] K_A ({K_A}) != K_B ({K_B})!")
    return is_valid


def run_diffie_hellman_simulation(title: str, p: int, g: int, a: int, b: int, show_cycle: bool = False) -> dict:
    """
    Menjalankan seluruh 8 tahapan simulasi Diffie-Hellman Key Exchange secara berurutan.
    """
    print("\n" + "=" * 78)
    print(f"SIMULASI DIFFIE-HELLMAN: {title}")
    print("=" * 78)

    p, g = step1_setup_public_parameters(p, g, show_cycle=show_cycle)
    a, b = step2_select_private_keys(a, b, p)
    A = step3_compute_alice_public_key(g, a, p, verbose=True)
    B = step4_compute_bob_public_key(g, b, p, verbose=True)
    B_received, A_received = step5_exchange_public_keys(A, B, g, p)
    K_A = step6_compute_alice_shared_secret(B_received, a, p, verbose=True)
    K_B = step7_compute_bob_shared_secret(A_received, b, p, verbose=True)
    verified = step8_verify_shared_secret(K_A, K_B, g, a, b, p)

    print("\n  RINGKASAN PARAMETER DAN HASIL:")
    print(f"  +----------------------------------------+--------------------------------+")
    print(f"  | Parameter / Variabel                   | Nilai                          |")
    print(f"  +----------------------------------------+--------------------------------+")
    print(f"  | Bilangan Prima (p / n)                 | {p:<30} |")
    print(f"  | Generator / Akar Primitif (g)          | {g:<30} |")
    print(f"  | Private Key Alice (a / x)              | {a:<30} |")
    print(f"  | Private Key Bob (b / y)                | {b:<30} |")
    print(f"  | Public Key Alice (A / X = g^a mod p)   | {A:<30} |")
    print(f"  | Public Key Bob (B / Y = g^b mod p)     | {B:<30} |")
    print(f"  | Shared Secret Alice (K_A = B^a mod p)  | {K_A:<30} |")
    print(f"  | Shared Secret Bob (K_B = A^b mod p)    | {K_B:<30} |")
    print(f"  | Status Verifikasi (K_A == K_B)         | {'VALID (SAMA)' if verified else 'TIDAK VALID':<30} |")
    print(f"  +----------------------------------------+--------------------------------+")

    return {
        "p": p, "g": g, "a": a, "b": b,
        "A": A, "B": B, "K_A": K_A, "K_B": K_B,
        "verified": verified
    }


def demonstrate_primitive_root_concept():
    """
    Demonstrasi konsep Akar Primitif dan Logaritma Diskrit sesuai Slide 5, 6, dan 7
    pada PPT Pertemuan ke-9.
    """
    print("=" * 78)
    print("PENDAHULUAN: KONSEP AKAR PRIMITIF & LOGARITMA DISKRIT (PPT SLIDE 4 - 7)")
    print("=" * 78)

    print("\n1. Uji Akar Primitif p = 7, a = 3 (Contoh PPT Slide 5):")
    res_3 = is_primitive_root(3, 7, show_cycle=True)
    print(f"   => Apakah 3 adalah akar primitif dari 7? {res_3} (Semua 6 nilai muncul tepat satu kali)")

    print("\n2. Uji Bukan Akar Primitif p = 7, a = 2 (Contoh PPT Slide 6):")
    res_2 = is_primitive_root(2, 7, show_cycle=True)
    print(f"   => Apakah 2 adalah akar primitif dari 7? {res_2} (Hanya menghasilkan nilai {{1, 2, 4}})")

    print("\n3. Contoh Logaritma Diskrit p = 41, g = 7 (Contoh PPT Slide 7):")
    val = modular_exponentiation(7, 3, 41, verbose=False)
    print(f"   Diketahui 7 adalah akar primitif dari p = 41: {is_primitive_root(7, 41)}")
    print(f"   Perhitungan 7^3 mod 41 = {val} (kongruen dengan 15 mod 41)")
    print(f"   Maka x = 3 adalah logaritma diskrit dari 15 dalam basis 7 mod 41.")


def demonstrate_input_validation():
    """
    Demonstrasi pengujian penanganan kondisi input yang tidak valid (error handling).
    """
    print("\n" + "=" * 78)
    print("PENGUJIAN VALIDASI INPUT DAN PENANGANAN KONDISI TIDAK VALID")
    print("=" * 78)

    invalid_cases = [
        ("Modulus p bukan bilangan prima (p=15, g=3)", 15, 3, 5, 7),
        ("Generator g bukan akar primitif (p=7, g=2 sesuai Slide 6 PPT)", 7, 2, 3, 4),
        ("Private key di luar rentang 1..p-2 (p=23, g=5, a=25, b=10)", 23, 5, 25, 10),
    ]

    for desc, p_val, g_val, a_val, b_val in invalid_cases:
        print(f"\n[Uji Kasus Tidak Valid] {desc}")
        try:
            step1_setup_public_parameters(p_val, g_val, show_cycle=False)
            step2_select_private_keys(a_val, b_val, p_val)
        except ValueError as err:
            print(f"  -> Berhasil menangkap pengecualian (ValueError): {err}")


# ==============================================================================
# BAGIAN 3: PROGRAM UTAMA (MAIN EXECUTION)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 78)
    print("TUGAS MATA KULIAH KRIPTOGRAFI - IMPLEMENTASI DIFFIE-HELLMAN KEY EXCHANGE")
    print("-" * 78)
    print("Kelompok 5 - Anggota:")
    print("  1. Putu Yudi Nandanjaya Wiraguna  (5027241080)")
    print("  2. Raihan Fahri Ghazali           (5027241061)")
    print("  3. I Gede Bagus Saka Sinatrya     (5027241088)")
    print("=" * 78)

    # 1. Tampilkan demonstrasi konsep dasar dari PPT Slide 4-7
    demonstrate_primitive_root_concept()

    # 2. Skenario 1: Parameter sesuai Contoh PPT Pertemuan ke-9 Slide 11
    #    n (p) = 251, g = 6, x (a) = 124, y (b) = 158
    #    Catatan: Nilai a=124 dan b=158 adalah nilai contoh tetap dari PPT
    #    perkuliahan untuk keperluan pengujian dan verifikasi hasil.
    run_diffie_hellman_simulation(
        title="SKENARIO 1 - CONTOH MATERI PPT PERTEMUAN KE-9 (SLIDE 11)",
        p=251,
        g=6,
        a=124,
        b=158,
        show_cycle=False
    )

    # 3. Skenario 2: Parameter Kecil untuk Verifikasi Manual Langkah demi Langkah
    #    p = 23, g = 5, a = 6, b = 15
    run_diffie_hellman_simulation(
        title="SKENARIO 2 - PARAMETER KECIL UNTUK VERIFIKASI MANUAL (p=23, g=5)",
        p=23,
        g=5,
        a=6,
        b=15,
        show_cycle=True
    )

    # 4. Demonstrasi validasi input tidak valid
    demonstrate_input_validation()

    # 5. Mode Interaktif Opsional (jika dijalankan dengan argumen --interactive)
    if "--interactive" in sys.argv:
        print("\n" + "=" * 78)
        print("MODE INTERAKTIF DIFFIE-HELLMAN")
        print("=" * 78)
        try:
            u_p = int(input("Masukkan bilangan prima p       : "))
            u_g = int(input("Masukkan generator g            : "))
            u_a = int(input(f"Masukkan private key Alice (1..{u_p-2}): "))
            u_b = int(input(f"Masukkan private key Bob   (1..{u_p-2}): "))
            run_diffie_hellman_simulation("SIMULASI INPUT PENGGUNA", u_p, u_g, u_a, u_b)
        except Exception as exc:
            print(f"[ERROR INPUT] {exc}")
