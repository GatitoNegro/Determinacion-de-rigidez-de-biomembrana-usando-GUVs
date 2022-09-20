# Proyecto-Integrador-Determinacion-de-rigidez-de-biomembrana-usando-GUVs
# guvis guvis

#### Universidad Nacional de Córdoba
#### Facultad de Ciencias Exactas Físicas y Naturales
#### Ingeniería Biomédica


Determinación de la rigidez a la flexión de biomembranas mediante el análisis de la fluctuación de su forma a partir de imágenes provenientes de videos de microscopía


### Autores:
### Amante, Sofia Veronica
### Scurti, Pablo Ezequiel

#### Directora:  Rulloni, Valeria
#### Co-Directora: Wilke, Natalia


#### Se pretende generar una herramienta que permita determinar la rigidez de membranas de vesículas unilamelares gigantes GUVs (por sus siglas en inglés, giant unilamellar vesicles) en presencia de diversos efectores, principalmente péptidos antimicrobianos. \n

Las GUVs son muy utilizadas como modelo de biomembrana debido a que tienen tamaños micrométricos y por tanto pueden observarse mediante microscopía óptica.
El desarrollo de este proyecto se realiza en lenguaje Python y comienza en la utilización de los videos de microscopía proporcionados por el laboratorio de Biomembranas del CIQUIBIC. Se inicia con la codificación de sus imágenes en matrices utilizables para su procesamiento digital en escala de grises que implica el filtrado morfológico y determinación del contorno en una escala bidimensional (ángulo polar, radio). Esta re-parametrización del contorno lo transforma en una señal unidimensional, radio en función del ángulo polar, para ser analizada según la variación en el tiempo de  sus componentes de frecuencia. \n

Luego continúa con el procesamiento matemático de estos datos utilizando un modelo que describe la amplitud cuadrática media de modos armónicos esféricos, la cual depende de la rigidez a la flexión de este tipo de membranas. 
Durante este proceso se utilizan diversidad de herramientas para su desarrollo. Por un lado definiciones, desarrollos y funciones matemáticas como polinomios de Legendre, modos de contorno expandido de Fourier, varianza y metodologías de iteración para definir un resultado en la rigidez a la flexión de las membranas, con el mínimo error. Por otro lado se tienen las herramientas virtuales y de software utilizadas tanto para el desarrollo, visualización y generación de interfaz de interacciones con los usuarios, ellas son Colaboratory, Visual Studio Code, plataforma Github y Streamlit. 
Se obtiene por resultado una herramienta computacional de acceso y uso simple e intuitivo, que cuenta con el manual instructivo de uso explicado paso a paso. 
El usuario o laboratorista puede cargar el video a analizar en formato .mp4 desde  su computador e iniciar el procesamiento del video.  
Dada la variedad en la calidad de la señal y tipos de ruido de los  videos que se pueden obtener por microscopía óptica confocal, se tiene la posibilidad de ajustar parámetros de procesamiento de imágenes, preestablecidos por defecto, para lograr los ajustes adecuados para el video que desea analizar.
Se dispone la información en gráficos e impresiones por pantalla, tanto en etapas intermedias (resultados en cada instancia) como al finalizar el procesamiento (valores de rigidez a la flexión de la membrana), logrando así brindar información complementaria que ayuda al laboratorista en su proceso de análisis o estudio en desarrollo en el cual haga uso de esta información. 
Se habilitan los manuales instructivos de ambas plataformas adjuntos en este mismo repositorio. 

### Córdoba, septiembre de 2022
