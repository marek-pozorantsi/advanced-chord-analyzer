"""Temporal chord hypothesis rescoring. Scores are relative, not calibrated."""

def chord_root(name):
    if not name or name == 'N': return None
    root = name.split('/')[0]
    names={'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
    for prefix in sorted(names,key=len,reverse=True):
        if root.startswith(prefix):return names[prefix]
    return None

def transition(a,b,penalty=0.13):
    if a==b:return 0.10
    ra,rb=chord_root(a),chord_root(b)
    # Adjacent chord changes cost a modest amount; common fifth or fourth roots
    # are slightly easier than unrelated changes. This is an explicit prior,
    # never a claim that the progression is correct.
    if ra is not None and rb is not None and (ra-rb)%12 in (5,7):return -penalty*0.55
    return -penalty

def smooth_segments(segments,penalty=0.13):
    """Viterbi decode among per-window top-k candidates. Does not modify inputs."""
    if not segments:return []
    layers=[]
    for seg in segments:
        opts=seg.get('alternatives') or [{'name':seg['name'],'score':0.0}]
        states={}
        for cand in opts:
            name=cand['name'];score=float(cand.get('score',0))
            if name not in states or score>states[name]:states[name]=score
        layers.append(states)
    history=[]; prev={}
    for i,layer in enumerate(layers):
        curr={};back={}
        for name,local in layer.items():
            if i==0:curr[name]=local;back[name]=None
            else:
                parent=max(prev,key=lambda p:prev[p]+transition(p,name,penalty))
                curr[name]=local+prev[parent]+transition(parent,name,penalty)
                back[name]=parent
        history.append(back);prev=curr
    chosen=[None]*len(layers);chosen[-1]=max(prev,key=prev.get)
    for i in range(len(layers)-1,0,-1):chosen[i-1]=history[i][chosen[i]]
    return chosen

def merge_windows(windows,chosen):
    merged=[]
    for original,name in zip(windows,chosen):
        seg=dict(original);seg['name']=name
        seg['context_changed']=name!=original['name']
        seg['raw_name']=original['name']
        seg['evidence']=dict(original.get('evidence',{}))
        if merged and merged[-1]['name']==seg['name']:
            prev=merged[-1];prev['end']=seg['end'];prev['context_changed']=prev['context_changed'] or seg['context_changed']
            prev['detected_notes']=list(dict.fromkeys(prev.get('detected_notes',[])+seg.get('detected_notes',[])))[:24]
            prev['evidence']['detected_notes']=prev['detected_notes']
        else:merged.append(seg)
    return merged
