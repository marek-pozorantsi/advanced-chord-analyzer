"""Optional genuine polyphonic note inference using Spotify Basic Pitch.
Best suited to a separated instrument stem. No mocked AI results.
"""
from pathlib import Path
import numpy as np


def infer_notes(audio_path):
    try:
        from basic_pitch.inference import predict
    except ImportError as exc:
        raise ValueError('Brak Basic Pitch na serwerze; wymagany Python 3.10/3.11 i instalacja requirements-transcription.txt.') from exc
    # predict performs actual model inference; generated models may initialize on first run.
    _, _, events = predict(str(audio_path))
    out=[]
    for event in events:
        start,end,pitch,amplitude = event[:4]
        if end <= start or amplitude <= 0: continue
        out.append({'start':float(start),'end':float(end),'midi':int(pitch),'strength':float(amplitude),
                    'name':midi_name(int(pitch))})
    return out


def midi_name(note):
    names=['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
    return names[note%12]+str(note//12-1)


def notes_to_chroma(events,start,end):
    """Duration-weighted active MIDI note classes for a time interval."""
    chroma=np.zeros(12,dtype=float)
    active=[]
    for event in events:
        overlap=max(0.,min(end,event['end'])-max(start,event['start']))
        if overlap<=0: continue
        weighted=overlap*max(0.,event['strength'])
        chroma[event['midi']%12]+=weighted
        active.append((weighted,event))
    active.sort(key=lambda x:x[0],reverse=True)
    return chroma,[e['name'] for _,e in active[:16]]
