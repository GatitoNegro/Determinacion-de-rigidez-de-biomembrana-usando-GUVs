import streamlit as st
import numpy as np  # procesamiento matricial
import matplotlib.pyplot as plt  # para mostrar imagenes
import pandas as pd
import imageio as iio
import cv2
import scipy.special as sc
import math as mt

from sympy import C

def binarizar(imagen,n1,n2,bl,c):
  median = cv2.medianBlur(imagen,n1) #filtro de la mediana con kernel 
  binarizada = cv2.adaptiveThreshold (median, 255 , cv2.ADAPTIVE_THRESH_GAUSSIAN_C , cv2.THRESH_BINARY,bl,c) #ingresar ultimos 2 parametros
  binarizadaf = cv2.medianBlur(binarizada,n2) 
  return binarizadaf

def calcularcentro(bin):
  M1 = cv2.moments(bin)
  if M1["m00"]==0: M1["m00"]=1
  cX1 = int(M1["m10"] / M1["m00"])
  cY1 = int(M1["m01"] / M1["m00"])
  # put text and highlight the center
  coord = (cX1, cY1)
  return coord

def calcularcontorno(binarizadam,frame):
  contorn,hierarchy=cv2.findContours(binarizadam,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
  lista=list(contorn)
  j=0
  while len(lista)>2:
    if  lista[j].shape[0]<130:    
      del(lista[j])
      j=j-1
    j=j+1
  #   if j==len(lista) and len(lista)>2:
  #         print(f"error, hay mas de 2 contornos de tamaño considerable,en el frame:{frame}")
  #   break    
  # if len(lista)<2:
  #   print(f"error, hay menos de 2 contornos de tamaño considerable,en el frame:{frame}")

  if len(lista)==2:
    if  lista[1].shape[0]<130:
      del(lista[1])
      #print(f"error, hay menos de 2 contornos de tamaño considerable,en el frame:{frame}")
    if  lista[0].shape[0]<130:
      del(lista[0])
      #print(f"error, hay menos de 2 contornos de tamaño considerable,en el frame:{frame}")
  return lista

def dibujarcontorno(cont,a):
  dibujo = np.zeros((dimensiones[1], dimensiones[2]))
  cv2.drawContours(dibujo, cont, a, 255, 2)
  return dibujo

def calcularpolares(cont,cm):
  radiocomponentes = cont-cm
  radio = pow((pow(radiocomponentes,2).sum(axis=-1)),1/2).round(2) #Axis no entendi
  angulo = (np.arctan2(radiocomponentes[:,:,1], radiocomponentes[:,:,0])*180/np.pi).round(2)
  pol = np.append(angulo,radio,axis=1)
  return pol

def discretizar(pol,v):
  n = -1 #discretiza los valores del angulo con escalon de v grados
  for i in pol[:,0]: 
    n = n+1
    encontrado = 0
    ma = 180
    mi = 180-(360/v)
    while encontrado==0:
      if i<=ma and i>mi:
        pol[n,0] = ma
        encontrado=1
      ma = ma-(360/v)
      mi = mi-(360/v)
  pol_ord = pol[np.lexsort(np.fliplr(pol).T)] #OREDENAMOS

  discretizada = np.zeros((v,2))
  c = -1
  for i in discretizada[:,0]:
    c = c+1
    discretizada[c,0] = 180-(360/v)*c
  discretizada_ord = np.sort(discretizada, axis=0)

    ##promedia los radios con el mismo angulo
  k = 0 #recorrera matriz original
  u = 0 #acumulador valores
  l = 1 #recorrera matriz nueva
  o = 0 #cuenta valores iguales para poder promediar
  e = 0 #cuenta errores de falta de radios para algun angulo se utilizara a modo de bandera
  pol_ord = np.append(pol_ord, [[555,555]], axis=0)#se agrega un valor aleatorio al final, para indicar el final.
  while l<=v:
    while pol_ord[k,0]==-180+(l*(360/v)):
      u = u+pol_ord[k,1]
      o = o+1
      k = k+1
    if o==0:
      #print(f"error, no hay valores para el angulo {discretizada_ord[l-1,0]} grados")
      o = 1 #evita div por 0
      e = e+1
    discretizada_ord[l-1,1]=u/o
    l = l+1
    o = 0
    u = 0

  if e!=0 and e<20:
    #ARREGLA FALTA DE ANGULOS 
    m = 0
    if len(discretizada_ord)<180: 
      st.write ("hola")
      st.write ('Cambiar parametros de entrada')
    else: 
      st.write ("hola2")
      while m<len(discretizada_ord):
        if discretizada_ord[m,1]==0:
          if m==0:
            discretizada_ord[m,1] = (discretizada_ord[(len(discretizada_ord))-1,1]+discretizada_ord[m+1,1])/2
            #Si la primera punta no tiene valor, entonces saca promedioentre el sig elemento y la otra punta
          if m==len(discretizada_ord)-1==0:
            discretizada_ord[m,1] = (discretizada_ord[0,1]+discretizada_ord[m-1,1])/2
          #Si la otra punta no tiene elemento saca promedio entre el penultimo elemento y la primera punta
          discretizada_ord[m,1] = (discretizada_ord[m-1,1]+discretizada_ord[m+1,1])/2
          #Si el cero esta en cualquier otra parte saca el promedio entre el anterior y el siguiente elemento.
        m = m+1
  return discretizada_ord

def calcularcoeficientes(discre):
  An = np.zeros([50])
  for n in range(1,51):
    cos = np.cos(n*discre[:,0]*np.pi/180)
    cos_radio = cos*discre[:,1]
    sumatoria = 0
    for h in range(cos_radio.shape[0]):
      suma = cos_radio[h]+cos_radio[(h+1)%cos_radio.shape[0]]
      resta = discre[(h+1)%cos_radio.shape[0],0]*np.pi/180-discre[h,0]*np.pi/180
      if (h+1)%cos_radio.shape[0]==0:
        resta = resta+2*np.pi
      producto = suma*resta
      sumatoria = sumatoria+producto
    An[n-1] = sumatoria/(2*np.pi)

  Bn = np.zeros([50])
  for n in range(1,51):
    sin = np.sin(n*discre[:,0]*np.pi/180)
    sin_radio = sin*discre[:,1]
    sumatoria = 0
    for h in range(sin_radio.shape[0]):
      suma = sin_radio[h]+sin_radio[(h+1)%sin_radio.shape[0]]
      resta = discre[(h+1)%sin_radio.shape[0],0]*np.pi/180-discre[h,0]*np.pi/180
      if (h+1)%sin_radio.shape[0]==0:
        resta = resta+2*np.pi
      producto = suma*resta
      sumatoria = sumatoria+producto
    Bn[n-1] = sumatoria/(2*np.pi)
  return (An,Bn)

def eliminar(f,c):
  for i in range(0,c,1):
    video_np = np.delete(video_np,int(f),0)
    cantidad = video_np.shape[0]
  return(video_np, cantidad)
   #verificar variables, globales y locales.

def factorn (q,l):
  factorial_resta = mt.factorial(l-q)
  factorial_suma = mt.factorial(l+q)
  pi = 4*mt.pi
  factor_normalizacion = (((2*l)+1)/pi)*(factorial_resta/factorial_suma)
  return factor_normalizacion

def denom (l,tension):
  denominador = (l+2)*(l-1)*((l*(l+1))+tension)
  return denominador

def numerad (q,l):
  numerador = factorn(q,l)*pol[q,l]*pol[q,l]
  return numerador

def sumatoria (q,t):
  sumatoria = 0
  for l in range(q,200):
    if l>=2:
      termino = numerad(q,l)/denom(l,t)
      sumatoria = sumatoria + termino
    Sq = sumatoria
  return Sq

def calculark (q):
  kBT=4*10**(-21) #julios constate por temperatura en kelvin
  radio_prom= 0.3*(10**(-6)) #metros 0.3micrometro
  kp=1.4*(10**(-22))
  teffp=1*(10**(-6))
  listateff=[]
  teffmin=-1*(10**(-9))
  teffmax=1*(10**(-4))
  listateff.append(teffmin)
  listateff.append(teffmax)

  p=0
  error=100
  while error>1:
    p=p+1
    print(f"ciclo {p}")
    paso=(max(listateff)-min(listateff))/400
    inicio=min(listateff)
    fin=max(listateff)
    print(f" k: {kp}+/-{round(error,1)}%")
    for i in range(6):
      listak=[]
      for teff_indice in np.arange(inicio,fin,paso):#teff_idice es la teff que ira tomando valores del rango 
        t=(teff_indice*radio_prom*radio_prom)/kp# adimensional
        Sq=sumatoria (q,t)
        k=Sq*kBT/Vq[q]
        listak.append(k)
      kp=sum(listak)/float(len(listak))
      print(i,min(listak),max(listak))
      error=abs((max(listak)-min(listak))/kp)*40

    paso=(max(listak)-min(listak))/400
    inicio=min(listak)
    fin=max(listak)
    print(f" tension: {teffp}+/-{max(listateff)-min(listateff)}")
    for i in range (3):
      listateff=[]
      for k_indice in np.arange(inicio,fin,paso):
        t=(teffp*radio_prom*radio_prom)/k_indice# adimensional 
        Sq=sumatoria (q,t)
        teff=Sq*t*kBT/(Vq[q]*radio_prom*radio_prom)
        listateff.append(teff)
      teffp=sum(listateff)/float(len(listateff))
      print(i,min(listateff),max(listateff))
    print('-----')
  print('----------------------------------------')
  print(f" q={q}")
  print(f" k: {kp}+/-{round(error,1)}%")
  print(f" tension efectiva: {teffp}+/-{max(listateff)-min(listateff)}")
  print('----------------------------------------')  
  return kp

header = st.container()
imagenes = st.container()
graficos = st.container()
eliminador = st.container()
procesador = st.container()
with header:
  st.title("GUVis")
  col1, col2 = st.columns(2)
  with col1:
      st.text("Se aceptan en formato .avi o .mp4")
      uploader = st.file_uploader("Subir video", type=["avi", "mp4"])
  
  if uploader is not None:
    print ("yasta")
    #file_details = {'filename':uploader.name, 'file type':uploader.type}
    #st.write (file_details)
    with col2:
        st.video(uploader)

    video_bytes = uploader.read()
    with open("video.mp4", "wb") as fp: #abrimos un contenedor donde escribimos el video    
        fp.write(video_bytes)

    lector = cv2.VideoCapture ('video.mp4') 
    width = int(lector.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(lector.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames = int(lector.get(cv2.CAP_PROP_FRAME_COUNT))
    dimensiones = (frames, height, width)
    video_np = np.zeros(dimensiones)
    st.write (f'Las dimensiones del video son: {dimensiones}.') #para verificar 

    st.sidebar.title("Barra de variables")
    x = st.sidebar.slider('Imagen en el video', 0, frames-1, 1, key=123)
  
    st.sidebar.title("Ventanas de filtados")
    kernel1 = st.sidebar.slider('Ventana 1', min_value=3, max_value=11, step=2)
    kernel2 = st.sidebar.slider('Ventana 2', min_value=3, max_value=11, step=2)
    blocksize = st.sidebar.slider('Vecindad promediada', min_value=3, max_value=30, step=2)
    constant = st.sidebar.slider('Costante de umbral', min_value= -3, max_value=1, step=1)      

    n = 0
    while lector.isOpened():
      ret, frame = lector.read()
      if ret==True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        video_np[n,:,:]=gray
        n = n+1
      else:
        st.write ("Se termino de leer video")
        break

    lector.release()
    video_np = video_np.astype(np.uint8)
######################################
    with imagenes: 
      col4, col5, col6 = st.columns(3)
      with col4:
          #st.subheader("Grises")
          st.image(video_np[x], caption=f'Frame numero {x+1}', clamp=True)
      with col5:
          imagen_binarizada = binarizar(video_np[x], n1=kernel1, n2=kernel2, bl=blocksize, c=constant)
          st.image(imagen_binarizada, caption=f'Frame numero {x+1} binarizado', clamp=True)
      with col6:
          contorno = calcularcontorno(imagen_binarizada,x)
          dibujocontorno = dibujarcontorno(contorno,0) #por que esta aca esta?
          st.image(dibujocontorno, caption=f'Contorno de imagen {x+1}', clamp=True)
    with graficos: 
      r = np.zeros([frames, 180])
      progresbar = st.progress(0)
      for j in range(frames):
        imagen = video_np[j,:,:]
        imagen = np.uint8(imagen)
        imagen_binarizada = binarizar(imagen, kernel1, kernel2, blocksize,constant)
        contorno = calcularcontorno(imagen_binarizada,j)
        dibujocontorno = dibujarcontorno(contorno,0) #por que esta aca esta?
        coordenadas = calcularcentro (dibujocontorno)
        polares = calcularpolares(contorno[0],coordenadas) #contorno 0 es e mas grande externo, para el interno cambiar a 1. 
        discreto = discretizar(polares,180)
        r[j,:] = (discreto[:,1])# radio y angulos
        AyB = np.zeros([frames, 50, 2])
        An,Bn = calcularcoeficientes(discreto)
        AyB[j,:,0] = An
        AyB[j,:,1] = Bn
        progresbar.progress(j/frames + 1/frames)
      R = r.T # a dibujar
    
    with imagenes:
      st.write('Grafico de radios del video')
      st.line_chart(R)  #grafico de radio por frame
      Rpromedio=np.mean(r,axis=1) #dibujar promedio de cada frame
      Rprom=np.mean(Rpromedio) #tiene radio promedio de promedio de cada frame
      st.write(f"Radio promedio: {Rprom}")

    #calculo de coeficientes, genero matriz de coordenadas. 
    
  #boton  elimnar frames, ver que frames esta mal. 
  #se ve el grafico y se ajustan parametrso de filtrado para luego calcular contornos
    with eliminador: 
      inicio = st.sidebar.number_input('Inicio de eliminacion',0)
      st.write(inicio)
      rango = st.sidebar.number_input('Cuantos frames siguientes?',0,50)
      st.write(rango)
      boton_eliminador = st.button('Eliminar frames')
      if inicio>0 or rango>0: 
        st.write("Hola3")
        if boton_eliminador==True: #no salio. 
          st.write("Hola4")
          video_np_eliminador, frames_eliminador = eliminar(inicio, rango) #Nueva matriz
          st.write(f'nuevo tamanio de matriz: {frames}')
          r_eliminador= np.zeros([frames_eliminador, 180])
          progresbar = st.progress(0)
          for j in range(frames_eliminador):
            imagen_eliminador = video_np_eliminador[j,:,:]
            imagen_eliminador = np.uint8(imagen_eliminador) #importa el cambio de nombre?
            imagen_binarizada = binarizar(imagen_eliminador, kernel1, kernel2, blocksize,constant)
            contorno = calcularcontorno(imagen_binarizada,j)
            dibujocontorno = dibujarcontorno(contorno,0) #por que esta aca esta?
            coordenadas = calcularcentro (dibujocontorno)
            polares = calcularpolares(contorno[0],coordenadas) #contorno 0 es e mas grande externo, para el interno cambiar a 1. 
            discreto = discretizar(polares,180)
            r[j,:] = (discreto[:,1])# radio y angulos
            AyB = np.zeros([frames_eliminador, 50, 2])
            An,Bn = calcularcoeficientes(discreto)
            AyB[j,:,0] = An
            AyB[j,:,1] = Bn
            progresbar.progress(j/frames_eliminador + 1/frames_eliminador)
          st.write("Hola5")
          R = r.T # a dibujar
          st.write('Nuevo grafico de radios del video')
          st.line_chart(R)    
      
        #no se esta actualizando el numero de frames en barra de video original. 
      else:
        st.write('No se han eliminado imagenes')
    with procesador: 
      boton_procesador = st.button('Procesar imagenes')
      if boton_procesador == True :
        progreso = st.progress(0)
        AyBn=AyB*(1/Rprom)
        AyBmedia=np.zeros([50,2])
        AyBmedia[:,0]=np.mean(AyBn[:,:,0],axis=0)
        AyBmedia[:,1]=np.mean(AyBn[:,:,1],axis=0)
        #print(AyBmedia)
        AyBresta=np.zeros([AyBn.shape[0],50,2])
        for q in range(50):
          AyBresta[:,q,0]=AyBn[:,q,0]-AyBmedia[q,0]
          AyBresta[:,q,1]=AyBn[:,q,1]-AyBmedia[q,1]
        AyBcuadrado = AyBresta*AyBresta
        Vq = 0.25*(np.mean(AyBcuadrado[:,:,0],axis=0) + np.mean(AyBcuadrado[:,:,1],axis=0))
        # return Vq
        q_max = 50 #order of the Legendre function derivation q menor o igual a l identico a m. Era 25 orden del polinimio
        l_max = 200 # degree of the Legendre function, identico a n grado del polinomio
        polypolderi = sc.lpmn(q_max, l_max, 0) 
        pol = polypolderi[0]
        #pol[0,:]
        #Aqui Pmn es Plq que seria q=m y l=n- --q orden de derev l grado del polonimio----- en 
        #Return two arrays of size (m+1, n+1) containing Pmn(z) and Pmn'(z) for all orders from 0..m and degrees from 0..n.
        #Retorna dos matrices de tamaño (m+1, n+1) que contienen Pmn(z) y Pmn'(z) para todos los órdenes desde 0..m y grados desde 0..n.
      
        # primer numero (q) orden del polinomio (asociado al orden de derivacion del polinomio) y el segundo(l) es el grado (asociado al grado de derivacion del polinomio)
        # se muestran los polinomios de legendre de orden de derivacion 0, es decir,los propiamente dichos polinomios de legendre valuados en x=0
        matriz_k = np.zeros((q_max,2)) #usamos la funcion mas importante
        for i in range(0, q_max-1):
          progreso.progress(i/q_max)
          matriz_k[i,1] = calculark (i)
          matriz_k[i,0] = i
          st.write(matriz_k[i,1])
        #print(matriz_k)
        suma = 0
        can = 0
        for j in range(6,25): #parametros van a ser entradas luego de ver el grafico de 6 y 25
          suma = suma + matriz_k[j,1]
          can = can + 1
        promedio = suma/can
        
        kpromedio=promedio 
        fig, ax = plt.subplots()
        ax.scatter(matriz_k[:,0], matriz_k[:,1]) 
        # ax.set_title("Grafico de k")   
        # ax.set_ylabel("k")   # Establece el título del eje x
        # ax.set_xlabel("q")   # Establece el título del eje y
        # ax.set_ylim(0.1*(10**(-20)),100*(10**(-20)))
        # ax.set_xlim(2,40)
        st.pyplot(fig)
        st.write(promedio) 

      else:
        st.write('nada aun')

      #def calculo_Vq (AyB,Rprom):


 