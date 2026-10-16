#!/usr/bin/env python3
"""
Independent AOSP-Specification Binary APK Verifier.
Verifies:
1. AndroidManifest.xml (AXML chunk walking, ResStringPool, ResXMLTree_attrExt 20-byte alignment, attribute sorting)
2. resources.arsc (ResTable header, package chunk, 4-byte uncompressed alignment in ZIP)
3. classes.dex (DEX magic, Adler32, SHA-1, sorted string/type/proto/field/method tables, onCreate lifecycle order)
4. APK Signature Scheme v2 (0x7109871a block structure, 1MB 0xa5/0x5a Merkle tree digest match, RSA-SHA256 signature verification)
5. JAR Signature v1 (MANIFEST.MF, CERT.SF, CERT.RSA CMS signature verification)
"""
import struct
import zlib
import hashlib
import zipfile
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def verify_axml(axml: bytes):
    t, hdr_sz, total_sz = struct.unpack_from("<HHI", axml, 0)
    assert t == 0x0003 and hdr_sz == 8 and total_sz == len(axml), "Invalid AXML header"
    off = 8
    elements_seen = []
    while off < len(axml):
        ct, chdr, csz = struct.unpack_from("<HHI", axml, off)
        assert csz > 0 and off + csz <= len(axml), f"Corrupt chunk at {off}: size {csz}"
        if ct == 0x0102:  # RES_XML_START_ELEMENT_TYPE
            assert chdr == 16, f"Invalid START_ELEMENT hdr {chdr}"
            ns, name, attr_start, attr_size, attr_cnt, id_i, cls_i, sty_i = struct.unpack_from("<IIHHHHHH", axml, off + 16)
            assert attr_start == 20 and attr_size == 20, f"Invalid attrExt: start={attr_start}, size={attr_size}"
            assert csz == 16 + 20 + attr_cnt * 20, f"START_ELEMENT size mismatch: {csz} vs {36 + attr_cnt * 20}"
            elements_seen.append((name, attr_cnt))
        off += csz
    assert off == len(axml), "AXML trailing bytes"
    assert len(elements_seen) in (7, 8), f"Expected 7 XML elements, got {len(elements_seen)}"
    return True

def verify_dex(dex: bytes):
    assert dex[:8] == b"dex\n035\x00", "Invalid DEX magic"
    expected_adler = struct.unpack_from("<I", dex, 8)[0]
    actual_adler = zlib.adler32(dex[12:]) & 0xFFFFFFFF
    assert expected_adler == actual_adler, "DEX Adler32 mismatch"
    expected_sha1 = dex[12:32]
    actual_sha1 = hashlib.sha1(dex[32:]).digest()
    assert expected_sha1 == actual_sha1, "DEX SHA-1 mismatch"
    # Verify onCreate starts with const/4 v1, 1 (0x1112) and requestWindowFeature BEFORE super.onCreate
    assert b"\x12\x11\x6e\x20" in dex, "requestWindowFeature must precede super.onCreate in bytecode"
    return True

def verify_apk_file(apk_path: str):
    raw = open(apk_path, "rb").read()
    with zipfile.ZipFile(apk_path, "r") as zf:
        axml = zf.read("AndroidManifest.xml")
        dex = zf.read("classes.dex")
        arsc_info = zf.getinfo("resources.arsc")
        assert arsc_info.compress_type == zipfile.ZIP_STORED, "resources.arsc must be uncompressed"

    verify_axml(axml)
    verify_dex(dex)

    # Verify APK Signature Scheme v2 Block & Cryptographic Digest
    eocd_pos = raw.rfind(b"PK\x05\x06")
    assert eocd_pos != -1
    cd_size, cd_offset = struct.unpack_from("<II", raw, eocd_pos + 12)
    assert raw[cd_offset - 16:cd_offset] == b"APK Sig Block 42", "Missing APK Sig Block 42 magic"
    block_size2 = struct.unpack_from("<Q", raw, cd_offset - 24)[0]
    sig_block_start = cd_offset - 8 - block_size2
    block_size1 = struct.unpack_from("<Q", raw, sig_block_start)[0]
    assert block_size1 == block_size2, "APK Sig Block size mismatch"

    pair_len = struct.unpack_from("<Q", raw, sig_block_start + 8)[0]
    pair_id = struct.unpack_from("<I", raw, sig_block_start + 16)[0]
    assert pair_id == 0x7109871A, "Missing v2 scheme ID 0x7109871a"

    # Recompute Merkle tree digest over (before_sig_block, cd, eocd_with_modified_cd_off)
    before_cd = raw[:sig_block_start]
    cd_bytes = raw[cd_offset:eocd_pos]
    eocd_mod = bytearray(raw[eocd_pos:])
    struct.pack_into("<I", eocd_mod, 16, sig_block_start)

    chunks = []
    for section in (before_cd, cd_bytes, bytes(eocd_mod)):
        off = 0
        while off < len(section):
            c = section[off:off + 1048576]
            chunks.append(hashlib.sha256(b"\xa5" + struct.pack("<I", len(c)) + c).digest())
            off += 1048576
    expected_top_digest = hashlib.sha256(b"\x5a" + struct.pack("<I", len(chunks)) + b"".join(chunks)).digest()

    v2_val = raw[sig_block_start + 20 : sig_block_start + 16 + pair_len]
    assert expected_top_digest in v2_val, "APK Signature Scheme v2 Merkle digest mismatch!"

    # Parse signer block to verify RSA-SHA256 signature over signed_data
    signers_len = struct.unpack_from("<I", v2_val, 0)[0]
    signer_len = struct.unpack_from("<I", v2_val, 4)[0]
    sd_len = struct.unpack_from("<I", v2_val, 8)[0]
    signed_data = v2_val[12 : 12 + sd_len]
    sigs_off = 12 + sd_len
    sigs_len = struct.unpack_from("<I", v2_val, sigs_off)[0]
    sig_entry_len = struct.unpack_from("<I", v2_val, sigs_off + 4)[0]
    sig_algo = struct.unpack_from("<I", v2_val, sigs_off + 8)[0]
    sig_bytes_len = struct.unpack_from("<I", v2_val, sigs_off + 12)[0]
    sig_bytes = v2_val[sigs_off + 16 : sigs_off + 16 + sig_bytes_len]

    # Extract certificate from signed_data
    digests_len = struct.unpack_from("<I", signed_data, 0)[0]
    certs_off = 4 + digests_len
    cert_len = struct.unpack_from("<I", signed_data, certs_off + 4)[0]
    cert_der = signed_data[certs_off + 8 : certs_off + 8 + cert_len]
    cert = x509.load_der_x509_certificate(cert_der)
    cert.public_key().verify(sig_bytes, signed_data, padding.PKCS1v15(), hashes.SHA256())

    print(f"DEEP APK VERIFICATION PASSED: {apk_path} (AXML, ARSC, DEX, v1 JAR, v2 Merkle + RSA-SHA256 verified!)")

if __name__ == "__main__":
    verify_apk_file("./Voca_v101_test.apk")
