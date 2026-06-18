# Cuerda vibrante 1D

Simulación de una cuerda vibrante mediante diferencias finitas. El audio se genera directamente a partir de la evolución física de la cuerda, no desde una librería de síntesis.

El proyecto genera una señal WAV desde el desplazamiento de la cuerda en una posición de pickup, permite visualizar el espectro, exportar una animación de la cuerda y validar la simulación contra la predicción analítica de Fourier.

## Requisitos

El proyecto usa Python `>=3.10` y `uv` como gestor de entorno, dependencias y ejecución.

Desde la raíz del repositorio, la instalación recomendada es:

```bash
uv sync --extra dev
```

Esto crea o actualiza `.venv`, instala las dependencias principales y agrega las dependencias de desarrollo necesarias para correr los tests.

No hace falta activar el entorno manualmente. Los comandos del proyecto se ejecutan con `uv run`.

## Uso rápido

Generar el WAV principal:

```bash
uv run cuerda
```

Generar WAV, espectro y validación contra Fourier:

```bash
uv run cuerda --validate --plot
```

Generar una animación de la cuerda como HTML:

```bash
uv run cuerda --animate
```

Los archivos generados quedan en `outputs/`.

## Salidas generadas

El comando base genera:

```text
outputs/cuerda.wav
```

El WAV incluye por defecto `0.25 s` de silencio inicial y un fade-in corto de `0.005 s`. Esto no cambia la simulación física; solo mejora la escucha al abrir el archivo, evitando que la nota empiece exactamente en la primera muestra.

Cuando se usa `--plot`, también se genera:

```text
outputs/spectrum.png
```

Cuando se usa `--animate`, se genera por defecto:

```text
outputs/cuerda.html
```

Para abrir la animación en Ubuntu:

```bash
xdg-open outputs/cuerda.html
```

Para abrirla desde WSL:

```bash
explorer.exe "$(wslpath -w outputs/cuerda.html)"
```

La salida HTML es la opción recomendada para animaciones, porque no depende del backend gráfico interactivo de Matplotlib. Si se quiere intentar abrir una ventana directamente, se puede usar:

```bash
uv run cuerda --show
```

## Parámetros de simulación

Los parámetros principales se controlan desde la CLI.

```bash
uv run cuerda --f1 110 --duration 5 --pluck 0.25 --pickup 0.8 --sigma0 0.6 --sigma1 0.00012
```

`f1` define la frecuencia fundamental deseada. `duration` define la duración de la simulación en segundos. `pluck` define la posición del pulsado como fracción de la longitud de la cuerda. `pickup` define la posición del micrófono virtual, también como fracción de la longitud. `sigma0` controla el amortiguamiento global y `sigma1` controla la pérdida adicional de los armónicos altos.

La frecuencia de muestreo por defecto es `44100 Hz`. Puede cambiarse con:

```bash
uv run cuerda --fs 48000
```

La animación acepta una tasa de cuadros configurable:

```bash
uv run cuerda --animate --fps 30
```

También se puede elegir explícitamente el archivo HTML de salida:

```bash
uv run cuerda --animate outputs/demo.html
```

## Parámetros de audio

El silencio inicial y el fade-in pertenecen al renderizado del WAV, no al modelo físico. La simulación sigue empezando en $t=0$ con la cuerda ya pulsada y liberada.

Cambiar la duración del silencio inicial:

```bash
uv run cuerda --lead-silence 0.5
```

Desactivar el silencio inicial:

```bash
uv run cuerda --lead-silence 0
```

Cambiar el fade-in inicial:

```bash
uv run cuerda --fade-in 0.01
```

Desactivar el fade-in:

```bash
uv run cuerda --fade-in 0
```

Los valores por defecto son:

```text
lead_silence = 0.25
fade_in = 0.005
```

## Tests

Los tests verifican propiedades mínimas del modelo físico y del pipeline numérico. En particular, validan que el pulsado triangular alcance exactamente la amplitud máxima en el punto de pulsado, que la simulación rechace configuraciones inestables que violan la condición CFL, y que el quinto armónico quede casi anulado cuando `pluck_pos = 0.2`.

Para correrlos:

```bash
uv run pytest -q
```

Para correrlos desde una sincronización limpia:

```bash
rm -rf .venv
uv sync --extra dev
uv run pytest -q
```

## Modelo físico

La cuerda se modela con una ecuación de onda 1D amortiguada:

$$
\begin{aligned}
u_{tt}+2\sigma_0u_t-2\sigma_1u_{xxt}=c^2u_{xx}.
\end{aligned}
$$

El término $\sigma_0$ introduce amortiguamiento global. El término $\sigma_1$ introduce pérdidas dependientes de la frecuencia, haciendo que los armónicos altos decaigan más rápido que la fundamental.

La velocidad de onda se elige a partir de la frecuencia fundamental deseada:

$$
\begin{aligned}
c = 2Lf_1.
\end{aligned}
$$

La condición de estabilidad usada por el esquema explícito es la condición CFL:

$$
\begin{aligned}
r = \frac{c,dt}{dx} \le 1.
\end{aligned}
$$

Si una configuración viola esa condición, la simulación levanta `ValueError`.

## Validación contra Fourier

El desplazamiento inicial es un pulsado triangular. Para ese tipo de condición inicial, la serie de Fourier predice la amplitud relativa de cada modo normal de la cuerda.

La amplitud modal esperada para el modo $m$ es proporcional a:

$$
\begin{aligned}
b_m =
\frac{2hL^2}{m^2\pi^2x_p(L-x_p)}
\sin\left(\frac{m\pi x_p}{L}\right).
\end{aligned}
$$

Como el audio se toma en una posición de pickup, la amplitud observada también queda multiplicada por:

$$
\begin{aligned}
\sin\left(\frac{m\pi x_{\text{pickup}}}{L}\right).
\end{aligned}
$$

Por ejemplo, si `pluck = 0.2`, el quinto armónico queda casi anulado porque el punto de pulsado coincide con un nodo de ese modo.

La validación se ejecuta con:

```bash
uv run cuerda --validate
```

## Estructura del proyecto

```text
cuerda_vibrante/
├── .gitignore
├── pyproject.toml
├── uv.lock
├── README.md
├── examples/
│   └── demo.py
├── tests/
│   └── test_model.py
└── src/
    └── cuerda/
        ├── __init__.py
        ├── analysis.py
        ├── cli.py
        ├── config.py
        ├── io.py
        ├── model.py
        └── plots.py
```

`model.py` contiene el núcleo físico y numérico. `analysis.py` contiene el espectro y la comparación contra Fourier. `io.py` escribe el WAV y aplica el silencio inicial y el fade-in. `plots.py` genera espectro y animación. `cli.py` conecta todo en el comando `cuerda`.

## Desarrollo

El paquete usa layout `src/`. El nombre del proyecto es `cuerda-vibrante`, pero el módulo importable se llama `cuerda`.

La configuración relevante en `pyproject.toml` es:

```toml
[build-system]
requires = ["uv_build>=0.11.21,<0.12"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = "cuerda"
module-root = "src"
```

Esto evita que el backend busque un módulo llamado `cuerda_vibrante`, que sería la normalización automática del nombre del proyecto.

Para verificar desde dónde se está importando el paquete:

```bash
uv run python -c "import cuerda; print(cuerda.__file__)"
```

La salida debería apuntar a:

```text
src/cuerda/__init__.py
```

## Archivos ignorados

El repositorio no debe versionar archivos generados, caches, entornos virtuales ni metadata local de build.

El `.gitignore` debería excluir, como mínimo:

```text
__pycache__/
*.pyc
.pytest_cache/
.venv/
*.egg-info/
build/
dist/
outputs/
*.wav
*.png
```
