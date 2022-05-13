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
  An=np.zeros([50])
  for n in range(1,51):
    cos=np.cos(n*discre[:,0]*np.pi/180)
    cos_radio=cos*discre[:,1]
    sumatoria=0
    for h in range(cos_radio.shape[0]):
      suma=cos_radio[h]+cos_radio[(h+1)%cos_radio.shape[0]]
      resta=discre[(h+1)%cos_radio.shape[0],0]*np.pi/180-discre[h,0]*np.pi/180
      if (h+1)%cos_radio.shape[0]==0:
        resta=resta+2*np.pi
      producto=suma*resta
      sumatoria=sumatoria+producto
    An[n-1]=sumatoria/(2*np.pi)

  Bn=np.zeros([50])
  for n in range(1,51):
    sin=np.sin(n*discre[:,0]*np.pi/180)
    sin_radio=sin*discre[:,1]
    sumatoria=0
    for h in range(sin_radio.shape[0]):
      suma=sin_radio[h]+sin_radio[(h+1)%sin_radio.shape[0]]
      resta=discre[(h+1)%sin_radio.shape[0],0]*np.pi/180-discre[h,0]*np.pi/180
      if (h+1)%sin_radio.shape[0]==0:
        resta=resta+2*np.pi
      producto=suma*resta
      sumatoria=sumatoria+producto
    Bn[n-1]=sumatoria/(2*np.pi)
  return (An,Bn)

def construir_contorno(frames, video_np):
  r=np.zeros([frames, 180])
  for j in range(frames):
    imagen=video_np[j,:,:]
    imagen = np.uint8(imagen)
    imagen_binarizada = binarizar(imagen, kernel1, kernel2, blocksize,constant)
    contorno = calcularcontorno(imagen_binarizada,j)
    dibujocontorno = dibujarcontorno(contorno,0) #por que esta aca esta?
    coordenadas = calcularcentro (dibujocontorno)
    polares = calcularpolares(contorno[0],coordenadas) #contorno 0 es e mas grande externo, para el interno cambiar a 1. 
    discreto = discretizar(polares,180)
    r[j,:]=(discreto[:,1])# radio y angulos
    AyB=np.zeros([frames, 50, 2])
    An,Bn = calcularcoeficientes(discreto)
    AyB[j,:,0]=An
    AyB[j,:,1]=Bn
  return (r,AyB)

def eliminar(f,c,video_np):
  for i in range(0,c,1):
    video_np=np.delete(video_np,int(f),0)
    cantidad = video_np.shape[0]
  return(video_np,cantidad)
   #verificar variables, globales y locales.


header = st.container()
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
        #st.subheader("Video subido")
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
    st.write (dimensiones) #para verificar 

    st.sidebar.title("Barra de ingresos")
    x = st.sidebar.slider('Imagen en el video', 0, frames-1, 1, key=123)
    st.sidebar.write('Numero de frame:', x+1)

    st.sidebar.title("Tamaño de ventanas")
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
######################################

    video_np = video_np.astype(np.uint8)
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
        st.image(dibujocontorno, caption=f'Contorno de imagen {x}', clamp=True)
  
    r, AyB = construir_contorno(frames, video_np)
    R = r.T # a dibujar
    st.write('dibujo de r')
    st.line_chart(R)  #grafico de radio por frame

    Rpromedio=np.mean(r,axis=1) #dibujar promedio de cada frame
    Rprom=np.mean(Rpromedio) #tiene radio promedio de promedio de cada frame
    st.write(f"Radio promedio: {Rprom}")

    #calculo de coeficientes, genero matriz de coordenadas. 
    
  #boton  elimnar frames, ver que frames esta mal. 
  #se ve el grafico y se ajustan parametrso de filtrado para luego calcular contornos
    inicio = st.sidebar.number_input('Inicio de eliminacion',0)
    rango = st.sidebar.number_input('Cuantos frames siguientes?',0,50)
    
    if st.button('Eliminar frames'):
      video_np, frames = eliminar(inicio,rango,video_np) 
      st.write(f'nuevo tamanio de matriz: {frames}')
      r,AyB = construir_contorno(frames, video_np)
      R = r.T # a dibujar
      st.write('dibujo de r')
      st.line_chart(R)    
      st.write('okay')   
      #no se esta actualizando el numero de frames en barra de video original. 
    else:
      st.write('Nada para eliminar')

    if st.button('Procesar imagenes'):
      st.write('Se calculara valores Vq y de k PROXIMAMENTE')      
    else:
      st.write('nada aun')

# UBICAR FUNCIONES  
    def calculo_Vq (AyB,Rprom):
      AyBn=AyB*(1/Rprom)
      AyBmedia=np.zeros([50,2])
      AyBmedia[:,0]=np.mean(AyBn[:,:,0],axis=0)
      AyBmedia[:,1]=np.mean(AyBn[:,:,1],axis=0)
      #print(AyBmedia)
      AyBresta=np.zeros([AyBn.shape[0],50,2])
      for q in range(50):
        AyBresta[:,q,0]=AyBn[:,q,0]-AyBmedia[q,0]
        AyBresta[:,q,1]=AyBn[:,q,1]-AyBmedia[q,1]
      AyBcuadrado=AyBresta*AyBresta
      Vq=0.25*(np.mean(AyBcuadrado[:,:,0],axis=0)+np.mean(AyBcuadrado[:,:,1],axis=0))
      return Vq

    q_max=50#order of the Legendre function derivation q menor o igual a l identico a m. Era 25 ''''''''''''''orden del polinimio
    l_max=200 # degree of the Legendre function, identico a n ''''''''''''''''''''''''''''''''''''''''''''grado del polinomio
    polypolderi=sc.lpmn(q_max, l_max, 0) #Aqui Pmn es Plq que seria q=m y l=n- --q orden de derev l grado del polonimio----- en 
    #Return two arrays of size (m+1, n+1) containing Pmn(z) and Pmn'(z) for all orders from 0..m and degrees from 0..n.
    #Retorna dos matrices de tamaño (m+1, n+1) que contienen Pmn(z) y Pmn'(z) para todos los órdenes desde 0..m y grados desde 0..n.

    pol=polypolderi[0]
    pol[0,:]# primer numero (q) orden del polinomio (asociado al orden de derivacion del polinomio) y el segundo(l) es el grado (asociado al grado de derivacion del polinomio)
    # se muestran los polinomios de legendre de orden de derivacion 0, es decir,los propiamente dichos polinomios de legendre valuados en x=0
    #matris_k=np.zeros((q_max,2)) #usamos la funcion mas importante
    #for i in range(0,q_max-1):
    #  matris_k[i,1]=calculark (i)
    #  matris_k[i,0]=i
    #print(matris_k)
    #suma=0
    #can=0
    #for j in range(6,25): #parametros van a ser entradas luego de ver el grafico de 6 y 25
    #  suma=suma+matris_k[j,1]
    #  can=can+1
    #promedio=suma/can
    #print (promedio)
    #kpromedio=promedio 
    #plt.figure(figsize=(15,20))
    #plt.scatter(matris_k[:,0],matris_k[:,1])   # Dibuja el gráfico
    #plt.title("k fl binari comun  mediana 21 humbral 19 sin filtro mediana ultimo k 1.2746920005570453e-19 ")   # Establece el título del gráfico
    #plt.ylabel("k")   # Establece el título del eje x
    #plt.xlabel("q")   # Establece el título del eje y
    #plt.ylim(1*(10**(-20)),30*(10**(-20)))
    #plt.xlim(2,40)
    #plt.yticks(np.arange(1*(10**(-18)),25*(10**(-19))))
    #plt.xticks(np.arange(0,50,1))
    #print("k promedio ")
    #print (promedio)
    #st.line_chart()

 
