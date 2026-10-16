from harmony_v2 import rank_chords

def test_simple_b_minor():
    # Polish Hm = B, D, F# (pitch classes 11, 2, 6)
    x=[0]*12
    for pc in (11,2,6):x[pc]=1
    assert rank_chords(x)[0]["name"]=="Bm"

def test_simple_c_major():
    x=[0]*12
    for pc in (0,4,7):x[pc]=1
    assert rank_chords(x)[0]["name"]=="C"
