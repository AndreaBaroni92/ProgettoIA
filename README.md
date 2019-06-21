# ProgettoIA
## Requisiti
- Python version 3.X
- [GeoPy](https://geopy.readthedocs.io/en/stable/)
- [jsonschema](https://pypi.org/project/jsonschema/)
## Cartelle

- **DatasetGraphml**: Contiene un insieme di file in formato .graphml che rappresentano la topologia di una rete

## Programmi principali


- **ProgettoIA/gen/crt_reqs.py** (dato un numero fissato di domini  genera un set di richieste e di domain constraint in formato .json)  
E' possibile modificare il numero di domini, richieste, e domain constraint che vengono generati settando opportuni parametri

- **ProgettoIA/gen/gen_map.py** utilizzo :  gen_map.py -i mappa.graphml -o mappa.dzn.  
Converte una mappa dal formato .graphml ai  formato .dzn con un numero fissato di nodi per dominio

```
e.g., python3 gen_map.py -i Map/grande/Highwinds.graphml -o mappa.dzn
```

- **ProgettoIA/gen/main.py** Questo programma utilizza i due script precedenti, in particolare, genera un insieme di richieste in formato .json e mappe in formato .dzn. Le mappe che devono essere convertite vengono prese dalla cartella  **ProgettoIA/gen/Map**  
E' possibile specificare quanti nodi per dominio debbano essere generati e il numero delle richieste. 

```
python3 main.py
```

- **ProgettoIA/model/model.mzn** E' un programma scritto in MiniZinc che prende in input una richiesta in formato .dzn una mappa in formato.dzn e stabilisce se la richiesta viene soddisfatta  
- **ProgettoIA/run/convertitore.py** utilizzo convertitore.<span>py -r User_request.json -c domain_constraints.json -o Request.dzn;  

- **ProgettoIA/run/chuffed.py** Esegue una serie di test automatici per verificare se le richieste contenute nella cartella testbed vengono soddisfatte, viene prodotto un report nella cartella result1 

- **ProgettoIA/run/chuffed2.py** E' una variante dello script chuffed.<span>py . Quando una richiesta viene soddisfatta i nodi utilizzati nel calcolo della soluzione vengono eliminati dalla mappa, e la mappa così aggiornata viene utilizzata per la richiesta successiva.  

```
python3 chuffed2.py
```

- **NB** i file chuffed.<span>py  e chuffed2.<span>py utilizzano per il calcolo della soluzione un eseguibile fzn-chuffed.exe che funziona solo su architeture Windows. Se si vuole utilizzare i file chuffed.<span>py  e chuffed2.<span>py su diverse architetture si richiede la sostituzione dell'eseguibile fzn-chuffed.exe con uno compatibile con la piattaforma in uso  
- **ProgettoIA/rlt** Contiene dei grafici e degli script per generare grafici dai risultati ottenuti



 

