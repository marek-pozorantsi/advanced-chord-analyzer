# Advanced Chord Analyzer v0.6 — research prototype

Building on v0.5, this version adds a **temporal chord decoder** (`context.py`) and **time-weighted evaluation** (`evaluate.py`). All existing source modes and optional Demucs / Basic Pitch integrations remain. Note: chord-label smoothing is not evidence of higher accuracy.

## New functionality
- Temporal Viterbi re-ranking over the five candidate chords per 0.5-second analysis frame. This uses a configurable soft penalty for chord changes, slightly favoring stable sequences; strong new chord evidence still wins.
- Context on/off checkbox in the web app, reported number of changed frame hypotheses, and explanation when context changed a selected result.
- Merge adjacent windows *after* context decoding, preserving detected-note evidence.
- CLI evaluation against hand-annotated JSON interval references: `python evaluate.py reference.json prediction.json`. Output includes duration-weighted exact-label match, coverage, and error intervals.
- Unit tests for persistence, strong changes, evaluation and merging.

## Run
Python 3.11 recommended (on the backend/server):
```
python -m venv .venv
# activate your venv
pip install -r requirements.txt
# for optional model modes on server:
pip install -r requirements-ai.txt
pip install -r requirements-transcription.txt
uvicorn server:app --host 127.0.0.1 --port 8000
```
Then open http://127.0.0.1:8000. For use from another machine a hosted server and HTTPS are needed. FFmpeg is necessary for various compressed sources. Running AI requires weights, RAM and compute resources; installing packages alone does not provide a working inference environment.

Run tests with `python -m unittest -v test_harmony.py test_context.py`.

## Honest limitations
- No full musical benchmark or real-world accuracy comparison has yet been performed.
- The temporal model is only a lightweight continuity prior, **not** learned harmonic grammar, so it can sometimes hide genuine quick changes.
- Evaluation uses exact chord labels, without enharmonic equivalence or harmony-weighted scoring. Comparing only exact labels can penalize musically equivalent interpretations. Reference labels must be manually verified.
- The application remains a backend-based source prototype, not a hosted web service. No public deployment, GPU service, or MT3 inference is included.
- Browser capture depends on browser permissions and streaming service restrictions. No circumvention of DRM.
