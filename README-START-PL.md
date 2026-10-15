# Advanced Chord Analyzer v0.7 – jak uruchomić

## Na Windows
1. Rozpakuj ZIP do dowolnego katalogu.
2. Kliknij dwa razy **URUCHOM_WINDOWS.bat**. Wymaga zainstalowanego Pythona 3.11 i dostępu do internetu przy pierwszym uruchomieniu; do dekodowania MP3/WebM może być potrzebny FFmpeg dostępny w PATH.
3. Poczekaj na instalację bibliotek i otwórz **http://127.0.0.1:8000** (nie otwieraj `static/index.html`!).
4. Wybierz plik lub przechwytywanie dźwięku karty. Po zakończeniu utworu kliknij **Zatrzymaj** (maksymalnie po 10 minutach nagrywanie samo się kończy), a następnie **Analizuj nagranie**.
5. Domyślnie dostępny jest **Szybki — widmo**. Modele Demucs / Basic Pitch to oddzielne instalacje serwerowe i wymagają silniejszego sprzętu.

## Hosting online
Repozytorium można wdrożyć z załączonego Dockerfile na platformie obsługującej Docker i Pythona, z trwałym procesem serwera HTTP. Ustaw port dostarczony przez hosting; komenda startowa jest w Dockerfile. To wdraża **tylko tryb spektralny**, ponieważ modele AI nie są instalowane domyślnie. Do trybów AI potrzebny jest osobny serwer z odpowiednimi zależnościami i zasobami CPU/GPU. Użytkownik nie otrzymuje automatycznie publicznego adresu po pobraniu ZIP — konieczne jest rzeczywiste wdrożenie na wybrany hosting.

## Ograniczenia
To prototyp badawczy. Niezweryfikowana dokładność na komercyjnych nagraniach. Przechwytywanie audio z karty zależy od uprawnień i ograniczeń serwisów; nie obchodzi zabezpieczeń DRM. W obecnym prototypie analiza nie jest kolejką zadań, a sam licznik nagrywania nie jest postępem analizy. Nie przesyłaj poufnych nagrań na publicznie dostępny serwer bez zabezpieczeń uwierzytelniających.
