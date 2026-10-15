"""Duration-weighted evaluation against reference intervals (JSON).
Usage: python evaluate.py reference.json prediction.json
Both JSON files: {"segments":[{"start":0,"end":1,"name":"Cmaj7"},...]}
"""
import argparse,json

def evaluate(reference,predicted):
    ref=reference['segments'];pred=predicted['segments']
    bounds=sorted(set([v for s in ref+pred for v in (float(s['start']),float(s['end']))]))
    correct=covered=total=0.0
    errors=[]
    for a,b in zip(bounds,bounds[1:]):
        if b<=a:continue
        center=(a+b)*0.5
        r=next((s['name'] for s in ref if s['start']<=center<s['end']),None)
        if r is None:continue
        p=next((s['name'] for s in pred if s['start']<=center<s['end']),None)
        duration=b-a;total+=duration
        if p is not None:covered+=duration
        if p==r:correct+=duration
        else:errors.append({'start':a,'end':b,'expected':r,'predicted':p})
    return {'reference_seconds':round(total,3),'covered_seconds':round(covered,3),
            'exact_match_accuracy':round(correct/total,4) if total else None,
            'coverage':round(covered/total,4) if total else None,'errors':errors}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('reference');parser.add_argument('prediction');args=parser.parse_args()
    with open(args.reference,encoding='utf-8') as f:r=json.load(f)
    with open(args.prediction,encoding='utf-8') as f:p=json.load(f)
    print(json.dumps(evaluate(r,p),ensure_ascii=False,indent=2))
