"""Experimental Harmony Engine v2 — evidence-first chord scoring.

This module is NOT connected to the production audio pipeline yet.
Input: 12 chroma strengths ordered C,C#,D,Eb,E,F,F#,G,Ab,A,Bb,B.
Bass: optional pitch class. No claim of audio recognition accuracy.
"""
import numpy as np

ROOTS=("C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B")
TRIADS={"":(0,4,7),"m":(0,3,7),"dim":(0,3,6),"aug":(0,4,8),
        "sus2":(0,2,7),"sus4":(0,5,7)}
SEVENTHS={"7":(0,4,7,10),"maj7":(0,4,7,11),"m7":(0,3,7,10),
          "m7b5":(0,3,6,10),"dim7":(0,3,6,9)}
EXTENSIONS={"9":(0,2,4,7,10),"maj9":(0,2,4,7,11),
            "m9":(0,2,3,7,10),"11":(0,2,4,5,7,10),
            "m11":(0,2,3,5,7,10),"13":(0,2,4,7,9,10)}
ALL={**TRIADS,**SEVENTHS,**EXTENSIONS}

def rank_chords(chroma, bass_pc=None, limit=5):
    energy=np.asarray(chroma,dtype=float)
    if energy.shape!=(12,) or not np.all(np.isfinite(energy)):
        raise ValueError("Expected twelve finite chroma values")
    energy=np.maximum(energy,0)
    if energy.max()<=0:return [{"name":"N","score":0.0}]
    energy=energy/(energy.max()+1e-9)
    # Major/minor triads receive a prior, extended chords need observed support.
    results=[]
    for root in range(12):
        for quality,intervals in ALL.items():
            pcs=tuple(sorted({(root+i)%12 for i in intervals}))
            core=set((root+i)%12 for i in intervals[:3])
            inside=float(np.sum(energy[list(pcs)]))
            outside=float(np.sum(energy[[i for i in range(12) if i not in pcs]]))
            mandatory_penalty=sum(max(0,0.38-energy[p])*0.95 for p in core)
            # Extensions must be evidenced, not inferred from faint harmonics/noise.
            extra=sorted(set(pcs)-core)
            extension_penalty=sum(max(0,0.37-energy[p])*1.45 for p in extra)
            score=inside-1.25*outside-mandatory_penalty-extension_penalty
            score-=0.21*max(0,len(pcs)-3)
            if quality in TRIADS:score+=0.25
            name=ROOTS[root]+quality
            if bass_pc is not None and bass_pc!=root:
                if bass_pc not in pcs:score-=0.50
                name+="/"+ROOTS[bass_pc]
            results.append({"name":name,"score":round(score,4),"notes":[ROOTS[p] for p in pcs]})
    return sorted(results,key=lambda c:c["score"],reverse=True)[:limit]
