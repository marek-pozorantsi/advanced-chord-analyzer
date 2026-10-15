import unittest
from context import smooth_segments, merge_windows
from evaluate import evaluate
class ContextTests(unittest.TestCase):
    def test_smoothing_avoids_one_frame_flip(self):
        inp=[{'name':'Cmaj7','alternatives':[{'name':'Cmaj7','score':1.0},{'name':'G7','score':0.7}]},
             {'name':'G7','alternatives':[{'name':'G7','score':1.01},{'name':'Cmaj7','score':1.0}]},
             {'name':'Cmaj7','alternatives':[{'name':'Cmaj7','score':1.0},{'name':'G7','score':0.7}]}]
        self.assertEqual(smooth_segments(inp),['Cmaj7']*3)
    def test_strong_change_remains(self):
        inp=[{'name':'C','alternatives':[{'name':'C','score':2.},{'name':'G','score':0.}]},
             {'name':'G','alternatives':[{'name':'C','score':0.},{'name':'G','score':2.}]}]
        self.assertEqual(smooth_segments(inp),['C','G'])
    def test_evaluation(self):
        a={'segments':[{'start':0,'end':2,'name':'C'},{'start':2,'end':4,'name':'G'}]}
        b={'segments':[{'start':0,'end':3,'name':'C'},{'start':3,'end':4,'name':'G'}]}
        self.assertEqual(evaluate(a,b)['exact_match_accuracy'],0.75)
    def test_merge(self):
        a=[{'start':0,'end':.5,'name':'C','detected_notes':['C4'],'evidence':{}},
           {'start':.5,'end':1,'name':'G','detected_notes':['E4'],'evidence':{}}]
        out=merge_windows(a,['C','C']);self.assertEqual(len(out),1)
        self.assertEqual(out[0]['detected_notes'],['C4','E4'])
if __name__=='__main__':unittest.main()
