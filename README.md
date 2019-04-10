# ProgettoIA
## Requisiti
- Python version 3.X
- [GeoPy](https://geopy.readthedocs.io/en/stable/)
- [jsonschema](https://pypi.org/project/jsonschema/)
## Cartelle

-**examplesMapGraphml** : Contiene esempi di mappe in formato .graphml  
-**userRequest** : Contiene esempi di richieste nel formato .json  
-**domainConstraints**: Contiene esempi di domain Constraints nel formato .json  

## Comandi per eseguire i programmi
### Per convertire la mappa dal formato .graphml al formato .dzn
```
python gen_map.py -i <input_file.graphml> -o <output_file.dzn>
```
### Per convertire le richieste dal formato .json al formato .dzn

```
 python convertitore.py -r <request> -c <domain_constraints> -o <output_file> 
```
