# jobManagerPro

jobManagerPro to zbiór skryptów, które były dla mnie przydatne w czasie prowadzenia obliczeń chemicznych z wykorzystaniem infrastruktury plgrid (aczkolwiek mogą zostać wykorzystane wszędzie, gdzie stosuje się system kolejkowy slurm). Część z nich jest przydatna jeśli chodzi o zarządzanie zakolejkowanymi zadaniami, inne mogą okazać się ciekawymi rozwiązaniami dla osób wykorzystujących oprogramowanie AMBER lub Gaussian i chcą zautowatyzować schematyczne sekwencje obliczeniowe. 

# Instalacja

Jest prymitywna. Najzwyczajniej w świecie sklonuj repozytorium w katalogu domowym:

```
cd
git clone https://github.com/chemiczny/jobManagerPro
```

a następnie przejdź do świezo utworzonego katalogu i uruchom w nim skrypt printAliases.py

```
cd jobManagerPro
python3 printAliases.py
```

W ten sposób wyświetlone zostaną wszystkie aliasy, które mogą Ci się przydać. Oczywiście równie dobrze można je od razu przekierować do swojego pliku z aliasami np.:

```
python3 printAliases.py >> ~/.bash_aliases
```

Jedynym zewnętrznym modułem, który jest potrzebny do pracy z jobManagerPro jest networkx, dostępny tutaj: https://networkx.github.io/
Jeśli korzystasz z infrastruktury plgrid to nie musisz niczego dodatkowo instalować.

# Użytkowanie

## Kilka dodatków do zarządzania zadaniami w kolejce

Kiedy zaczynałem prowadzić obliczenia chemiczne zauważyłem, że mając kilka zadań do nadzoru łatwo się z nimi pogubić (przegapić zakończenie obliczeń, które trwały już 3 dni, a później szukać w którym katalogu znajdują się logi...). Dlatego sam używam nieco innych komend niż ```sbatch``` i ```squeue``` do analizy tego co się aktualnie dzieje w kolejce.

**sbatchPy** 

Użytkowanie: ``` sbatchPy skrypt.slurm [komentarz] ```

Ta komenda po prostu wrzuca zadanie do kolejki, przy okazji zapisując je w taki sposób by móc ją monitorować za pomocą komendy opisanej poniżej. Przy okazji można też dodać komentarz (opcjonalnie).

**squeuePy**

Użytkowanie: ``` squeuePy [hasło do wyszukania] ```

Wykonując samo ```squeuePy``` po prostu wyświetlimy aktualny stan zadań (oczywiście tylko tych, które zostały dodane do kolejki za pomocą sbatchPy). W terminalu powinniśmy zobaczyć coś takiego:

```
Joby uruchomione lub oczekujace:
jobID		20897617
Running Dir	/net/scratch/people/lol/auto_MD/dipterocarpol/MD
Script file:	amber.in
Comment		Controlled by graph
Status		R
Time:		21:33:33
Partition	plgrid
######################################################################
Joby ukonczone
jobID		20446599
Running Dir	/net/scratch/people/lol/amber_QMMM_MD/scan
Script file:	wham.slurm
######################################################################
```

Od razu widać więc pełną ścieżkę do katalogu, z którego uruchomiliśmy zadanie, komentarz (opcjonalnie), a także osobno wylistowane ukończone zadania. Oczywiście, gdyby lista ukończonych zadań miała tylko rosnąć w czasie, to nie miałoby to wielkiego sensu. Do usuwania danych z tej listy służy następna komenda.

Można też przefiltrować wyniki wyświetlane przez ```squeuePy```. Dodanie kolejnego argumentu spowoduje, że zostaną wyświetlone te zadania, które zawierają (w komentarzu lub ścieżce lub nazwie skryptu) daną frazę. Np. wykonanie ```squeuePy scan``` wyświetli:

```
Joby uruchomione lub oczekujace:
Joby ukonczone
jobID		20446599
Running Dir	/net/scratch/people/lol/amber_QMMM_MD/scan
Script file:	wham.slurm
######################################################################
```

Dzięki temu moźna łatwo zweryfikować np. ile zadań zostało uruchomionych z danego podfolderu itd. Na wszelki wypadek usunięte w ten sposób zadania są zapisywane w pliku ```finished.csv``` w katalogu ```~/jobManagerPro/```.

**sremovePy**

Użytkowanie: ``` sremovePy idZadania```

W ten sposób usuwamy zadania z listy kontrolowanej przez ```squeuePy```. Wykonanie komendy ```sremovePy``` na zadaniu, które jest w stanie ```running``` nie spowoduje jego zatrzymania, a jedynie przestanie być monitorowane przez jobManagerPro. Możliwe jest podanie wielu id w celu usunięcia więcej niż jednego zadania.

## Automatyzacja sekwencji obliczeń

Już wkrótce

# Gaussian

# AMBER
