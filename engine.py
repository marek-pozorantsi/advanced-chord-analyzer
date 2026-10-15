"""Baseline spectral harmony analysis. NOT an AI transcription model."""
import numpy as np
import librosa

NAMES = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
# intervals, canonical suffix; wide vocabulary intentionally includes overlapping hypotheses
QUALITIES = [
 ('', [0,4,7]), ('m',[0,3,7]), ('5',[0,7]),
 ('dim',[0,3,6]), ('aug',[0,4,8]), ('sus2',[0,2,7]), ('sus4',[0,5,7]),
 ('6',[0,4,7,9]), ('m6',[0,3,7,9]), ('add9',[0,2,4,7]), ('m(add9)',[0,2,3,7]),
 ('7',[0,4,7,10]), ('maj7',[0,4,7,11]), ('m7',[0,3,7,10]),
 ('m(maj7)',[0,3,7,11]), ('m7b5',[0,3,6,10]), ('dim7',[0,3,6,9]),
 ('9',[0,2,4,7,10]), ('maj9',[0,2,4,7,11]), ('m9',[0,2,3,7,10]),
 ('11',[0,2,4,5,7,10]), ('m11',[0,2,3,5,7,10]),
 ('13',[0,2,4,7,9,10]), ('maj13',[0,2,4,7,9,11]), ('m13',[0,2,3,7,9,10]),
 ('7sus4',[0,5,7,10]), ('9sus4',[0,2,5,7,10]), ('13sus4',[0,2,5,7,9,10]),
 ('7b9',[0,1,4,7,10]), ('7#9',[0,3,4,7,10]), ('7#11',[0,4,6,7,10]),
 ('7b5',[0,4,6,10]), ('7#5',[0,4,8,10]),
 ('7b13',[0,4,7,8,10]), ('7alt',[0,1,3,4,6,8,10]),
 ('m9b5',[0,2,3,6,10]), ('maj7#11',[0,4,6,7,11]),
 ('m(maj9)',[0,2,3,7,11]), ('7b9#11',[0,1,4,6,7,10]),
 ('9#11',[0,2,4,6,7,10]), ('7#9b13',[0,3,4,7,8,10])
]

def candidates(harmony, bass, amount=3, note_chroma=None):
    h=np.maximum(np.array(harmony,dtype=float),0)
    b=np.maximum(np.array(bass,dtype=float),0)
    if h.max()<1e-8:
        return [{'name':'N','score':0.0,'notes':[]}]
    h=h/(np.linalg.norm(h)+1e-8)
    b=b/(b.sum()+1e-8)
    # When note transcription exists, favor a candidate that explains actually
    # detected notes. Keep missing roots possible, but avoid rewarding huge sets.
    observed=None
    if note_chroma is not None:
        observed=np.maximum(np.asarray(note_chroma,dtype=float),0)
        if observed.sum()>0: observed=observed/(observed.sum()+1e-9)
        else: observed=None
    result=[]
    for root in range(12):
        for suffix,intervals in QUALITIES:
            pcs=np.array(sorted(set((root+i)%12 for i in intervals)))
            mask=np.zeros(12);mask[pcs]=1
            # Rewards explained energy; penalizes unexplained tones and over-complex hypotheses.
            inside=float(np.dot(h,mask))
            outside=float(np.dot(h,1-mask))
            essential=[root]
            if 3 in intervals: essential.append((root+3)%12)
            if 4 in intervals: essential.append((root+4)%12)
            if 10 in intervals: essential.append((root+10)%12)
            if 11 in intervals: essential.append((root+11)%12)
            essential_score=float(np.mean(h[essential])) if essential else 0
            complexity=max(0,len(pcs)-3)
            base=inside-0.52*outside+0.4*essential_score-0.075*complexity
            if observed is not None:
                coverage=float(np.dot(observed,mask))
                # Complexity penalty also discourages speculative 11/13 labels.
                base += 0.80*coverage - 0.055*complexity
                # Lack of root does not exclude rootless voicings; gently penalize it.
                if observed[root]<0.025: base-=0.035
            # Rootless interpretations allowed: test bass independently, but small penalty for non-chord bass.
            for basspc in range(12):
                bass_weight=float(b[basspc])
                if bass_weight<0.10: continue
                name=NAMES[root]+suffix+(('/'+NAMES[basspc]) if basspc!=root else '')
                val=base+0.42*bass_weight-(0.11 if basspc not in pcs else 0)
                result.append((val,name,pcs.tolist()))
            # Candidate without firm bass assignment
            result.append((base-0.10,NAMES[root]+suffix,pcs.tolist()))
    result.sort(reverse=True,key=lambda x:x[0])
    dedup=[];seen=set()
    for val,name,pcs in result:
        if name in seen:continue
        seen.add(name)
        dedup.append({'name':name,'score':round(float(val),3),'notes':[NAMES[p] for p in pcs]})
        if len(dedup)>=amount:break
    return dedup

def analyze(path, bass_path=None, harmony_path=None, note_events=None, use_context=True, context_penalty=0.13):
    y,sr=librosa.load(path,sr=22050,mono=True,duration=600)
    if len(y)<sr:raise ValueError('Nagranie musi mieć przynajmniej 1 sekundę.')
    hop=512
    # CQT: harmonic representation with semitone resolution and low-frequency bass bins
    if harmony_path:
        yh,_=librosa.load(harmony_path,sr=sr,mono=True,duration=600)
        yh=librosa.util.fix_length(yh,size=len(y))
    else:
        yh=y
    harm=librosa.effects.harmonic(yh,margin=3)
    cqt=np.abs(librosa.cqt(harm,sr=sr,hop_length=hop,fmin=librosa.note_to_hz('C1'),n_bins=84,bins_per_octave=12))
    # CQT bins begin at C1, thus modulo twelve is pitch class
    chroma=np.zeros((12,cqt.shape[1]))
    for pc in range(12):
        chroma[pc]=np.sum(cqt[pc::12],axis=0)
    # Low register C1–B2 for bass; bass spectrum is not a dedicated separated stem
    bass=np.zeros_like(chroma)
    if bass_path:
        yb,_=librosa.load(bass_path,sr=sr,mono=True,duration=600)
        yb=librosa.util.fix_length(yb,size=len(y))
        bcqt=np.abs(librosa.cqt(yb,sr=sr,hop_length=hop,fmin=librosa.note_to_hz('C1'),n_bins=36,bins_per_octave=12))
        for pc in range(12):
            bass[pc,:min(bass.shape[1],bcqt.shape[1])]=bcqt[pc,:bass.shape[1]]+0.7*bcqt[pc+12,:bass.shape[1]]+0.25*bcqt[pc+24,:bass.shape[1]]
    else:
        for pc in range(12):
            bass[pc]=cqt[pc]+cqt[pc+12]
    duration=len(y)/sr
    # overlapping analysis windows allow sub-beat change detection later
    step=0.5; window=1.2
    segments=[]
    if note_events is not None:
        from transcription import notes_to_chroma
    t=0.0
    while t<duration:
        end=min(t+step,duration)
        center=(t+end)/2
        f0=max(0,int((center-window/2)*sr/hop))
        f1=min(chroma.shape[1],max(f0+1,int((center+window/2)*sr/hop)))
        h=np.median(chroma[:,f0:f1],axis=1)
        b=np.median(bass[:,f0:f1],axis=1)
        detected_notes=[]
        midi_chroma=None
        if note_events is not None:
            midi_chroma,detected_notes=notes_to_chroma(note_events,t,end)
            if midi_chroma.sum()>0:
                # Normalize each representation before fusion; 60% weighted transcription.
                h=0.4*(h/(h.sum()+1e-9))+0.6*(midi_chroma/(midi_chroma.sum()+1e-9))
        opts=candidates(h,b,5, midi_chroma if note_events is not None else None)
        segments.append({'start':round(t,2),'end':round(end,2),'name':opts[0]['name'], 'alternatives':opts,
                         'bass':NAMES[int(np.argmax(b))], 'detected_notes':detected_notes, 'edited':False, 'evidence':{'detected_notes':detected_notes, 'bass_pitch_class':NAMES[int(np.argmax(b))], 'source':'AI + widmo' if note_events is not None else 'widmo'}})
        t=end
    from context import smooth_segments, merge_windows
    chosen=smooth_segments(segments,context_penalty) if use_context else [seg['name'] for seg in segments]
    context_changes=sum(a!=b['name'] for a,b in zip(chosen,segments))
    merged=merge_windows(segments,chosen)
    return {'duration':round(duration,2),'segments':merged,
            'engine':('Basic Pitch + CQT' if note_events is not None else ('Demucs + spektralny CQT' if bass_path else 'Spektralny CQT'))+' v0.6',
            'context_enabled':use_context, 'context_changes':context_changes, 'context_penalty':context_penalty, 'separation_used':bool(bass_path), 'transcription_used':note_events is not None, 'note_event_count':len(note_events) if note_events is not None else 0,
            'warning':('Wyniki pochodzą z rzeczywistej transkrypcji Basic Pitch i widma CQT; nie są zweryfikowane i mogą zawierać błędy. MT3 nie jest zintegrowany.' if note_events is not None else 'To hipotezy spektralne, bez transkrypcji nut AI. Złożone akordy mogą być błędne.')}
