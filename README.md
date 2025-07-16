# PLAIN

Este repositorio contiene un script para fichar automáticamente en PLAIN. El script se ejecuta en segundo plano en un ordenador y lee archivos de configuración <code>.json</code> para ver con que frecuencia tiene que fichar y por quién ha de hacerlo.

## Requisitos

Antes de empezar a usar este programa, hay que instalar las dependencias del programa. Para ello, se debe tener [`conda`](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) instalado en el sistema. En el repositorio se provee de dos archivos, para dos maneras diferentes de instalar las dependencias del programa en un entorno de [`conda`](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html).

#### [`conda`](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html)

El archivo `plain.yml` contiene la especificación del entorno de [`conda`](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) necesario para ejecutar este programa. Para instalar este entorno directamente, se puede ejecutar el siguiente comando,

```bash
conda env create -n <name> -f plain.yml
```

El problema de instalar así las dependencias es que el solver de [`conda`](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) tiene que resolver las versiones de los paquetes para instalar el entorno. Para ello, existe la segunda opción

#### [`conda-lock`](https://conda.github.io/conda-lock/)

[`conda-lock`](https://conda.github.io/conda-lock/) es un programa que permite create `lockfiles` de entornos de [`conda`](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html), en los que el entorno ya esta resuelto con versiones especificas para cada plataforma (`linux-64`, `win-64`, `osx-64`, `osx-arm64`), de forma que lo único necesario a la hora de instalar el entorno de [`conda`](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) contenido en el `lockfile` sea descargar los paquetes directamente e instalarlos. El archivo `plain.lock.yml` es un lockfile para las plataformas mencionadas con los paquetes contenidos en `plain.yml`. La única pega de este método de instalación es que requiere tener instalado [`conda-lock`](https://conda.github.io/conda-lock/) de antemano en otro entorno de [`conda`](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) o en el mismo sistema.

Para instalar el entorno contenido en `plain.lock.yml`, solo haría falta ejecutar el siguiente comando,

```bash
conda-lock install -n <name> plain.lock.yml
```

## Instalación

Hay varios modos de uso para este programa, una vez instalado. El programa esta diseñado como un paquete de python, instalable usando el siguiente comando dentro del directorio en el que se haya clonado el repositorio,

```bash
pip install .
```

Una vez instalado como paquete o desde el directorio del repositorio, se puede ejecutar el programa simplemente llamando al módulo con python,

```bash
python -m plainchecker --help
```

O directamente usando el comando `plainchecker` en la terminal, con el entorno de [`conda`](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) en el que se haya instalado el paquete activado.

También se proporcionan los scripts `plainchecker.sh` para `linux/osx` y `plainchecker.bat` para `win`. Para especificar el entorno con el que se ha de ejecutar el programa usando estos entry points, hay que ajustar la variable de entorno `PLAIN_ENV` para ser igual a la variable de entorno `CONDA_PREFIX` del entorno de ejecución de [`conda`](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) en el que se encuentran las dependencias. Esto permite al usuario poder usar el programa sin tener que activar directamente el entorno de ejecución deseado.

## Uso

Una vez instalado, podemos siempre consultar el modo de uso de `plainchecker` del siguiente modo,

```bash
$ plainchecker --help
Usage: plainchecker [OPTIONS] COMMAND [ARGS]...

  Plainchecker command to control check-in bot.

Options:
  --help  Show this message and exit.

Commands:
  config  Update user configuration for PlainChecker.
  create  Create a new user configuration for PlainChecker.
  lsserv  List all available PlainChecker servers.
  remove  Remove a user configuration from PlainChecker.
  send    Send a command to the PlainChecker server.
  start   Start check-in server to check in automatically with a given...
  stop    Stop a PlainChecker server.
```

Como es aparente de esta página de ayuda, `plainchecker` cuenta con varios subcomandos para utilizar el programa de fichaje automático. A continuación se explican uno por uno.

Se puede controlar la ubicación de los directorios donde se guardan las configuraciones y los logs del programa usando las variables de entorno `PLAINCHECKER_CONFIG_DIR` y `PLAINCHECKER_LOG_DIR`.

### Comandos

Hay varios comandos para controlar el bot y manejar las configuraciones del mismo.

#### `plainchecker create`

Comando utilizado para crear una nueva configuración para un usuario nuevo en PLAIN. A continuación se muestra su uso,

```bash
plainchecker create --work-days 1-5 --exceptions 01/08/2025-10/08/2025 --schedule 10:00-13:00 myusername myemail@example.com
```

Para más detalles, aquí se muestra su página de ayuda,

```bash
$ plainchecker create --help
Usage: plainchecker create [OPTIONS] USERNAME EMAIL

  Create a new user configuration for PlainChecker.

Options:
  -w, --work-days TEXT            Work days for the user, e.g. '1-5' for
                                  Monday to Friday or 3 for Wednesday.
  -x, --exceptions TEXT           Exceptions for the user, e.g. '01/01/2023,
                                  02/01/2023' or '01/01/2023-05/01/2023'.
  -s, --schedule TEXT             Schedule for the user, e.g. '09:00-17:00'
                                  for 9 AM to 5 PM.
  -l, --log-level [NOTSET|DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL]
                                  Logging level for the user configuration.
                                  Default is INFO.
  --help                          Show this message and exit.
```

#### `plainchecker config`

Comando utilizado para modificar la configuración de un usuario existente. A continuación se muestra su uso,

```bash
plainchecker config --work-days 1-3 --workdays 5 myusername myemail@example.com
```

Para más detalles, aquí se muestra su página de ayuda,

```bash
$ plainchecker config --help 
Usage: plainchecker config [OPTIONS] USERNAME EMAIL

  Update user configuration for PlainChecker.

Options:
  -w, --work-days TEXT            Work days for the user, e.g. '1-5' for
                                  Monday to Friday or 3 for Wednesday.
  -x, --exceptions TEXT           Exceptions for the user, e.g. '01/01/2023,
                                  02/01/2023' or '01/01/2023-05/01/2023'.
  -s, --schedule TEXT             Schedule for the user, e.g. '09:00-17:00'
                                  for 9 AM to 5 PM.
  -l, --log-level [NOTSET|DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL]
                                  Logging level for the user configuration.
                                  Default is INFO.
  --help                          Show this message and exit.
```

#### `plainchecker remove`

Comando utilizado para eliminar la configuración de un usuario existente. A continuación se muestra su uso,

```bash
plainchecker remove myusername myemail@example.com
```

Para más detalles, aquí se muestra su página de ayuda,

```bash
$ plainchecker remove --help 
Usage: plainchecker remove [OPTIONS] USERNAME EMAIL

  Remove a user configuration from PlainChecker.

Options:
  -l, --log-level [NOTSET|DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL]
                                  Logging level for the user configuration.
                                  Default is INFO.
  --help                          Show this message and exit.
```

#### `plainchecker start`

Comando utilizado para iniciar el programa que ficha automáticamente cada cierto tiempo. A continuación se muestra su uso,

```bash
plainchecker start --frequency 24
```

Para más detalles, aquí se muestra su página de ayuda,

```bash
$ plainchecker start --help  
Usage: plainchecker start [OPTIONS]

  Start check-in server to check in automatically with a given frequency

Options:
  -f, --frequency FLOAT         How often do you want the bot to check-in the
                                users? (in hours, default: 24)
  -em, --extra-time-mean FLOAT  How many extra minutes on average do you want
                                the machine to addto your check-in schedule?
                                (default: 5)
  -es, --extra-time-std FLOAT   Tune out the std of extra minutes the machine
                                addsto your check-in schedule (default: 1)
  --help                        Show this message and exit.
```

#### `plainchecker stop`

Comando utilizado para parar el programa que ficha automáticamente cada cierto tiempo. A continuación se muestra su uso,

```bash
plainchecker stop --host 127.0.0.1 --port 21201
```

Para más detalles, aquí se muestra su página de ayuda,

```bash
$ plainchecker stop --help  
Usage: plainchecker stop [OPTIONS]

  Stop a PlainChecker server.

Options:
  -H, --host TEXT      Host address of the PlainChecker server. Default is
                       'localhost'.
  -P, --port INTEGER   Port number of the PlainChecker server. Default is
                       5000.
  -t, --timeout FLOAT  Timeout for the server response in seconds. Default is
                       5 seconds.
  --help               Show this message and exit.
```

#### `plainchecker lsserv`

Comando utilizado para visualizar la lista de servidores plainchecker ejecutándose actualmente. A continuación se muestra su uso,

```bash
plainchecker lsserv
```

Para más detalles, aquí se muestra su página de ayuda,

```bash
$ plainchecker lsserv --help
Usage: plainchecker lsserv [OPTIONS]

  List all available PlainChecker servers.

Options:
  -t, --timeout FLOAT  Timeout for the server response in seconds. Default is
                       0.5 seconds.
  --help               Show this message and exit.
```

#### `plainchecker send`

Comando utilizado para enviar comandos a servidores de plainchecker. El comando `stop` para el servidor y el comando `ping` hace que el servidor responda con `pong`. A continuación se muestra su uso,

```bash
plainchecker send --host 127.0.0.1 --port 21201 ping
```

Para más detalles, aquí se muestra su página de ayuda,

```bash
$ plainchecker send --help   
Usage: plainchecker send [OPTIONS] COMMAND

  Send a command to the PlainChecker server.

Options:
  -H, --host TEXT                 Host address of the PlainChecker server.
                                  Default is 'localhost'.
  -P, --port INTEGER              Port number of the PlainChecker server.
                                  Default is 5000.
  -t, --timeout FLOAT             Timeout for the server response in seconds.
                                  Default is 5 seconds.
  -l, --log-level [NOTSET|DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL]
                                  Logging level for the command. Default is
                                  INFO.
  --help                          Show this message and exit.
```