from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import subprocess
import sys
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from engine import analyze
from transcription import infer_notes

ROOT=Path(__file__).resolve().parent
app=FastAPI(title='Advanced Chord Analyzer v0.7')
app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
ALLOWED={'.wav','.mp3','.flac','.ogg','.m4a','.webm','.mp4'}
MAX_BYTES=100*1024*1024

@app.get('/')
def home():return FileResponse(ROOT/'static'/'index.html')

@app.get('/health')
def health():
    return {'status': 'ok', 'version': '0.7-deploy'}

@app.get('/capabilities')
def capabilities():
    return {'demucs_installed':importlib.util.find_spec('demucs') is not None,
            'basic_pitch_installed':importlib.util.find_spec('basic_pitch') is not None,
            'ffmpeg_installed':shutil.which('ffmpeg') is not None,
            'model':'htdemucs',
            'note':'Zainstalowany pakiet nie oznacza, że wagi modelu zostały pobrane.'}

@app.post('/analyze')
async def analyze_file(file:UploadFile=File(...), mode:str=Form('spectral'), context_enabled:bool=Form(True), context_penalty:float=Form(0.13)):
    if mode not in ('spectral','demucs','transcription','deep'):
        raise HTTPException(400,'Nieznany tryb analizy')
    if not 0 <= context_penalty <= 1:
        raise HTTPException(400,'Kara kontekstowa musi być w zakresie 0–1')
    ext=Path(file.filename or '').suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400,'Dozwolony format: MP3/WAV/FLAC/OGG/M4A/WEBM/MP4')
    data=await file.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:raise HTTPException(413,'Limit 100 MB')
    with TemporaryDirectory() as d:
        wd=Path(d)
        path=wd/('input'+ext);path.write_bytes(data)
        try:
            # Normalize for compatibility with ffmpeg-supported container formats.
            if ext in {'.webm','.mp4','.m4a'}:
                output=wd/'converted.wav'
                if not shutil.which('ffmpeg'):
                    raise ValueError('Brak FFmpeg na serwerze.')
                subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y',
                    '-i',str(path),'-vn','-ac','2','-ar','44100',str(output)],
                    timeout=120,check=True,capture_output=True)
                path=output
            if mode in ('demucs','deep'):
                if importlib.util.find_spec('demucs') is None:
                    raise ValueError('Brak Demucs. Zainstaluj zależności z requirements-ai.txt na serwerze.')
                out=wd/'stems'
                cmd=[sys.executable,'-m','demucs','-n','htdemucs','-o',str(out),str(path)]
                try:
                    proc=subprocess.run(cmd,timeout=1200,capture_output=True,text=True)
                except subprocess.TimeoutExpired:
                    raise ValueError('Przekroczono 20-minutowy limit separacji. Spróbuj krótszego fragmentu lub serwera GPU.')
                if proc.returncode:
                    raise ValueError('Demucs nie zakończył separacji: '+(proc.stderr or proc.stdout)[-1100:])
                stems=out/'htdemucs'/path.stem
                bass=stems/'bass.wav'; other=stems/'other.wav'
                if not bass.is_file() or not other.is_file():
                    raise ValueError('Demucs nie wygenerował wymaganych ścieżek bass.wav i other.wav.')
                notes=infer_notes(str(other)) if mode=='deep' else None
                result=analyze(str(path),bass_path=str(bass),harmony_path=str(other),note_events=notes,use_context=context_enabled,context_penalty=context_penalty)
                result['stems_used']=['bass','other']
                result['separation_model']='htdemucs'
                return result
            if mode=='transcription':
                return analyze(str(path),note_events=infer_notes(str(path)),use_context=context_enabled,context_penalty=context_penalty)
            return analyze(str(path),use_context=context_enabled,context_penalty=context_penalty)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise HTTPException(422,'Problem z dekodowaniem pliku (FFmpeg): '+str(e))
        except ValueError as e:
            raise HTTPException(422,str(e))
        except Exception as e:
            raise HTTPException(422,'Analiza nie powiodła się: '+str(e))
