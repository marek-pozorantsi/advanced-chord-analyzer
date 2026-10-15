"""Small deterministic smoke checks, not an accuracy benchmark."""
import unittest
import numpy as np
from engine import candidates, NAMES
from transcription import notes_to_chroma

class HarmonyTests(unittest.TestCase):
    def test_rootless_is_considered(self):
        h=np.zeros(12); h[[2,4,7,11]]=1
        b=np.zeros(12); b[0]=1
        names=[a['name'] for a in candidates(h,b,8,note_chroma=h)]
        self.assertIn('Cmaj9',names)
        self.assertIn('Em7/C',names)

    def test_detected_note_overlap(self):
        events=[{'start':0.0,'end':2.0,'midi':64,'strength':1,'name':'E4'},
                {'start':1.0,'end':3.0,'midi':67,'strength':0.5,'name':'G4'}]
        h,notes=notes_to_chroma(events,0.5,1.5)
        self.assertGreater(h[4],h[7]);self.assertEqual(set(notes),{'E4','G4'})

    def test_all_zero_silence(self):
        z=np.zeros(12)
        self.assertEqual(candidates(z,z)[0]['name'],'N')

if __name__=='__main__': unittest.main()
