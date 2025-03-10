# Grafo de Visibilidad

## Instalación

1. Crea un ambiente virtual en la carpeta del proyecto para no modificar las librerías que ya tienes instaladas.

```sh
python -m venv .venv
source .venv/bin/activate
```

2. Instala las dependencias.

```sh
pip install -r requirements.txt
```

## Uso

El programa principal es `src/main.py`. Tiene varios argumentos opcionales. Puedes utilizar `-h` para mostrar las opciones.

```sh
python src/main.py -h
```

El resultado es:

```sh
usage: main.py [-h] [--complete] [--width WIDTH] [--height HEIGHT] [--fps FPS]
options:
-h, --help       show this help message and exit
--complete       Muestra todos los vértices: grafo de visibilidad completo
--width WIDTH    Ancho en píxeles de la ventana
--height HEIGHT  Altura en píxeles de la ventana
--fps FPS        FPS de la simulación
```


Como todos son opcionales, no tienes que usar ninguno de los parámetros. Sin embargo, por default, el algoritmo utilizado es el `grafo de visibilidad reducido`. Si quieres utilizar el grafo de visibilidad completo, agrega el argumento `--complete`. Es decir:


Para correr el grafo de visibilidad completo:

```sh
python src/main.py --complete
```

Para correr el grafo de visibilidad reducido:

```sh
python src/main.py
```

Puedes cambiar el punto de partida (cuadro blanco pequeño) haciendo `clic izquierdo`, con `clic derecho` puedes cambiar la meta (cuadro blanco grande). Al oprimir la `tecla p` el cuadro blanco se dirigirá hacia la meta, pero se detendrá si la oprimes de nuevo.
