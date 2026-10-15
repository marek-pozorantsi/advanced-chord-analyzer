# Advanced Chord Analyzer — wdrożenie online

## Czym jest ta paczka
Wersja v0.7 z plikiem `render.yaml` i endpointem `/health`. Konfiguracja wdraża *wyłącznie podstawowy silnik widmowy*. Wersje Demucs i Basic Pitch wymagają osobnych pakietów, wag modeli oraz mocniejszej instancji (najlepiej GPU).

## Uruchomienie na Render
1. Utwórz NOWE repozytorium na GitHub — zalecane prywatne. Przenieś zawartość tego folderu **bez folderu nadrzędnego** do repozytorium, tak aby `Dockerfile` i `render.yaml` były w katalogu głównym.
2. W serwisie Render wybierz `New` → `Blueprint` i wskaż repozytorium; potwierdź konfigurację, sprawdzając koszt i plan.
3. Poczekaj na zbudowanie i uruchomienie usługi. Dopiero wtedy uzyskasz URL `https://...onrender.com`.
4. Otwórz `/health` — powinno zwrócić `status: ok`.
5. Zacznij od krótkiego WAV/MP3 i trybu `Szybki — widmo (bez AI)`.

Uwaga: plan darmowy może mieć limity czasu, RAM i usypianie; dla długich plików, Demucs i Basic Pitch nie zapewnia stabilnych wyników. Koszty hostingu zależą od bieżącego cennika Render.

## Ograniczenia
- Link YouTube/Apple Music nie oznacza automatycznego pobrania lub analizy audio; przechwycenie dźwięku zależy od uprawnień przeglądarki i dostępności strumienia.
- Backend liczy analizę w jednym żądaniu; nie ma jeszcze prawdziwego raportowania etapów pracy.
- Nie testowano produkcyjnego wdrożenia w Render ani jakości AI na rzeczywistych utworach.
- Nagrania są przetwarzane tymczasowo, ale hosting ma dostęp do przesyłanego audio; nie wysyłaj poufnych materiałów na niezaufany serwer.
